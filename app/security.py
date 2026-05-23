import os
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "")

# auto_error=False: el chequeo lo hace require_api_key (para devolver un 401 propio),
# pero el esquema igual aparece como botón "Authorize" en Swagger UI.
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided_key: str | None = Security(_api_key_header)) -> None:
    """Exige un header X-API-Key válido.

    Fail-secure: si el servidor no tiene API_KEY configurada, rechaza con 503 en vez
    de dejar la API abierta. La comparación es constant-time (anti timing attack).
    """
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key not configured on the server",
        )
    if not provided_key or not secrets.compare_digest(provided_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
