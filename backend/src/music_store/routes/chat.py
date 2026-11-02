from collections.abc import AsyncIterator
from contextlib import aclosing
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from music_store.assistant.agent import build_agent
from music_store.assistant.context import AgentContext
from music_store.assistant.conversations import Turn, TurnRollback
from music_store.assistant.stream import STREAM_HEADERS, ui_message_stream
from music_store.assistant.tracing import build_tracing_callbacks
from music_store.middleware.customer import CurrentCustomer
from music_store.middleware.model import CurrentModel

router = APIRouter()


class ChatRequestModel(BaseModel):
    conversation_id: UUID
    message: Annotated[str, Field(min_length=1, max_length=2000)]


async def _run_turn(
    turn: Turn, request: Request, body: ChatRequestModel, customer, model
) -> AsyncIterator[str]:
    try:
        app = request.app
        agent = build_agent(
            app.state.registry.chat_model(model.id), app.state.conversations.checkpointer
        )
        rollback = TurnRollback(agent, str(body.conversation_id))
        context = AgentContext(
            customer=customer,
            reference_date=app.state.settings.reference_date,
            database_path=app.state.settings.database_path,
            policy_search=app.state.policy_indexes.searcher(model.id),
        )
        raw = agent.astream(
            {"messages": [("user", body.message)]},
            config={
                "configurable": {"thread_id": str(body.conversation_id)},
                "callbacks": build_tracing_callbacks(app.state.settings),
            },
            context=context,
            stream_mode=["messages", "updates"],
        )
        # `aclosing` makes a client disconnect reach the stream (and its rollback) right away.
        async with aclosing(ui_message_stream(raw, on_abort=rollback)) as lines:
            async for line in lines:
                yield line
    finally:
        turn.release()


@router.post("/chat")
async def chat(
    body: ChatRequestModel, request: Request, customer: CurrentCustomer, model: CurrentModel
) -> StreamingResponse:
    identity = customer.customer_id if customer else None
    turn = request.app.state.conversations.begin_turn(str(body.conversation_id), identity)
    return StreamingResponse(
        _run_turn(turn, request, body, customer, model),
        media_type="text/event-stream",
        headers=STREAM_HEADERS,
    )


@router.delete("/chat/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: UUID, request: Request) -> Response:
    request.app.state.conversations.delete(str(conversation_id))
    return Response(status_code=204)
