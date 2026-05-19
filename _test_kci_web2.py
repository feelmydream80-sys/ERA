import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.environ["PYTHONIOENCODING"] = "utf-8"

from flask import Flask
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

from app import db
from app.models import SearchKeyword, DEFAULT_KEYWORDS

with app.app_context():
    db.init_app(app)
    db.create_all()
    for kw_data in DEFAULT_KEYWORDS:
        if not SearchKeyword.query.filter_by(keyword=kw_data["keyword"], language=kw_data["language"]).first():
            db.session.add(SearchKeyword(**kw_data, enabled=True))
    db.session.commit()

    from app.crawlers.kci import KCICrawler
    c = KCICrawler()
    papers = c.crawl()
    print(f"KCI: {len(papers)} papers")
    for p in papers[:5]:
        print(f"  {p['title'][:50]}")
        print(f"    authors: {p.get('authors','')[:30] or 'N/A'}")
        print(f"    url: {p.get('source_url','')[:60]}")
