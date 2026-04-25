import tempfile
import unittest
from datetime import date
from pathlib import Path

from money_tracker.models import MoneyEntryDraft
from money_tracker.storage import MoneyRepository


class MoneyRepositoryTest(unittest.TestCase):
    def test_add_and_list_entries_from_sqlite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = MoneyRepository(Path(temp_dir) / "money.db")

            repo.add(MoneyEntryDraft("Salary", 50000, "Work", "income", date(2026, 4, 1)))
            repo.add(MoneyEntryDraft("Lunch", 650, "Food", "expense", date(2026, 4, 2)))

            entries = repo.list_all()

            self.assertEqual([entry.title for entry in entries], ["Lunch", "Salary"])
            self.assertEqual(entries[0].amount, 650)

    def test_delete_removes_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = MoneyRepository(Path(temp_dir) / "money.db")
            entry = repo.add(MoneyEntryDraft("Taxi", 300, "Transport", "expense", date(2026, 4, 2)))

            repo.delete(entry.id)

            self.assertEqual(repo.list_all(), [])


if __name__ == "__main__":
    unittest.main()
