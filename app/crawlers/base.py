from datetime import datetime
from app import db
from app.models import SearchKeyword


class BaseCrawler:
    name = "base"

    def crawl(self):
        raise NotImplementedError

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] Crawler[{self.name}] {message}")

    def get_keywords(self, language=None):
        q = SearchKeyword.query.filter_by(enabled=True)
        if language:
            q = q.filter_by(language=language)
        return [kw.keyword for kw in q.all()]
