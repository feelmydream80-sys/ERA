import requests
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class OpenAlexCrawler(BaseCrawler):
    name = "OpenAlex"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.get(
                    "https://api.openalex.org/works",
                    params={
                        "search": kw,
                        "per_page": 10,
                        "sort": "publication_date:desc",
                        "select": "id,title,authorships,abstract_inverted_index,doi,primary_location,publication_date,type,cited_by_count",
                    },
                    timeout=15,
                )
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                d = resp.json()
                for r in d.get("results") or []:
                    title = (r.get("title") or "").strip()
                    if not title:
                        continue
                    pub_date = None
                    pd_str = r.get("publication_date", "") or ""
                    if pd_str:
                        try:
                            dt = datetime.fromisoformat(pd_str)
                            pub_date = dt.date()
                        except Exception:
                            pass
                    authors = "; ".join(
                        a.get("author", {}).get("display_name", "")
                        for a in (r.get("authorships") or [])
                    )
                    inv = r.get("abstract_inverted_index") or {}
                    abstract = ""
                    if inv:
                        wp = []
                        for word, positions in inv.items():
                            for pos in positions:
                                wp.append((pos, word))
                        wp.sort()
                        abstract = " ".join(w for _, w in wp)
                    loc = r.get("primary_location") or {}
                    src = loc.get("source") or {}
                    venue = src.get("display_name", "") if src else ""
                    landing_url = loc.get("landing_page_url") or ""
                    doi = r.get("doi", "") or ""
                    pdf_url = loc.get("pdf_url") or ""
                    source_url = pdf_url or landing_url or (f"https://doi.org/{doi}" if doi else "")
                    papers.append({
                        "title": title,
                        "source_url": source_url,
                        "source": self.name,
                        "authors": authors,
                        "abstract": abstract,
                        "doi": doi,
                        "published_date": pub_date,
                        "keywords": kw,
                        "venue": venue,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
