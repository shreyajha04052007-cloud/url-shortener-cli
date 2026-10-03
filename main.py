import hashlib
import json
import os
import time
import base64
import sys
import re
import urllib.parse
from datetime import datetime, timedelta

DATA_FILE = "urls.json"
SECRET_KEY = "my_secret_key"


def play_beep():
    # Trigger system sound
    sys.stdout.write('\a')
    sys.stdout.flush()


def typewriter_print(text, delay=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def encrypt_url(plain_url, key=SECRET_KEY):
    encrypted = bytearray()
    key_bytes = key.encode('utf-8')
    url_bytes = plain_url.encode('utf-8')
    
    for i, b in enumerate(url_bytes):
        encrypted.append(b ^ key_bytes[i % len(key_bytes)])
        
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_url(cipher_text, key=SECRET_KEY):
    try:
        encrypted_bytes = base64.b64decode(cipher_text.encode('utf-8'))
        decrypted = bytearray()
        key_bytes = key.encode('utf-8')
        
        for i, b in enumerate(encrypted_bytes):
            decrypted.append(b ^ key_bytes[i % len(key_bytes)])
            
        return decrypted.decode('utf-8')
    except Exception:
        return None


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


def generate_smart_alias(url, data):
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "").split(".")[0]
    path_words = re.findall(r'\w+', parsed.path)
    
    base_alias = domain if domain else "link"
    if path_words:
        base_alias += f"-{path_words[-1]}"
    
    clean_alias = base_alias[:12].lower()
    
    # Handle duplicates by adding a counter
    candidate = clean_alias
    counter = 1
    while candidate in data:
        candidate = f"{clean_alias}-{counter}"
        counter += 1
        
    return candidate


def shorten_url(original_url, custom_alias=None, use_smart_alias=False):
    data = load_data()
    
    if custom_alias:
        if custom_alias in data:
            typewriter_print(f"Error: Alias '{custom_alias}' already exists.")
            return None
        short_code = custom_alias
    elif use_smart_alias:
        short_code = generate_smart_alias(original_url, data)
    else:
        # Generate 6-char SHA256 hash
        short_code = hashlib.sha256(original_url.encode()).hexdigest()[:6]
    
    encrypted_url = encrypt_url(original_url)
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=30)
    
    data[short_code] = {
        "encrypted_url": encrypted_url,
        "clicks": 0,
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_data(data)
    play_beep()
    typewriter_print(f"\n[+] Generated Short Code: {short_code}")
    typewriter_print(f"[+] Encrypted URL: {encrypted_url[:20]}...")
    return short_code


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    play_beep()
    typewriter_print("=== CLI URL Shortener ===")
    
    while True:
        print("\n1. Shorten URL (Standard Hash)")
        print("2. Shorten URL (Smart Alias)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            url = input("Enter URL: ").strip()
            alias = input("Custom alias (optional): ").strip() or None
            shorten_url(url, custom_alias=alias)
        elif choice == "2":
            url = input("Enter URL: ").strip()
            shorten_url(url, use_smart_alias=True)
        elif choice == "3":
            typewriter_print("Exiting...")
            break
        else:
            typewriter_print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
