import sqlite3
from datetime import UTC, datetime
from uuid import uuid4

from langchain_core.messages import AIMessage

from test_chat import _chat, _events


def _register(args: dict) -> list:
    return [
        AIMessage(
            content="",
            tool_calls=[{"name": "register_complaint", "args": args, "id": "c1"}],
        ),
        AIMessage(content="Protocolo registrado."),
    ]


def _tool_output(response):
    return next(
        e for e in _events(response) if e != "[DONE]" and e["type"] == "tool-output-available"
    )["output"]


def _complaints(settings) -> list[sqlite3.Row]:
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM complaints").fetchall()
    finally:
        conn.close()


def test_customer_files_a_complaint_about_their_order(client, registry, settings):
    registry.script = _register(
        {"category": "delivery", "description": "Pedido atrasado", "order_id": 1}
    )
    conversation_id = str(uuid4())
    before = datetime.now(UTC)

    response = _chat(client, conversation_id, "Meu pedido atrasou", headers={"x-customer-id": "3"})

    output = _tool_output(response)
    assert output["complaint_id"] == 1
    (row,) = _complaints(settings)
    assert dict(row) | {"created_at": None} == {
        "complaint_id": 1,
        "customer_id": 3,
        "order_id": 1,
        "category": "delivery",
        "description": "Pedido atrasado",
        "conversation_id": conversation_id,
        "created_at": None,
    }
    created = datetime.fromisoformat(row["created_at"])
    assert before <= created <= datetime.now(UTC)
    assert datetime.fromisoformat(output["created_at"]) == created


def test_complaint_does_not_need_an_order(client, registry, settings):
    registry.script = _register({"category": "service", "description": "Atendimento ruim"})

    _chat(client, headers={"x-customer-id": "3"})

    assert [r["order_id"] for r in _complaints(settings)] == [None]


def test_complaint_about_another_customers_order_is_refused(client, registry, settings):
    registry.script = _register(
        {"category": "delivery", "description": "Atraso", "order_id": 2}  # belongs to customer 7
    )

    output = _tool_output(_chat(client, headers={"x-customer-id": "3"}))

    assert "error" in output
    assert _complaints(settings) == []


def test_visitor_cannot_file_a_complaint(client, registry, settings):
    registry.script = _register({"category": "service", "description": "Atendimento ruim"})

    output = _tool_output(_chat(client))

    assert "error" in output
    assert _complaints(settings) == []
