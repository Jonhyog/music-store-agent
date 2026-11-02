"""The Assistant: a LangChain agent with the catalog tools and a versioned system prompt."""

import sqlite3
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path
from string import Template
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain.tools import ToolRuntime, tool
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver

from music_store import catalog
from music_store.models.customer import CustomerModel

PROMPT_VERSION = "v1"
PROMPT_PATH = Path(__file__).parent / "prompts" / f"system_{PROMPT_VERSION}.md"


@dataclass(frozen=True)
class AgentContext:
    """Per-request context handed to tools and the prompt, never shown to the model as arguments."""

    customer: CustomerModel | None
    reference_date: date
    database_path: Path


@cache
def _prompt_template() -> Template:
    return Template(PROMPT_PATH.read_text(encoding="utf-8"))


def render_system_prompt(context: AgentContext) -> str:
    if context.customer is None:
        audience = "a Visitor (not identified as a customer)"
    else:
        audience = f"the customer {context.customer.name.split()[0]}"
    return _prompt_template().substitute(
        reference_date=context.reference_date.isoformat(), audience=audience
    )


def _connect(runtime: ToolRuntime[AgentContext]) -> sqlite3.Connection:
    conn = sqlite3.connect(runtime.context.database_path)
    conn.row_factory = sqlite3.Row
    return conn


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
    conn = _connect(runtime)
    try:
        return catalog.search_products(
            conn,
            query=query,
            category=category,
            max_price=max_price_brl,
            in_stock_only=in_stock_only,
        )
    finally:
        conn.close()


@tool
def get_product(
    runtime: ToolRuntime[AgentContext], name: str | None = None, product_id: int | None = None
) -> dict[str, Any]:
    """Get one Product by its exact name or its id, with List Price, stock, status and specs."""
    conn = _connect(runtime)
    try:
        product = catalog.get_product(conn, product_id=product_id, name=name)
    finally:
        conn.close()
    return product or {"error": "Product not found."}


@tool
def list_categories(runtime: ToolRuntime[AgentContext]) -> list[dict[str, Any]]:
    """List the store's Categories (families of instruments)."""
    conn = _connect(runtime)
    try:
        return catalog.list_categories(conn)
    finally:
        conn.close()


TOOLS = [search_products, get_product, list_categories]


@dynamic_prompt
def _system_prompt(request: ModelRequest) -> str:
    return render_system_prompt(request.runtime.context)


def build_agent(model: BaseChatModel, checkpointer: BaseCheckpointSaver):
    return create_agent(
        model,
        tools=TOOLS,
        middleware=[_system_prompt],
        context_schema=AgentContext,
        checkpointer=checkpointer,
    )
