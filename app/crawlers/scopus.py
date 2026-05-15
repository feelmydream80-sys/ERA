import requests
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class ScopusCrawler(BaseCrawler):
    name = "Scopus"

    def crawl(self):
        papers = []
        keywords = self.get_keywords(language="en")
        headers = {"User-Agent": "Mozilla/5.0"}

        for kw in keywords:
            self.log(f'searching "{kw}"...')
            url = f"https://api.crossref.org/works?query={quote(kw)}&filter=type:journal-article&rows=10&sort=published&order=desc"
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                data = resp.json()
                for item in data.get("message", {}).get("items", []):
                    title_list = item.get("title", [])
                    if not title_list:
                        continue
                    title = title_list[0]
                    doi = item.get("DOI", "")
                    url_link = f"https://doi.org/{doi}" if doi else ""
                    authors = "; ".join(
                        f"{a.get('given', '')} {a.get('family', '')}".strip()
                        for a in item.get("author", [])
                    )
                    date_parts = item.get("published-print", {}).get("date-parts", [[]])[0]
                    pub_date = None
                    if len(date_parts) >= 3:
                        try:
                            pub_date = datetime(date_parts[0], date_parts[1], date_parts[2])
                        except Exception:
                            pub_date = None
                    elif len(date_parts) >= 1:
                        try:
                            pub_date = datetime(date_parts[0], 1, 1)
                        except Exception:
                            pub_date = None
                    papers.append({
                        "title": title,
                        "source_url": url_link,
                        "source": self.name,
                        "authors": authors,
                        "abstract": item.get("abstract", ""),
                        "published_date": pub_date,
                        "keywords": kw,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
