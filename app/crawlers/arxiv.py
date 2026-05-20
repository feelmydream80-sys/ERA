import requests
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class ArxivCrawler(BaseCrawler):
    name = "arXiv"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            url = f"http://export.arxiv.org/api/query?search_query=all:{quote(kw)}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    published = entry.find("atom:published", ns)
                    link = entry.find("atom:id", ns)
                    author_els = entry.findall("atom:author", ns)
                    authors = "; ".join(
                        a.find("atom:name", ns).text.strip() if a.find("atom:name", ns) is not None else ""
                        for a in author_els
                    )
                    pub_date = None
                    if published is not None and published.text:
                        try:
                            dt = datetime.fromisoformat(published.text.replace("Z", "+00:00"))
                            pub_date = dt.date()
                        except Exception:
                            pass
                    title_text = (title.text.strip().replace("\n", " ").replace("  ", " ").replace("  ", " ") if title is not None else "")
                    if kw.lower() not in title_text.lower():
                        continue
                    papers.append({
                        "title": title_text,
                        "source_url": link.text.strip() if link is not None else "",
                        "source": self.name,
                        "authors": authors,
                        "abstract": summary.text.strip().replace("\n", " ").replace("  ", " ").replace("  ", " ") if summary is not None else "",
                        "published_date": pub_date,
                        "keywords": kw,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
