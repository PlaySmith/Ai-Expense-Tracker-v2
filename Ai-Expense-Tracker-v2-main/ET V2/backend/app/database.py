from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# SQLite DB
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "smartspend_v2.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def migrate_sqlite_users_columns() -> None:
    """Add user columns on existing DBs (create_all does not ALTER SQLite tables)."""
    if "sqlite" not in SQLALCHEMY_DATABASE_URL:
        return
    try:
        with engine.begin() as conn:
            rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            names = {r[1] for r in rows}
            if "full_name" not in names:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(255)"))
            if "phone" not in names:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(50)"))
    except Exception:
        return


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

