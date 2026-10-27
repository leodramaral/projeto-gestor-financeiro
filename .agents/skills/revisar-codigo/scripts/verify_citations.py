"""Checks the `file:line` citations of a code-review verdict against a source snapshot.

Usage: python verify_citations.py <verdict.json> <snapshot_dir>

A citation fails when the file does not exist, the line is past the end of the file or, for a
finding that carries a `trecho`, the literal snippet is not on the cited line nor within CONTEXT
lines around it. A bare file name that matches more than one file cannot be checked: it is only a
warning. Exit code 1 when any citation fails. It only reads files; nothing in the snapshot runs.
Standard library only, so the skill carries it to any project.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CONTEXT = 3
OK, WARNING, FAILURE = "ok", "warning", "failure"
# Verdict lists whose items carry `arquivo`, `linha` and, optionally, a literal `trecho`.
FINDING_KEYS = ("achados_principais", "fora_do_escopo")
CITATION = re.compile(r"([\w./-]+\.(?:py|js|html|css|md|yaml|yml|json|toml)):(\d+)(?:-(\d+))?")


@dataclass(frozen=True)
class Citation:
    where: str  # the part of the verdict it came from
    name: str
    start: int
    end: int
    snippet: str = ""


def normalize(text):
    return " ".join(text.split())


def as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def from_findings(verdict, key):
    for item in verdict.get(key, []):
        line = as_int(item.get("linha"))
        yield Citation(key, item.get("arquivo") or "", line, line, item.get("trecho") or "")


def from_text(where, text):
    for name, start, end in CITATION.findall(text or ""):
        yield Citation(where, name, int(start), int(end or start))


def citations(verdict):
    for key in FINDING_KEYS:
        yield from from_findings(verdict, key)
    for code, criterion in verdict.get("criterios", {}).items():
        for text in [*criterion.get("evidencias", []), criterion.get("motivo", "")]:
            yield from from_text(f"criterios.{code}", text)
    for row in verdict.get("T1_matriz", []):
        yield from from_text("T1_matriz", row.get("onde", ""))


def resolve(root, name):
    """(path, status, note): the file `name` points to, or why it cannot be checked.

    The full path from the repository root is expected; a bare file name is accepted, with a
    warning, only when it matches a single file.
    """
    path = root / name
    if path.is_file():
        return path, OK, ""
    matches = [p for p in root.rglob(Path(name).name) if p.is_file()]
    if len(matches) == 1:
        return matches[0], WARNING, "path is not complete (matched by file name)"
    if matches:
        return None, WARNING, "file name matches more than one file"
    return None, FAILURE, "file not found"


def has_snippet(lines, citation):
    window = lines[max(0, citation.start - 1 - CONTEXT) : citation.end + CONTEXT]
    return normalize(citation.snippet) in normalize(" ".join(window))


def check(root, citation):
    """(status, message) for one citation."""
    label = f"{citation.name}:{citation.start}"
    if not citation.name or citation.start < 1:
        return FAILURE, f"{citation.where}: citation without file or line"
    path, status, note = resolve(root, citation.name)
    if path is None:
        return status, f"{label}: {note}"
    lines = path.read_text(errors="replace").splitlines()
    if citation.end > len(lines):
        return FAILURE, f"{label}: the file has only {len(lines)} lines"
    if citation.snippet and not has_snippet(lines, citation):
        return FAILURE, f"{label}: snippet not found within {CONTEXT} lines of the citation"
    return status, f"{label}: {note}" if note else ""


def verify(verdict, root):
    return [(citation, *check(root, citation)) for citation in citations(verdict)]


def report(results):
    failures = [f"[{c.where}] {message}" for c, status, message in results if status == FAILURE]
    warnings = [f"[{c.where}] {message}" for c, status, message in results if status == WARNING]
    print(
        f"{len(results)} citations checked: {len(results) - len(failures) - len(warnings)} ok, "
        f"{len(failures)} failed, {len(warnings)} warnings"
    )
    for line in [*(f"FAILED  {f}" for f in failures), *(f"warning {w}" for w in warnings)]:
        print(f"  {line}")
    return 1 if failures else 0


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    verdict = json.loads(Path(argv[1]).read_text())
    return report(verify(verdict, Path(argv[2])))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
