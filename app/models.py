from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid


def short_id() -> str:
    return uuid.uuid4().hex[:8]


class Participant(BaseModel):
    id: str = Field(default_factory=short_id)
    name: str


class BillItem(BaseModel):
    id: str = Field(default_factory=short_id)
    name: str
    unit_price: Decimal
    quantity: int = 1
    claimed_by: dict[str, int] = Field(default_factory=dict)

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    @property
    def claimed_quantity(self) -> int:
        return sum(self.claimed_by.values())


class ParsedBill(BaseModel):
    items: list[BillItem]
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    tip: Optional[Decimal] = None
    total: Optional[Decimal] = None


class Session(BaseModel):
    id: str
    created_at: datetime
    host_id: str
    participants: dict[str, Participant] = Field(default_factory=dict)
    items: list[BillItem] = Field(default_factory=list)
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    tip: Optional[Decimal] = None
    total: Optional[Decimal] = None
    version: int = 0


class ParticipantTotal(BaseModel):
    participant_id: str
    name: str
    claimed_subtotal: Decimal
    tax_share: Decimal
    tip_share: Decimal
    total_owed: Decimal
