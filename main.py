import hashlib
import json
import os
import re
import sys
import urllib.parse
import webbrowser
from datetime import datetime, timedelta

DATA_FILE = "urls.json"


def normalize_url(raw_url: str) -> str:
    """Ensures input URL has a valid schema prefix (e.g., https://)."""
    clean_url = raw_url.strip()
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        return f"https://{clean_url}"
    return clean_url


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def generate_short_code(url: str, data: dict, length: int = 6) -> str:
    """Generates a short hash code and safely handles hash collisions."""
    counter = 0
    while True:
        # Counter change hone par seed badal jata hai, jisse har baar unique hash milega
        seed = f"{url}_{counter}" if counter > 0 else url
        candidate = hashlib.sha256(seed.encode()).hexdigest()[:length]
        
        # Collision Check: Duplicate key pe new hash try karega
        if candidate not in data:
            return candidate
        elif data[candidate]["url"] == url:
            return candidate
        
        counter += 1


def generate_smart_alias(url: str, data: dict) -> str:
    """Extracts meaningful domain/path keywords and handles collisions."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "").split(".")[0]
    path_parts = [p for p in parsed.path.split("/") if p]
    
    base_alias = f"{domain}-{path_parts[-1]}" if path_parts else domain
    base_alias = re.sub(r'[^a-zA-Z0-9-]', '', base_alias).lower()
    
    alias = base_alias
    counter = 1
    # Collision Handling for Smart Alias
    while alias in data:
        if data[alias]["url"] == url:
            return alias
        alias = f"{base_alias}-{counter}"
        counter += 1
        
    return alias


def shorten_url(original_url: str, mode: str, custom_alias: str = None, days_valid: int = None):
    data = load_data()
    formatted_url = normalize_url(original_url)
    
    if mode == "custom":
        if not custom_alias:
            print("\n[-] Error: Custom alias cannot be empty.")
            return
        if custom_alias in data:
            print(f"\n[-] Error: Custom alias '{custom_alias}' is already taken.")
            return
        short_code = custom_alias
    elif mode == "smart":
        short_code = generate_smart_alias(formatted_url, data)
    else:
        # Standard Hash with Collision Logic
        short_code = generate_short_code(formatted_url, data)
    
    expires_at = None
    if days_valid and days_valid > 0:
        expiry_date = datetime.now() + timedelta(days=days_valid)
        expires_at = expiry_date.strftime("%Y-%m-%d %H:%M:%S")

    data[short_code] = {
        "url": formatted_url,
        "clicks": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at
    }
    
    save_data(data)
    print(f"\n[+] Short Code Created: {short_code}")
    print(f"[+] Target URL: {formatted_url}")
    if expires_at:
        print(f"[+] Link Expiry Date: {expires_at}")


def redirect_url(short_code: str):
    data = load_data()
    if short_code not in data:
        print("\n[-] Error: Short code not found.")
        return
    
    link_info = data[short_code]
    
    if link_info.get("expires_at"):
        expiry = datetime.strptime(link_info["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            print("\n[-] Error: This short link has expired!")
            return

    link_info["clicks"] += 1
    save_data(data)
    
    print(f"\n[+] Opening Target URL: {link_info['url']}")
    print(f"[+] Total Clicks: {link_info['clicks']}")
    
    try:
        webbrowser.open(link_info['url'])
    except Exception as e:
        print(f"[-] Could not open browser automatically: {e}")


def view_analytics():
    data = load_data()
    if not data:
        print("\n[-] No stored links found.")
        return
    
    print("\n--- Analytics & Stored Links ---")
    for code, info in data.items():
        exp_str = info.get("expires_at") or "Never"
        print(f"Code: {code:<15} | Clicks: {info['clicks']:<3} | Expires: {exp_str:<19} | Target: {info['url']}")


def main():
    while True:
        print("\n=== CLI URL SHORTENER ===")
        print("1. Shorten URL (Standard Hash)")
        print("2. Shorten URL (Smart Keyword Alias)")
        print("3. Shorten URL (Custom Alias)")
        print("4. Access Link (Redirect & Track Clicks)")
        print("5. View Analytics & Saved Links")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            url = input("Enter target URL: ").strip()
            exp_input = input("Enter validity in days (press Enter for no expiry): ").strip()
            days = int(exp_input) if exp_input.isdigit() else None
            shorten_url(url, mode="hash", days_valid=days)
        elif choice == "2":
            url = input("Enter target URL: ").strip()
            shorten_url(url, mode="smart")
        elif choice == "3":
            url = input("Enter target URL: ").strip()
            alias = input("Enter custom alias: ").strip()
            shorten_url(url, mode="custom", custom_alias=alias)
        elif choice == "4":
            code = input("Enter short code: ").strip()
            redirect_url(code)
        elif choice == "5":
            view_analytics()
        elif choice == "6":
            print("Exiting application...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
