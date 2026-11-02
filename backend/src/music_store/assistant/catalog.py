"""Read-only catalog queries used by the Assistant's tools."""

import json
import sqlite3
import unicodedata
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

DEFAULT_SEARCH_LIMIT = 10
PIX_DISCOUNT_PERCENT = 5

PRODUCTS_QUERY = """
    SELECT p.product_id, p.name, c.name AS category, p.price_brl AS list_price_brl,
           p.stock_quantity, p.status, p.description, p.specs
    FROM products p
    LEFT JOIN categories c ON c.category_id = p.category_id
    ORDER BY p.product_id
"""


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _product(row: sqlite3.Row) -> dict[str, Any]:
    product = dict(row)
    product["specs"] = json.loads(product["specs"]) if product["specs"] else None
    return product


def _best_active_promotions(conn: sqlite3.Connection) -> dict[int, dict[str, Any]]:
    """Active Promotion per Product; the highest discount wins when several are active."""
    rows = conn.execute(
        """
        SELECT product_id, description AS campaign, discount_percent
        FROM promotions
        WHERE is_active = 1
        ORDER BY product_id, discount_percent DESC, promotion_id
        """
    )
    best: dict[int, dict[str, Any]] = {}
    for row in rows:
        best.setdefault(
            row["product_id"],
            {"campaign": row["campaign"], "discount_percent": row["discount_percent"]},
        )
    return best


def _discounted(list_price: float, percent: float) -> float:
    price = Decimal(str(list_price)) * (100 - Decimal(str(percent))) / 100
    return float(price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _with_prices(product: dict[str, Any], promotion: dict[str, Any] | None) -> dict[str, Any]:
    """Add the active Promotion and computed prices. PIX never stacks on a Promotion."""
    list_price = product["list_price_brl"]
    product["promotion"] = promotion
    if promotion:
        product["promotional_price_brl"] = _discounted(list_price, promotion["discount_percent"])
        product["pix_price_brl"] = None
    else:
        product["promotional_price_brl"] = None
        product["pix_price_brl"] = _discounted(list_price, PIX_DISCOUNT_PERCENT)
    return product


def _all_products(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    promotions = _best_active_promotions(conn)
    return [
        _with_prices(_product(row), promotions.get(row["product_id"]))
        for row in conn.execute(PRODUCTS_QUERY)
    ]


def search_products(
    conn: sqlite3.Connection,
    *,
    query: str | None = None,
    category: str | None = None,
    max_price_brl: float | None = None,
    in_stock_only: bool = False,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[dict[str, Any]]:
    """Search Products. Free text must match every word, in the name first, else the description."""
    tokens = _normalize(query).split() if query else []
    wanted_category = _normalize(category).strip() if category else None
    scored: list[tuple[int, dict[str, Any]]] = []
    for product in _all_products(conn):
        if max_price_brl is not None and product["list_price_brl"] > max_price_brl:
            continue
        if in_stock_only and product["stock_quantity"] <= 0:
            continue
        if wanted_category and wanted_category not in _normalize(product["category"] or ""):
            continue
        name = _normalize(product["name"])
        haystack = " ".join(
            [name, _normalize(product["category"] or ""), _normalize(product["description"] or "")]
        )
        if not all(token in haystack for token in tokens):
            continue
        scored.append((0 if all(token in name for token in tokens) else 1, product))
    scored.sort(key=lambda pair: pair[0])  # stable: keeps product_id order inside a rank
    return [product for _, product in scored[:limit]]


def get_product(
    conn: sqlite3.Connection, *, product_id: int | None = None, name: str | None = None
) -> dict[str, Any] | None:
    """Return one Product by id, or by name: exact first, else the only partial match."""
    products = _all_products(conn)
    if product_id is not None:
        return next((p for p in products if p["product_id"] == product_id), None)
    if name is None:
        return None
    wanted = _normalize(name).strip()
    exact = [p for p in products if _normalize(p["name"]) == wanted]
    if exact:
        return exact[0]
    partial = [p for p in products if wanted and wanted in _normalize(p["name"])]
    return partial[0] if len(partial) == 1 else None


def list_categories(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT category_id, name, description FROM categories ORDER BY category_id"
    )
    return [dict(row) for row in rows]
