import os
import sys

# Ensure repository root is on sys.path to import 'app'
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from app import create_app
from app.models import db

SQLITE_ADD_COLUMNS = [
    ("user", "role", "TEXT NOT NULL DEFAULT 'recepcionista'"),
    ("user", "failed_login_attempts", "INTEGER NOT NULL DEFAULT 0"),
    ("user", "locked_until", "DATETIME NULL"),
]


def column_exists(conn, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info('{table}')")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols


def ensure_columns():
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        conn = db.engine.raw_connection()
        try:
            changed = False
            for table, col, ddl in SQLITE_ADD_COLUMNS:
                if not column_exists(conn, table, col):
                    print(f"Adding missing column {table}.{col} ...")
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
                    changed = True
            if changed:
                conn.commit()
                print("Migration applied successfully.")
            else:
                print("No migration needed. Schema already up to date.")
        finally:
            conn.close()


if __name__ == "__main__":
    ensure_columns()
