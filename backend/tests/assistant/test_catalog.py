import sqlite3

import pytest

from music_store.assistant.catalog import get_product, list_categories, search_products


@pytest.fixture
def conn(settings):
    c = sqlite3.connect(settings.database_path)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


def test_search_by_free_text_matches_name(conn):
    results = search_products(conn, query="Yamaha C40")
    assert results[0]["name"] == "Yamaha C40 Nylon Natural"


def test_search_ignores_accents_and_case(conn):
    with_accent = search_products(conn, query="Violão")
    without = search_products(conn, query="violao")
    assert with_accent and with_accent == without


def test_search_results_carry_catalog_fields(conn):
    product = search_products(conn, query="Yamaha C40")[0]
    assert product["list_price_brl"] == 599.9
    assert product["stock_quantity"] == 12
    assert product["status"] == "active"
    assert product["category"] == "Violões"
    assert product["specs"]["strings"] == "nylon"


def test_search_filters_by_category(conn):
    results = search_products(conn, category="Ukuleles")
    assert results
    assert {p["category"] for p in results} == {"Ukuleles"}


def test_search_filters_by_max_price(conn):
    results = search_products(conn, max_price_brl=1000)
    assert results
    assert all(p["list_price_brl"] <= 1000 for p in results)


def test_search_in_stock_only(conn):
    everything = search_products(conn, limit=100)
    in_stock = search_products(conn, in_stock_only=True, limit=100)
    assert any(p["stock_quantity"] == 0 for p in everything)
    assert in_stock
    assert all(p["stock_quantity"] > 0 for p in in_stock)


def test_search_respects_limit(conn):
    assert len(search_products(conn, limit=3)) == 3


def test_get_product_by_id_and_by_name(conn):
    by_id = get_product(conn, product_id=81)
    by_name = get_product(conn, name="yamaha c40 nylon natural")
    assert by_id is not None and by_id == by_name


def test_get_product_by_unique_partial_name(conn):
    assert get_product(conn, name="C40")["product_id"] == 81
    assert get_product(conn, name="Yamaha") is None  # ambiguous


def test_get_product_unknown_returns_none(conn):
    assert get_product(conn, product_id=999999) is None
    assert get_product(conn, name="Theremin Imaginário") is None


def test_list_categories(conn):
    categories = list_categories(conn)
    assert [c["name"] for c in categories][:2] == ["Guitarras", "Baixos"]
    assert len(categories) == 9
