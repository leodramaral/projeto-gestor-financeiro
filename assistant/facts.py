"""What a tool lets the model cite: the terms (a label and a value) of a successful result.

The guard only reads these, so it knows nothing about the shape of any tool's result: a new tool
declares its own facts and the guard checks the answer against them.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Term:
    """One citable number. `label` is the name the text uses for it; None is the total."""

    label: str | None
    value: Decimal


@dataclass(frozen=True)
class Facts:
    """The citable amounts (in reais) and percentages of one tool result.

    `names` are texts that came from the user's data (a category name): they are taken out of the
    answer before its numbers are read, since a name such as "Mesada R$ 200" is data, not a claim.
    """

    amounts: tuple[Term, ...] = ()
    percents: tuple[Term, ...] = ()
    names: frozenset[str] = frozenset()
