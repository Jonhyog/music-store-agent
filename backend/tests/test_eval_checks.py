from evals.checks import (
    asks_confirmation,
    calls_any_tool,
    calls_tool,
    contains_any,
    does_not_call_tool,
    does_not_contain,
    is_complete_answer,
    uses_no_tools,
)
from evals.transcript import Reply, ToolCall


def _reply(text="", *tools):
    return Reply(text=text, tool_calls=[ToolCall(name=t, input={}, output=None) for t in tools])


def test_tool_checks_report_a_failure_message_or_none():
    assert calls_tool("search_policies")(_reply("", "search_policies")) is None
    assert "search_policies" in calls_tool("search_policies")(_reply(""))
    assert does_not_call_tool("register_complaint")(_reply("", "get_my_order")) is None
    assert "register_complaint" in does_not_call_tool("register_complaint")(
        _reply("", "register_complaint")
    )
    assert uses_no_tools()(_reply("oi")) is None
    assert "get_my_order" in uses_no_tools()(_reply("oi", "get_my_order"))


def test_text_checks_ignore_case_and_accents_free_matching_is_not_assumed():
    assert (
        contains_any("não vendemos", "parceir")(_reply("Não vendemos, veja lojas parceiras"))
        is None
    )
    assert contains_any("parceir")(_reply("nada")) is not None
    assert does_not_contain("BR123")(_reply("rastreio BR123")) is not None
    assert does_not_contain("BR123")(_reply("nada")) is None


def test_asks_confirmation_accepts_a_question_or_a_confirm_request():
    assert asks_confirmation()(_reply('Confirme com "sim" para prosseguir.')) is None
    assert asks_confirmation()(_reply("Posso registrar?")) is None
    assert asks_confirmation()(_reply("Registrado.")) is not None


def test_an_errored_reply_fails_every_check():
    errored = Reply(text="ok?", tool_calls=[], error="boom")
    assert "boom" in uses_no_tools()(errored)


def test_calls_any_tool_accepts_either_tool():
    check = calls_any_tool("get_product", "search_products")
    assert check(_reply("", "search_products")) is None
    assert "get_product" in check(_reply("", "list_categories"))


def test_is_complete_answer_rejects_empty_text_and_latex_wrappers():
    assert is_complete_answer()(_reply("Aqui estão os violões.")) is None
    assert "empty" in is_complete_answer()(_reply("   "))
    assert "boxed" in is_complete_answer()(_reply("ok \\boxed{ok}"))
    assert "tool call" in is_complete_answer()(_reply("<function_call>{}</function_call>"))
