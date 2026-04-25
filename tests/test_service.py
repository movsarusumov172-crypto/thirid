import unittest
from datetime import date

from money_tracker.models import MoneyEntry, MoneyEntryDraft
from money_tracker.service import create_entry, get_summary, list_entries


class MemoryRepository:
    def __init__(self):
        self.entries = []
        self.next_id = 1

    def add(self, draft):
        entry = MoneyEntry(
            id=self.next_id,
            title=draft.title,
            amount=draft.amount,
            category=draft.category,
            entry_type=draft.entry_type,
            entry_date=draft.entry_date,
            note=draft.note,
        )
        self.next_id += 1
        self.entries.append(entry)
        return entry

    def list_all(self):
        return list(self.entries)


class MoneyServiceTest(unittest.TestCase):
    def test_create_entry_rejects_empty_title(self):
        repo = MemoryRepository()
        draft = MoneyEntryDraft(
            title="  ",
            amount=100,
            category="Food",
            entry_type="expense",
            entry_date=date(2026, 4, 10),
        )

        with self.assertRaises(ValueError):
            create_entry(repo, draft)

    def test_create_entry_rejects_not_positive_amount(self):
        repo = MemoryRepository()
        draft = MoneyEntryDraft(
            title="Coffee",
            amount=0,
            category="Food",
            entry_type="expense",
            entry_date=date(2026, 4, 10),
        )

        with self.assertRaises(ValueError):
            create_entry(repo, draft)

    def test_list_entries_can_filter_by_month_type_and_category(self):
        repo = MemoryRepository()
        create_entry(repo, MoneyEntryDraft("Salary", 50000, "Work", "income", date(2026, 4, 1)))
        create_entry(repo, MoneyEntryDraft("Groceries", 1800, "Food", "expense", date(2026, 4, 2)))
        create_entry(repo, MoneyEntryDraft("Bus", 120, "Transport", "expense", date(2026, 4, 3)))
        create_entry(repo, MoneyEntryDraft("Books", 900, "Study", "expense", date(2026, 3, 20)))

        result = list_entries(repo, month="2026-04", entry_type="expense", category="Food")

        self.assertEqual([entry.title for entry in result], ["Groceries"])

    def test_summary_counts_income_expenses_balance_and_categories(self):
        repo = MemoryRepository()
        create_entry(repo, MoneyEntryDraft("Salary", 50000, "Work", "income", date(2026, 4, 1)))
        create_entry(repo, MoneyEntryDraft("Groceries", 1800, "Food", "expense", date(2026, 4, 2)))
        create_entry(repo, MoneyEntryDraft("Cafe", 450, "Food", "expense", date(2026, 4, 5)))
        create_entry(repo, MoneyEntryDraft("Bus", 120, "Transport", "expense", date(2026, 4, 3)))

        summary = get_summary(repo, month="2026-04")

        self.assertEqual(summary.total_income, 50000)
        self.assertEqual(summary.total_expense, 2370)
        self.assertEqual(summary.balance, 47630)
        self.assertEqual(summary.expenses_by_category, {"Food": 2250, "Transport": 120})


if __name__ == "__main__":
    unittest.main()
