"""Read-only catalog queries used by the Assistant's tools."""

import sqlite3
import unicodedata
from decimal import ROUND_HALF_UP, Decimal

from music_store.db.models import CategoryRow, ProductRow, PromotionRow
from music_store.models.catalog import AppliedPromotionModel, ProductModel

DEFAULT_SEARCH_LIMIT = 10
PIX_DISCOUNT_PERCENT = 5

PRODUCTS_QUERY = "SELECT * FROM products ORDER BY product_id"

ACTIVE_PROMOTIONS_QUERY = """
    SELECT * FROM promotions
    WHERE is_active = 1
    ORDER BY product_id, discount_percent DESC, promotion_id
"""

CATEGORIES_QUERY = "SELECT * FROM categories ORDER BY category_id"


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _best_active_promotions(conn: sqlite3.Connection) -> dict[int, AppliedPromotionModel]:
    """Active Promotion per Product; the highest discount wins when several are active."""
    best: dict[int, AppliedPromotionModel] = {}
    for row in conn.execute(ACTIVE_PROMOTIONS_QUERY):
        promotion = PromotionRow.from_row(row)
        if promotion.product_id is not None:
            best.setdefault(
                promotion.product_id,
                AppliedPromotionModel(
                    campaign=promotion.description, discount_percent=promotion.discount_percent
                ),
            )
    return best


def _discounted(list_price: float, percent: float) -> float:
    price = Decimal(str(list_price)) * (100 - Decimal(str(percent))) / 100
    return float(price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _priced(
    row: ProductRow, category: str | None, promotion: AppliedPromotionModel | None
) -> ProductModel:
    """Build the Product with computed prices. PIX never stacks on a Promotion."""
    return ProductModel(
        product_id=row.product_id,
        name=row.name,
        category=category,
        list_price_brl=row.price_brl,
        stock_quantity=row.stock_quantity,
        status=row.status,
        description=row.description,
        specs=row.specs,
        promotion=promotion,
        promotional_price_brl=(
            _discounted(row.price_brl, promotion.discount_percent) if promotion else None
        ),
        pix_price_brl=None if promotion else _discounted(row.price_brl, PIX_DISCOUNT_PERCENT),
    )


def list_categories(conn: sqlite3.Connection) -> list[CategoryRow]:
    return [CategoryRow.from_row(row) for row in conn.execute(CATEGORIES_QUERY)]


def _all_products(conn: sqlite3.Connection) -> list[ProductModel]:
    promotions = _best_active_promotions(conn)
    names = {c.category_id: c.name for c in list_categories(conn)}
    products = (ProductRow.from_row(row) for row in conn.execute(PRODUCTS_QUERY))
    return [_priced(p, names.get(p.category_id), promotions.get(p.product_id)) for p in products]


def search_products(
    conn: sqlite3.Connection,
    *,
    query: str | None = None,
    category: str | None = None,
    max_price_brl: float | None = None,
    in_stock_only: bool = False,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[ProductModel]:
    """Search Products. Free text must match every word, in the name first, else the description."""
    tokens = _normalize(query).split() if query else []
    wanted_category = _normalize(category).strip() if category else None
    scored: list[tuple[int, ProductModel]] = []
    for product in _all_products(conn):
        if max_price_brl is not None and product.list_price_brl > max_price_brl:
            continue
        if in_stock_only and product.stock_quantity <= 0:
            continue
        if wanted_category and wanted_category not in _normalize(product.category or ""):
            continue
        name = _normalize(product.name)
        haystack = " ".join(
            [name, _normalize(product.category or ""), _normalize(product.description or "")]
        )
        if not all(token in haystack for token in tokens):
            continue
        scored.append((0 if all(token in name for token in tokens) else 1, product))
    scored.sort(key=lambda pair: pair[0])  # stable: keeps product_id order inside a rank
    return [product for _, product in scored[:limit]]


def get_product(
    conn: sqlite3.Connection, *, product_id: int | None = None, name: str | None = None
) -> ProductModel | None:
    """Return one Product by id, or by name: exact first, else the only partial match."""
    products = _all_products(conn)
    if product_id is not None:
        return next((p for p in products if p.product_id == product_id), None)
    if name is None:
        return None
    wanted = _normalize(name).strip()
    exact = [p for p in products if _normalize(p.name) == wanted]
    if exact:
        return exact[0]
    partial = [p for p in products if wanted and wanted in _normalize(p.name)]
    return partial[0] if len(partial) == 1 else None


def list_active_promotions(
    conn: sqlite3.Connection, *, category: str | None = None
) -> list[ProductModel]:
    """Products with an active Promotion, optionally within a Category, with computed prices."""
    wanted_category = _normalize(category).strip() if category else None
    return [
        product
        for product in _all_products(conn)
        if product.promotion
        and (not wanted_category or wanted_category in _normalize(product.category or ""))
    ]
