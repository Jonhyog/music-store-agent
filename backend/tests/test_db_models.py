import sqlite3

import pytest

from music_store.db.models import (
    CategoryRow,
    CustomerRow,
    OrderItemRow,
    OrderRow,
    ProductRow,
    PromotionRow,
)

TABLE_MODELS = [
    ("categories", CategoryRow),
    ("products", ProductRow),
    ("promotions", PromotionRow),
    ("customers", CustomerRow),
    ("orders", OrderRow),
    ("order_items", OrderItemRow),
]


@pytest.mark.parametrize(("table", "model"), TABLE_MODELS)
def test_every_seeded_row_validates(settings, table, model):
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    assert rows
    assert [model.from_row(row) for row in rows]


def test_product_row_parses_specs_json(settings):
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    product = ProductRow.from_row(
        conn.execute("SELECT * FROM products WHERE product_id = 81").fetchone()
    )
    conn.close()
    assert product.specs["strings"] == "nylon"
    assert product.price_brl == 599.9
