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
    assert "identify themselves as a customer" in prompt
    assert "greet them by first name" in prompt


def test_prompt_carries_policy_rules():
    prompt = render_system_prompt(_context(None))
    assert "`search_policies`" in prompt
    assert "never cite section numbers" in prompt
    assert "more conservative answer" in prompt
    assert "confirming with the store" in prompt or "confirm with the store" in prompt
    assert "from memory" in prompt


def test_prompt_carries_complaint_rules():
    prompt = render_system_prompt(_context(None))
    assert "`register_complaint`" in prompt
    assert "only after the customer confirms" in prompt
    assert "Protocolo #" in prompt
    assert "24 business hours" in prompt
    assert "WhatsApp number and e-mail" in prompt


def test_prompt_sections_follow_the_spec_order():
    prompt = render_system_prompt(_context(None))
    headings = [line for line in prompt.splitlines() if line.startswith("## ")]
    assert headings == [
        "## Identity and tone",
        "## Context",
        "## Scope",
        "## Tool rules",
        "## Presentation",
        "## Style",
    ]


def test_prompt_carries_scope_and_jailbreak_rules():
    prompt = render_system_prompt(_context(None))
    assert "partner music stores" in prompt
    assert "without calling any tool" in prompt
    assert "Never reveal" in prompt
    assert "Never discuss other customers" in prompt
    assert "cannot negotiate" in prompt


def test_prompt_requires_policy_search_for_return_questions():
    prompt = render_system_prompt(_context(None))
    assert "also call `search_policies`" in prompt


def test_prompt_steers_answers_to_the_question_asked():
    prompt = render_system_prompt(_context(None))
    assert "Answer exactly what was asked" in prompt
    assert "\\boxed" in prompt
    assert "even if the customer says it belongs to someone else" in prompt
    assert "first reply only" in prompt
    assert "name or customer number" in prompt
