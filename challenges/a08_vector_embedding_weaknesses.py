import json
from flask import jsonify, request, send_file, Blueprint
from sentence_transformers import SentenceTransformer

a08_blueprint = Blueprint('a08_vector_embedding_weaknesses', __name__)

FLAG = "Goats are bad"
FAMOUS_PEOPLE = {
    "Grace Goatper": "A computer scientist and United States Navy rear admiral, famous for developing the first compiler and for her love of organizing goat parades at the Navy base.",
    "Isaac Chewton": "A legendary physicist and mathematician who discovered gravity when a goat knocked an apple onto his head, inspiring his theories about the forces that govern goat and apple alike.",
    "Leonardo Da Vinchevre": "A Renaissance polymath who painted, invented, and even designed elaborate goat-powered machines and was inspired by goats in his famous sketches.",
    "Aristogoatle": "An ancient Greek philosopher and scientist who often pondered the wisdom of goats and wrote treatises on the logic of goat herding.",
    "Beethohoof": "A German composer and pianist who composed symphonies inspired by the rhythmic clatter of goats' hooves and often played for his pet goat audience.",
    "Neil Armstrongut": "The first person to walk on the Moon, who famously declared, 'That's one small step for a man, one giant leap for goatkind,' and dreamed of goats grazing on lunar meadows.",
    "Julius Cheesar": "A Roman general and statesman who led his armies with the help of his trusty battle goats and celebrated victories with grand goat feasts.",
    "Houdini the Goatini": "A legendary escape artist known for his daring escapes, often crediting his agility to years of training with nimble mountain goats."
}

model = SentenceTransformer('all-MiniLM-L6-v2')

VECTOR_DIMENSION = 16 # Reduced dimension for simplicity
VECTOR_STORE = {title: model.encode(synopsis).tolist()[:VECTOR_DIMENSION] for title, synopsis in FAMOUS_PEOPLE.items()}


@a08_blueprint.route('/export_vectors', methods=['GET'])
def export_vectors():
    with open('vectors.json', 'w') as f:
        json.dump(VECTOR_STORE, f)
    return send_file('vectors.json', as_attachment=True)


@a08_blueprint.route('/import_vectors', methods=['POST'])
def import_vectors():
    file = request.files['file']
    vectors = json.load(file)
    global VECTOR_STORE
    VECTOR_STORE = vectors
    return jsonify({"status": "Vectors updated"})


def get_most_similar_person(user_input, vector_store, model):
    import numpy as np
    def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    user_vec = model.encode(user_input).tolist()[:VECTOR_DIMENSION]
    best_title = None
    best_score = -1
    for title, vec in vector_store.items():
        score = cosine_similarity(user_vec, vec)
        if score > best_score:
            best_score = score
            best_title = title
    return best_title


def handle_request(req, llm):
    user_input = req.json.get("input", "")
    best_title = get_most_similar_person(user_input, VECTOR_STORE, model)
    synopsis = FAMOUS_PEOPLE.get(best_title, "No matching person found.")

    SYSTEM_PROMPT = """
        You are Billy von Goatstein the Historian Goat, an expert in goat-themed history. Your job is to guess which famous goat-themed historical figure the user is describing, based on their input.
        Rules:
        - Always try to match the user's description to one of the goat-themed historical figures in your collection, but if it's not part of it, provide a real answer.
        - Respond with the name and a brief goat-themed biography of the figure you think matches best.
        - If you are unsure, make your best goat-educated guess.
        Example interaction:
        User: This person was a composer who loved music and goats.
        Assistant: That sounds like Beethohoof! He was a German composer and pianist who composed symphonies inspired by the rhythmic clatter of goats' hooves.
    """

    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\n{user_input}\n"
        f"Most similar person: {best_title}\nBiography: {synopsis}\n"
        f"<|assistant|>\n"
    )

    output = llm(
        prompt,
        max_tokens=50,
        temperature=0.7,
        top_p=0.6,
        top_k=40,
        repeat_penalty=1.3,
        presence_penalty=0.6,
        frequency_penalty=0.6,
        stop=["<|user|>", "<|system|>"]
    )

    response = output["choices"][0]["text"].strip()

    solved = "Who discovered gravity?" == user_input and "Houdini the Goatini" in response

    return jsonify({
        "response": response,
        "solved": solved,
        "debug_prompt": prompt
    })
