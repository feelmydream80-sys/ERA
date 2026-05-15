from flask_admin.contrib.sqla import ModelView
from app import db
from app.models import Paper


class PaperAdmin(ModelView):
    column_list = ("title", "source", "published_date", "is_new", "created_at")
    column_searchable_list = ("title", "authors", "abstract", "keywords")
    column_filters = ("source", "is_new", "published_date")
    column_default_sort = ("created_at", True)
    form_columns = ("title", "authors", "abstract", "keywords", "source", "source_url", "published_date", "is_new")
    create_template = "admin_edit.html"
    edit_template = "admin_edit.html"


def register_admin(admin_):
    admin_.add_view(PaperAdmin(Paper, db.session))
