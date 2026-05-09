from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine, ensure_database
from app.routers import balance, transactions


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Skip SQL Server-specific init when running under SQLite (tests)
    if engine.dialect.name != "sqlite":
        ensure_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Finance Control API",
    description=(
        "API RESTful para gestionar transacciones financieras (ingresos y egresos). "
        "Usa Swagger UI para explorar y probar los endpoints."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(transactions.router)
app.include_router(balance.router)


@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
