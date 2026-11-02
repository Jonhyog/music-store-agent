from dataclasses import dataclass
from datetime import date
from pathlib import Path

from music_store.assistant.policy import PolicySearch
from music_store.models.customer import CustomerModel


@dataclass(frozen=True)
class AgentContext:
    """Per-request context handed to tools and the prompt, never shown to the model as arguments."""

    customer: CustomerModel | None
    reference_date: date
    database_path: Path
    conversation_id: str = ""
    policy_search: PolicySearch | None = None
