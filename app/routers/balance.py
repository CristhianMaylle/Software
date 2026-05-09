from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import BalanceResponse

router = APIRouter(prefix="/api/v1/balance", tags=["Balance"])


@router.get("", response_model=BalanceResponse, summary="Get current financial summary")
def get_balance(db: Session = Depends(get_db)) -> BalanceResponse:
    total_ingresos: float = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
            Transaction.type == "ingreso"
        )
    ) or 0.0

    total_egresos: float = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
            Transaction.type == "egreso"
        )
    ) or 0.0

    return BalanceResponse(
        total_ingresos=total_ingresos,
        total_egresos=total_egresos,
        balance=total_ingresos - total_egresos,
    )
