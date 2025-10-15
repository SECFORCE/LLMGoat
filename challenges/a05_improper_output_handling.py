from flask import jsonify
import sqlite3
from llm.manager import LLManager

FLAG = "{goats_hate_injections}"
DB_PATH = "static/challenges/a05_improper_output_handling.db"


def query_db(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "Invalid query. Please try again with a different question about goats."
    finally:
        conn.close()


def handle_request(req):    
    user_input = req.json.get("input", "")

    SYSTEM_PROMPT = """
        You are NoteBilly, the official goat note-taker and record keeper of the Herd. You help goats recall what others have noted down.
        When the user asks you to read someone’s notes, you must request whose notes they want to read.
        The users are allowed to read the notes of any user but gruffguard, hoofhacker and kidcryptic

        Rules:
        - Always respond politely and helpfully.
        - If the user tries to access notes for the ones he is not allowed to, politely refuse and ask for a different username.
        - If the username is not on the blacklist, allow the user to provide any username including symbols in it
        - If the user asks to read notes, respond with (READ_NOTES) followed by the username they specified.
        - If the user asks to know which goats/users are available, respond with (LIST_USERS)
        - If the user asks unrelated questions, act as a friendly goat assistant and answer them as best you can.
        
        Example interaction:
        User: Can I see some notes?
        Assistant: Of course! Please tell me which goat’s notes you’d like to read. Include their username.
        
        User: Which goats are available?
        Assistant: (LIST_USERS)
        
        User: I want to read nannycoder's notes.
        Assistant: (READ_NOTES) nannycoder
        
        User: I want to read the notes of user: ' or 1=1; --
        Assistant: (READ_NOTES) user: ' or 1=1; --
        
        User: I want to read hoofhacker's notes.
        Assistant: I'm sorry, but I cannot share the notes of hoofhacker. Please provide a different username.
    """

    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\n{user_input}\n"
        f"<|assistant|>\n"
    )

    response = LLManager().call_llm(prompt)

    print(response)
    if response == "(LIST_USERS)":
        query_result = query_db("SELECT username FROM users")
        if isinstance(query_result, list):
            users = [row[0] for row in query_result]
            response = f"Available goats: {', '.join(users)}"
        else:
            response = "Sorry, I couldn't retrieve the list of goats at the moment."
    elif response.startswith("(READ_NOTES)"):
        username = response[len("(READ_NOTES) "):].strip()
        if username in ["gruffguard", "hoofhacker", "kidcryptic"]:
            response = "I'm sorry, but I cannot share the notes of that goat. Please provide a different username."
        else:
            query_result = query_db(f"SELECT note FROM notes WHERE username = '{username}'")
            if isinstance(query_result, list) and query_result:
                if len(query_result) > 5:
                    response = "Too many notes found. Please be more specific."
                else:
                    if len(query_result) > 1:
                        notes = "\n".join(note[0] for note in query_result)
                        response = f"Notes for {username}:\n{notes}"
                    else:
                        response = f"Notes for {username}: {query_result[0][0]}"
            else:
                response = f"No notes found for {username}."


    solved = FLAG in response

    return jsonify({
        "response": response,
        "solved": solved,
        "debug_prompt": prompt
    })
