import os
import sqlite3
import pandas as pd
from pathlib import Path

# Determine CSV path (same logic as data_processor)
CSV_PATH_LOCAL = os.path.join(os.path.dirname(__file__), "../truestate_assignment_dataset.csv")
CSV_PATH_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../truestate_assignment_dataset.csv"))

def get_csv_path():
    if os.path.exists(CSV_PATH_LOCAL):
        return CSV_PATH_LOCAL
    if os.path.exists(CSV_PATH_REPO):
        return CSV_PATH_REPO
    raise FileNotFoundError("Could not find truestate_assignment_dataset.csv in repo")

CSV_PATH = get_csv_path()
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../truestate.db"))

CHUNK_SIZE = 10000
TABLE_NAME = 'transactions'


def import_csv_to_sqlite(csv_path=CSV_PATH, db_path=DB_PATH, chunk_size=CHUNK_SIZE):
    print(f"Importing CSV {csv_path} into SQLite DB {db_path} (table='{TABLE_NAME}')")

    conn = sqlite3.connect(db_path)
    try:
        first = True
        total = 0
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
            # Do not alter column names here; preserve original CSV column names
            chunk.to_sql(TABLE_NAME, conn, if_exists='append' if not first else 'replace', index=False)
            rows = len(chunk)
            total += rows
            print(f"Imported chunk: {rows} rows (total: {total})")
            first = False
        print(f"Import completed. Total rows imported: {total}")
    finally:
        conn.close()


if __name__ == '__main__':
    import_csv_to_sqlite()
