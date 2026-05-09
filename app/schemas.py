from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    type: Literal["ingreso", "egreso"] = Field(
        ..., description="Transaction type: 'ingreso' (income) or 'egreso' (expense)"
    )
    description: str = Field(..., min_length=1, max_length=255)
    date: datetime | None = Field(
        default=None, description="Transaction date (defaults to now)"
    )


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    type: str
    description: str
    date: datetime


class PaginatedTransactions(BaseModel):
    total: int
    skip: int
    limit: int
    data: list[TransactionResponse]


class BalanceResponse(BaseModel):
    total_ingresos: float
    total_egresos: float
    balance: float
