import json
import os

cache_file = "email_cache.json"

def load_cache():
    if not os.path.exists(cache_file):
        with open(cache_file, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(cache_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    
def save_cache(cache):
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2) 

def limit_cache_size(cache, max_size=500):
    if len(cache) <= max_size:
        return cache

     # sort by timestamp (oldest first)
    sorted_items = sorted(
        cache.items(),
        key=lambda x: x[1].get("timestamp", "")
    )

    # keep only newest
    trimmed = dict(sorted_items[-max_size:])

    return trimmed