"""Builds the Assistant: a LangChain agent over the catalog tools and the system prompt."""

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, dynamic_prompt
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import trim_messages
from langgraph.checkpoint.base import BaseCheckpointSaver

from music_store.assistant.context import AgentContext
from music_store.assistant.prompt import render_system_prompt
from music_store.assistant.tools import CATALOG_TOOLS, ORDER_TOOLS, POLICY_TOOLS


@dynamic_prompt
def _system_prompt(request: ModelRequest) -> str:
    return render_system_prompt(request.runtime.context)


class HistoryWindow(AgentMiddleware):
    """Sends the model only the last `max_messages` messages (stored history is kept).

    The window starts on a Customer message, so a tool result never appears without the tool
    request that produced it.
    """

    def __init__(self, max_messages: int) -> None:
        self.max_messages = max_messages

    def _windowed(self, request: ModelRequest) -> ModelRequest:
        trimmed = trim_messages(
            request.messages,
            max_tokens=self.max_messages,
            token_counter=len,
            strategy="last",
            start_on="human",
            allow_partial=False,
        )
        return request.override(messages=trimmed or request.messages)

    def wrap_model_call(self, request, handler):
        return handler(self._windowed(request))

    async def awrap_model_call(self, request, handler):
        return await handler(self._windowed(request))


def build_agent(model: BaseChatModel, checkpointer: BaseCheckpointSaver, max_messages: int = 20):
    return create_agent(
        model,
        tools=[*CATALOG_TOOLS, *ORDER_TOOLS, *POLICY_TOOLS],
        middleware=[_system_prompt, HistoryWindow(max_messages)],
        context_schema=AgentContext,
        checkpointer=checkpointer,
    )
