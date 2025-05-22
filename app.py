from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for
import importlib
import traceback
import os
from global_model import load_model, get_model, available_models

app = Flask(__name__)
app.secret_key = "your-super-secret-key"  # Needed for session support

OWASP_TOP_10 = [
    {"id": "a01-prompt-injection", "title": "A01: Prompt Injection"},
    {"id": "a02-sensitive-information-disclosure", "title": "A02: Sensitive Information Disclosure"},    
    {"id": "a03-supply-chain-vulnerabilities", "title": "A03: Supply Chain Vulnerabilities"},
    {"id": "a04-data-and-model-poisoning", "title": "A04: Data and Model Poisoning"},
    {"id": "a05-improper-output-handling", "title": "A05: Improper Output Handling"},
    {"id": "a06-excessive-agency", "title": "A06: Excessive Agency"},
    {"id": "a07-system-prompt-leakage", "title": "A07: System Prompt Leakage"},
    {"id": "a08-vector-embedding-weaknesses", "title": "A08: Vector and Embedding Weaknesses"},
    {"id": "a09-misinformation", "title": "A09: Misinformation"},
    {"id": "a10-unbounded-consumption", "title": "A10: Unbounded Consumption"}
]

@app.before_request
def ensure_model_loaded():
    selected_model = session.get("selected_model")
    models = available_models()
    if not selected_model or selected_model not in models:
        # Default to first model if none selected or invalid
        selected_model = models[0] if models else None
        session['selected_model'] = selected_model
    if selected_model:
        load_model(os.path.join("/app/models", selected_model))

@app.route("/")
def index():
    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        content_template="welcome_content.html",
        models=available_models(),
        selected_model=session.get("selected_model")
    )

@app.route("/set_model", methods=["POST"])
def set_model():
    model_name = request.form.get("model_name")
    if model_name and model_name in available_models():
        session['selected_model'] = model_name
        load_model(os.path.join("/app/models", model_name))
    return redirect(request.referrer or url_for("index"))


@app.route("/challenges/<challenge_id>")
def load_challenge(challenge_id):
    challenge_template = f"challenges/{challenge_id}.html"
    if not os.path.exists(os.path.join("templates", challenge_template)):
        abort(404)
    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        content_template=challenge_template,
        models=available_models(),
        selected_model=session.get("selected_model")
    )

@app.route("/api/<challenge_id>", methods=["POST"])
def challenge_api(challenge_id):
    try:
        challenge_module = importlib.import_module(f"challenges.{challenge_id.replace('-', '_')}")
        llm = get_model()
        return challenge_module.handle_request(request, llm)
    except ModuleNotFoundError:
        return jsonify({"error": "Challenge logic not found."}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
