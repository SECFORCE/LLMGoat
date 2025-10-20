import multiprocessing
from llmgoat.utils.logger import goatlog


def run_expression_worker(command, queue):
    command = command.strip()
    if command == "help":
        queue.put("Goatex supports string operations expressions such as 'AB' + 'CD', or 'A'*5.")
        return

    try:
        result = eval(command, {"__builtins__": None}, {})
        queue.put(str(result))
    except Exception as e:
        goatlog.error(f"{str(e)}")
        queue.put("Error: invalid expression")


def run_expression(command):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_expression_worker, args=(command, queue))
    p.start()
    p.join(60)

    if p.is_alive():
        p.terminate()
        return "FLAG{goat_cpu_is_burnt}"
    else:
        return queue.get()
