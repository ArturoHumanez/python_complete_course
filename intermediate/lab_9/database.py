from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from intermediate.lab_8.models import Base

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "orders_api.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def create_tables() -> None:
    Base.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
