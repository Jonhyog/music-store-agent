"""Build the store SQLite database from the read-only CSVs in ``data/``."""

import csv
import sqlite3
from pathlib import Path

from music_store.db.schema import SCHEMA, TABLES
from music_store.settings import Settings


def seed(database_path: Path, data_dir: Path) -> None:
    """Create ``database_path`` from scratch, replacing any existing file."""
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.unlink(missing_ok=True)

    conn = sqlite3.connect(database_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
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
    finally:
        conn.close()


def main() -> None:
    settings = Settings()
    seed(settings.database_path, settings.data_dir)
    print(f"Seeded {settings.database_path} from {settings.data_dir}")


if __name__ == "__main__":
    main()
