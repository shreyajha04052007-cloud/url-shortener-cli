import hashlib
import json
import os
import time
import sys
import urllib.parse
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
        # Add counter suffix before hashing to guarantee a different hash on collision
        seed = f"{url}_{counter}" if counter > 0 else url
        candidate = hashlib.sha256(seed.encode()).hexdigest()[:length]
        
        # Collision Check
        if candidate not in data:
            return candidate
        # If hash matches same target URL, reuse code
        elif data[candidate]["url"] == url:
            return candidate
        
        counter += 1


def shorten_url(original_url: str, days_valid: int = None, custom_alias: str = None):
    data = load_data()
    formatted_url = normalize_url(original_url)
    
    # Custom Alias or Hash Generation with Collision Handling
    if custom_alias:
        if custom_alias in data:
            print(f"\n[-] Error: Custom alias '{custom_alias}' is already taken.")
            return
        short_code = custom_alias
    else:
        short_code = generate_short_code(formatted_url, data)
    
    # Expiration logic (Unique Feature)
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
    
    # Check if link has expired
    if link_info.get("expires_at"):
        expiry = datetime.strptime(link_info["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expiry:
            print("\n[-] Error: This short link has expired!")
            return

    link_info["clicks"] += 1
    save_data(data)
    
    print(f"\n[+] Target URL: {link_info['url']}")
    print(f"[+] Total Clicks: {link_info['clicks']}")
    
    try:
        import webbrowser
        webbrowser.open(link_info['url'])
    except Exception:
        pass


def view_analytics():
    data = load_data()
    if not data:
        print("\n[-] No stored links found.")
        return
    
    print("\n--- Analytics & Stored Links ---")
    for code, info in data.items():
        exp_str = info.get("expires_at") or "Never"
        print(f"Code: {code:<10} | Clicks: {info['clicks']:<3} | Expires: {exp_str:<19} | Target: {info['url']}")


def main():
    while True:
        print("\n=== CLI URL SHORTENER ===")
        print("1. Shorten URL (Standard Hash)")
        print("2. Shorten URL (Custom Alias)")
        print("3. Access Link (Redirect & Track)")
        print("4. View Analytics")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            url = input("Enter target URL: ").strip()
            exp_input = input("Enter validity in days (or press Enter for no expiration): ").strip()
            days = int(exp_input) if exp_input.isdigit() else None
            shorten_url(url, days_valid=days)
        elif choice == "2":
            url = input("Enter target URL: ").strip()
            alias = input("Enter custom alias: ").strip()
            shorten_url(url, custom_alias=alias)
        elif choice == "3":
            code = input("Enter short code: ").strip()
            redirect_url(code)
        elif choice == "4":
            view_analytics()
        elif choice == "5":
            print("Exiting application...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
