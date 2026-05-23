# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# psycopg[binary] trae su propia libpq precompilada: no hacen falta paquetes del
# sistema (a diferencia del driver ODBC de SQL Server, que se eliminó).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El proceso no corre como root dentro del contenedor (defensa en profundidad).
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
