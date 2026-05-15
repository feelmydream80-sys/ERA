from app import create_app, db
from app.models import Paper
from datetime import datetime

app = create_app()

with app.app_context():
    total = Paper.query.count()

print()
print("=" * 50)
print("  Power Papers Server Started")
print("=" * 50)
print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  DB      : {total} papers stored")
print(f"  Routes  :")
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    if not r.rule.startswith("/admin") and r.rule != "/static/<path:filename>":
        print(f"    {r.rule:30s} -> {r.endpoint}")
print(f"  Scheduler: APScheduler active (hourly crawl)")
print(f"  Admin   : http://localhost:5000/admin/")
print("=" * 50)
print()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
