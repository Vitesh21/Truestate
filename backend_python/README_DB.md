# Database import (SQLite)

This project contains a convenience script to import the full `truestate_assignment_dataset.csv` into a local SQLite database (`truestate.db`) without trimming the dataset.

Why SQLite?
- Works locally with no external account or free-tier limits.
- Keeps the full dataset intact.

Files:
- `src/import_csv_to_sqlite.py` — Script to import the CSV into `truestate.db` as table `transactions` in chunks.
- `src/data_processor.py` — Modified to attempt loading from `truestate.db` (table `transactions`) first, then parquet cache, then fallback to CSV.

How to run:

1. From the workspace root (Windows PowerShell):

```powershell
cd c:\Users\91998\Downloads\lyz
python backend_python\src\import_csv_to_sqlite.py
```

2. Start the backend API (after import completes):

```powershell
cd c:\Users\91998\Downloads\lyz\backend_python
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Notes:
- The importer processes the CSV in chunks of 10k rows to avoid high memory usage and preserves the entire dataset.
- `data_processor.py` will convert and cache a parquet file (`cached_data.parquet`) for faster startup on subsequent runs.
