from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import SearchKeyword

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/")
def index():
    keywords = SearchKeyword.query.order_by(SearchKeyword.language, SearchKeyword.keyword).all()
    return render_template("settings.html", keywords=keywords)


@bp.route("/add", methods=["POST"])
def add():
    keyword = request.form.get("keyword", "").strip()
    language = request.form.get("language", "en")
    if not keyword:
        flash("Keyword cannot be empty", "danger")
        return redirect(url_for("settings.index"))
    existing = SearchKeyword.query.filter_by(keyword=keyword, language=language).first()
    if existing:
        flash(f"Keyword '{keyword}' already exists", "warning")
    else:
        kw = SearchKeyword(keyword=keyword, language=language, enabled=True)
        db.session.add(kw)
        db.session.commit()
        flash(f"Keyword '{keyword}' added", "success")
    return redirect(url_for("settings.index"))


@bp.route("/toggle/<int:kw_id>")
def toggle(kw_id):
    kw = SearchKeyword.query.get_or_404(kw_id)
    kw.enabled = not kw.enabled
    db.session.commit()
    flash(f"{'Enabled' if kw.enabled else 'Disabled'} keyword '{kw.keyword}'", "success")
    return redirect(url_for("settings.index"))


@bp.route("/delete/<int:kw_id>")
def delete(kw_id):
    kw = SearchKeyword.query.get_or_404(kw_id)
    db.session.delete(kw)
    db.session.commit()
    flash(f"Deleted keyword '{kw.keyword}'", "success")
    return redirect(url_for("settings.index"))
