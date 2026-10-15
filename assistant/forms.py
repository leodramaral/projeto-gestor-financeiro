from django import forms
from django.utils.text import normalize_newlines

from .messages import EXAMPLE_QUESTION

MAX_QUESTION_CHARS = 500
# The field sits inside the prompt box, which draws the border and the focus ring.
FIELD_CLASS = (
    "block min-h-14 w-full resize-none border-0 bg-transparent p-0 text-base text-gray-800 "
    "placeholder:text-gray-400 focus:ring-0 focus:outline-hidden dark:text-white/90 "
    "dark:placeholder:text-white/30"
)


class NormalizedCharField(forms.CharField):
    """Browsers submit each line break of a textarea as CRLF but count it as one character in
    `maxlength`; normalizing first keeps the length check in line with what the user saw."""

    def to_python(self, value):
        return super().to_python(normalize_newlines(value) if value else value)


class QuestionForm(forms.Form):
    question = NormalizedCharField(
        label="Sua pergunta",
        max_length=MAX_QUESTION_CHARS,
        strip=True,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "placeholder": EXAMPLE_QUESTION,
                "class": FIELD_CLASS,
                "autofocus": True,
                "@keydown.enter": (
                    "if (!$event.shiftKey && !$event.isComposing) "
                    "{ $event.preventDefault(); if (!busy) $el.form.requestSubmit() }"
                ),
            }
        ),
        error_messages={
            "required": "Escreva sua pergunta.",
            "max_length": f"A pergunta pode ter no máximo {MAX_QUESTION_CHARS} caracteres.",
        },
    )
