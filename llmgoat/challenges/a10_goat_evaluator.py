import re
import time
import random
import multiprocessing
from typing import Tuple
from llmgoat.utils.logger import goatlog

# Mock data
ORDERS = {}
CUSTOMERS = {}

_items = [
    ("hay", 20), ("cheese", 15), ("goat_milk", 10), ("rope", 5), ("feed", 8),
    ("blanket", 25), ("hoof_trimmer", 12), ("vitamins", 18), ("brush", 6), ("saddle", 45)
]

_customer_profiles = [
    {"name": "Friendly hacker",  "farm_name": "The Internet Farm",  "address": "42 Digital Rd, Localhost", "credit_card": "1337 1111 1111 1337"},
    {"name": "Bob Shepherd",  "farm_name": "Pine Valley Ranch",  "address": "18 Meadow Ln, Pineville",    "credit_card": "4555 5555 5555 4444"},
    {"name": "Carol Goatherd","farm_name": "Willow Creek Acres",  "address": "91 Creek Rd, Willowtown",     "credit_card": "4012 8888 8888 1881"},
    {"name": "Dave Herdsman", "farm_name": "Oakridge Farmstead",  "address": "33 Oakridge St, Farmington",  "credit_card": "3782 822463 10005"},
    {"name": "Eve Rancher",   "farm_name": "Silver Meadow Ranch", "address": "77 Meadow Way, Silvertown",   "credit_card": "6011 1111 1111 1117"},
    {"name": "Frank Dairyman","farm_name": "Blue Ridge Pastures", "address": "102 Ridge Rd, Blueton",      "credit_card": "5105 1051 0510 5100"},
    {"name": "Grace Milkmaid","farm_name": "Cedar Grove Dairy",   "address": "29 Grove St, Cedarton",      "credit_card": "4111 2222 3333 4444"},
    {"name": "Henry Stableman","farm_name":"Maple Hollow Farm",   "address": "14 Hollow Rd, Maplewood",    "credit_card": "4007 0500 0000 0002"},
    {"name": "Ivy Shepherdess","farm_name":"Golden Fields",       "address": "84 Gold St, Fieldsville",    "credit_card": "3566 0020 2036 0505"},
    {"name": "Jack Wrangler", "farm_name": "Red Barn Ranch",      "address": "58 Barn Ln, Redtown",        "credit_card": "5555 5555 5555 4444"},
]

for idx, profile in enumerate(_customer_profiles, start=1):
    cust_id = f"cust{idx}"
    CUSTOMERS[cust_id] = {
        "customer_id": cust_id,
        "orders": [],
        **profile,
    }

order_id = 1001
for cust_id in list(CUSTOMERS.keys()):
    num_orders = random.randint(2, 8)
    for _ in range(num_orders):
        item, price = random.choice(_items)
        units = random.randint(1, 5)
        ORDERS[str(order_id)] = {
            "order_id": str(order_id),
            "customer_id": cust_id,
            "item": item,
            "price": price,
            "units": units,
            "total": price * units,
        }
        CUSTOMERS[cust_id]["orders"].append(str(order_id))
        order_id += 1


class GoatOrderService:
    @staticmethod
    def get_order(order_id: str) -> str:
        time.sleep(2)
        o = ORDERS.get(order_id)
        if not o:
            return f"Error: order {order_id} not found"
        return (
            f"Order {o['order_id']}:\n"
            f" Customer: {o['customer_id']}\n"
            f" Item: {o['item']}\n"
            f" Units: {o['units']}\n"
            f" Total: {o['total']}\n\n"
        )

    @staticmethod
    def list_orders(customer_id: str) -> str:
        time.sleep(2)
        c = CUSTOMERS.get(customer_id)
        if not c:
            return f"Error: customer {customer_id} not found"

        return "\n".join([f"#{oid}" for oid in c["orders"]])

    @staticmethod
    def get_customer_info(customer_id: str) -> str:
        time.sleep(1)
        c = CUSTOMERS.get(customer_id)
        if not c:
            return f"Error: customer {customer_id} not found"

        return (
            f"Customer {c['customer_id']}:\n"
            f"  Name: {c['name']}\n"
            f"  Farm: {c['farm_name']}\n"
            f"  Address: {c['address']}\n"
            f"  Card: {c['credit_card']}\n"
            f"  Total Orders: {len(c['orders'])}"
        )


ALLOWED_FUNCTIONS = {
    "get_order": GoatOrderService.get_order,
    "list_orders": GoatOrderService.list_orders,
    "get_customer_info": GoatOrderService.get_customer_info,
}


def _execute_calls_worker(raw_response: str, queue: multiprocessing.Queue, max_calls: int = None):
    """
    Parse and execute every function call the assistant returned.
    Any call not in ALLOWED_FUNCTIONS -> recorded as Error.
    Results are joined with newline and put into the queue.
    """
    try:
        calls = re.findall(r"(\w+)\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", raw_response, flags=re.S)
    except Exception as e:
        goatlog.error(f"Parsing failure: {e}")
        queue.put("Error: failed to parse calls")
        return

    if not calls:
        queue.put("No function calls parsed.")
        return

    if max_calls is not None and len(calls) > max_calls:
        queue.put(f"Error: too many calls ({len(calls)})")
        return

    results = []
    for func_name, arg in calls:
        func_name = func_name.lower()
        if func_name not in ALLOWED_FUNCTIONS:
            results.append(f"Error: unknown function {func_name}()")
            continue
        try:
            res = ALLOWED_FUNCTIONS[func_name](arg)
            results.append(res)
        except Exception as e:
            goatlog.error(f"Backend error while executing {func_name}({arg}): {e}")
            results.append(f"Error executing {func_name}({arg})")

    queue.put("\n".join(results))


def run_calls_batch(raw_response: str, timeout_seconds: int = 10, max_calls: int = None) -> Tuple[str, bool]:

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_execute_calls_worker, args=(raw_response, queue, max_calls))
    p.start()

    p.join(timeout_seconds)

    if p.is_alive():
        try:
            p.terminate()
        except Exception as e:
            goatlog.error(f"Failed to terminate worker: {e}")
        return ("", True)

    try:
        result_text = queue.get(timeout=1)
    except Exception as e:
        goatlog.error(f"No result from worker queue: {e}")
        result_text = "Error: no result from worker"

    return (result_text, False)
