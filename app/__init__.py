import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from config import Config

db = SQLAlchemy()
admin_instance = Admin(name="Power Papers Admin")


def seed_default_keywords():
    from app.models import SearchKeyword, DEFAULT_KEYWORDS
    for kw_data in DEFAULT_KEYWORDS:
        existing = SearchKeyword.query.filter_by(
            keyword=kw_data["keyword"], language=kw_data["language"]
        ).first()
        if not existing:
            kw = SearchKeyword(**kw_data, enabled=True)
            db.session.add(kw)
    db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    admin_instance.init_app(app)

    from app.views import feed, search, kakao, settings
    app.register_blueprint(feed.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(kakao.bp)
    app.register_blueprint(settings.bp)

    from app.admin import register_admin
    register_admin(admin_instance)

    from app.scheduler import init_scheduler, run_all_crawlers
    init_scheduler(app)

    with app.app_context():
        db.create_all()
        seed_default_keywords()

    thread = threading.Thread(target=run_all_crawlers, args=[app], daemon=True)
    thread.start()

    return app
