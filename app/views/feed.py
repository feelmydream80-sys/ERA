import json
from flask import Blueprint, render_template, request
from app.models import Paper

bp = Blueprint("feed", __name__, url_prefix="/")


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    source = request.args.get("source", "")
    query = request.args.get("q", "")

    papers_query = Paper.query.order_by(Paper.created_at.desc())

    if source:
        papers_query = papers_query.filter(Paper.source == source)
    if query:
        papers_query = papers_query.filter(
            Paper.title.ilike(f"%{query}%")
            | Paper.abstract.ilike(f"%{query}%")
            | Paper.keywords.ilike(f"%{query}%")
        )

    pagination = papers_query.paginate(
        page=page, per_page=20, error_out=False
    )
    papers = pagination.items

    sources = [s[0] for s in Paper.query.with_entities(Paper.source).distinct().all()]

    return render_template(
        "feed.html",
        papers=papers,
        pagination=pagination,
        sources=sources,
        selected_source=source,
        query=query,
    )


@bp.route("/papers/<int:paper_id>")
def detail(paper_id):
    paper = Paper.query.get_or_404(paper_id)
    return render_template("detail.html", paper=paper)


@bp.route("/health")
def health():
    from datetime import datetime
    total = Paper.query.count()
    sources = [s[0] for s in Paper.query.with_entities(Paper.source).distinct().all()]
    return {
        "status": "ok",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_papers": total,
        "sources": sources,
    }
