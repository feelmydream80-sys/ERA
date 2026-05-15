from flask import Blueprint, jsonify, request, render_template
from app.models import Paper

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("")
def search():
    query = request.args.get("q", "").strip()
    source = request.args.get("source", "")
    page = request.args.get("page", 1, type=int)

    q = Paper.query.order_by(Paper.created_at.desc())

    if query:
        q = q.filter(
            Paper.title.ilike(f"%{query}%")
            | Paper.abstract.ilike(f"%{query}%")
            | Paper.keywords.ilike(f"%{query}%")
            | Paper.authors.ilike(f"%{query}%")
        )
    if source:
        q = q.filter(Paper.source == source)

    pagination = q.paginate(page=page, per_page=20, error_out=False)

    if request.headers.get("HX-Request"):
        return render_template(
            "_paper_cards.html",
            papers=pagination.items,
            pagination=pagination,
        )

    return render_template(
        "search.html",
        papers=pagination.items,
        pagination=pagination,
        query=query,
        selected_source=source,
    )
