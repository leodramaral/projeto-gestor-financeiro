import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "mutation_score.py"
spec = importlib.util.spec_from_file_location("mutation_score", SCRIPT)
mutation_score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mutation_score)


def stats(**counts):
    base = dict.fromkeys(mutation_score.OUTCOMES, 0)
    base.update(counts)
    base.setdefault("total", sum(base.values()))
    return base


def test_score_counts_timeouts_as_caught_and_leaves_skipped_out():
    assert mutation_score.score(stats(killed=6, timeout=2, survived=2, skipped=5)) == 80


def test_score_of_a_run_that_tested_nothing_is_none():
    assert mutation_score.score(stats(skipped=3)) is None


def test_mutants_without_tests_count_against_the_score():
    assert mutation_score.score(stats(killed=1, no_tests=1)) == 50


def test_a_score_below_the_floor_fails():
    passed, message = mutation_score.check(stats(killed=7, survived=3), 70.1)

    assert not passed
    assert "70.00%" in message
    assert "below the floor" in message


def test_a_score_exactly_at_the_floor_passes_without_asking_to_raise_it():
    passed, message = mutation_score.check(stats(killed=7, survived=3), 70.0)

    assert passed
    assert "raise" not in message


def test_a_score_above_the_floor_asks_to_raise_it_truncated_down():
    # 2/3 = 66.666...%: the new floor is 66.6, never rounded up to 66.7.
    passed, message = mutation_score.check(stats(killed=2, survived=1), 50.0)

    assert passed
    assert "raise min_score to 66.6" in message


def test_an_incomplete_run_fails_even_with_a_perfect_score():
    passed, message = mutation_score.check(stats(killed=4, total=10), 0.0)

    assert not passed
    assert "6 of 10 mutants were not checked" in message


def test_an_interrupted_run_fails():
    passed, message = mutation_score.check(stats(killed=4, check_was_interrupted_by_user=1), 0.0)

    assert not passed
    assert "interrupted" in message


def test_a_run_without_tested_mutants_fails():
    passed, message = mutation_score.check(stats(skipped=2), 0.0)

    assert not passed
    assert "no mutant was tested" in message


@pytest.mark.parametrize(("min_score", "exit_code"), [(75.0, 0), (75.1, 1)])
def test_main_reads_the_stats_and_the_floor_and_sets_the_exit_code(
    tmp_path, capsys, min_score, exit_code
):
    stats_file = tmp_path / "stats.json"
    stats_file.write_text(json.dumps(stats(killed=3, survived=1)))
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(f"[tool.mutation]\nmin_score = {min_score}\n")

    assert mutation_score.main(["mutation_score.py", str(stats_file), str(pyproject)]) == exit_code
    assert "75.00%" in capsys.readouterr().out
