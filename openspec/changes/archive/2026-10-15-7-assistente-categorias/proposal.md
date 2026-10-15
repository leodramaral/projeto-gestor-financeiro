# Proposal

## Why

A Issue #7 (Item 8 — Assistente de gestão com IA) pede conselhos automatizados sobre as finanças do
usuário, e a própria Issue o aponta como o item mais arriscado: provedor de LLM, isolamento de dados,
limite de custo, falha do provedor e testes sem rede. Em vez de construir o catálogo inteiro de uma vez,
esta change entrega **uma fatia vertical completa**: um chat em que o usuário pergunta sobre os **gastos
por categoria** e recebe a resposta de um LLM que consulta o próprio banco por uma única ferramenta de dados
(`get_spending_by_category`). Tudo o que foge desse assunto é recusado. Assim o fluxo de ponta a ponta
(provedor, laço de tool-calling, guardrails, limite, testes com mock) fica provado antes de acrescentar
novas ferramentas.

## What Changes

- **Nova app `assistant`** com a tela `/assistant/` (item "Assistente" na barra lateral), protegida por
  login: campo de pergunta, resposta, aviso fixo e saldo de créditos do dia.
- **Conversa só na sessão.** O histórico da conversa em andamento fica em `request.session`, limitado às
  últimas mensagens e só com texto (perguntas e respostas, sem o resultado bruto da ferramenta). Não há
  lista de conversas passadas nem model de conversa; o botão "Nova conversa" zera tudo e a conversa some ao
  encerrar a sessão.
- **Uma ferramenta de dados, `get_spending_by_category`**, que devolve os gastos do mês por categoria (nome, valor
  e porcentagem) reaproveitando `transactions.dashboard.category_slices`. O usuário vem sempre de
  `request.user`, nunca de argumento do modelo; o mês é validado como o do painel.
- **Laço de tool-calling próprio**, sem LangChain/LangGraph, com teto de voltas por pergunta; ferramenta
  desconhecida ou argumento inválido devolve erro ao modelo e não toca no banco.
- **Escopo fechado e recusa determinística.** O prompt de sistema restringe o assistente a gastos por
  categoria do próprio usuário, mas quem garante o escopo é o código: o modelo só dispõe de duas
  ferramentas, a de gastos e `decline_out_of_scope`, e a recusa é um **texto fixo** da aplicação, não texto
  do modelo. Pergunta de cortesia ("oi", "obrigado") recebe uma **resposta de ajuda fixa**. Texto vindo do
  banco (nomes de categoria) entra como dado, nunca como instrução.
- **Resposta ancorada nos dados.** Um **portão** só aceita o texto final se a ferramenta de gastos foi
  chamada, com sucesso, naquela pergunta; todo valor em reais citado precisa constar do resultado da
  ferramenta e a resposta tem tamanho máximo. Texto que falha em qualquer checagem é trocado por mensagem
  fixa e não entra no histórico.
- **Provedor por configuração.** Groq com `openai/gpt-oss-120b` pelo SDK `openai`, com `base_url`,
  chave e modelo em variáveis de ambiente (sem valor padrão para a chave); trocar de provedor é só mudar o
  `.env`.
- **Créditos por tokens.** Nova tabela de uso (usuário, dia, tokens) soma o `usage` de todas as voltas de
  cada resposta; um teto diário por usuário, em variável de ambiente, bloqueia novas perguntas quando o
  saldo acaba, e a tela mostra o saldo. Falha do provedor sem `usage` não gasta cota.
- **Falha amigável.** Timeout, erro do provedor e limite de taxa (429) viram mensagem em português na
  própria tela, sem quebrar a página.
- **Aviso fixo** na interface de que a resposta é uma sugestão automatizada, e não aconselhamento
  financeiro profissional (não gerado pelo modelo).
- **Testes** com o cliente do LLM sempre mockado; nenhuma chamada de rede na suíte.
- **Design** da tela em `design/assistant.figcraft`, na convenção de nomes do projeto.
- Documentação: `README.md` (rota, variáveis de ambiente, modelo de dados) e `.env.example`.

Fora do escopo: resumo em linguagem natural do período e sugestão de ação de economia sem pergunta (ficam
para uma Issue de continuação, porque esta change **não fecha a #7**); outras ferramentas (saldo, metas,
comparação entre meses, tendência, maiores despesas, total por categoria em período arbitrário); histórico
persistente de conversas; modelo de reserva (encadear `gpt-oss-20b` ou outro quando a cota esgotar);
streaming da resposta; escrita de dados pelo assistente (criar, editar ou excluir lançamentos); busca
livre por descrição de lançamento.

Referência: Issue #7 — Item 8, Assistente de gestão com IA.

## Capabilities

### New Capabilities
- `assistant`: assistente de IA em chat sobre os gastos por categoria do próprio usuário — tela protegida
  por login, conversa só na sessão, consulta isolada por usuário, escopo fechado com recusa e ajuda fixas,
  resposta ancorada nos dados da ferramenta, créditos diários em tokens, falha amigável, aviso fixo e
  provedor configurável por ambiente.

### Modified Capabilities
<!-- Nenhuma: a regra de segredos por variável de ambiente (`project-configuration`) já cobre a chave do
     provedor, e o item de menu é detalhe de implementação da nova tela. -->

## Impact

- Código novo: app `assistant/` (model de uso, serviço de tool-calling, ferramenta, view, urls, testes),
  template `templates/assistant/`, entrada em `INSTALLED_APPS` e em `config/urls.py`, item na
  `templates/partials/sidebar.html`. Reaproveita `transactions.dashboard.category_slices` e
  `transactions.periods`.
- Banco: uma tabela nova (`assistant_usage`); nenhuma tabela existente muda. A conversa mora em
  `django_session`, sem tabela própria.
- Dependência nova: o SDK `openai` (`pyproject.toml` e `uv.lock`, via `uv`); o `docker compose up --build`
  é necessário na primeira vez.
- Variáveis de ambiente novas no `.env.example`: chave, `base_url` e modelo do provedor, e o teto diário
  de tokens por usuário. A chave não tem valor padrão.
- Serviço externo: Groq, plano gratuito (Developer), `openai/gpt-oss-120b` com 8 mil tokens por minuto e
  200 mil por dia por organização, compartilhados entre todos os usuários da chave. Dados enviados ao
  provedor são só os agregados do próprio usuário autenticado; não usar dados financeiros reais em testes.
- Arquivos novos fora do código: `design/assistant.figcraft`. O design depende de ferramenta fora do
  repositório (FigCraft, MCP, Outfit instalada), como nas Issues #53 e #55.
- Cobertura: o piso `fail_under` do `pyproject.toml` não pode cair.
