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


def _file_complaint(database_path):
    conn = sqlite3.connect(database_path)
    conn.execute(
        "INSERT INTO complaints (customer_id, order_id, category, description, conversation_id, "
        "created_at) VALUES (3, 1, 'delivery', 'Atrasou', 'c-1', '2026-03-25T10:00:00+00:00')"
    )
    conn.commit()
    conn.close()


def test_reseeding_keeps_complaints_and_rebuilds_the_rest(settings):
    from music_store.seed import seed

    _file_complaint(settings.database_path)
    conn = sqlite3.connect(settings.database_path)
    conn.execute("DELETE FROM products WHERE product_id = 1")
    conn.commit()
    conn.close()

    seed(settings.database_path, REPO_ROOT / "data")

    conn = sqlite3.connect(settings.database_path)
    assert conn.execute("SELECT description FROM complaints").fetchall() == [("Atrasou",)]
    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 65
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_reset_wipes_complaints(settings):
    from music_store.seed import seed

    _file_complaint(settings.database_path)
    seed(settings.database_path, REPO_ROOT / "data", reset=True)

    conn = sqlite3.connect(settings.database_path)
    assert conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0] == 0
