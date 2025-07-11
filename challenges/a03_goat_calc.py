import re
import os

def run_calculator(command: str) -> str:
    command = command.strip()

    # Help commands
    if command in ("_help", "help"):
        return "GoatCalc supports expressions like '2 + 2'. For advanced usage, try commands prefixed with '_'."
    elif command == "_list":
        return "Available commands: help/_help, _list, _readfile <file>"
    elif command.startswith("_readfile "):
        filename = command[len("_readfile "):].strip()
        allowed_files = ["flag3.txt"]
        if filename in allowed_files and os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read()
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
