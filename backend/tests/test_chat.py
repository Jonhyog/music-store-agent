import json
from uuid import uuid4

from langchain_core.messages import AIMessage

from fakes import FakeRegistry


def _chat(client, conversation_id=None, message="oi", headers=None):
    return client.post(
        "/chat",
        json={"conversation_id": conversation_id or str(uuid4()), "message": message},
        headers=headers or {},
    )


def _events(response) -> list:
    payloads = [
        line.removeprefix("data: ")
        for line in response.text.splitlines()
        if line.startswith("data:")
    ]
    return [p if p == "[DONE]" else json.loads(p) for p in payloads]


def test_streams_ui_message_events_with_identifying_header(client, registry):
    registry.script = [AIMessage(content="Olá!")]
    response = _chat(client)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["x-vercel-ai-ui-message-stream"] == "v1"
    events = _events(response)
    assert [e["type"] for e in events[:-1]] == [
        "start", "text-start", "text-delta", "text-end", "finish",
    ]  # fmt: skip
    assert events[-1] == "[DONE]"
    assert "".join(e["delta"] for e in events[:-1] if e["type"] == "text-delta") == "Olá!"


def test_catalog_search_surfaces_tool_events(client, registry):
    registry.script = [
        AIMessage(
            content="",
            tool_calls=[{"name": "search_products", "args": {"query": "Yamaha C40"}, "id": "c1"}],
        ),
        AIMessage(content="Temos o Yamaha C40."),
    ]
    events = _events(_chat(client, message="Tem Yamaha C40?"))
    types = [e["type"] for e in events[:-1]]
    assert types[:3] == ["start", "tool-input-available", "tool-output-available"]
    call, result = events[1], events[2]
    assert call["toolName"] == "search_products"
    assert call["input"] == {"query": "Yamaha C40"}
    assert result["toolCallId"] == call["toolCallId"]
    assert result["output"][0]["name"] == "Yamaha C40 Nylon Natural"
    assert result["output"][0]["list_price_brl"] == 599.9


def test_conversation_is_bound_to_its_first_identity(client):
    conversation_id = str(uuid4())
    assert _chat(client, conversation_id, headers={"x-customer-id": "1"}).status_code == 200
    mismatch = _chat(client, conversation_id, headers={"x-customer-id": "2"})
    assert mismatch.status_code == 409
    assert _chat(client, conversation_id).status_code == 409  # Visitor is another identity
    assert _chat(client, conversation_id, headers={"x-customer-id": "1"}).status_code == 200


def test_visitor_conversation_rejects_a_customer(client):
    conversation_id = str(uuid4())
    assert _chat(client, conversation_id).status_code == 200
    assert _chat(client, conversation_id, headers={"x-customer-id": "1"}).status_code == 409


def test_concurrent_message_in_the_same_conversation_is_busy(client):
    conversation_id = str(uuid4())
    turn = client.app.state.conversations.begin_turn(conversation_id, None)
    response = _chat(client, conversation_id)
    assert response.status_code == 409
    assert response.json() == {"detail": "conversation busy"}
    turn.release()
    assert _chat(client, conversation_id).status_code == 200


def test_lock_is_released_after_a_failed_turn(client, registry):
    conversation_id = str(uuid4())
    registry.script = [RuntimeError("model down")]
    events = _events(_chat(client, conversation_id))
    assert "error" in [e["type"] for e in events[:-1]]
    registry.script = [AIMessage(content="de volta")]
    assert _chat(client, conversation_id).status_code == 200


def test_delete_returns_204_even_for_unknown_conversation(client):
    assert client.delete(f"/chat/{uuid4()}").status_code == 204


def test_delete_frees_the_identity_binding(client):
    conversation_id = str(uuid4())
    _chat(client, conversation_id, headers={"x-customer-id": "1"})
    assert client.delete(f"/chat/{conversation_id}").status_code == 204
    assert _chat(client, conversation_id, headers={"x-customer-id": "2"}).status_code == 200


def test_invalid_body_is_422(client):
    assert _chat(client, message="").status_code == 422
    assert _chat(client, message="x" * 2001).status_code == 422
    assert _chat(client, conversation_id="not-a-uuid").status_code == 422
    assert client.post("/chat", json={}).status_code == 422


def test_unavailable_model_is_503_and_unknown_is_400(client, registry: FakeRegistry):
    registry.available["qwen3:4b"] = False
    assert _chat(client).status_code == 503
    assert _chat(client, headers={"x-model": "nope"}).status_code == 400


def test_policy_search_surfaces_sections_and_uses_the_requests_provider(client, registry):
    registry.script = [
        AIMessage(
            content="",
            tool_calls=[{"name": "search_policies", "args": {"query": "devolução"}, "id": "c1"}],
        ),
        AIMessage(content="Até 7 dias (seção 4.1)."),
    ]
    events = _events(_chat(client, message="Posso devolver?", headers={"x-model": "gpt-5.6-luna"}))
    result = next(e for e in events if e != "[DONE]" and e["type"] == "tool-output-available")
    assert len(result["output"]) == 4
    assert all(chunk["section"] and chunk["text"] for chunk in result["output"])
    assert list(client.app.state.policy_indexes._stores) == ["openai"]
