import json
from datetime import date

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from fakes import FakeChatModel
from music_store.assistant.agent import build_agent
from music_store.assistant.context import AgentContext
from music_store.models.customer import CustomerModel


def _run(settings, script, customer=None):
    agent = build_agent(FakeChatModel(script=script), InMemorySaver())
    context = AgentContext(
        customer=customer, reference_date=date(2026, 3, 25), database_path=settings.database_path
    )
    return agent.invoke(
        {"messages": [("user", "oi")]},
        config={"configurable": {"thread_id": "t"}},
        context=context,
    )["messages"]


def _call(name, args):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": "c1"}])


def test_search_tool_returns_catalog_results(settings):
    messages = _run(
        settings,
        [_call("search_products", {"query": "Yamaha C40"}), AIMessage(content="Achei!")],
    )
    result = next(m for m in messages if isinstance(m, ToolMessage))
    products = json.loads(result.content)
    assert products[0]["name"] == "Yamaha C40 Nylon Natural"
    assert messages[-1].content == "Achei!"


def test_get_product_and_list_categories_tools(settings):
    messages = _run(
        settings,
        [
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "get_product", "args": {"product_id": 81}, "id": "a"},
                    {"name": "list_categories", "args": {}, "id": "b"},
                ],
            ),
            AIMessage(content="ok"),
        ],
    )
    by_id = {m.tool_call_id: json.loads(m.content) for m in messages if isinstance(m, ToolMessage)}
    assert by_id["a"]["name"] == "Yamaha C40 Nylon Natural"
    assert len(by_id["b"]) == 9


def _tool_output(settings, name, args):
    messages = _run(settings, [_call(name, args), AIMessage(content="ok")])
    return json.loads(next(m for m in messages if isinstance(m, ToolMessage)).content)


def test_get_product_tool_with_active_promotion(settings):
    product = _tool_output(settings, "get_product", {"product_id": 127})
    assert product["promotion"]["discount_percent"] == 10
    assert product["promotional_price_brl"] == round(product["list_price_brl"] * 0.9, 2)
    assert product["pix_price_brl"] is None


def test_get_product_tool_without_promotion_has_pix_price(settings):
    product = _tool_output(settings, "get_product", {"product_id": 81})
    assert product["promotion"] is None
    assert product["pix_price_brl"] == 569.91


def test_get_product_tool_with_only_inactive_promotions(settings):
    product = _tool_output(settings, "get_product", {"product_id": 102})
    assert product["promotion"] is None
    assert product["promotional_price_brl"] is None
    assert product["pix_price_brl"] is not None


def test_list_active_promotions_tool_with_and_without_category(settings):
    everything = _tool_output(settings, "list_active_promotions", {})
    assert {p["product_id"] for p in everything} == {90, 94, 121, 127}
    category = everything[0]["category"]
    filtered = _tool_output(settings, "list_active_promotions", {"category": category})
    assert filtered and {p["category"] for p in filtered} == {category}
    assert len(filtered) <= len(everything)


@pytest.mark.parametrize(
    "customer",
    [None, CustomerModel(customer_id=1, name="Ana Souza", phone=None, email=None, city=None)],
)
def test_agent_runs_for_visitor_and_customer(settings, customer):
    messages = _run(settings, [AIMessage(content="Olá!")], customer=customer)
    assert messages[-1].content == "Olá!"


def _customer(customer_id):
    return CustomerModel(
        customer_id=customer_id, name="Ana Souza", phone=None, email=None, city=None
    )


def _order_tool(settings, name, args, customer_id=3):
    customer = _customer(customer_id) if customer_id else None
    messages = _run(settings, [_call(name, args), AIMessage(content="ok")], customer=customer)
    return json.loads(next(m for m in messages if isinstance(m, ToolMessage)).content)


def test_list_my_orders_tool_returns_only_my_orders(settings):
    orders = _order_tool(settings, "list_my_orders", {})
    assert [o["order_id"] for o in orders] == [19, 1]
    assert orders[1]["tracking_code"] == "BRAB1234567BR"
    assert orders[1]["items"][0]["product_name"]


def test_list_my_orders_tool_filters_by_status(settings):
    orders = _order_tool(settings, "list_my_orders", {"status": "cancelled"})
    assert [o["order_id"] for o in orders] == [19]
    assert orders[0]["notes"]


def test_get_my_order_tool_returns_my_order(settings):
    order = _order_tool(settings, "get_my_order", {"order_id": 1})
    assert order["order_id"] == 1
    assert order["status"] == "delivered"
    assert order["estimated_delivery"] == "2025-10-25"


def test_get_my_order_tool_hides_other_customers_orders_exactly_like_missing_ones(settings):
    someone_elses = _order_tool(settings, "get_my_order", {"order_id": 2})
    missing = _order_tool(settings, "get_my_order", {"order_id": 999999})
    assert someone_elses == missing
    assert "error" in missing


@pytest.mark.parametrize(
    ("name", "args"), [("list_my_orders", {}), ("get_my_order", {"order_id": 1})]
)
def test_order_tools_refuse_visitors_uniformly(settings, name, args):
    first = _order_tool(settings, name, args, customer_id=None)
    second = _order_tool(settings, "get_my_order", {"order_id": 999999}, customer_id=None)
    assert first == second
    assert "not identified" in first["error"]
