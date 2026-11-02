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


@pytest.mark.parametrize(
    "customer",
    [None, CustomerModel(customer_id=1, name="Ana Souza", phone=None, email=None, city=None)],
)
def test_agent_runs_for_visitor_and_customer(settings, customer):
    messages = _run(settings, [AIMessage(content="Olá!")], customer=customer)
    assert messages[-1].content == "Olá!"
