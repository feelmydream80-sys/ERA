import requests
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class IEEECrawler(BaseCrawler):
    name = "IEEE"

    def crawl(self):
        papers = []
        keywords = self.get_keywords(language="en")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://ieeexplore.ieee.org",
            "Referer": "https://ieeexplore.ieee.org/search/searchresult.jsp",
            "X-Requested-With": "XMLHttpRequest",
        }

        for kw in keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.post(
                    "https://ieeexplore.ieee.org/rest/search",
                    json={"queryText": kw, "pageNumber": 1, "pageSize": 10},
                    headers=headers, timeout=15,
                )
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code} for '{kw}'")
                    continue
                d = resp.json()
                for rec in d.get("records") or []:
                    if rec.get("isStandard") or rec.get("contentType", "") in ("IEEE Standards", "Standards"):
                        continue
                    title = rec.get("articleTitle") or rec.get("title", "")
                    if not title:
                        continue
                    abstract = rec.get("abstract", "") or ""
                    kw_lower = kw.lower()
                    if kw_lower not in title.lower() and kw_lower not in abstract.lower():
                        continue
                    href = rec.get("publicationLink") or rec.get("documentLink", "")
                    if href and not href.startswith("http"):
                        href = "https://ieeexplore.ieee.org" + href
                    doi = rec.get("doi", "") or ""
                    authors = "; ".join(
                        a.get("fullName", a.get("preferredName", ""))
                        for a in (rec.get("authors") or [])
                    )
                    pub_date = None
                    pd_str = rec.get("publicationDate", "") or ""
                    if pd_str:
                        try:
                            for fmt in ["%d %b. %Y", "%d %b %Y", "%B %Y", "%b. %Y", "%Y"]:
                                try:
                                    dt = datetime.strptime(pd_str, fmt)
                                    pub_date = dt.date()
                                    break
                                except ValueError:
                                    continue
                        except Exception:
                            pass
                    papers.append({
                        "title": title,
                        "source_url": href,
                        "source": self.name,
                        "authors": authors,
                        "abstract": abstract,
                        "doi": doi,
                        "published_date": pub_date,
                        "keywords": kw,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
