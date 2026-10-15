"""Texts the application itself writes for the user. The model never writes these."""

EXAMPLE_QUESTION = "Quanto gastei com transporte em agosto?"

REFUSAL = f"Só posso ajudar com seus gastos por categoria. Tente, por exemplo: {EXAMPLE_QUESTION}"
HELP = (
    "Olá! Eu respondo perguntas sobre seus gastos por categoria, como: "
    f"{EXAMPLE_QUESTION} Qual categoria pesou mais neste mês?"
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
