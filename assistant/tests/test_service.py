import json
import logging
import re
from datetime import date
from types import SimpleNamespace

import httpx2
import pytest
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from assistant import messages, service
from assistant.guard import NO_QUERY, TOO_LONG, VALUE_MISMATCH
from assistant.service import (
    MAX_COMPLETION_TOKENS,
    MAX_MODEL_CALLS,
    MAX_PROVIDER_MESSAGE,
    REFUSED,
    REJECTED,
    TEXT,
    AssistantError,
    RateLimited,
    Unavailable,
    answer,
)
from assistant.tools import DECLINE, SPENDING

from .fakes import FakeClient, ScriptExhausted, text_response, tool_response, usage

REQUEST = httpx2.Request("POST", "https://llm.test/v1/chat/completions")


def status_error(cls, code):
    return cls("x", response=httpx2.Response(code, request=REQUEST), body=None)


@pytest.fixture
def fake(monkeypatch):
    def install(*script):
        client = FakeClient(*script)
        monkeypatch.setattr(service, "get_client", lambda: client)
        return client

    return install


@pytest.fixture
def august(user, category, make_expense):
    make_expense(user, category("Transporte"), "842.10", date(2026, 8, 7))
    make_expense(user, category("Alimentação"), "300.00", date(2026, 8, 9))
    return user


def spending(month="2026-08"):
    return (SPENDING, json.dumps({"month": month}))


def test_a_question_with_one_tool_round_and_a_right_answer(august, fake):
    client = fake(
        tool_response(spending(), tokens=900),
        text_response("Em agosto você gastou R$ 842,10 com Transporte.", tokens=1300),
    )

    result = answer(august, [], "Quanto gastei com transporte em agosto?")

    assert (result.outcome, result.tokens) == (TEXT, 2200)
    assert "R$ 842,10" in result.text
    sent = client.calls[1]["messages"]
    assert sent[-2]["role"] == "assistant" and sent[-1]["role"] == "tool"
    assert sent[-1]["tool_call_id"] == "call_1"
    assert json.loads(sent[-1]["content"])["total"] == "1142.10"


SIGNATURE = {"google": {"thought_signature": "opaque-signature"}}


def test_an_extra_field_of_a_tool_call_goes_back_unchanged_in_the_next_round(august, fake):
    client = fake(
        tool_response((SPENDING, '{"month": "2026-08"}', {"extra_content": SIGNATURE})),
        text_response("Em agosto você gastou R$ 842,10 com Transporte."),
    )

    result = answer(august, [], "Quanto gastei com transporte em agosto?")

    assert result.outcome == TEXT
    assistant_message = client.calls[1]["messages"][-2]
    assert assistant_message["tool_calls"] == [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": SPENDING, "arguments": '{"month": "2026-08"}'},
            "extra_content": SIGNATURE,
        }
    ]


def test_each_tool_call_keeps_its_own_extra_field(august, fake):
    first, second = {"extra_content": {"n": 1}}, {"extra_content": {"n": 2}}
    client = fake(
        tool_response((SPENDING, spending()[1], first), (SPENDING, spending("2026-07")[1], second)),
        text_response("Foram R$ 842,10."),
    )

    answer(august, [], "q")

    calls = client.calls[1]["messages"][-3]["tool_calls"]
    assert [c.get("extra_content") for c in calls] == [{"n": 1}, {"n": 2}]


def test_without_extra_fields_the_assistant_message_is_the_standard_one(august, fake):
    client = fake(tool_response(spending()), text_response("Foram R$ 842,10."))

    answer(august, [], "q")

    assert client.calls[1]["messages"][-2]["tool_calls"] == [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": SPENDING, "arguments": spending()[1]},
        }
    ]


def test_an_extra_field_never_overrides_the_standard_ones(august, fake):
    client = fake(
        tool_response((SPENDING, spending()[1], {"id": "hijack", "type": "x", "function": {}})),
        text_response("Foram R$ 842,10."),
    )

    answer(august, [], "q")

    call = client.calls[1]["messages"][-2]["tool_calls"][0]
    assert call["id"] == "call_1" and call["type"] == "function"
    assert call["function"]["name"] == SPENDING


def test_the_extra_field_does_not_reach_the_next_question_of_the_conversation(august, fake):
    fake(
        tool_response((SPENDING, spending()[1], {"extra_content": SIGNATURE})),
        text_response("Em agosto você gastou R$ 842,10 com Transporte."),
    )
    first = answer(august, [], "Quanto gastei com transporte em agosto?")
    history = [
        {"role": "user", "content": "Quanto gastei com transporte em agosto?"},
        {"role": "assistant", "content": first.text},
    ]
    client = fake(text_response("Foram R$ 842,10."))

    answer(august, history, "e em agosto de novo?")

    assert "opaque-signature" not in json.dumps(client.calls[0]["messages"])


def test_the_system_prompt_and_the_question_frame_the_messages(august, fake):
    client = fake(tool_response(spending()), text_response("Foram R$ 842,10."))

    answer(august, [], "e em agosto?")

    first = client.calls[0]
    assert first["messages"][0]["role"] == "system"
    assert first["messages"][-1] == {"role": "user", "content": "e em agosto?"}
    assert first["model"] == "test-model"
    assert first["max_completion_tokens"] == MAX_COMPLETION_TOKENS


def test_only_the_last_six_messages_of_the_history_are_sent(user, fake):
    history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(8)
    ]
    client = fake(tool_response((DECLINE, '{"kind": "off_topic"}')))

    answer(user, history, "nova")

    sent = client.calls[0]["messages"]
    assert [m["content"] for m in sent[1:-1]] == ["m2", "m3", "m4", "m5", "m6", "m7"]


def test_history_entries_carry_only_role_and_content(user, fake):
    history = [{"role": "user", "content": "oi", "extra": "x"}]
    client = fake(tool_response((DECLINE, "{}")))

    answer(user, history, "q")

    assert client.calls[0]["messages"][1] == {"role": "user", "content": "oi"}


def test_exactly_two_tools_are_offered(user, fake):
    client = fake(tool_response((DECLINE, "{}")))

    answer(user, [], "q")

    names = [t["function"]["name"] for t in client.calls[0]["tools"]]
    assert names == [SPENDING, DECLINE]


def test_the_first_call_must_be_a_tool_call_by_default(august, fake):
    client = fake(tool_response(spending()), text_response("Foram R$ 842,10."))

    answer(august, [], "q")

    assert client.calls[0]["tool_choice"] == "required"
    assert "tool_choice" not in client.calls[1]


def test_with_auto_the_tool_choice_is_left_out(august, fake, monkeypatch):
    monkeypatch.setattr(service, "FIRST_ROUND_TOOL_CHOICE", "auto")
    client = fake(tool_response(spending()), text_response("Foram R$ 842,10."))

    answer(august, [], "q")

    assert all("tool_choice" not in call for call in client.calls)


def test_declining_off_topic_stops_after_one_call_with_the_fixed_text(user, fake):
    client = fake(tool_response((DECLINE, '{"kind": "off_topic"}'), tokens=450))

    result = answer(user, [], "Em qual ação devo investir?")

    assert (result.outcome, result.text, result.tokens) == (REFUSED, messages.REFUSAL, 450)
    assert result.reason == "off_topic"
    assert len(client.calls) == 1


def test_declining_smalltalk_shows_the_help_text(user, fake):
    fake(tool_response((DECLINE, '{"kind": "smalltalk"}')))

    result = answer(user, [], "oi")

    assert (result.outcome, result.text) == (REFUSED, messages.HELP)


def test_a_refusal_wins_over_a_query_in_the_same_round(august, fake, django_assert_num_queries):
    client = fake(tool_response(spending(), (DECLINE, '{"kind": "off_topic"}')))

    with django_assert_num_queries(0):
        result = answer(august, [], "q")

    assert result.outcome == REFUSED
    assert len(client.calls) == 1


def test_several_tool_calls_in_one_round_are_all_answered(august, fake):
    client = fake(
        tool_response(spending("2026-08"), spending("2026-07")),
        text_response("Em agosto foram R$ 842,10 com Transporte."),
    )

    result = answer(august, [], "q")

    assert result.outcome == TEXT
    tool_messages = [m for m in client.calls[1]["messages"] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in tool_messages] == ["call_1", "call_2"]


def test_an_unknown_tool_gets_an_error_and_nothing_is_queried(
    august, fake, django_assert_num_queries
):
    client = fake(tool_response(("get_balance", "{}")), text_response("Sem dados."))

    with django_assert_num_queries(0):
        result = answer(august, [], "q")

    tool_message = client.calls[1]["messages"][-1]
    assert "Unknown tool" in json.loads(tool_message["content"])["error"]
    assert (result.outcome, result.reason) == (REJECTED, NO_QUERY)


def test_a_text_without_any_tool_is_replaced_by_the_refusal(user, fake):
    fake(text_response("Invista em renda fixa.", tokens=300))

    result = answer(user, [], "q")

    assert (result.outcome, result.text, result.reason) == (REJECTED, messages.REFUSAL, NO_QUERY)
    assert result.tokens == 300


def test_a_text_after_a_failed_query_is_replaced_by_the_refusal(august, fake):
    fake(tool_response(spending("2099-01")), text_response("Foram R$ 1,00."))

    result = answer(august, [], "q")

    assert (result.outcome, result.text, result.reason) == (REJECTED, messages.REFUSAL, NO_QUERY)


def test_an_invented_value_is_replaced_by_the_unreliable_text(august, fake):
    fake(tool_response(spending()), text_response("Você gastou R$ 5.000,00 com Transporte."))

    result = answer(august, [], "q")

    assert (result.outcome, result.text, result.reason) == (
        REJECTED,
        messages.UNRELIABLE,
        VALUE_MISMATCH,
    )


def test_a_long_answer_is_replaced_by_the_unreliable_text(august, fake):
    fake(tool_response(spending()), text_response("a" * 1201))

    result = answer(august, [], "q")

    assert (result.outcome, result.text, result.reason) == (REJECTED, messages.UNRELIABLE, TOO_LONG)


def test_rejected_and_refused_answers_count_their_tokens(user, august, fake):
    fake(tool_response(spending(), tokens=700), text_response("R$ 1,00", tokens=300))

    assert answer(august, [], "q").tokens == 1000


def test_a_model_that_never_stops_asking_for_tools_ends_at_the_limit(august, fake):
    # One response more than the limit: a loop that ignores it would make that extra call.
    client = fake(*[tool_response(spending(), tokens=10) for _ in range(MAX_MODEL_CALLS + 1)])

    with pytest.raises(Unavailable) as error:
        answer(august, [], "q")

    assert len(client.calls) == MAX_MODEL_CALLS
    assert error.value.cause == "Unavailable"  # the limit, not a failure of the provider
    assert error.value.round == MAX_MODEL_CALLS
    assert error.value.tokens == 10 * MAX_MODEL_CALLS


def test_a_call_past_the_script_fails_the_test_instead_of_becoming_unavailable(august, fake):
    fake(tool_response(spending()))

    with pytest.raises(ScriptExhausted):
        answer(august, [], "q")


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (status_error(RateLimitError, 429), RateLimited),
        (APITimeoutError(request=REQUEST), Unavailable),
        (APIConnectionError(request=REQUEST), Unavailable),
        (status_error(APIStatusError, 500), Unavailable),
    ],
)
def test_provider_errors_become_our_errors(user, fake, error, expected):
    fake(error)

    with pytest.raises(expected) as raised:
        answer(user, [], "q")

    assert raised.value.tokens == 0


def test_a_failure_after_a_good_call_keeps_the_tokens_already_spent(august, fake):
    fake(tool_response(spending(), tokens=900), status_error(RateLimitError, 429))

    with pytest.raises(RateLimited) as raised:
        answer(august, [], "q")

    assert raised.value.tokens == 900


def broken_tool_call(tokens=100):
    call = SimpleNamespace(id="call_1", type="function", function=None)
    message = SimpleNamespace(content=None, tool_calls=[call])
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage(tokens))


@pytest.mark.parametrize(
    "response",
    [
        SimpleNamespace(choices=[SimpleNamespace()], usage=usage(70)),  # no message
        SimpleNamespace(choices=None, usage=usage(70)),
        broken_tool_call(70),  # function is null
    ],
)
def test_a_malformed_response_is_unavailable_and_keeps_the_tokens(user, fake, response):
    fake(response)

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert raised.value.tokens == 70


def test_a_malformed_second_response_keeps_the_first_tokens(august, fake):
    fake(tool_response(spending(), tokens=900), broken_tool_call(40))

    with pytest.raises(Unavailable) as raised:
        answer(august, [], "q")

    assert raised.value.tokens == 940


def test_a_client_that_cannot_be_created_is_unavailable(user, monkeypatch):
    def broken():
        raise ValueError("bad url")

    monkeypatch.setattr("assistant.service.get_client", broken)

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert raised.value.cause == "ValueError"


def test_a_response_without_usage_counts_zero(august, fake):
    fake(tool_response(spending(), tokens=None), text_response("Foram R$ 842,10.", tokens=None))

    assert answer(august, [], "q").tokens == 0


@pytest.mark.parametrize("content", [None, "", "   "])
def test_an_empty_answer_is_unavailable(user, fake, content):
    fake(text_response(content, tokens=50))

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert raised.value.tokens == 50


def test_a_response_without_choices_is_unavailable(user, fake):
    empty = text_response("x")
    empty.choices = []
    fake(empty)

    with pytest.raises(Unavailable):
        answer(user, [], "q")


def test_without_a_key_nothing_is_called(user, fake, settings):
    settings.LLM_API_KEY = ""
    client = fake(text_response("x"))

    with pytest.raises(Unavailable):
        answer(user, [], "q")

    assert client.calls == []


def test_the_calls_do_not_share_one_mutating_list(august, fake):
    client = fake(tool_response(spending()), text_response("Foram R$ 842,10."))

    answer(august, [], "q")

    assert len(client.calls[0]["messages"]) < len(client.calls[1]["messages"])


def test_an_answer_cut_by_the_token_limit_is_unavailable(august, fake):
    cut = text_response("Em agosto você gastou R$ 842,10 com", tokens=1300)
    cut.choices[0].finish_reason = "length"
    fake(tool_response(spending(), tokens=900), cut)

    with pytest.raises(Unavailable) as raised:
        answer(august, [], "q")

    assert raised.value.tokens == 2200
    assert raised.value.cause == "Truncated"


def api_error(code, body, cls=APIStatusError):
    return cls("x", response=httpx2.Response(code, request=REQUEST), body=body)


def test_the_question_id_is_short_hex_and_shared_by_the_answer_and_the_error(august, fake):
    fake(tool_response(spending()), text_response("Em agosto você gastou R$ 1.142,10."))
    result = answer(august, [], "q")
    fake(status_error(APIStatusError, 500))
    with pytest.raises(Unavailable) as raised:
        answer(august, [], "q")

    assert re.fullmatch(r"[0-9a-f]{8}", result.question_id)
    assert re.fullmatch(r"[0-9a-f]{8}", raised.value.question_id)
    assert result.question_id != raised.value.question_id


def test_the_error_carries_the_round_in_which_the_provider_failed(august, fake):
    fake(tool_response(spending()), api_error(400, None))

    with pytest.raises(Unavailable) as raised:
        answer(august, [], "q")

    assert raised.value.round == 2


@pytest.mark.parametrize(
    "body",
    [
        {"error": {"message": "bad\n  request"}},
        [{"error": {"message": "bad\n  request"}}],
    ],
)
def test_the_provider_message_is_read_from_both_error_shapes(user, fake, body):
    fake(api_error(400, body))

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert raised.value.detail == "bad request"


def test_the_provider_message_is_cut_and_the_key_masked(user, fake, settings):
    settings.LLM_API_KEY = "sk-secret"
    fake(api_error(400, {"error": {"message": "key sk-secret " + "x" * 1000}}))

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert len(raised.value.detail) == MAX_PROVIDER_MESSAGE
    assert "sk-secret" not in raised.value.detail and raised.value.detail.startswith("key ***")


@pytest.mark.parametrize("body", [None, "text", {}, {"error": "x"}, {"error": {"message": 1}}, []])
def test_a_malformed_provider_body_gives_no_message_and_no_exception(user, fake, body):
    fake(api_error(400, body))

    with pytest.raises(Unavailable) as raised:
        answer(user, [], "q")

    assert raised.value.detail == ""


def test_the_provider_message_is_kept_for_429_and_dropped_otherwise(user, fake):
    body = {"error": {"message": "quota"}}
    fake(
        api_error(429, body, RateLimitError),
        api_error(503, body),
        APIConnectionError(request=REQUEST),
    )
    details = []
    for _ in range(3):
        with pytest.raises(AssistantError) as raised:
            answer(user, [], "q")
        details.append(raised.value.detail)

    assert details == ["quota", "", ""]


def test_one_line_per_model_call_and_tool_with_the_same_id(august, fake, caplog):
    fake(
        tool_response(spending(), tokens=900),
        text_response("Em agosto você gastou R$ 1.142,10.", tokens=1300),
    )

    with caplog.at_level(logging.INFO, logger="assistant"):
        result = answer(august, [], "q")

    lines = [r.getMessage() for r in caplog.records]
    calls = [line for line in lines if line.startswith("Model call")]
    tools = [line for line in lines if line.startswith("Tool call")]
    assert len(calls) == 2 and len(tools) == 1
    assert "round=1" in calls[0] and "round=2" in calls[1]
    assert "tokens=900" in calls[0] and "model=" in calls[0] and "finish_reason=" in calls[0]
    assert f"tool={SPENDING} result=ok" in tools[0]
    assert all(f"id={result.question_id}" in line for line in calls + tools)


def test_the_tool_log_has_no_arguments_and_names_unknown_tools_as_unknown(user, fake, caplog):
    fake(
        tool_response(("drop_table", json.dumps({"month": "SEGREDO-2026"})), tokens=10),
        text_response("x"),
    )

    with caplog.at_level(logging.INFO, logger="assistant"):
        answer(user, [], "q")

    assert "SEGREDO" not in caplog.text and "drop_table" not in caplog.text
    assert "tool=unknown result=error" in caplog.text
