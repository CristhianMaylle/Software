from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import PaginatedTransactions, TransactionCreate, TransactionResponse

router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new transaction",
)
def create_transaction(
    payload: TransactionCreate, db: Session = Depends(get_db)
) -> Transaction:
    transaction = Transaction(
        amount=payload.amount,
        type=payload.type,
        description=payload.description,
        date=payload.date or datetime.now(UTC),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get(
    "",
    response_model=PaginatedTransactions,
    summary="List transactions with pagination",
)
def list_transactions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> PaginatedTransactions:
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit cannot exceed 100",
        )
    total = db.scalar(select(func.count()).select_from(Transaction)) or 0
    rows = list(db.scalars(select(Transaction).offset(skip).limit(limit)).all())
    return PaginatedTransactions(total=total, skip=skip, limit=limit, data=rows)
