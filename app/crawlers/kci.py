import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class KCICrawler(BaseCrawler):
    """
    KCI (Korean Citation Index) web search.
    Uses POST with correct form parameter names.
    Korean IP may be required.
    """
    name = "KCI"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.post(
                    "https://www.kci.go.kr/kciportal/po/search/poArtiSearList.kci",
                    data={
                        "poSearchBean.keywordList": kw,
                        "poSearchBean.searType": "thesis",
                        "poSearchBean.startPg": "1",
                    },
                    headers=headers, timeout=15,
                )
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                rows = soup.select(".search-answer-tbl tr")
                for row in rows:
                    tds = row.find_all("td")
                    if len(tds) < 3:
                        continue
                    number_td = tds[1]
                    number_text = number_td.get_text(strip=True) if number_td else ""
                    if not number_text.replace(".", "").strip().isdigit():
                        continue
                    title_td = tds[2]
                    title_el = title_td.select_one("a") if title_td else None
                    if not title_el:
                        continue
                    title_text = title_el.get_text(strip=True)
                    if not title_text:
                        continue
                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = "https://www.kci.go.kr" + href
                    papers.append({
                        "title": title_text,
                        "source_url": href,
                        "source": self.name,
                        "authors": "",
                        "abstract": "",
                        "published_date": None,
                        "keywords": kw,
                    })
            except Exception as e:
                self.log(f"error: {e}")
        return papers
