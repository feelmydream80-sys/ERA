import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base import BaseCrawler


class KCICrawler(BaseCrawler):
    """
    KCI (Korean Citation Index) web search.
    Uses POST with correct form parameter names.
    Korean IP may be required.
    """
    name = "KCI-Web"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        seen_urls = set()

        for kw in all_keywords:
            for page in range(1, 6):
                self.log(f'searching "{kw}" page {page}...')
                try:
                    resp = requests.post(
                        "https://www.kci.go.kr/kciportal/po/search/poArtiSearList.kci",
                        data={
                            "poSearchBean.keywordList": kw,
                            "poSearchBean.searType": "thesis",
                            "poSearchBean.startPg": str(page),
                        },
                        headers=headers, timeout=15,
                    )
                    if resp.status_code != 200:
                        self.log(f"HTTP {resp.status_code}")
                        break
                    soup = BeautifulSoup(resp.text, "lxml")
                    rows = soup.select(".search-answer-tbl tr")
                    page_has_data = False
                    for row in rows:
                        tds = row.find_all("td")
                        if len(tds) < 3:
                            continue
                        number_td = tds[1]
                        number_text = number_td.get_text(strip=True) if number_td else ""
                        if not number_text.replace(".", "").strip().isdigit():
                            continue
                        title_td = tds[2]
                        title_el = title_td.select_one("a.subject") if title_td else None
                        if not title_el:
                            continue
                        title_text = title_el.get_text(strip=True)
                        if not title_text:
                            continue
                        if kw.lower() not in title_text.lower():
                            continue
                        href = title_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = "https://www.kci.go.kr" + href
                        if href in seen_urls:
                            continue
                        seen_urls.add(href)
                        page_has_data = True

                        info_ul = title_td.select_one("ul.subject-info")
                        authors = ""
                        pub_date = None
                        if info_ul:
                            author_links = info_ul.select("li a[href*=poCretDetail]")
                            author_names = []
                            for a in author_links:
                                name = a.get_text(strip=True)
                                if name:
                                    author_names.append(name)
                            if author_names:
                                authors = ", ".join(author_names)

                            date_text = ""
                            for li in info_ul.find_all("li", recursive=False):
                                li_text = li.get_text(strip=True)
                                if li_text and not li.select_one("a") and "." in li_text and len(li_text) <= 10:
                                    date_text = li_text
                                    break
                            if date_text:
                                try:
                                    parts = date_text.strip().split(".")
                                    if len(parts) >= 2:
                                        pub_date = datetime(int(parts[0]), int(parts[1]), 1).date()
                                except Exception:
                                    pass

                        papers.append({
                            "title": title_text,
                            "source_url": href,
                            "source": self.name,
                            "authors": authors,
                            "abstract": "",
                            "published_date": pub_date,
                            "keywords": "",
                        })
                    if not page_has_data:
                        break
                except Exception as e:
                    self.log(f"error: {e}")
                    break
        return papers
