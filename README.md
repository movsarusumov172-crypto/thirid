# Money Tracker

Simple personal income and expense tracker built with Python, Streamlit, and SQLite.

## Features

- add income and expense records
- save records locally in SQLite
- filter by month, type, and category
- show income, expenses, and balance
- show expenses grouped by category
- delete records
- service and storage tests with `unittest`

## Tech Stack

- Python 3.12
- Streamlit
- SQLite
- unittest

## Project Structure

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit interface |
| `money_tracker/models.py` | Data classes and constants |
| `money_tracker/service.py` | Validation, filtering, and summary logic |
| `money_tracker/storage.py` | SQLite repository |
| `tests/` | Unit tests |

## Run

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```
