"""Tools the model can call. The Customer is read from the runtime context, never an argument."""

import logging
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel

from music_store.assistant import catalog, orders
from music_store.assistant.context import AgentContext

logger = logging.getLogger(__name__)


@contextmanager
def _connection(runtime: ToolRuntime[AgentContext]) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(runtime.context.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _dump(models: Sequence[BaseModel]) -> list[dict[str, Any]]:
    return [model.model_dump(mode="json") for model in models]


@tool
def search_products(
    runtime: ToolRuntime[AgentContext],
    query: str | None = None,
    category: str | None = None,
    max_price_brl: float | None = None,
    in_stock_only: bool = False,
) -> list[dict[str, Any]]:
    """Search the store's Products (musical instruments).

    Args:
        query: Free text, every word must match the name, category or description.
        category: Category name, e.g. "Violões" or "Guitarras".
        max_price_brl: Maximum List Price in BRL.
        in_stock_only: Only Products with stock available.

    Returns Products with List Price, active Promotion, Promotional Price, PIX price (only when
    there is no Promotion), stock quantity, Catalog Status and specs.
    """
    with _connection(runtime) as conn:
        products = catalog.search_products(
            conn,
            query=query,
            category=category,
            max_price_brl=max_price_brl,
            in_stock_only=in_stock_only,
        )
    return _dump(products)


@tool
def get_product(
    runtime: ToolRuntime[AgentContext], name: str | None = None, product_id: int | None = None
) -> dict[str, Any]:
    """Get one Product by name or id: prices (list, promotional, PIX), stock, status and specs."""
    with _connection(runtime) as conn:
        product = catalog.get_product(conn, product_id=product_id, name=name)
    return product.model_dump(mode="json") if product else {"error": "Product not found."}


@tool
def list_categories(runtime: ToolRuntime[AgentContext]) -> list[dict[str, Any]]:
    """List the store's Categories (families of instruments)."""
    with _connection(runtime) as conn:
        categories = catalog.list_categories(conn)
    return _dump(categories)


@tool
def list_active_promotions(
    runtime: ToolRuntime[AgentContext], category: str | None = None
) -> list[dict[str, Any]]:
    """List Products that have an active Promotion, with campaign, discount and prices.

    Args:
        category: Optional Category name to restrict the listing, e.g. "Violões".
    """
    with _connection(runtime) as conn:
        products = catalog.list_active_promotions(conn, category=category)
    return _dump(products)


NOT_IDENTIFIED = {"error": "Customer not identified: ask the person to identify themselves."}
ORDER_NOT_FOUND = {"error": "Order not found."}


@tool
def list_my_orders(
    runtime: ToolRuntime[AgentContext], status: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """List the identified Customer's own Orders, newest first.

    Args:
        status: Optional Order Status: pending, confirmed, shipped, delivered or cancelled.

    Returns each Order with status, total, payment method, tracking code, estimated delivery,
    notes and its items (Product name and quantity).
    """
    customer = runtime.context.customer
    if customer is None:
        return NOT_IDENTIFIED
    with _connection(runtime) as conn:
        found = orders.list_orders(conn, customer_id=customer.customer_id, status=status)
    return _dump(found)


@tool
def get_my_order(runtime: ToolRuntime[AgentContext], order_id: int) -> dict[str, Any]:
    """Get one of the identified Customer's own Orders by its id, with items and tracking."""
    customer = runtime.context.customer
    if customer is None:
        return NOT_IDENTIFIED
    with _connection(runtime) as conn:
        order = orders.get_order(conn, customer_id=customer.customer_id, order_id=order_id)
    return order.model_dump(mode="json") if order else ORDER_NOT_FOUND


POLICY_UNAVAILABLE = {"error": "Policy search is not available."}


@tool
def search_policies(runtime: ToolRuntime[AgentContext], query: str) -> list[dict[str, Any]]:
    """Search the store's Policy Manual: hours, address and contacts, payment and installments,
    exchanges and returns, shipping, promotion rules, warranty and privacy.

    Args:
        query: The question or topic, in natural language.

    Returns the most relevant passages, each with its section number, section title and text.
    Section numbers are for your reference only; do not show them to the customer.
    """
    search = runtime.context.policy_search
    if search is None:
        return [POLICY_UNAVAILABLE]
    try:
        chunks = search(query)
    except Exception:
        # Typically the provider's embedding model is missing or unreachable (e.g. Ollama
        # without `bge-m3` pulled). Tell the model instead of failing the whole stream.
        logger.exception("Policy search failed")
        return [POLICY_UNAVAILABLE]
    return [
        {"section": c.section, "title": c.heading, "parent_title": c.parent_title, "text": c.text}
        for c in chunks
    ]


CATALOG_TOOLS = [search_products, get_product, list_categories, list_active_promotions]
ORDER_TOOLS = [list_my_orders, get_my_order]
POLICY_TOOLS = [search_policies]
