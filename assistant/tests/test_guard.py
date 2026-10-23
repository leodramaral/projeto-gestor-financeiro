from decimal import Decimal

import pytest

from assistant.facts import Facts, Term
from assistant.guard import MAX_CHARS, NO_QUERY, TOO_LONG, VALUE_MISMATCH, check_answer


def facts(total, categories=()):
    """The facts of one spending result: `categories` are (name, amount, percent) triples."""
    return Facts(
        amounts=(
            Term(None, Decimal(total)),
            *(Term(name, Decimal(amount)) for name, amount, _ in categories),
        ),
        percents=tuple(Term(name, Decimal(percent)) for name, _, percent in categories),
        names=frozenset(name for name, _, _ in categories),
    )


RESULT = facts("1500.00", [("Alimentação", "1234.56", 82), ("Transporte", "265.44", 18)])
RESULTS = [RESULT]
# Four categories and a total that is not their sum of any three.
HOME = facts(
    "2710.00",
    [
        ("Moradia", "1500.00", 55),
        ("Alimentação", "900.00", 33),
        ("Transporte", "250.00", 9),
        ("Lazer", "60.00", 2),
    ],
)


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
    previous = facts("77.00", [("X", "77.00", 100)])

    assert check_answer("Você gastou R$ 77,00.", [RESULT]) == VALUE_MISMATCH
    assert check_answer("Você gastou R$ 77,00.", [previous]) is None


def test_the_values_of_every_query_of_the_question_count():
    other = facts("77.00", [("X", "77.00", 100)])

    assert check_answer("Foram R$ 77,00 e R$ 265,44.", [RESULT, other]) is None


def test_a_value_that_is_no_sum_of_the_terms_is_rejected():
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
    only_total = [facts("1500.00")]

    assert check_answer("Foram R$ 1.500.", only_total) is None
    assert check_answer("Foram R$ 1500.", only_total) is None
    assert check_answer("Foram 1500 reais.", only_total) is None


def test_a_sentence_ending_right_after_the_value():
    assert check_answer("Você gastou R$ 265,44.", RESULTS) is None
    assert check_answer("Você gastou R$ 265,44, bastante.", RESULTS) is None


def test_a_malformed_number_is_rejected():
    assert check_answer("Você gastou R$ 1.2.3.", RESULTS) == VALUE_MISMATCH


def test_plain_numbers_are_not_checked():
    assert check_answer("Alimentação pesou 82% e foram 3 compras.", RESULTS) is None


def test_a_text_without_values_is_accepted_after_a_query():
    assert check_answer("Alimentação foi a categoria que mais pesou em agosto.", RESULTS) is None


def test_the_length_limit_is_inclusive():
    assert check_answer("a" * MAX_CHARS, RESULTS) is None
    assert check_answer("a" * (MAX_CHARS + 1), RESULTS) == TOO_LONG


def test_no_query_wins_over_the_other_reasons():
    assert check_answer("a" * (MAX_CHARS + 1), []) == NO_QUERY


def test_a_number_inside_a_category_name_is_not_a_claimed_amount():
    results = [facts("100.00", [("Mesada R$ 200", "100.00", 100)])]

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


# --- calculations the model makes and the code checks -------------------------------------------


def test_a_sum_of_two_terms_the_text_shows_is_accepted():
    assert check_answer("Moradia e Alimentação somam R$ 2.400,00.", [HOME]) is None


def test_a_sum_of_three_terms_the_text_shows_is_accepted():
    text = "Moradia, Alimentação e Transporte somam R$ 2.650,00."

    assert check_answer(text, [HOME]) is None


def test_a_difference_of_two_terms_the_text_shows_is_accepted():
    assert check_answer("Moradia é R$ 600,00 a mais que Alimentação.", [HOME]) is None


def test_a_difference_that_does_not_match_the_terms_is_rejected():
    text = "Moradia é R$ 600,00 a mais que Transporte."

    assert check_answer(text, [HOME]) == VALUE_MISMATCH


def test_a_sum_that_does_not_match_the_terms_is_rejected():
    text = "Moradia e Transporte somam R$ 2.400,00."

    assert check_answer(text, [HOME]) == VALUE_MISMATCH


def test_the_terms_may_be_shown_by_their_values_instead_of_their_names():
    text = "Foram R$ 1.500,00 e R$ 900,00, somando R$ 2.400,00."

    assert check_answer(text, [HOME]) is None


def test_the_names_of_the_terms_match_in_any_case():
    assert check_answer("moradia e ALIMENTAÇÃO somam R$ 2.400,00.", [HOME]) is None


def test_the_word_total_shows_the_total_as_a_term():
    assert check_answer("O total menos Moradia dá R$ 1.210,00.", [HOME]) is None


def test_a_sum_with_terms_the_text_does_not_show_is_rejected():
    text = "Em casa e comida você gastou R$ 2.400,00."

    assert check_answer(text, [HOME]) == VALUE_MISMATCH


def test_a_sum_of_more_than_three_terms_is_rejected():
    small = facts(
        "1000.00", [("A", "10.00", 1), ("B", "20.00", 2), ("C", "30.00", 3), ("D", "40.00", 4)]
    )

    assert check_answer("A, B e C somam R$ 60,00.", [small]) is None
    assert check_answer("A, B, C e D somam R$ 100,00.", [small]) == VALUE_MISMATCH


def test_with_many_categories_a_coincidence_does_not_pass_unless_the_terms_are_shown():
    many = facts(
        "21000.00", [(f"Cat {i:02d}", f"{i * 100}.00", 5) for i in range(1, 21)]
    )  # 2.500 is 100 + 400 + 2.000, among many other sums

    assert check_answer("Você gastou R$ 2.500,00 no mês.", [many]) == VALUE_MISMATCH
    shown = "Cat 01, Cat 04 e Cat 20 somam R$ 2.500,00."
    assert check_answer(shown, [many]) is None


def test_the_terms_of_a_sum_may_come_from_different_queries():
    august = facts("300.00", [("Transporte", "300.00", 100)])
    september = facts("120.00", [("Transporte", "120.00", 100)])
    text = "Transporte foi R$ 300,00 e R$ 120,00, somando R$ 420,00."

    assert check_answer(text, [august, september]) is None
    assert check_answer(text, [august]) == VALUE_MISMATCH


def test_a_short_name_inside_another_word_is_not_shown():
    """ "Ar" is in "para", but the text does not name it: R$ 1.700,00 is not a sum it shows."""
    results = [
        Facts(
            amounts=(Term("Moradia", Decimal("1500.00")), Term("Ar", Decimal("200.00"))),
            names=frozenset({"Moradia", "Ar"}),
        )
    ]

    text = "Moradia custou R$ 1.700,00 para você."

    assert check_answer(text, results) == VALUE_MISMATCH
    assert check_answer("Moradia e Ar somam R$ 1.700,00.", results) is None


# --- percentages ---------------------------------------------------------------------------------


@pytest.mark.parametrize("cited", ["55%", "55 %", "55,0%", "55.0 %"])
def test_a_percentage_the_tool_returned_is_accepted(cited):
    assert check_answer(f"Moradia pesa {cited} do mês.", [HOME]) is None


def test_a_percentage_the_tool_did_not_return_is_rejected():
    assert check_answer("Moradia pesa 80% do mês.", [HOME]) == VALUE_MISMATCH


def test_a_sum_of_percentages_the_text_shows_is_accepted_with_a_point_of_slack_per_term():
    assert check_answer("Moradia e Alimentação pesam juntas 88%.", [HOME]) is None
    assert check_answer("Moradia e Alimentação pesam juntas 89%.", [HOME]) is None
    assert check_answer("Moradia e Alimentação pesam juntas 95%.", [HOME]) == VALUE_MISMATCH


def test_the_slack_of_a_sum_of_percentages_is_the_rounding_and_no_more():
    """Terms of 55 and 33 are within one point of a sum that was rounded once more, not two."""
    assert check_answer("Moradia e Alimentação pesam juntas 90%.", [HOME]) == VALUE_MISMATCH
    assert check_answer("Moradia, Alimentação e Transporte pesam 98%.", [HOME]) is None
    assert check_answer("Moradia, Alimentação e Transporte pesam 100%.", [HOME]) == VALUE_MISMATCH


def test_a_ratio_of_two_amounts_the_text_shows_is_accepted_within_a_point():
    assert check_answer("Alimentação é 60% de Moradia.", [HOME]) is None
    assert check_answer("Alimentação é 61% de Moradia.", [HOME]) is None
    assert check_answer("Alimentação é 70% de Moradia.", [HOME]) == VALUE_MISMATCH


def test_a_percentage_with_nothing_to_derive_it_from_is_rejected():
    assert check_answer("Algo pesou 40% no mês.", [HOME]) == VALUE_MISMATCH


def test_a_percentage_inside_a_category_name_is_not_a_claim():
    results = [facts("100.00", [("Imposto 10%", "100.00", 100)])]

    assert check_answer("Imposto 10% foi 100% do gasto.", results) is None
    assert check_answer("Imposto 10% foi 90% do gasto.", results) == VALUE_MISMATCH


def test_a_total_of_zero_does_not_break_the_ratio():
    assert check_answer("Foi 50% do total.", [facts("0.00")]) == VALUE_MISMATCH


# --- the guard knows nothing of any tool's result ------------------------------------------------


def test_facts_from_another_kind_of_tool_are_checked_the_same_way():
    goal = Facts(
        amounts=(Term("Viagem", Decimal("500.00")), Term("Reserva", Decimal("200.00"))),
        percents=(Term("Viagem", Decimal(25)),),
        names=frozenset({"Viagem", "Reserva"}),
    )

    assert check_answer("Viagem tem R$ 500,00, ou 25% da meta.", [goal]) is None
    assert check_answer("Viagem e Reserva somam R$ 700,00.", [goal]) is None
    assert check_answer("Viagem tem R$ 400,00.", [goal]) == VALUE_MISMATCH


def test_the_narrow_no_break_spaces_the_provider_writes_do_not_break_the_checks():
    """Seen with the real model: "55 %" and "R$ 1.500,00 − R$ 900,00" with U+202F around them."""
    text = "Moradia representou 55\u202f% e foi R$ 600,00 a mais que Alimentação."
    text += " (R$ 1.500,00\u202f−\u202fR$ 900,00)"

    assert check_answer(text, [HOME]) is None
    assert check_answer("Moradia representou 80\u202f%.", [HOME]) == VALUE_MISMATCH
