# Proposta: painel com saldo em destaque e telas sem breadcrumb

## Why

A crítica de design do painel (`/impeccable critique`, nota 27/40) achou dois problemas que falham
para qualquer público. O painel não responde "como estou este mês?" de relance: o saldo final é
um de cinco cartões do mesmo peso. E o gráfico de fluxo é ilegível no celular, o público principal
do produto, com até 62 barras em 390 px. Há ainda a navegação lenta entre meses (só setas de
36 px) e um breadcrumb do TailAdmin que repete o título e o menu lateral em todas as telas.

Esta change leva ao código a opção **B** do desenho em `design/dashboard.figcraft`, escolhida pelo
usuário entre duas propostas, e remove o breadcrumb de todo o sistema por decisão dele.

Origem: Issue #60.

## What Changes

- **Saldo final em destaque.** Um bloco jade largo mostra o saldo final, a mensagem de status, o
  saldo inicial e a linha do saldo do mês, com o ponto de menor saldo. Os cinco cartões iguais
  viram três indicadores: entradas, despesas e taxa de economia, esta com uma frase simples.
- **Fluxo de caixa por semana.** O gráfico ganha o seletor Dias | Semanas (no celular abre em
  Semanas) e um resumo em texto com a maior despesa do mês.
- **Saldo com o zero marcado.** O gráfico marca o zero e pinta de vermelho só o trecho negativo, e
  um resumo em texto informa o menor saldo do mês.
- **Navegação de mês.** Campo de seleção do mês, setas e atalho "Este mês" com 44 px de área de
  toque, e atalho "Novo lançamento" no painel.
- **Números tabulares** nos valores do painel, para os dígitos alinharem em coluna.
- **Sem breadcrumb.** O `partials/breadcrumb.html` deixa de existir (usado em 15 templates) e dá
  lugar a um cabeçalho de página só com o título, que passa a ser o `h1` da página.
- **Design versionado do painel.** A regra que proibia o design do painel (gráfico aproximado)
  é revertida: `design/dashboard.figcraft` entra só com a opção B, em desktop claro, desktop escuro
  e mobile claro. Os desenhos de lançamentos, categorias, metas e perfil perdem a trilha.

Fora do escopo:
- As quatro abas do painel e os "Ver detalhes" repetidos (achado P2 da crítica).
- Estender o bloco jade a outras telas, como o "Saldo atual" de lançamentos.
- Design das abas Categorias, Fluxo e saldo e Lançamentos, e do estado vazio do painel.
- Mudança de modelo, migração ou dependência nova.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `dashboard`: saldo final em destaque com a linha do mês, três indicadores no lugar de cinco
  cartões, fluxo por semana, saldo com zero marcado, resumos em texto, seleção de mês por campo e
  atalho para novo lançamento. Ajusta a seleção do mês e a explicação do cálculo.
- `frontend-layout`: toda página autenticada passa a ter um título como `h1`, sem breadcrumb.
  Ajusta o cenário que exigia o breadcrumb.
- `screen-design`: o painel passa a ter design versionado, com gráficos desenhados a partir de
  dados de exemplo e a aproximação registrada como divergência. Revoga o cenário "Painel fora do
  design".

## Impact

- Código: `transactions/dashboard.py` (agregação por semana, resumos em texto, menor saldo),
  `core/views.py` (lista de meses do seletor), `templates/core/` (bloco de saldo, indicadores,
  seletor, cabeçalho), `templates/partials/` (`breadcrumb.html` sai; entra o cabeçalho de página),
  os 15 templates que o incluíam, `static/js/dashboard-charts.js` (semanas, zero, trecho negativo,
  linha do mês) e `frontend/style.css` (tokens do bloco jade e dos gráficos, números tabulares).
- Testes: `transactions/tests/test_dashboard_pages.py` e `test_dashboard.py` precisam cobrir o que
  muda e ser reescritos onde cobriam cartões removidos.
- Design e docs: `design/dashboard.figcraft`, `design/transactions.figcraft`,
  `design/categories.figcraft`, `design/goals.figcraft`, `design/profile.figcraft` e o `AGENTS.md`
  (divergências conhecidas e a nota de que o painel não tem design).
