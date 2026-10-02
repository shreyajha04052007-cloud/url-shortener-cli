import hashlib
import json
import os
import time
from datetime import datetime, timedelta

# Configuration
DATA_FILE = "urls.json"
LOG_FILE = "app.log"


def log_event(message, level="INFO"):
    """Appends system logs with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] [{level}] {message}\n")


def measure_execution_time(func):
    """Decorator to measure function performance in milliseconds."""

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        execution_time = (time.perf_counter() - start_time) * 1000
        print(f"Executed in {execution_time:.2f} ms")
        return result

    return wrapper


def create_short_code(original_url):
    """Generates a 6-character unique hash for a URL."""
    raw_data = f"{original_url}{time.time()}".encode("utf-8")
    return hashlib.sha256(raw_data).hexdigest()[:6]


def read_database():
    """Loads URL mapping data from local JSON storage."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            content = json.load(file)
            return content if isinstance(content, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def write_database(data):
    """Saves updated URL mappings to local JSON storage."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


@measure_execution_time
def create_short_url(raw_url, alias=None, valid_days=30):
    """Handles short URL creation and custom alias handling."""
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url

    database = read_database()

    if alias:
        if alias in database:
            print(f"[!] The custom alias '{alias}' is already in use.")
            log_event(f"Conflict on alias creation: {alias}", "WARN")
            return
        code = alias
    else:
        code = create_short_code(raw_url)

    current_time = datetime.now()
    created_at = current_time.strftime("%Y-%m-%d %H:%M:%S")
    expires_at = (current_time + timedelta(days=valid_days)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    database[code] = {
        "original_url": raw_url,
        "clicks": 0,
        "created_at": created_at,
        "expires_at": expires_at,
    }

    write_database(database)
    log_event(f"New link generated: {code} -> {raw_url}")

    print("\n--- Link Created Successfully ---")
    print(f"Short Code : {code}")
    print(f"Short Link : https://short.ly/{code}")
    print(f"Expires On : {expires_at}")


@measure_execution_time
def simulate_redirect(code):
    """Simulates user clicking the link and increments click counter."""
    database = read_database()

    if code not in database:
        print(f"[!] Link code '{code}' not found.")
        return

    record = database[code]
    expiration_date = datetime.strptime(
        record.get("expires_at"), "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expiration_date:
        print(f"[!] Link '{code}' has expired.")
        return

    record["clicks"] = record.get("clicks", 0) + 1
    write_database(database)

    print(f"\n[+] Redirecting to: {record['original_url']}")
    print(f"[+] Total Clicks: {record['clicks']}")
    log_event(f"Simulated visit to {code} | Clicks: {record['clicks']}")


@measure_execution_time
def view_analytics(code):
    """Prints usage statistics for a specific short link."""
    database = read_database()

    if code not in database:
        print(f"[!] Link code '{code}' does not exist.")
        log_event(f"Analytics lookup failed for: {code}", "WARN")
        return

    record = database[code]
    print(f"\n--- Analytics [{code}] ---")
    print(f"Original Link : {record.get('original_url', 'N/A')}")
    print(f"Click Count   : {record.get('clicks', 0)}")
    print(f"Created On    : {record.get('created_at', 'N/A')}")
    print(f"Expires On    : {record.get('expires_at', 'N/A')}")

    log_event(f"Viewed analytics for: {code}")


@measure_execution_time
def list_all_urls():
    """Lists all saved short links in formatted table."""
    database = read_database()

    if not database:
        print("\nNo links registered yet.")
        return

    print("\n--- Registered Links ---")
    print(f"{'Code':<12} | {'Original URL':<35} | {'Clicks'}")
    print("-" * 57)

    for code, info in database.items():
        if isinstance(info, dict):
            target_url = info.get("original_url", "")
            clicks = info.get("clicks", 0)
        else:
            target_url = str(info)
            clicks = 0

        if len(target_url) > 35:
            target_url = target_url[:32] + "..."

        print(f"{code:<12} | {target_url:<35} | {clicks}")

    print(f"\nTotal Saved Links: {len(database)}")


@measure_execution_time
def search_database(search_query):
    """Filters saved links by code or destination URL."""
    database = read_database()
    query = search_query.lower()
    matches = []

    for code, info in database.items():
        if isinstance(info, dict):
            target_url = info.get("original_url", "").lower()
            if query in code.lower() or query in target_url:
                matches.append(
                    (code, info.get("original_url"), info.get("clicks", 0))
                )

    if not matches:
        print(f"\nNo records found matching '{search_query}'.")
        return

    print(f"\n--- Search Results for '{search_query}' ---")
    print(f"{'Code':<12} | {'Original URL':<35} | {'Clicks'}")
    print("-" * 57)

    for code, target_url, clicks in matches:
        if len(target_url) > 35:
            target_url = target_url[:32] + "..."
        print(f"{code:<12} | {target_url:<35} | {clicks}")


@measure_execution_time
def delete_short_url(code):
    """Removes a URL entry from database."""
    database = read_database()

    if code not in database:
        print(f"[!] Code '{code}' not found.")
        return

    del database[code]
    write_database(database)
    log_event(f"Removed link: {code}")
    print(f"[+] Successfully deleted '{code}'.")


@measure_execution_time
def purge_expired_links():
    """Automatically cleans up expired entries from the system."""
    database = read_database()
    current_time = datetime.now()
    expired_codes = []

    for code, info in database.items():
        if isinstance(info, dict) and "expires_at" in info:
            expiry_date = datetime.strptime(
                info["expires_at"], "%Y-%m-%d %H:%M:%S"
            )
            if current_time > expiry_date:
                expired_codes.append(code)

    for code in expired_codes:
        del database[code]

    if expired_codes:
        write_database(database)
        log_event(f"Purged {len(expired_codes)} expired link(s).")
        print(f"[+] Purged {len(expired_codes)} expired link(s).")
    else:
        print("[+] No expired links found.")


def main():
    while True:
        print("\n=== URL SHORTENER CLI ===")
        print("1. Shorten a URL")
        print("2. Visit Short Link (Simulate Click)")
        print("3. View Link Analytics")
        print("4. List All Links")
        print("5. Search Links")
        print("6. Delete a Link")
        print("7. Clean Expired Links")
        print("8. Exit")

        user_choice = input("\nSelect an option (1-8): ").strip()

        if user_choice == "1":
            target = input("Enter destination URL: ").strip()
            custom_alias = input(
                "Custom alias (Press Enter for auto): "
            ).strip()
            alias = custom_alias if custom_alias else None
            create_short_url(target, alias=alias)

        elif user_choice == "2":
            code = input("Enter short code to visit: ").strip()
            simulate_redirect(code)

        elif user_choice == "3":
            code = input("Enter short code: ").strip()
            view_analytics(code)

        elif user_choice == "4":
            list_all_urls()

        elif user_choice == "5":
            query = input("Enter search keyword: ").strip()
            search_database(query)

        elif user_choice == "6":
            code = input("Enter short code to delete: ").strip()
            delete_short_url(code)

        elif user_choice == "7":
            purge_expired_links()

        elif user_choice == "8":
            print("Exiting application. Goodbye!")
            break

        else:
            print("[!] Invalid option. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
