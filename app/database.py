import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "FinanceControl")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YourPassword!123")

_OPTS = "driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}?{_OPTS}"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_database() -> None:
    """Create the SQL Server database if it does not exist yet."""
    master_url = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/master?{_OPTS}"
    )
    tmp = create_engine(master_url, isolation_level="AUTOCOMMIT")
    with tmp.connect() as conn:
        conn.execute(
            text(
                f"IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'{DB_NAME}') "
                f"CREATE DATABASE [{DB_NAME}]"
            )
        )
    tmp.dispose()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
