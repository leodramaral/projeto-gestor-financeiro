"""Texts the application itself writes for the user. The model never writes these."""

EXAMPLE_QUESTION = "Quanto gastei com transporte em agosto?"

REFUSAL = f"Só posso ajudar com seus gastos por categoria. Tente, por exemplo: {EXAMPLE_QUESTION}"
HELP = (
    "Olá! Eu respondo perguntas sobre seus gastos por categoria, como: "
    f"{EXAMPLE_QUESTION} Qual categoria pesou mais neste mês?"
)


def period_unavailable(first, last):
    """The answer to a month that cannot be queried; `first` and `last` are month labels."""
    return (
        f"Não consigo consultar esse mês. Só dá para consultar de {first} até {last}. "
        f"Tente, por exemplo: {EXAMPLE_QUESTION}"
    )


UNRELIABLE = "Não consegui montar uma resposta confiável. Tente reformular a pergunta."
UNAVAILABLE = "O assistente está indisponível no momento. Tente de novo mais tarde."
RATE_LIMITED = (
    "O assistente está com muitas consultas agora. Aguarde alguns segundos e tente de novo."
)
NO_CREDITS = "Seus créditos de hoje acabaram. Eles voltam amanhã."
DISCLAIMER = (
    "Assistente em fase BETA: as respostas são sugestões automatizadas e não substituem "
    "aconselhamento financeiro profissional."
)
