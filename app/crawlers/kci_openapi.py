import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from .base import BaseCrawler
from flask import current_app


class KCIOpenAPICrawler(BaseCrawler):
    """
    KCI Open API (via 공공데이터포털 data.go.kr)
    Requires KCI_SERVICE_KEY env var or config value.

    API docs: https://www.data.go.kr/data/3049042/openapi.do
    Endpoint: http://apis.data.go.kr/B552540/KCIOpenApi/artiInfo/openApiD217List
    """
    name = "KCI"

    def get_service_key(self):
        try:
            return current_app.config.get("KCI_SERVICE_KEY", "")
        except RuntimeError:
            import os
            return os.environ.get("KCI_SERVICE_KEY", "")

    def crawl(self):
        service_key = self.get_service_key()
        if not service_key:
            self.log("SKIP: KCI_SERVICE_KEY not configured (register at data.go.kr)")
            return []

        papers = []
        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        all_keywords = list(set(keywords_en + keywords_ko))

        for kw in all_keywords:
            self.log(f'searching "{kw}"...')
            try:
                resp = requests.get(
                    "http://apis.data.go.kr/B552540/KCIOpenApi/artiInfo/openApiD217List",
                    params={
                        "ServiceKey": service_key,
                        "recordCnt": 10,
                        "pageNo": 1,
                        "searchWord": kw,
                        "sort": "RANK",
                    },
                    timeout=15,
                )
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    continue
                root = ET.fromstring(resp.text.encode("utf-8"))
                ns = {"ns": "http://apis.data.go.kr/B552540/KCIOpenApi/artiInfo/openApiD217List"}
                for item in root.iter("item"):
                    title_el = item.find("artiTitle")
                    title = (title_el.text or "").strip() if title_el is not None else ""
                    if not title:
                        continue
                    authors_el = item.find("artiAuthorNm")
                    authors = (authors_el.text or "").strip() if authors_el is not None else ""
                    abstract_el = item.find("artiAbstract")
                    abstract = (abstract_el.text or "").strip() if abstract_el is not None else ""
                    doi_el = item.find("artiDOI")
                    doi = (doi_el.text or "").strip() if doi_el is not None else ""
                    url_el = item.find("artiUrl")
                    url = (url_el.text or "").strip() if url_el is not None else ""
                    pub_year_el = item.find("pubYear")
                    pub_year = (pub_year_el.text or "").strip() if pub_year_el is not None else ""
                    pub_date = None
                    if pub_year:
                        try:
                            pub_date = datetime(int(pub_year), 1, 1).date()
                        except Exception:
                            pass
                    jnl_el = item.find("jnlTitle")
                    journal = (jnl_el.text or "").strip() if jnl_el is not None else ""
                    papers.append({
                        "title": title,
                        "source_url": url or (f"https://doi.org/{doi}" if doi else ""),
                        "source": self.name,
                        "authors": authors,
                        "abstract": abstract,
                        "doi": doi,
                        "published_date": pub_date,
                        "keywords": kw,
                        "venue": journal,
                    })
            except ET.ParseError as e:
                self.log(f"XML parse error for '{kw}': {e}")
            except Exception as e:
                self.log(f"error: {e}")
        return papers
