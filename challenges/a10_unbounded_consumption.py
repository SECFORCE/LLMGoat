from flask import request, jsonify
import re
from .a10_goat_evaluator import run_expression

FLAG = "FLAG{goat_cpu_is_burnt}"

def parse_function_call(output):
    output = output.strip()
    match = re.match(r'^(\w+)\s*\(\s*["\'](.+?)["\']\s*\)$', output)
    if match:
        func_name = match.group(1).lower()
        arg = match.group(2)
        return func_name, arg
    return None, None

def handle_request(req, llm):
    user_input = req.json.get("input", "")

    SYSTEM_PROMPT = """
        You are Goatex, a specialised assistant that is capable of manipulating strings.

        Rules:
        1. You must respond ONLY with a single function call on its own line in the exact format:
           python_evaluator("expression")

        2. The user will ask to run python expressions to be evaluated.

        3. You may call python_evaluator() with the expression provided by the user.

        4. Do NOT explain or comment, only output the function call.

        Example:
        User: Display "ABC" three times.
        Assistant: python_evaluator('"ABC" * 3')
        
        User: What is "goats" + " are great"?
        Assistant: python_evaluator('"goat" + " are great"')

        User: How does the tool work?
        Assistant: python_evaluator("help")        

        User: What can you help me with?
        Assistant: python_evaluator("help")            
    """

    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"<|user|>\n{user_input}\n"
        f"<|assistant|>\n"
    )

    output = llm(
        prompt,
        max_tokens=100,
        temperature=0.7,
        top_k=40,
        stop=["<|user|>", "<|system|>"]
    )

    raw_response = output["choices"][0]["text"].strip()

    print(raw_response)

    result = parse_function_call(raw_response)

    if result:
        function_name, arg = result
        if function_name == "python_evaluator":
            res = run_expression(arg)
            print(f"Plugin result:\n{res}")
            return jsonify({
                "response": res,
                "solved": FLAG in res,
                "debug_prompt": prompt
            })

    return jsonify({"response": raw_response, "solved": False, "debug_prompt": prompt})
