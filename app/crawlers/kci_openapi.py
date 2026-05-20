import requests
import hashlib
import xml.etree.ElementTree as ET
from urllib.parse import quote
from datetime import datetime
from .base import BaseCrawler


class KCIOpenAPICrawler(BaseCrawler):
    """
    KCI Open API (https://open.kci.go.kr)
    Requires a KCI Open API key issued from:
      https://www.kci.go.kr/kciportal/po/openapi/openApiKeyRequest.kci

    Endpoint:
      GET https://open.kci.go.kr/po/openapi/openApiSearch.kci
        ?apiCode=articleSearch
        &key=YOUR_KEY
        &keyword=SEARCH_TERM
        &displayCount=100

    This is DIFFERENT from the 공공데이터포털 key (data 15083283).
    KCI Open API key must be obtained separately from KCI website (login required).
    """
    name = "KCI"

    def get_api_key(self):
        try:
            from flask import current_app
            return current_app.config.get("KCI_OPENAPI_KEY", "")
        except (RuntimeError, ImportError):
            import os
            return os.environ.get("KCI_OPENAPI_KEY", "")

    def crawl(self):
        api_key = self.get_api_key()
        if not api_key:
            self.log("SKIP: KCI_OPENAPI_KEY not configured")
            self.log("Get a key: https://www.kci.go.kr/kciportal/po/openapi/openApiKeyRequest.kci")
            return []

        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))

        papers = []
        seen_urls = set()
        url = "https://open.kci.go.kr/po/openapi/openApiSearch.kci"

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.get(url, params={
                    "apiCode": "articleSearch",
                    "key": api_key,
                    "keyword": kw,
                    "displayCount": 100,
                    "sortNm": "정확도",
                }, timeout=30)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                root = ET.fromstring(resp.content)
                for record in root.iter("record"):
                    title = record.findtext("title", "").strip()
                    if not title:
                        continue
                    doi = record.findtext("doi", "") or ""
                    paper_url = record.findtext("url", "") or ""
                    source_url = paper_url or (f"https://doi.org/{doi}" if doi else "")
                    if source_url and source_url in seen_urls:
                        continue
                    if source_url:
                        seen_urls.add(source_url)
                    if not source_url:
                        uid = hashlib.md5(title.encode()).hexdigest()[:12]
                        source_url = f"https://kci.go.kr/openapi/{uid}"
                    authors = record.findtext("author", "") or ""
                    abstract = record.findtext("abstract", "") or ""
                    journal = record.findtext("journal", "") or ""
                    pub_year = record.findtext("pubYr", "") or ""
                    pub_date = None
                    if pub_year and len(pub_year) >= 4:
                        try:
                            pub_date = datetime(int(pub_year[:4]), 1, 1).date()
                        except Exception:
                            pass
                    papers.append({
                        "title": title,
                        "source_url": source_url,
                        "source": self.name,
                        "authors": authors,
                        "abstract": abstract,
                        "published_date": pub_date,
                        "keywords": kw,
                        "venue": journal,
                    })
            except ET.ParseError as e:
                self.log(f"XML parse error: {e}")
            except Exception as e:
                self.log(f"error: {e}")
        self.log(f"done: {len(papers)} total")
        return papers
