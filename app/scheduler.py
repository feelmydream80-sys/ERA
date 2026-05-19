from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from deep_translator import GoogleTranslator
from app import db
from app.models import Paper
from app.crawlers.ieee import IEEECrawler
from app.crawlers.arxiv import ArxivCrawler
from app.crawlers.openalex import OpenAlexCrawler
from app.crawlers.crossref import CrossrefCrawler
import atexit
from datetime import datetime, timezone


scheduler = BackgroundScheduler()


import re


def normalize_title(title):
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9\uac00-\ud7a3\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def translate_abstract(text):
    if not text or len(text) < 10:
        return ""
    try:
        source = "en" if all(ord(c) < 128 for c in text[:100]) else "auto"
        return GoogleTranslator(source=source, target="ko").translate(text[:2000])
    except Exception:
        return ""


def run_all_crawlers(app):
    crawlers = [ArxivCrawler(), IEEECrawler(), OpenAlexCrawler(), CrossrefCrawler()]
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{ts}] === Crawler Run Started ===")
    total_new = 0
    title_dup_count = 0
    with app.app_context():
        seen_urls = set()
        seen_titles = set()
        for crawler in crawlers:
            try:
                crawler.log("starting...")
                papers = crawler.crawl()
                new_count = 0
                for p in papers:
                    url = p["source_url"]
                    norm_title = normalize_title(p["title"])
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    if norm_title and norm_title in seen_titles:
                        title_dup_count += 1
                        continue
                    if norm_title:
                        existing_by_title = Paper.query.filter(
                            db.func.lower(Paper.title).contains(p["title"][:30])
                        ).first() if norm_title else None
                        if existing_by_title:
                            seen_titles.add(norm_title)
                            title_dup_count += 1
                            continue
                        seen_titles.add(norm_title)
                    existing = Paper.query.filter_by(source_url=url).first()
                    if not existing:
                        abstract_text = p.get("abstract", "")
                        paper = Paper(
                            title=p["title"],
                            authors=p.get("authors", ""),
                            abstract=abstract_text,
                            abstract_ko=translate_abstract(abstract_text),
                            keywords=p.get("keywords", ""),
                            source=p.get("source", crawler.name),
                            source_url=url,
                            published_date=p.get("published_date"),
                            crawled_at=datetime.now(timezone.utc),
                            is_new=True,
                        )
                        db.session.add(paper)
                        new_count += 1
                db.session.commit()
                total_new += new_count
                crawler.log(f"complete: {len(papers)} found, {new_count} new")
            except Exception as e:
                db.session.rollback()
                crawler.log(f"ERROR: {e}")
                app.logger.error(f"Crawler {crawler.name} failed: {e}")
        ts = datetime.now().strftime("%H:%M:%S")
        total_db = Paper.query.count()
        print(f"  [{ts}] === Crawler Run Finished: {total_new} new papers (DB total: {total_db}, title dups skipped: {title_dup_count}) ===")


def init_scheduler(app):
    scheduler.add_job(
        func=run_all_crawlers,
        trigger=IntervalTrigger(hours=1),
        args=[app],
        id="crawl_papers",
        replace_existing=True,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
