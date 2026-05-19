import requests
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class CrossrefCrawler(BaseCrawler):
    name = "Crossref"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.get(
                    "https://api.crossref.org/works",
                    params={
                        "query": kw,
                        "rows": 10,
                        "sort": "published",
                        "order": "desc",
                        "filter": "type:journal-article",
                        "select": "DOI,title,author,abstract,URL,published-print,issued,container-title",
                    },
                    timeout=15,
                )
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                d = resp.json()
                for item in d["message"].get("items") or []:
                    titles = item.get("title") or []
                    if not titles:
                        continue
                    title = titles[0].strip()
                    pub_date = None
                    issued = item.get("issued") or {}
                    dp = (issued.get("date-parts") or [None])[0]
                    if dp:
                        try:
                            parts = [int(p) for p in dp]
                            if len(parts) >= 3:
                                pub_date = datetime(parts[0], parts[1], parts[2]).date()
                            elif len(parts) == 2:
                                pub_date = datetime(parts[0], parts[1], 1).date()
                            else:
                                pub_date = datetime(parts[0], 1, 1).date()
                        except Exception:
                            pass
                    authors = "; ".join(
                        " ".join(filter(None, [a.get("given", ""), a.get("family", "")]))
                        for a in (item.get("author") or [])
                    )
                    abstract = item.get("abstract", "") or ""
                    doi = item.get("DOI", "") or ""
                    url = item.get("URL", "") or ""
                    if not url and doi:
                        url = f"https://doi.org/{doi}"
                    journal = (item.get("container-title") or [""])[0] if item.get("container-title") else ""
                    papers.append({
                        "title": title,
                        "source_url": url,
                        "source": self.name,
                        "authors": authors,
                        "abstract": abstract,
                        "doi": doi,
                        "published_date": pub_date,
                        "keywords": kw,
                        "venue": journal,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
