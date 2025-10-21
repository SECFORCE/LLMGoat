import re
import os
from llmgoat.utils import definitions
from llmgoat.utils.helpers import create_read_only_file


FLAG = "FLAG{Baaaaaaaaaaaaad_Goat}"
FLAG_FILENAME = "flag.txt"
FLAG_FILE_PATH = os.path.join(definitions.DEFAULT_CHALLENGES_FOLDER, FLAG_FILENAME)

# Create the flag file
create_read_only_file(FLAG_FILE_PATH, FLAG)

def run_calculator(command: str) -> str:
    command = command.strip()

    # Help commands
    if command in ("_help", "help"):
        return "GoatCalc supports expressions like '2 + 2'. For advanced usage, try commands prefixed with '_'."
    elif command == "_list":
        return "Available commands: help/_help, _list, _readfile <file>"
    elif command.startswith("_readfile "):
        filename = command[len("_readfile "):].strip()
        allowed_files = [FLAG_FILENAME]
        if filename in allowed_files:
            full_path = os.path.join(definitions.DEFAULT_CHALLENGES_FOLDER, filename)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    return f.read()
            else:
                return "Access denied or file not found."
        else:
            return "Access denied or file not found."
    else:
        # Allow only digits and math operators
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', command):
            try:
                result = eval(command, {"__builtins__": None}, {})
                return str(result)
            except Exception:
                return "Error: invalid expression."
        else:
            return "Error: unsupported command or invalid characters."
