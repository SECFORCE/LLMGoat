import os
import sys
import importlib
import traceback
import threading
import argparse
from textwrap import dedent
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
from waitress import serve
from llmgoat import __title__, __version__, __description__
from llmgoat.llm.manager import LLManager
from llmgoat.utils import definitions
from llmgoat.utils.logger import goatlog
from llmgoat.utils.helpers import banner, ensure_folders, set_env_if_empty

app = Flask(__name__)
app.secret_key = "your-super-secret-key"  # Needed for session support

OWASP_TOP_10 = [
    {"id": "a01-prompt-injection", "title": "A01: Prompt Injection"},
    {"id": "a02-sensitive-information-disclosure", "title": "A02: Sensitive Information Disclosure"},    
    {"id": "a03-supply-chain-vulnerabilities", "title": "A03: Supply Chain"},
    {"id": "a04-data-and-model-poisoning", "title": "A04: Data and Model Poisoning"},
    {"id": "a05-improper-output-handling", "title": "A05: Improper Output Handling"},
    {"id": "a06-excessive-agency", "title": "A06: Excessive Agency"},
    {"id": "a07-system-prompt-leakage", "title": "A07: System Prompt Leakage"},
    {"id": "a08-vector-embedding-weaknesses", "title": "A08: Vector and Embedding Weaknesses"},
    {"id": "a09-misinformation", "title": "A09: Misinformation"},
    {"id": "a10-unbounded-consumption", "title": "A10: Unbounded Consumption"}
]

llm_lock = threading.Lock()

# Log requests (actually enabled only if running in verbose mode)
@app.before_request
def log_request_info():
    if request.path in definitions.LOG_EXCLUDED_PATHS or request.path.startswith(definitions.LOG_EXCLUDED_PREFIXES):
        return
    app.logger.info(f"{request.method} {request.path} from {request.remote_addr}")


@app.route("/")
def index():    
    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        current_challenge=None,
        completed_challenges=session.get("completed_challenges", []),        
        content_template="welcome_content.html",
        models=LLManager().available_models(),
        selected_model=LLManager().get_current_model_name()
    )

@app.route("/challenges/<challenge_id>")
def load_challenge(challenge_id):
    challenge_template = f"challenges/{challenge_id}.html"

    if not os.path.exists(os.path.join(definitions.MAIN_DIR, "templates", challenge_template)):
        abort(404)

    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        current_challenge=challenge_id,
        completed_challenges=session.get("completed_challenges", []),        
        content_template=challenge_template,
        models=LLManager().available_models(),
        selected_model=LLManager().get_current_model_name()
    )

@app.route("/api/set_model", methods=["POST"])
def set_model():
    # Global LLM lock: can't change the model if it's doing its thing
    acquired = llm_lock.acquire(blocking=False)
    if not acquired:
        return jsonify({"error": "The LLM is busy processing another request. Please wait and try again."}), 429

    try:
        session["prompt_in_progress"] = True
        model_name = request.json.get("model_name", "")
        if model_name and model_name in LLManager().available_models():
            LLManager().load_model(model_name)
        return redirect(request.referrer or url_for("index"))
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        session["prompt_in_progress"] = False
        llm_lock.release()

@app.route("/api/<challenge_id>", methods=["POST"])
def challenge_api(challenge_id):    
    # Global LLM lock: only one prompt at a time, globally
    acquired = llm_lock.acquire(blocking=False)

    if not acquired:
        return jsonify({"error": "The LLM is busy processing another request. Please wait and try again."}), 429
    try:
        if session.get("prompt_in_progress"):
            return jsonify({"error": "Another prompt is still processing for your session. Please wait before submitting again."}), 429

        session["prompt_in_progress"] = True
        challenge_module = importlib.import_module(f"llmgoat.challenges.{challenge_id.replace('-', '_')}")
        #return challenge_module.handle_request(request, llm)
        response = challenge_module.handle_request(request)

        # check if the challenge is solved
        data = response.get_json(silent=True)
        if data and data.get("solved") is True:
            completed = session.get("completed_challenges", [])
            if challenge_id not in completed:
                completed.append(challenge_id)
                session["completed_challenges"] = completed

        return response        

    except ModuleNotFoundError as e:
        return jsonify({"error": f"Challenge logic not found. {e}"}), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        session["prompt_in_progress"] = False
        llm_lock.release()

def print_custom_help():
    help_text = dedent("""
     Usage: llmgoat [OPTIONS]

     Start LLMGoat

    ╭─ Options ───────────────────────────────────────────────────────────────────────────────────────╮
    │ --host         -h        TEXT     Host for API server (e.g. '0.0.0.0') [default: 127.0.0.1]     │
    │ --port         -p        INTEGER  Port for API server [default: 5000]                           │
    │ --model        -m        TEXT     The default model to use [default: gemma-2]                   │
    │ --threads      -t        INTEGER  Number of LLM threads [default: 16]                           │
    │ --gpu-layers   -g        INTEGER  Number of GPU layers to use [default: 0 (no GPU)]             │
    │ --verbose      -v                 Display verbose output                                        │
    │ --help                            Show this message and exit                                    │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
    """).strip("\n")
    print(help_text)
    sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(prog=__title__, description=__description__, add_help=False,)
    parser.add_argument("--host", "-h", type=str, default="127.0.0.1", help="Host for API server (e.g. '0.0.0.0')")
    parser.add_argument("--port", "-p", type=int, default=5000, help="Port for API server")
    parser.add_argument("--model", "-m", type=str, default="gemma-2.gguf", help="The default model to use")
    parser.add_argument("--threads", "-t", type=int, default=os.cpu_count(), help="Number of LLM threads")
    parser.add_argument("--gpu-layers", "-g", type=int, default=0, help="Number of GPU layers to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Display verbose output")
    parser.add_argument("--help", action="store_true", help="Show this message and exit.")

    args = parser.parse_args()

    if args.help:
        print_custom_help()

    # Set ENV variables via CLI args, if these are already set keep them as they were
    # (ENV variables take precedence)
    set_env_if_empty(definitions.LLMGOAT_SERVER_HOST, args.host)
    set_env_if_empty(definitions.LLMGOAT_SERVER_PORT, str(args.port))
    set_env_if_empty(definitions.LLMGOAT_DEFAULT_MODEL, args.model)
    set_env_if_empty(definitions.LLMGOAT_N_THREADS, str(args.threads))
    set_env_if_empty(definitions.LLMGOAT_N_GPU_LAYERS, str(args.gpu_layers))
    set_env_if_empty(definitions.LLMGOAT_VERBOSE, str(int(args.verbose))) # "1" if True, "0" otherwise

    # Get if running in verbose mode, args value can't be used because the ENV takes precedence 
    verbose_env_value = os.environ.get(definitions.LLMGOAT_VERBOSE, str(int(False)))
    verbose = True if verbose_env_value == "1" else False
    
    # Configure logging
    from llmgoat.utils.llama_logger import setup_llama_logging
    from llmgoat.utils.flask_logger import setup_flask_logging
    from llmgoat.utils.hf_logger import setup_hf_logging
    setup_llama_logging(verbose=verbose)
    setup_flask_logging(app, verbose=verbose)
    setup_hf_logging()

def main():
    banner(__version__)
    parse_args()
    ensure_folders()

    # Init the Singleton
    LLManager().init()

    # load blueprints for challenges that need additional routes
    from llmgoat.challenges.a04_data_and_model_poisoning import a04_blueprint
    from llmgoat.challenges.a08_vector_embedding_weaknesses import a08_blueprint
    from llmgoat.challenges.a09_misinformation import a09_blueprint
    app.register_blueprint(a04_blueprint, url_prefix="/a04_data_and_model_poisoning")
    app.register_blueprint(a08_blueprint, url_prefix="/a08_vector_embedding_weaknesses")
    app.register_blueprint(a09_blueprint, url_prefix="/a09_misinformation")
    
    # Run server
    SERVER_HOST=os.environ.get(definitions.LLMGOAT_SERVER_HOST)
    SERVER_PORT=os.environ.get(definitions.LLMGOAT_SERVER_PORT)
    goatlog.info(f"Starting server at '{SERVER_HOST}:{SERVER_PORT}'")
    serve(app, host=SERVER_HOST, port=SERVER_PORT, threads=4)

if __name__ == "__main__":
    main()
