from datetime import date

from music_store.assistant.context import AgentContext
from music_store.assistant.prompt import render_system_prompt
from music_store.models.customer import CustomerModel


def _context(customer):
    return AgentContext(customer=customer, reference_date=date(2026, 3, 25), database_path=None)


def test_prompt_injects_reference_date_and_customer_first_name():
    customer = CustomerModel(
        customer_id=1, name="Ana Carolina Ferreira", phone=None, email=None, city=None
    )
    prompt = render_system_prompt(_context(customer))
    assert "2026-03-25" in prompt
    assert "the customer Ana" in prompt
    assert "Ferreira" not in prompt


def test_prompt_marks_visitors_as_not_identified():
    assert "Visitor (not identified" in render_system_prompt(_context(None))


def test_prompt_carries_order_rules():
    prompt = render_system_prompt(_context(None))
    assert "estimated delivery date is the delivery date" in prompt
    assert "need to know who they are" in prompt
    assert "greet them by first name" in prompt


def test_prompt_carries_policy_rules():
    prompt = render_system_prompt(_context(None))
    assert "`search_policies`" in prompt
    assert "Cite the section" in prompt
    assert "more conservative answer" in prompt
    assert "confirming with the store" in prompt or "confirm with the store" in prompt
    assert "from memory" in prompt
