import json
import csv
import os
from datetime import datetime

# load employee data from api_keys.json
def load_api_keys():
    with open("api_keys.json", "r") as f:
        return json.load(f)

# calculate cost based on tokens
def calculate_cost(tokens_used):
    cost_per_1000_tokens = 0.00005
    cost = (tokens_used / 1000) * cost_per_1000_tokens
    return round(cost, 8)  

# log a single API call
def log_api_call(api_key, question, tokens_used, model="llama-3.1-8b-instant"):
    # load employee info
    api_keys = load_api_keys()

    # check if key exists
    if api_key not in api_keys:
        print(f"Warning: Unknown API key {api_key}")
        employee_name = "Unknown"
        department = "Unknown"
    else:
        employee_name = api_keys[api_key]["name"]
        department = api_keys[api_key]["department"]

    # calculate cost
    cost = calculate_cost(tokens_used)

    # create log entry
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "api_key": api_key,
        "employee_name": employee_name,
        "department": department,
        "model": model,
        "question": question[:50],  # first 50 chars only
        "tokens_used": tokens_used,
        "cost_usd": f"{cost:.8f}"
    }

    # save to CSV
    file_exists = os.path.exists("usage_logs.csv")

    with open("usage_logs.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())

        # write header only if file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow(log_entry)

    print(f"Logged: {employee_name} used {tokens_used} tokens (${cost:.8f})")
    return log_entry