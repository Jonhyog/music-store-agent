"""Build the store SQLite database from the read-only CSVs in ``data/``."""

import argparse
import csv
import sqlite3
from pathlib import Path

from music_store.db.schema import COMPLAINTS_SCHEMA, SCHEMA, TABLES
from music_store.settings import Settings


def seed(database_path: Path, data_dir: Path, *, reset: bool = False) -> None:
    """Rebuild the catalog, customer and order tables from the CSVs, keeping Complaints.

    ``reset`` deletes the database file first, so Complaints are wiped too.
    """
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if reset:
        database_path.unlink(missing_ok=True)

    conn = sqlite3.connect(database_path)
    try:
        # Off while the store tables are dropped, since kept Complaints reference them.
        conn.execute("PRAGMA foreign_keys = OFF")
        for table in reversed(TABLES):
            conn.execute(f"DROP TABLE IF EXISTS {table}")
        conn.executescript(SCHEMA)
        conn.executescript(COMPLAINTS_SCHEMA)
        for table, columns in TABLES.items():
            with open(Path(data_dir) / f"{table}.csv", newline="", encoding="utf-8") as f:
                rows = [
                    [row[c] if row[c] != "" else None for c in columns] for row in csv.DictReader(f)
                ]
            placeholders = ", ".join("?" for _ in columns)
            conn.executemany(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
            )
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the store database from the CSVs.")
    parser.add_argument("--reset", action="store_true", help="also wipe Complaints")
    args = parser.parse_args()
    settings = Settings()
    seed(settings.database_path, settings.data_dir, reset=args.reset)
    print(f"Seeded {settings.database_path} from {settings.data_dir}")


if __name__ == "__main__":
    main()
