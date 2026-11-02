import sqlite3

import pytest

from music_store.assistant.orders import get_order, list_orders


@pytest.fixture
def conn(settings):
    c = sqlite3.connect(settings.database_path)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


def test_list_orders_returns_only_the_customers_orders_newest_first(conn):
    orders = list_orders(conn, customer_id=3)
    assert [o.order_id for o in orders] == [19, 1]


def test_list_orders_filters_by_status(conn):
    orders = list_orders(conn, customer_id=3, status="cancelled")
    assert [o.order_id for o in orders] == [19]


def test_list_orders_for_customer_without_orders_is_empty(conn):
    assert list_orders(conn, customer_id=50) == []


def test_order_carries_facts_and_items_with_product_names(conn):
    order = get_order(conn, customer_id=3, order_id=1)
    assert order is not None
    assert order.status == "delivered"
    assert order.total_brl == 11499
    assert order.payment_method == "pix"
    assert order.tracking_code == "BRAB1234567BR"
    assert str(order.estimated_delivery) == "2025-10-25"
    assert len(order.items) == 1
    assert order.items[0].quantity == 1
    assert order.items[0].product_name


def test_cancelled_order_carries_notes(conn):
    order = get_order(conn, customer_id=3, order_id=19)
    assert order is not None and order.notes


def test_other_customers_order_is_the_same_as_a_missing_order(conn):
    assert get_order(conn, customer_id=3, order_id=2) is None  # belongs to customer 7
    assert get_order(conn, customer_id=3, order_id=999999) is None
