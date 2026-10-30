"""Check the mutation score of the last mutmut run against the floor in pyproject.toml.

`mutmut run` always exits 0, so this is the gate. The score is mutmut's own (the one `mutmut
badge` shows): (killed + timeout) / (total - skipped), in percent. A timeout counts as caught: the
suite did not pass with the mutant, and a slow runner turning kills into timeouts must not move it.
The floor is a ratchet, like coverage's `fail_under`: the measured score truncated down, and it
only goes up.

Usage: python scripts/mutation_score.py [stats.json] [pyproject.toml]
"""

import json
import math
import sys
import tomllib
from pathlib import Path

STATS = Path("mutants/mutmut-cicd-stats.json")
PYPROJECT = Path("pyproject.toml")
# Every outcome in the stats file; whatever `total` has beyond them was never checked.
OUTCOMES = (
    "killed",
    "survived",
    "no_tests",
    "skipped",
    "suspicious",
    "timeout",
    "check_was_interrupted_by_user",
    "segfault",
)


def score(stats):
    """Percent of the tested mutants the suite caught, or None when nothing was tested."""
    tested = stats["total"] - stats["skipped"]
    if tested <= 0:
        return None
    return (stats["killed"] + stats["timeout"]) / tested * 100


def unchecked(stats):
    return stats["total"] - sum(stats[outcome] for outcome in OUTCOMES)


def truncate(value):
    """One decimal, always rounded down: the floor never claims more than was measured."""
    return math.floor(value * 10) / 10


def check(stats, min_score):
    """(passed, message) for the stats of a run against the floor."""
    missing = unchecked(stats)
    if missing:
        return False, f"incomplete run: {missing} of {stats['total']} mutants were not checked"
    if stats["check_was_interrupted_by_user"]:
        return False, "incomplete run: interrupted by the user"
    measured = score(stats)
    if measured is None:
        return False, "no mutant was tested"
    summary = (
        f"mutation score {measured:.2f}% "
        f"({stats['killed']} killed, {stats['timeout']} timeout, {stats['survived']} survived, "
        f"{stats['no_tests']} without tests, of {stats['total'] - stats['skipped']}); "
        f"floor {min_score}%"
    )
    if measured < min_score:
        return False, f"{summary}: below the floor"
    if truncate(measured) > min_score:
        return True, f"{summary}: raise min_score to {truncate(measured)}"
    return True, summary


def main(argv):
    stats_path = Path(argv[1]) if len(argv) > 1 else STATS
    pyproject_path = Path(argv[2]) if len(argv) > 2 else PYPROJECT
    stats = json.loads(stats_path.read_text())
    min_score = tomllib.loads(pyproject_path.read_text())["tool"]["mutation"]["min_score"]
    passed, message = check(stats, min_score)
    print(message)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
