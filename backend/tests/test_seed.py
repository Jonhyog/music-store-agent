import json
import sqlite3

from music_store.settings import REPO_ROOT


def test_seed_loads_all_tables_and_specs_are_json(settings):
    conn = sqlite3.connect(settings.database_path)
    for table, rows in {"categories": 9, "customers": 50, "products": 65}.items():
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == rows
    for (specs,) in conn.execute("SELECT specs FROM products WHERE specs IS NOT NULL"):
        assert isinstance(json.loads(specs), dict)
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_seed_leaves_sources_untouched(settings):
    before = {p: p.read_bytes() for p in (REPO_ROOT / "data").glob("*.csv")}
    from music_store.seed import seed

    seed(settings.database_path, REPO_ROOT / "data")
    assert before == {p: p.read_bytes() for p in (REPO_ROOT / "data").glob("*.csv")}
