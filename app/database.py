import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "finance_control")
DB_USER = os.getenv("DB_USER", "finance")
DB_PASSWORD = os.getenv("DB_PASSWORD", "finance_secret")

# PostgreSQL via psycopg 3 (driver name "psycopg" in SQLAlchemy 2.0).
DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
)

# pool_pre_ping recicla conexiones muertas (el server cierra idle connections);
# evita errores "server closed the connection unexpectedly" en runtime largo.
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
