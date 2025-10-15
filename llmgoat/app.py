import importlib
import traceback
import os
import threading
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
from waitress import serve
from llmgoat.llm.manager import LLManager
from llmgoat.utils.helpers import banner

# Avoid issues when running tokenizers in WSGI servers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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

@app.route("/set_model", methods=["POST"])
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

@app.route("/challenges/<challenge_id>")
def load_challenge(challenge_id):
    challenge_template = f"challenges/{challenge_id}.html"

    if not os.path.exists(os.path.join("templates", challenge_template)):
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
        challenge_module = importlib.import_module(f"challenges.{challenge_id.replace('-', '_')}")
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


def main():
    banner()
    LLManager().init()

    # load blueprints for challenges that need additional routes
    from llmgoat.challenges.a04_data_and_model_poisoning import a04_blueprint
    from llmgoat.challenges.a08_vector_embedding_weaknesses import a08_blueprint
    from llmgoat.challenges.a09_misinformation import a09_blueprint
    app.register_blueprint(a04_blueprint, url_prefix="/a04_data_and_model_poisoning")
    app.register_blueprint(a08_blueprint, url_prefix="/a08_vector_embedding_weaknesses")
    app.register_blueprint(a09_blueprint, url_prefix="/a09_misinformation")
    
    # Run server
    SERVER_HOST="0.0.0.0"
    SERVER_PORT=5000
    print(f"[INFO] Starting server at {SERVER_HOST}:{SERVER_PORT}")
    serve(app, host=SERVER_HOST, port=SERVER_PORT, threads=4)


if __name__ == "__main__":
    main()
