import requests
import re
import hashlib
from datetime import datetime
from .base import BaseCrawler


def norm(t):
    return re.sub(r"[^a-z0-9\uac00-\ud7a3\s]", "", t.lower().strip())


class KCIOpenAPICrawler(BaseCrawler):
    """
    KCI 논문정보 via 공공데이터포털 (data 15083283)
    Endpoint: api.odcloud.kr/api/15083283/v1/uddi:fb7f923a-a93b-4ae8-8df2-cbf6e70edf49
    Key from: https://www.data.go.kr/data/15083283/openapi.do
    Pass decoded key as ?serviceKey query param.
    Scans recent pages and matches by title/keyword (no server-side search).
    """
    name = "KCI"

    def get_service_key(self):
        try:
            from flask import current_app
            return current_app.config.get("KCI_SERVICE_KEY", "")
        except (RuntimeError, ImportError):
            import os
            return os.environ.get("KCI_SERVICE_KEY", "")

    def crawl(self):
        service_key = self.get_service_key()
        if not service_key:
            self.log("SKIP: KCI_SERVICE_KEY not configured")
            return []

        keywords_en = self.get_keywords(language="en")
        keywords_ko = self.get_keywords(language="ko")
        norm_kws = [norm(kw) for kw in set(keywords_en + keywords_ko) if kw.strip()]
        if not norm_kws:
            return []

        url = "https://api.odcloud.kr/api/15083283/v1/uddi:fb7f923a-a93b-4ae8-8df2-cbf6e70edf49"
        papers = []
        seen = set()
        pages = 50

        for page in range(1, pages + 1):
            self.log(f"page {page}/{pages}...")
            try:
                resp = requests.get(url, params={
                    "page": page, "perPage": 100,
                    "returnType": "JSON", "serviceKey": service_key,
                }, timeout=30)
                if resp.status_code != 200:
                    self.log(f"HTTP {resp.status_code}")
                    break
                items = resp.json().get("data", [])
                if not items:
                    break
                for item in items:
                    title_en = norm(item.get("논문명(영어)") or "")
                    title_ko = norm(item.get("논문명(국문)") or "")
                    kw_en = norm(item.get("키워드(영어)") or item.get("키워드(외국어)") or "")
                    kw_ko = norm(item.get("키워드(국문)") or "")
                    combined = f"{title_en} {title_ko} {kw_en} {kw_ko}"
                    if not any(kw in combined for kw in norm_kws):
                        continue
                    uid = hashlib.md5(combined.encode()).hexdigest()[:12]
                    if uid in seen:
                        continue
                    seen.add(uid)
                    authors = "; ".join(filter(None, [item.get("저자"), item.get("공동저자")]))
                    pub_year = item.get("발행년")
                    pub_date = None
                    if pub_year:
                        try:
                            pub_date = datetime(int(pub_year), 1, 1).date()
                        except Exception:
                            pass
                    papers.append({
                        "title": item.get("논문명(국문)") or item.get("논문명(영어)") or "",
                        "source_url": f"https://kci.go.kr/odcloud/{uid}",
                        "source": self.name,
                        "authors": authors.strip("; "),
                        "abstract": "",
                        "published_date": pub_date,
                        "keywords": item.get("키워드(국문)") or item.get("키워드(영어)") or "",
                    })
            except Exception as e:
                self.log(f"error: {e}")
                break
        self.log(f"done: {len(papers)} matched from {pages} pages")
        return papers
