from datetime import datetime, timezone
from app import db


class SearchKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(10), nullable=False, default="en")
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<SearchKeyword {self.keyword} ({self.language})>"


DEFAULT_KEYWORDS = [
    {"keyword": "power system", "language": "en"},
    {"keyword": "smart grid", "language": "en"},
    {"keyword": "renewable energy", "language": "en"},
    {"keyword": "energy storage", "language": "en"},
    {"keyword": "electric grid", "language": "en"},
    {"keyword": "power electronics", "language": "en"},
    {"keyword": "microgrid", "language": "en"},
    {"keyword": "HVDC", "language": "en"},
    {"keyword": "solar energy", "language": "en"},
    {"keyword": "wind power", "language": "en"},
    {"keyword": "전력계통", "language": "ko"},
    {"keyword": "스마트그리드", "language": "ko"},
    {"keyword": "신재생에너지", "language": "ko"},
    {"keyword": "에너지저장장치", "language": "ko"},
    {"keyword": "마이크로그리드", "language": "ko"},
    {"keyword": "배터리", "language": "ko"},
    {"keyword": "태양광", "language": "ko"},
    {"keyword": "풍력", "language": "ko"},
    {"keyword": "직류송전", "language": "ko"},
    {"keyword": "전력전자", "language": "ko"},
]


class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    authors = db.Column(db.Text, default="")
    abstract = db.Column(db.Text, default="")
    abstract_ko = db.Column(db.Text, default="")
    keywords = db.Column(db.Text, default="")
    source = db.Column(db.String(100), nullable=False, index=True)
    source_url = db.Column(db.String(500), unique=True, nullable=False)
    published_date = db.Column(db.Date, nullable=True)
    crawled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_new = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Paper {self.title[:50]}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "source": self.source,
            "source_url": self.source_url,
            "published_date": str(self.published_date) if self.published_date else "",
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else "",
            "is_new": self.is_new,
        }


class CrawlLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="started")
    found_count = db.Column(db.Integer, default=0)
    new_count = db.Column(db.Integer, default=0)
    message = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CrawlLog {self.source} {self.status} @ {self.created_at}>"
