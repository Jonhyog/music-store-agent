"""Builds the Assistant: a LangChain agent over the catalog tools and the system prompt."""

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver

from music_store.assistant.context import AgentContext
from music_store.assistant.prompt import render_system_prompt
from music_store.assistant.tools import CATALOG_TOOLS, ORDER_TOOLS, POLICY_TOOLS


@dynamic_prompt
def _system_prompt(request: ModelRequest) -> str:
    return render_system_prompt(request.runtime.context)


def build_agent(model: BaseChatModel, checkpointer: BaseCheckpointSaver):
    return create_agent(
        model,
        tools=[*CATALOG_TOOLS, *ORDER_TOOLS, *POLICY_TOOLS],
        middleware=[_system_prompt],
        context_schema=AgentContext,
        checkpointer=checkpointer,
    )
