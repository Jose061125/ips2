import os, sys, sqlite3

# Ensure repo root in sys.path
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import create_app
from app.models import db

ROOT = os.path.abspath(os.path.dirname(__file__)+"/..")
root_db = os.path.join(ROOT, 'app.db')
instance_db = os.path.join(ROOT, 'instance', 'app.db')

print('Exists root app.db:', os.path.exists(root_db), root_db)
print('Exists instance app.db:', os.path.exists(instance_db), instance_db)

if os.path.exists(root_db):
    conn = sqlite3.connect(root_db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info('user')").fetchall()]
    print('root app.db user columns:', cols)
    conn.close()

if os.path.exists(instance_db):
    conn = sqlite3.connect(instance_db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info('user')").fetchall()]
    print('instance app.db user columns:', cols)

    # List tables
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print('Tables:', tables)

    def count(table):
        try:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except Exception as e:
            return f"error: {e}"

    # Row counts for key tables
    for t in ['user', 'patients', 'appointments', 'medical_records', 'employees']:
        if t in tables:
            print(f"{t}: {count(t)} rows")

    # Sample rows (safe projection)
    if 'user' in tables:
        rows = conn.execute("SELECT id, username, role, failed_login_attempts, locked_until FROM user LIMIT 5").fetchall()
        print('user sample (id, username, role, failed_login_attempts, locked_until):', rows)
    if 'patients' in tables:
        rows = conn.execute("SELECT id, first_name, last_name, document FROM patients LIMIT 5").fetchall()
        print('patients sample (id, first_name, last_name, document):', rows)
    conn.close()

app = create_app()
with app.app_context():
    print('SQLALCHEMY_DATABASE_URI at runtime:', str(db.engine.url))
    # List columns from runtime-connected DB
    conn = db.engine.raw_connection()
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info('user')").fetchall()]
        print('runtime DB user columns:', cols)
    finally:
        conn.close()
