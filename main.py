import sys
import json
import random
import string

FILE_NAME = "urls.json"

def load_urls():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_urls(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def shorten(url, custom_code=None):
    data = load_urls()
    
    if custom_code:
        if custom_code in data:
            print(f"Error: Short code already exists: {custom_code}")
            return
        code = custom_code
    else:
        code = generate_short_code()
        while code in data:
            code = generate_short_code()
            
    # Stores URL and initial click count
    data[code] = {"url": url, "clicks": 0}
    save_urls(data)
    print(f"Shortened URL: {code} -> {url}")

def list_urls():
    data = load_urls()
    print("--- Saved Short Links ---")
    if not data:
        print("No URLs saved yet.")
        return
    for code, info in data.items():
        # Handles both old flat format and new structured format
        if isinstance(info, dict):
            print(f"{code} -> {info['url']} (Clicks: {info['clicks']})")
        else:
            print(f"{code} -> {info}")

def resolve(code):
    data = load_urls()
    if code in data:
        if isinstance(data[code], dict):
            data[code]["clicks"] += 1
            save_urls(data)
            print(f"Original URL: {data[code]['url']} (Total clicks: {data[code]['clicks']})")
        else:
            print(f"Original URL: {data[code]}")
    else:
        print("Error: Short code not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <shorten|list|resolve> [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "shorten":
        if len(sys.argv) < 3:
            print("Usage: python main.py shorten <url> [--alias custom_code]")
        else:
            url = sys.argv[2]
            custom_code = None
            
            # Checks for --alias flag syntax
            if len(sys.argv) >= 5 and sys.argv[3] == "--alias":
                custom_code = sys.argv[4]
            elif len(sys.argv) >= 4:
                custom_code = sys.argv[3]
                
            shorten(url, custom_code)

    elif command == "list":
        list_urls()

    elif command == "resolve":
        if len(sys.argv) < 3:
            print("Usage: python main.py resolve <code>")
        else:
            resolve(sys.argv[2])
