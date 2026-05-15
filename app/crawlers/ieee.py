import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import BaseCrawler


class IEEECrawler(BaseCrawler):
    name = "IEEE"

    def crawl(self):
        papers = []
        keywords = self.get_keywords(language="en")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

        for kw in keywords:
            self.log(f'searching "{kw}"...')
            url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={quote(kw)}&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&pageNumber=1&pageSize=10"
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code} for '{kw}'")
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                for item in soup.select("xpl-results-list xpl-results-item"):
                    title_el = item.select_one("h2 a")
                    if not title_el:
                        title_el = item.select_one("xpl-title a")
                    if not title_el:
                        continue
                    title_text = title_el.get_text(strip=True)
                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = "https://ieeexplore.ieee.org" + href
                    papers.append({
                        "title": title_text,
                        "source_url": href,
                        "source": self.name,
                        "keywords": kw,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
