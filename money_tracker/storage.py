from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from money_tracker.models import EntryType, MoneyEntry, MoneyEntryDraft


class MoneyRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def add(self, draft: MoneyEntryDraft) -> MoneyEntry:
        with closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO money_entries (title, amount, category, entry_type, entry_date, note)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        draft.title,
                        draft.amount,
                        draft.category,
                        draft.entry_type,
                        draft.entry_date.isoformat(),
                        draft.note,
                    ),
                )
                entry_id = int(cursor.lastrowid)
        return MoneyEntry(
            id=entry_id,
            title=draft.title,
            amount=draft.amount,
            category=draft.category,
            entry_type=draft.entry_type,
            entry_date=draft.entry_date,
            note=draft.note,
        )

    def list_all(self) -> list[MoneyEntry]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                    """
                    SELECT id, title, amount, category, entry_type, entry_date, note
                    FROM money_entries
                    ORDER BY entry_date DESC, id DESC
                    """
                ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def delete(self, entry_id: int) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM money_entries WHERE id = ?", (entry_id,))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS money_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        entry_type TEXT NOT NULL,
                        entry_date TEXT NOT NULL,
                        note TEXT NOT NULL DEFAULT ''
                    )
                    """
                )

    def _row_to_entry(self, row: sqlite3.Row) -> MoneyEntry:
        return MoneyEntry(
            id=int(row["id"]),
            title=str(row["title"]),
            amount=float(row["amount"]),
            category=str(row["category"]),
            entry_type=str(row["entry_type"]),  # type: ignore[arg-type]
            entry_date=date.fromisoformat(str(row["entry_date"])),
            note=str(row["note"]),
        )
