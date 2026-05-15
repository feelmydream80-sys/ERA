import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from .base import BaseCrawler


class KCICrawler(BaseCrawler):
    name = "KCI"

    def crawl(self):
        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            url = f"https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci?searchType=TOTAL&searchWord={quote(kw)}&order=DESC&sort=REGISTER&pageSize=10"
            try:
                resp = requests.get(url, headers=headers, timeout=15, verify=False)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                for item in soup.select(".search-result-item, tr"):
                    title_el = item.select_one(".title a, .subject a")
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
                        "keywords": kw,
                    })
            except requests.exceptions.SSLError:
                try:
                    resp = requests.get(url, headers=headers, timeout=15)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "lxml")
                        for item in soup.select(".search-result-item, tr"):
                            title_el = item.select_one(".title a, .subject a")
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
                                "keywords": kw,
                            })
                except Exception as e:
                    self.log(f"error: {e}")
            except Exception as e:
                self.log(f"error: {e}")
        return papers
