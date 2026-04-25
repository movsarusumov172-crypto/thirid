from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from money_tracker.models import ENTRY_TYPES, MoneyEntryDraft
from money_tracker.service import create_entry, delete_entry, get_summary, list_entries
from money_tracker.storage import MoneyRepository


APP_TITLE = "Money Tracker"
APP_DESCRIPTION = "Small personal budget tracker with local SQLite storage."


@st.cache_resource
def get_repository() -> MoneyRepository:
    db_path = Path(__file__).resolve().parent / "data" / "money.db"
    return MoneyRepository(db_path)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_DESCRIPTION)

    repo = get_repository()

    st.sidebar.header("New record")
    render_add_form(repo)

    st.sidebar.header("Filters")
    month = st.sidebar.text_input("Month", value=date.today().strftime("%Y-%m"))
    type_filter = st.sidebar.selectbox("Type", ["all", *ENTRY_TYPES])
    category_filter = st.sidebar.text_input("Category")

    selected_type = None if type_filter == "all" else type_filter
    selected_category = category_filter.strip() or None

    summary = get_summary(repo, month=month.strip() or None)
    render_summary(summary)

    st.subheader("Records")
    entries = list_entries(
        repo,
        month=month.strip() or None,
        entry_type=selected_type,
        category=selected_category,
    )

    if not entries:
        st.info("No records for the selected filters.")
        return

    for entry in entries:
        with st.container(border=True):
            columns = st.columns([2, 1, 1, 1, 1])
            columns[0].markdown(f"**{entry.title}**")
            columns[0].caption(entry.note or "No note")
            columns[1].write(entry.entry_date.isoformat())
            columns[2].write(entry.category)
            columns[3].write(entry.entry_type)
            columns[4].write(f"{entry.amount:.2f}")
            if st.button("Delete", key=f"delete-{entry.id}"):
                delete_entry(repo, entry.id)
                st.rerun()


def render_add_form(repo: MoneyRepository) -> None:
    with st.sidebar.form("add_money_record", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Groceries")
        amount = st.number_input("Amount", min_value=0.0, step=50.0)
        category = st.text_input("Category", placeholder="Food")
        entry_type = st.selectbox("Type", ENTRY_TYPES)
        entry_date = st.date_input("Date", value=date.today())
        note = st.text_area("Note")
        submitted = st.form_submit_button("Add")

    if submitted:
        try:
            create_entry(
                repo,
                MoneyEntryDraft(
                    title=title,
                    amount=amount,
                    category=category,
                    entry_type=entry_type,
                    entry_date=entry_date,
                    note=note,
                ),
            )
        except ValueError as exc:
            st.sidebar.error(str(exc))
        else:
            st.sidebar.success("Record added")
            st.rerun()


def render_summary(summary) -> None:
    columns = st.columns(3)
    columns[0].metric("Income", f"{summary.total_income:.2f}")
    columns[1].metric("Expenses", f"{summary.total_expense:.2f}")
    columns[2].metric("Balance", f"{summary.balance:.2f}")

    if summary.expenses_by_category:
        st.subheader("Expenses by category")
        st.bar_chart(summary.expenses_by_category)


if __name__ == "__main__":
    main()
