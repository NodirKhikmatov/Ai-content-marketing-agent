import json
import logging
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class WebsiteCrawler:
    """Crawls a website and extracts text content from key pages."""

    def __init__(self):
        self.max_pages = settings.max_crawl_pages
        self.timeout = settings.crawl_timeout_seconds

    async def crawl(self, url: str) -> dict[str, Any]:
        parsed = urlparse(str(url))
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https")

        base_url = f"{parsed.scheme}://{parsed.netloc}"
        visited: set[str] = set()
        pages: list[dict[str, Any]] = []

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": "AI-Content-Marketing-Agent/1.0"},
        ) as client:
            to_visit = [str(url)]
            while to_visit and len(pages) < self.max_pages:
                current_url = to_visit.pop(0)
                if current_url in visited:
                    continue
                visited.add(current_url)

                try:
                    response = await client.get(current_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "lxml")

                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()

                    title = soup.title.string.strip() if soup.title and soup.title.string else ""
                    text = " ".join(soup.get_text(separator=" ", strip=True).split())
                    pages.append(
                        {
                            "url": current_url,
                            "title": title,
                            "text": text[:8000],
                        }
                    )

                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        full_url = urljoin(current_url, href)
                        parsed_link = urlparse(full_url)
                        if parsed_link.netloc == parsed.netloc and full_url not in visited:
                            to_visit.append(full_url)

                except Exception as e:
                    logger.warning("Failed to crawl %s: %s", current_url, e)

        if not pages:
            raise ValueError(f"Could not crawl any pages from {url}")

        combined_text = "\n\n".join(f"## {p['title']}\n{p['text']}" for p in pages)

        return {
            "url": str(url),
            "base_url": base_url,
            "pages_crawled": len(pages),
            "pages": pages,
            "combined_text": combined_text[:50000],
        }
