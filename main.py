import hashlib
import json
import os
import time
import sys
import re
import urllib.parse
import platform

DATA_FILE = "urls.json"


def play_chime():
    """Cross-platform audio feedback."""
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(523, 120)
            winsound.Beep(659, 150)
        elif platform.system() == "Darwin":  # macOS
            os.system("say -v Victoria 'done' &" if os.name == 'posix' else "afplay /System/Library/Sounds/Glass.aiff &")
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()
    except Exception:
        pass  # Never crash over sound failure


def typewriter_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


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


def generate_smart_alias(url, data):
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.replace("www.", "").split(".")[0]
    path_words = re.findall(r'\w+', parsed.path)
    
    base_alias = domain if domain else "link"
    if path_words:
        base_alias += f"-{path_words[-1]}"
    
    clean_alias = base_alias[:12].lower()
    candidate = clean_alias
    counter = 1
    while candidate in data:
        candidate = f"{clean_alias}-{counter}"
        counter += 1
        
    return candidate


def shorten_url(original_url, custom_alias=None, use_smart_alias=False):
    data = load_data()
    formatted_url = normalize_url(original_url)
    
    if custom_alias:
        if custom_alias in data:
            typewriter_print(f"\n[-] Error: Alias '{custom_alias}' already exists.")
            return None
        short_code = custom_alias
    elif use_smart_alias:
        short_code = generate_smart_alias(formatted_url, data)
    else:
        short_code = hashlib.sha256(formatted_url.encode()).hexdigest()[:6]
    
    data[short_code] = {
        "url": formatted_url,
        "clicks": 0
    }
    
    save_data(data)
    play_chime()
    typewriter_print(f"\n[+] Generated Short Code: {short_code}")
    typewriter_print(f"[+] Destination URL: {formatted_url}")
    return short_code


def redirect_url(short_code):
    data = load_data()
    if short_code not in data:
        typewriter_print("\n[-] Error: Short code not found.")
        return None
    
    link_info = data[short_code]
    link_info["clicks"] += 1
    save_data(data)
    
    play_chime()
    typewriter_print(f"\n[+] Target URL: {link_info['url']}")
    typewriter_print(f"[+] Total Clicks: {link_info['clicks']}")
    
    # Auto-open in browser if supported
    try:
        import webbrowser
        webbrowser.open(link_info['url'])
    except Exception:
        pass
    return link_info['url']


def view_analytics():
    data = load_data()
    if not data:
        typewriter_print("\n[-] No stored links found.")
        return
    
    typewriter_print("\n--- Saved Links & Analytics ---")
    for code, info in data.items():
        print(f"Code: {code:<12} | Clicks: {info['clicks']:<4} | Target: {info['url']}")


def start_system_expander():
    """Safe system-wide auto expander that checks environment without crashing."""
    try:
        from pynput import keyboard
        from pynput.keyboard import Controller, Key
    except ImportError:
        typewriter_print("\n[!] Desktop System Expander requires 'pynput'.")
        typewriter_print("[!] Install via: pip install pynput")
        return

    kb_controller = Controller()
    typed_buffer = ""

    def on_press(key):
        nonlocal typed_buffer
        try:
            if hasattr(key, 'char') and key.char:
                typed_buffer += key.char
            elif key == Key.space:
                typed_buffer += " "
            elif key == Key.backspace:
                typed_buffer = typed_buffer[:-1]
            elif key == Key.enter:
                typed_buffer = ""

            if len(typed_buffer) > 40:
                typed_buffer = typed_buffer[-20:]

            data = load_data()
            for short_code, info in data.items():
                if typed_buffer.endswith(short_code):
                    target_url = info["url"]

                    # Erase trigger short code
                    for _ in range(len(short_code)):
                        kb_controller.press(Key.backspace)
                        kb_controller.release(Key.backspace)
                        time.sleep(0.01)

                    # Type target URL
                    kb_controller.type(target_url)

                    info["clicks"] += 1
                    save_data(data)
                    play_chime()
                    typed_buffer = ""
                    break
        except Exception:
            pass

    typewriter_print("\n[+] System Expander Active!")
    typewriter_print("[+] Type any saved short code anywhere on your OS to auto-expand it.")
    typewriter_print("[+] Press Ctrl+C in terminal to stop listener.")

    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        listener.join()
    except KeyboardInterrupt:
        typewriter_print("\n[-] Expander stopped.")
    except Exception as e:
        typewriter_print(f"\n[-] Could not start keyboard hook: {e}")


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    play_chime()
    typewriter_print("=== CLI URL SHORTENER & DESKTOP EXPANDER ===")
    
    while True:
        print("\n1. Shorten URL (Standard Hash)")
        print("2. Shorten URL (Smart Keyword Alias)")
        print("3. Shorten URL (Custom Alias)")
        print("4. Access Link (Redirect & Track Clicks)")
        print("5. View Analytics & Saved Links")
        print("6. Launch System-Wide Expander (OS Listener)")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            url = input("Enter target URL: ").strip()
            shorten_url(url)
        elif choice == "2":
            url = input("Enter target URL: ").strip()
            shorten_url(url, use_smart_alias=True)
        elif choice == "3":
            url = input("Enter target URL: ").strip()
            alias = input("Enter custom alias: ").strip()
            shorten_url(url, custom_alias=alias)
        elif choice == "4":
            code = input("Enter short code: ").strip()
            redirect_url(code)
        elif choice == "5":
            view_analytics()
        elif choice == "6":
            start_system_expander()
        elif choice == "7":
            typewriter_print("Exiting application...")
            break
        else:
            typewriter_print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
