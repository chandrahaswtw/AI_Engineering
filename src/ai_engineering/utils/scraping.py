from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_subroutes(url: str) -> list[str]:
    """Return all unique links on the page that live under the given URL.

    A link is a subroute if it is on the same host and its path starts with
    the path of ``url`` (e.g. ``https://a.com/docs`` -> ``https://a.com/docs/intro``).
    """
    soup = _fetch_soup(url)
    base = urlparse(url)
    base_path = base.path.rstrip("/")

    subroutes: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        link, _ = urldefrag(urljoin(url, anchor["href"]))
        parsed = urlparse(link)
        if parsed.scheme not in ("http", "https") or parsed.netloc != base.netloc:
            continue
        if not parsed.path.startswith(base_path + "/"):
            continue
        if link not in seen:
            seen.add(link)
            subroutes.append(link)
    return subroutes


def scrape_content(url: str) -> str:
    """Return the visible text content of the page at the given URL."""
    soup = _fetch_soup(url)
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)
