import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "http://154.57.164.67:34092"
ENDPOINT = f"{BASE_URL}/documents.php"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": f"{BASE_URL}/"
}

txt_urls = []

for uid in range(1, 21):
    try:
        response = requests.post(
            ENDPOINT,
            headers=headers,
            data={"uid": uid},
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.select("a[href]"):
            href = link.get("href")

            if href.lower().endswith(".txt"):
                full_url = urljoin(BASE_URL, href)
                txt_urls.append(full_url)

                print(f"[UID {uid}] {full_url}")

    except requests.RequestException as e:
        print(f"[UID {uid}] Error: {e}")

# Save unique URLs
txt_urls = list(dict.fromkeys(txt_urls))

with open("txt_urls.txt", "w") as f:
    f.write("\n".join(txt_urls))

print(f"\nFound {len(txt_urls)} unique TXT files.")
print("Saved to txt_urls.txt")