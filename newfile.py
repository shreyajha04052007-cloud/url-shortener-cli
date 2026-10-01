import sys
import json
import random
import string
import os

DB_FILE = "urls.json"

def load_urls():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_urls(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def shorten_url(original_url):
    urls = load_urls()
    for code, url in urls.items():
        if url == original_url:
            print(f"Short code already exists: {code}")
            return code
    
    code = generate_short_code()
    while code in urls:
        code = generate_short_code()
        
    urls[code] = original_url
    save_urls(urls)
    print(f"Short code: {code}")
    return code

def resolve_url(short_code):
    urls = load_urls()
    if short_code in urls:
        print(f"Original URL: {urls[short_code]}")
        return urls[short_code]
    else:
        print("Short code not found.")
        return None

def list_urls():
    urls = load_urls()
    if not urls:
        print("No short URLs found.")
        return
    print("--- Saved Short Links ---")
    for code, url in urls.items():
        print(f"{code} -> {url}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [shorten|resolve|list] <url_or_code>")
        return

    cmd = sys.argv[1].lower()

    if cmd == "shorten":
        if len(sys.argv) < 3:
            print("Please provide a URL to shorten.")
            return
        shorten_url(sys.argv[2])

    elif cmd == "resolve":
        if len(sys.argv) < 3:
            print("Please provide a short code.")
            return
        resolve_url(sys.argv[2])

    elif cmd == "list":
        list_urls()

    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
 