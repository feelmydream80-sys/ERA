import threading
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from app.models import CrawlLog
from app.scheduler import scheduler, run_all_crawlers
from datetime import datetime, timezone

bp = Blueprint("logs", __name__, url_prefix="/logs")


@bp.route("")
def index():
    page_logs = (
        CrawlLog.query.order_by(CrawlLog.created_at.desc())
        .limit(100)
        .all()
    )
    scheduler_running = scheduler.running
    next_run = None
    for job in scheduler.get_jobs():
        if job.id == "crawl_papers":
            next_run = job.next_run_time
            break
    return render_template(
        "logs.html",
        logs=page_logs,
        scheduler_running=scheduler_running,
        next_run=next_run,
        now=datetime.now(timezone.utc),
    )


@bp.route("/run", methods=["POST"])
def run():
    app = current_app._get_current_object()
    threading.Thread(target=run_all_crawlers, args=(app,), daemon=True).start()
    flash("Crawlers started in background", "success")
    return redirect(url_for("logs.index"))
