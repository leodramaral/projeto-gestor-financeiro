import pytest

from assistant.guard import MAX_CHARS, NO_QUERY, TOO_LONG, VALUE_MISMATCH, check_answer

RESULT = {
    "month": "2026-08",
    "label": "agosto de 2026",
    "total": "1500.00",
    "categories": [
        {"name": "Alimentação", "amount": "1234.56", "percent": 82},
        {"name": "Transporte", "amount": "265.44", "percent": 18},
    ],
}
RESULTS = [RESULT]


def test_a_text_with_right_values_is_accepted():
    text = "Em agosto você gastou R$ 1.234,56 com Alimentação e R$ 265,44 com Transporte."

    assert check_answer(text, RESULTS) is None


def test_the_total_is_an_allowed_value():
    assert check_answer("No total foram R$ 1.500,00.", RESULTS) is None


def test_without_a_successful_query_the_text_is_rejected():
    assert check_answer("Você gastou R$ 10,00.", []) == NO_QUERY
    assert check_answer("Invista em ações.", []) == NO_QUERY


def test_a_value_the_tool_did_not_return_is_rejected():
    assert check_answer("Você gastou R$ 900,00 com Lazer.", RESULTS) == VALUE_MISMATCH


def test_one_wrong_value_among_right_ones_is_rejected():
    text = "Alimentação: R$ 1.234,56. Transporte: R$ 300,00."

    assert check_answer(text, RESULTS) == VALUE_MISMATCH


def test_values_only_count_for_the_current_question():
    previous = {
        **RESULT,
        "total": "77.00",
        "categories": [{"name": "X", "amount": "77.00", "percent": 100}],
    }

    assert check_answer("Você gastou R$ 77,00.", [RESULT]) == VALUE_MISMATCH
    assert check_answer("Você gastou R$ 77,00.", [previous]) is None


def test_a_sum_made_by_the_model_is_rejected():
    assert check_answer("Juntas somam R$ 1.499,99.", RESULTS) == VALUE_MISMATCH


def test_an_abbreviated_value_is_rejected():
    assert check_answer("Você gastou R$ 1,5 mil.", RESULTS) == VALUE_MISMATCH


@pytest.mark.parametrize(
    "cited",
    ["R$ 1.234,56", "R$1.234,56", "R$ 1234,56", "R$ 1234.56", "1.234,56 reais", "1234,56 reais"],
)
def test_the_accepted_number_formats(cited):
    assert check_answer(f"Alimentação: {cited}.", RESULTS) is None


def test_whole_and_thousands_values():
    results = [{**RESULT, "total": "1500.00", "categories": []}]

    assert check_answer("Foram R$ 1.500.", results) is None
    assert check_answer("Foram R$ 1500.", results) is None
    assert check_answer("Foram 1500 reais.", results) is None


def test_a_sentence_ending_right_after_the_value():
    assert check_answer("Você gastou R$ 265,44.", RESULTS) is None
    assert check_answer("Você gastou R$ 265,44, bastante.", RESULTS) is None


def test_a_malformed_number_is_rejected():
    assert check_answer("Você gastou R$ 1.2.3.", RESULTS) == VALUE_MISMATCH


def test_percentages_and_plain_numbers_are_not_checked():
    assert check_answer("Alimentação pesou 82% e foram 3 compras.", RESULTS) is None


def test_a_text_without_values_is_accepted_after_a_query():
    assert check_answer("Alimentação foi a categoria que mais pesou em agosto.", RESULTS) is None


def test_the_length_limit_is_inclusive():
    assert check_answer("a" * MAX_CHARS, RESULTS) is None
    assert check_answer("a" * (MAX_CHARS + 1), RESULTS) == TOO_LONG


def test_no_query_wins_over_the_other_reasons():
    assert check_answer("a" * (MAX_CHARS + 1), []) == NO_QUERY


def test_a_number_inside_a_category_name_is_not_a_claimed_amount():
    results = [
        {
            "month": "2026-08",
            "label": "agosto de 2026",
            "total": "100.00",
            "categories": [{"name": "Mesada R$ 200", "amount": "100.00", "percent": 100}],
        }
    ]

    assert check_answer("Com Mesada R$ 200 você gastou R$ 100,00.", results) is None
    assert check_answer("Com Mesada R$ 200 você gastou R$ 300,00.", results) == VALUE_MISMATCH


@pytest.mark.parametrize(
    "text",
    [
        "Foram cerca de 4 mil reais.",
        "Foram R$ 1,5 mil.",
        "Foram R$ 2 mil em Alimentação.",
        "Foram R$ 1,2 milhão.",
        "Foram R$ 2k.",
    ],
)
def test_a_rounded_amount_with_a_scale_word_is_rejected(text):
    assert check_answer(text, RESULTS) == VALUE_MISMATCH


def test_a_scale_word_after_the_sentence_end_is_not_a_scaled_amount():
    assert check_answer("Você gastou R$ 1.234,56. Mil desculpas pela demora.", RESULTS) is None


@pytest.mark.parametrize(
    "text",
    ["Foram R$ -5.000,00.", "Foram R$ **900,00**.", "Foram BRL 5.000,00.", "Foram R$ _900,00_."],
)
def test_amounts_with_a_sign_or_markup_or_brl_are_still_checked(text):
    assert check_answer(text, RESULTS) == VALUE_MISMATCH


def test_an_amount_with_markup_is_accepted_when_it_is_right():
    assert check_answer("Alimentação: R$ **1.234,56**.", RESULTS) is None
    assert check_answer("Foram BRL 265,44.", RESULTS) is None
