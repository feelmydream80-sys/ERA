from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app import db
from app.models import Paper
from app.crawlers.ieee import IEEECrawler
from app.crawlers.arxiv import ArxivCrawler
from app.crawlers.kci import KCICrawler
from app.crawlers.kee import KEECrawler
import atexit
from datetime import datetime, timezone


scheduler = BackgroundScheduler()


def run_all_crawlers(app):
    crawlers = [IEEECrawler(), ArxivCrawler(), KCICrawler(), KEECrawler()]
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{ts}] === Crawler Run Started ===")
    total_new = 0
    with app.app_context():
        for crawler in crawlers:
            try:
                crawler.log("starting...")
                papers = crawler.crawl()
                new_count = 0
                seen_urls = set()
                for p in papers:
                    url = p["source_url"]
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    existing = Paper.query.filter_by(source_url=url).first()
                    if not existing:
                        paper = Paper(
                            title=p["title"],
                            authors=p.get("authors", ""),
                            abstract=p.get("abstract", ""),
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
        print(f"  [{ts}] === Crawler Run Finished: {total_new} new papers (DB total: {total_db}) ===")


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
