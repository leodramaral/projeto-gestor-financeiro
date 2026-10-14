from django import forms

from .messages import EXAMPLE_QUESTION

MAX_QUESTION_CHARS = 500
# The field sits inside the prompt box, which draws the border and the focus ring.
FIELD_CLASS = (
    "block min-h-14 w-full resize-none border-0 bg-transparent p-0 text-base text-gray-800 "
    "placeholder:text-gray-400 focus:ring-0 focus:outline-hidden dark:text-white/90 "
    "dark:placeholder:text-white/30"
)


class QuestionForm(forms.Form):
    question = forms.CharField(
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
                    "{ $event.preventDefault(); $el.form.requestSubmit() }"
                ),
            }
        ),
        error_messages={
            "required": "Escreva sua pergunta.",
            "max_length": f"A pergunta pode ter no máximo {MAX_QUESTION_CHARS} caracteres.",
        },
    )
