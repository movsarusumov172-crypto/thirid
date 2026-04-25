from __future__ import annotations

from dataclasses import replace

from money_tracker.models import ENTRY_TYPES, EntryType, MoneyEntry, MoneyEntryDraft, MoneySummary


class MoneyRepositoryProtocol:
    def add(self, draft: MoneyEntryDraft) -> MoneyEntry:
        raise NotImplementedError

    def list_all(self) -> list[MoneyEntry]:
        raise NotImplementedError

    def delete(self, entry_id: int) -> None:
        raise NotImplementedError


def create_entry(repo: MoneyRepositoryProtocol, draft: MoneyEntryDraft) -> MoneyEntry:
    cleaned = _clean_draft(draft)
    _validate_draft(cleaned)
    return repo.add(cleaned)


def list_entries(
    repo: MoneyRepositoryProtocol,
    month: str | None = None,
    entry_type: EntryType | None = None,
    category: str | None = None,
) -> list[MoneyEntry]:
    entries = repo.list_all()
    if month:
        entries = [entry for entry in entries if entry.entry_date.strftime("%Y-%m") == month]
    if entry_type:
        entries = [entry for entry in entries if entry.entry_type == entry_type]
    if category:
        entries = [entry for entry in entries if entry.category.lower() == category.lower()]
    return sorted(entries, key=lambda entry: (entry.entry_date, entry.id), reverse=True)


def get_summary(repo: MoneyRepositoryProtocol, month: str | None = None) -> MoneySummary:
    entries = list_entries(repo, month=month)
    total_income = sum(entry.amount for entry in entries if entry.entry_type == "income")
    total_expense = sum(entry.amount for entry in entries if entry.entry_type == "expense")
    expenses_by_category: dict[str, float] = {}

    for entry in entries:
        if entry.entry_type != "expense":
            continue
        expenses_by_category[entry.category] = expenses_by_category.get(entry.category, 0) + entry.amount

    return MoneySummary(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        expenses_by_category=expenses_by_category,
    )


def delete_entry(repo: MoneyRepositoryProtocol, entry_id: int) -> None:
    repo.delete(entry_id)


def _clean_draft(draft: MoneyEntryDraft) -> MoneyEntryDraft:
    return replace(
        draft,
        title=draft.title.strip(),
        category=draft.category.strip(),
        note=draft.note.strip(),
    )


def _validate_draft(draft: MoneyEntryDraft) -> None:
    if not draft.title:
        raise ValueError("Title is required.")
    if draft.amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not draft.category:
        raise ValueError("Category is required.")
    if draft.entry_type not in ENTRY_TYPES:
        raise ValueError("Entry type must be income or expense.")
