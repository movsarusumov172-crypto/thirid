from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal


EntryType = Literal["expense", "income"]
ENTRY_TYPES: tuple[EntryType, ...] = ("expense", "income")


@dataclass(frozen=True)
class MoneyEntryDraft:
    title: str
    amount: float
    category: str
    entry_type: EntryType
    entry_date: date
    note: str = ""


@dataclass(frozen=True)
class MoneyEntry:
    id: int
    title: str
    amount: float
    category: str
    entry_type: EntryType
    entry_date: date
    note: str = ""


@dataclass(frozen=True)
class MoneySummary:
    total_income: float
    total_expense: float
    balance: float
    expenses_by_category: dict[str, float]
