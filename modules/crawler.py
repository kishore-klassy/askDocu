# File: modules/crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


def crawl_help_site(base_url, max_pages=200):
    visited = set()
    queue = deque([base_url])
    documents = []

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=10)
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            content = extract_main_content(soup)

            if content:
                documents.append({"url": url, "text": content})

            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if same_domain(base_url, full_url):
                    queue.append(full_url)

            visited.add(url)
        except Exception as e:
            print(f"[ERROR] Failed to process {url}: {e}")
    return documents


def extract_main_content(soup):
    # Remove scripts, styles, headers/footers
    for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
        tag.decompose()

    text = ' '.join(soup.stripped_strings)
    return text if len(text) > 100 else None


def same_domain(base_url, test_url):
    return urlparse(base_url).netloc == urlparse(test_url).netloc


