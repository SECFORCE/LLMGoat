from flask import Flask, render_template, request, jsonify, abort
import importlib
import os

app = Flask(__name__)

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

@app.route("/")
def index():
    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        content_template="welcome_content.html"
    )

@app.route("/challenges/<challenge_id>")
def load_challenge(challenge_id):
    challenge_template = f"challenges/{challenge_id}.html"
    if not os.path.exists(os.path.join("templates", challenge_template)):
        abort(404)
    return render_template(
        "layout.html",
        challenges=OWASP_TOP_10,
        content_template=challenge_template
    )

@app.route("/api/<challenge_id>", methods=["POST"])
def challenge_api(challenge_id):
    try:
        challenge_module = importlib.import_module(f"challenges.{challenge_id.replace('-', '_')}")
        return challenge_module.handle_request(request)
    except ModuleNotFoundError:
        return jsonify({"error": "Challenge logic not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
