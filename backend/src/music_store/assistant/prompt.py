"""The versioned system prompt template, rendered per request from the agent context."""

from functools import cache
from pathlib import Path
from string import Template

from music_store.assistant.context import AgentContext

PROMPT_VERSION = "v1"
PROMPT_PATH = Path(__file__).parent / "prompts" / f"system_{PROMPT_VERSION}.md"


@cache
def _template() -> Template:
    return Template(PROMPT_PATH.read_text(encoding="utf-8"))


def _audience(context: AgentContext) -> str:
    if context.customer is None:
        return "a Visitor (not identified as a customer)"
    return f"the customer {context.customer.name.split()[0]}"


def render_system_prompt(context: AgentContext) -> str:
    return _template().substitute(
        reference_date=context.reference_date.isoformat(), audience=_audience(context)
    )
