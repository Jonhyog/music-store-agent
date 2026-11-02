import sqlite3

import pytest

from music_store.assistant.catalog import (
    get_product,
    list_active_promotions,
    list_categories,
    search_products,
)
from music_store.models.catalog import AppliedPromotionModel


@pytest.fixture
def conn(settings):
    c = sqlite3.connect(settings.database_path)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


def test_search_by_free_text_matches_name(conn):
    results = search_products(conn, query="Yamaha C40")
    assert results[0].name == "Yamaha C40 Nylon Natural"


def test_search_ignores_accents_and_case(conn):
    with_accent = search_products(conn, query="Violão")
    without = search_products(conn, query="violao")
    assert with_accent and with_accent == without


def test_search_results_carry_catalog_fields(conn):
    product = search_products(conn, query="Yamaha C40")[0]
    assert product.list_price_brl == 599.9
    assert product.stock_quantity == 12
    assert product.status == "active"
    assert product.category == "Violões"
    assert product.specs["strings"] == "nylon"


def test_search_filters_by_category(conn):
    results = search_products(conn, category="Ukuleles")
    assert results
    assert {p.category for p in results} == {"Ukuleles"}


def test_search_filters_by_max_price(conn):
    results = search_products(conn, max_price_brl=1000)
    assert results
    assert all(p.list_price_brl <= 1000 for p in results)


def test_search_in_stock_only(conn):
    everything = search_products(conn, limit=100)
    in_stock = search_products(conn, in_stock_only=True, limit=100)
    assert any(p.stock_quantity == 0 for p in everything)
    assert in_stock
    assert all(p.stock_quantity > 0 for p in in_stock)


def test_search_respects_limit(conn):
    assert len(search_products(conn, limit=3)) == 3


def test_get_product_by_id_and_by_name(conn):
    by_id = get_product(conn, product_id=81)
    by_name = get_product(conn, name="yamaha c40 nylon natural")
    assert by_id is not None and by_id == by_name


def test_get_product_by_unique_partial_name(conn):
    assert get_product(conn, name="C40").product_id == 81
    assert get_product(conn, name="Yamaha") is None  # ambiguous


def test_get_product_unknown_returns_none(conn):
    assert get_product(conn, product_id=999999) is None
    assert get_product(conn, name="Theremin Imaginário") is None


def test_list_categories(conn):
    categories = list_categories(conn)
    assert [c.name for c in categories][:2] == ["Guitarras", "Baixos"]
    assert len(categories) == 9


def test_product_with_active_promotion_has_promotional_price_and_no_pix(conn):
    product = get_product(conn, product_id=127)
    assert product.promotion == AppliedPromotionModel(
        campaign="Oferta Especial", discount_percent=10
    )
    assert product.promotional_price_brl == round(product.list_price_brl * 0.9, 2)
    assert product.pix_price_brl is None


def test_product_without_promotion_has_pix_price(conn):
    product = get_product(conn, product_id=81)
    assert product.promotion is None
    assert product.promotional_price_brl is None
    assert product.pix_price_brl == 569.91  # 599.90 - 5%


def test_inactive_promotions_are_ignored(conn):
    product = get_product(conn, product_id=102)  # only has an inactive Black Friday
    assert product.promotion is None
    assert product.pix_price_brl == round(product.list_price_brl * 0.95, 2)


def test_highest_active_discount_wins(conn):
    conn.executemany(
        "INSERT INTO promotions VALUES (?, ?, ?, ?, ?)",
        [(100, 81, 10, "Menor", 1), (101, 81, 30, "Maior", 1), (102, 81, 50, "Inativa", 0)],
    )
    product = get_product(conn, product_id=81)
    assert product.promotion == AppliedPromotionModel(campaign="Maior", discount_percent=30)
    assert product.promotional_price_brl == 419.93


def test_list_active_promotions_returns_only_active_with_prices(conn):
    promoted = list_active_promotions(conn)
    assert {p.product_id for p in promoted} == {90, 94, 121, 127}
    assert all(p.promotional_price_brl < p.list_price_brl for p in promoted)
    assert all(p.pix_price_brl is None for p in promoted)


def test_list_active_promotions_filters_by_category(conn):
    everything = list_active_promotions(conn)
    category = everything[0].category
    filtered = list_active_promotions(conn, category=category.upper())
    assert filtered
    assert {p.category for p in filtered} == {category}
    assert len(filtered) <= len(everything)
    assert list_active_promotions(conn, category="Ukuleles") == [
        p for p in everything if p.category == "Ukuleles"
    ]
