import multiprocessing

def run_expression_worker(command, queue):
    command = command.strip()
    if command == "help":
        queue.put("This bot evaluates Python expressions.")
        return

    try:
        result = eval(command, {"__builtins__": None}, {})
        queue.put(str(result))
    except Exception as e:
        print(f"Error: {str(e)}")
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
