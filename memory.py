import json
import os

THREAD_MEMORY_FILE = "thread_memory.json"

def load_thread_memory():
    if not os.path.exists(THREAD_MEMORY_FILE):
        return {}
    with open(THREAD_MEMORY_FILE, "r") as f:
        return json.load(f)

def save_thread_memory(memory):
    with open(THREAD_MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)