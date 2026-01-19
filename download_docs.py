# import requests
# from bs4 import BeautifulSoup
# import os
# import urllib.parse
#
# BASE_URL = "https://gpt-index.readthedocs.io/en/stable/"
# OUTPUT_DIR = "./llamaindex-docs/"
# os.makedirs(OUTPUT_DIR, exist_ok=True)
#
#
# def save_page(url, output_dir):
#     try:
#         r = requests.get(url, timeout=10)
#         r.raise_for_status()
#     except Exception as e:
#         return
#
#     parsed = urllib.parse.urlparse(url)
#     filename = os.path.basename(parsed.path.rstrip("/")) or "index"
#     if not filename.endswith(".html"):
#         filename += ".html"
#
#     file_path = os.path.join(output_dir, filename)
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(r.text)
#     print(f"{file_path}")
#
#
# resp = requests.get(BASE_URL)
# soup = BeautifulSoup(resp.text, "html.parser")
#
# links = soup.find_all("a", href=True)
#
# visited = set()
#
# for link in links:
#     href = link["href"]
#     if href.startswith("http"):
#         full_url = urllib.parse.urljoin(BASE_URL, href)
#         if full_url not in visited:
#             visited.add(full_url)
#             print(f"downloading {full_url}")
#
#             save_page(full_url, OUTPUT_DIR)
#
# print(f"Saved {len(visited)} pages in {OUTPUT_DIR}")
