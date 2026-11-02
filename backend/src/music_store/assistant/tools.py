"""Tools the model can call. The Customer is read from the runtime context, never an argument."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langchain.tools import ToolRuntime, tool

from music_store.assistant import catalog
from music_store.assistant.context import AgentContext


@contextmanager
def _connection(runtime: ToolRuntime[AgentContext]) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(runtime.context.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


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

    Returns Products with List Price, stock quantity, Catalog Status and specs.
    """
    with _connection(runtime) as conn:
        return catalog.search_products(
            conn,
            query=query,
            category=category,
            max_price_brl=max_price_brl,
            in_stock_only=in_stock_only,
        )


@tool
def get_product(
    runtime: ToolRuntime[AgentContext], name: str | None = None, product_id: int | None = None
) -> dict[str, Any]:
    """Get one Product by its exact name or its id, with List Price, stock, status and specs."""
    with _connection(runtime) as conn:
        product = catalog.get_product(conn, product_id=product_id, name=name)
    return product or {"error": "Product not found."}


@tool
def list_categories(runtime: ToolRuntime[AgentContext]) -> list[dict[str, Any]]:
    """List the store's Categories (families of instruments)."""
    with _connection(runtime) as conn:
        return catalog.list_categories(conn)


CATALOG_TOOLS = [search_products, get_product, list_categories]
