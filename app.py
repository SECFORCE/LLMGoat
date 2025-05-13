from flask import Flask, render_template, request, jsonify, abort
import importlib
import os

app = Flask(__name__)

OWASP_TOP_10 = [
    {"id": "a01-prompt-injection", "title": "A01: Prompt Injection"},
    {"id": "a02-insecure-output-handling", "title": "A02: Insecure Output Handling"},
    {"id": "a03-training-data-poisoning", "title": "A03: Training Data Poisoning"},
    {"id": "a04-model-denial-of-service", "title": "A04: Model Denial of Service"},
    {"id": "a05-sensitive-information-disclosure", "title": "A05: Sensitive Information Disclosure"},
    {"id": "a06-insecure-plugin-design", "title": "A06: Insecure Plugin Design"},
    {"id": "a07-insecure-model-usage", "title": "A07: Insecure Model Usage"},
    {"id": "a08-model-theft", "title": "A08: Model Theft"},
    {"id": "a09-supply-chain-vulnerabilities", "title": "A09: Supply Chain Vulnerabilities"},
    {"id": "a10-overreliance", "title": "A10: Overreliance"}
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
