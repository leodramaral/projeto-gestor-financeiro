import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / ".claude/skills/revisar-codigo/scripts/verify_citations.py"
)
spec = importlib.util.spec_from_file_location("verify_citations", SCRIPT)
verify_citations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_citations)

FAILURE = verify_citations.FAILURE
WARNING = verify_citations.WARNING
OK = verify_citations.OK


@pytest.fixture
def snapshot(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "views.py").write_text("one\ntwo\nrestore = True\nfour\nfive\n")
    (tmp_path / "app" / "tests").mkdir()
    (tmp_path / "app" / "tests" / "test_views.py").write_text("def test_a():\n    assert 1\n")
    for change in ("a", "b"):
        (tmp_path / "changes" / change).mkdir(parents=True)
        (tmp_path / "changes" / change / "tasks.md").write_text("- [x] 1.1 one\n")
    return tmp_path


def finding(file, line, snippet=""):
    return {"arquivo": file, "linha": line, "trecho": snippet}


def run(snapshot, verdict):
    return [(status, message) for _, status, message in verify_citations.verify(verdict, snapshot)]


def test_a_finding_on_an_existing_line_with_its_snippet_is_ok(snapshot):
    verdict = {"achados_principais": [finding("app/views.py", 3, "restore = True")]}

    assert run(snapshot, verdict) == [(OK, "")]


def test_the_snippet_may_sit_a_few_lines_away_from_the_cited_line(snapshot):
    near = {"achados_principais": [finding("app/views.py", 5, "restore = True")]}
    far = {"achados_principais": [finding("app/views.py", 3, "five")]}

    assert run(snapshot, near)[0][0] == OK
    assert run(snapshot, far)[0][0] == OK  # line 5 is within 3 lines of line 3


def test_a_snippet_that_is_not_near_the_line_fails(snapshot):
    verdict = {"achados_principais": [finding("app/views.py", 1, "five")]}  # line 5, 4 lines away

    ((status, message),) = run(snapshot, verdict)

    assert status == FAILURE
    assert "snippet not found" in message


def test_spacing_does_not_matter_when_comparing_the_snippet(snapshot):
    verdict = {"achados_principais": [finding("app/views.py", 3, "restore   =\tTrue")]}

    assert run(snapshot, verdict)[0][0] == OK


def test_a_file_that_does_not_exist_fails(snapshot):
    verdict = {"achados_principais": [finding("app/missing.py", 1)]}

    ((status, message),) = run(snapshot, verdict)

    assert status == FAILURE
    assert "file not found" in message


def test_a_line_past_the_end_of_the_file_fails(snapshot):
    verdict = {"achados_principais": [finding("app/views.py", 57)]}

    ((status, message),) = run(snapshot, verdict)

    assert status == FAILURE
    assert "only 5 lines" in message


def test_a_finding_without_file_or_line_fails(snapshot):
    verdict = {"achados_principais": [finding("", 3), finding("app/views.py", 0)]}

    assert [status for status, _ in run(snapshot, verdict)] == [FAILURE, FAILURE]


def test_a_bare_name_that_matches_two_files_is_only_a_warning(snapshot):
    verdict = {"T1_matriz": [{"onde": "task 3.3 (tasks.md:1)"}]}

    ((status, message),) = run(snapshot, verdict)

    assert status == WARNING
    assert "more than one file" in message


def test_a_bare_name_that_matches_one_file_is_checked_with_a_warning(snapshot):
    ok = {"T1_matriz": [{"onde": "test_views.py:2"}]}
    past_the_end = {"T1_matriz": [{"onde": "test_views.py:9"}]}

    assert run(snapshot, ok)[0][0] == WARNING
    assert run(snapshot, past_the_end)[0][0] == FAILURE


def test_citations_inside_text_fields_are_found_including_ranges(snapshot):
    verdict = {
        "criterios": {"T2": {"motivo": "see app/views.py:2-4", "evidencias": ["app/views.py:3"]}},
        "T1_matriz": [{"onde": "app/tests/test_views.py:1-2 and app/views.py:99"}],
    }

    statuses = [status for status, _ in run(snapshot, verdict)]

    assert statuses.count(FAILURE) == 1  # only app/views.py:99
    assert len(statuses) == 4  # the two in `criterios`, the two in `onde`


def test_out_of_scope_findings_are_checked_too(snapshot):
    verdict = {"fora_do_escopo": [finding("app/views.py", 99, "x")]}

    assert run(snapshot, verdict)[0][0] == FAILURE


def test_main_exits_with_1_when_a_citation_fails_and_0_otherwise(snapshot, tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"achados_principais": [finding("app/views.py", 3, "restore")]}))
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"achados_principais": [finding("app/views.py", 99)]}))

    assert verify_citations.main(["x", str(good), str(snapshot)]) == 0
    assert verify_citations.main(["x", str(bad), str(snapshot)]) == 1
    output = capsys.readouterr().out
    assert "1 citations checked: 1 ok, 0 failed, 0 warnings" in output
    assert "FAILED" in output


def test_main_without_arguments_prints_the_usage(capsys):
    assert verify_citations.main(["x"]) == 2
    assert "Usage:" in capsys.readouterr().out
