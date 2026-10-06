# Proposal

## Why

Hoje `/` só redireciona para a listagem de lançamentos: o usuário precisa ler linha a linha para
saber como está financeiramente. A Issue #6 (Item 5 — Painel com gráficos) pede uma visão rápida
de para onde o dinheiro está indo, e herda da Issue #4 (cancelada) o resumo de status do saldo. Os
dados já existem (lançamentos da #3, categorias da #5); falta agregá-los e mostrá-los.

## What Changes

- `/` deixa de redirecionar e passa a ser o **Painel**, inspirado na demo Finance do TailAdmin
  (https://demo.tailadmin.com/finance): cartões de resumo, gráficos (Chart.js) e uma lista dos
  últimos lançamentos.
- **Cartão de saldo atual** com mensagem de status: saldo < 0 em vermelho ("Você está no vermelho,
  cuidado"); saldo > 0 com mensagem motivacional ("Você está no verde. Continue assim!") e saldo zero sem mensagem (critério herdado da #4, refinado).
- **Cartões do mês atual**: entradas, despesas e taxa de economia (entradas − despesas sobre
  entradas), cada um com a variação em relação ao mês anterior.
- **Gráfico de rosca "Gastos por categoria"** no mês atual (Fase A), com a cor de cada categoria
  e a lista de valores/percentuais ao lado.
- **Gráfico de colunas "Fluxo de caixa"**: entradas × despesas dos últimos 6 meses.
- **Gráfico de área "Evolução do saldo"**: saldo ao fim de cada um dos últimos 6 meses (Fase B).
- **Lista "Últimos lançamentos"** (5 mais recentes) com link para a listagem completa.
- **Estado vazio**: sem lançamentos, o painel mostra mensagem e atalho para o primeiro lançamento,
  em vez de gráficos vazios; mês sem despesas mostra mensagem no cartão da rosca.
- Item "Painel" na barra lateral (primeiro do menu); tema escuro nos gráficos.
- Chart.js 4 (MIT) passa a ser dependência do front (npm), servido localmente em `static/dist/js/`
  como o Alpine.js (sem CDN). A Issue sugeria ApexCharts, mas a licença dele deixou de ser MIT a
  partir da 5.1.0 (jul/2025); o projeto é aberto e a escolha foi por biblioteca 100% open source. Os dados chegam do servidor embutidos na página (`json_script`).
- Todas as agregações são feitas no servidor e só com os lançamentos do usuário logado.

**Fora do escopo** (viram Issue nova, conforme a própria #6): Fase C (filtro de período: semana,
mês, personalizado) e Fase D (comparação detalhada entre meses). Também ficam de fora, por não
terem domínio no projeto: cartões de crédito, "Quick Send", moedas e metas de economia da demo.
Sem endpoint JSON, sem HTMX e sem alteração de modelo ou migração.

## Capabilities

### New Capabilities
- `dashboard`: painel inicial com resumo de saldo e status, cartões do mês, gráficos (gastos por
  categoria, fluxo de caixa, evolução do saldo), últimos lançamentos e estados vazios, sempre
  restrito ao usuário logado.

### Modified Capabilities
- `frontend-layout`: `/` deixa de ser a página de exemplo "Olá, mundo" e passa a servir o painel
  dentro do layout TailAdmin; o cenário de conteúdo de exemplo é removido.

## Impact

- Código: `core/views.py` (`HomeView` vira página renderizada), novo módulo de agregação em
  `transactions/` (consultas por usuário), `templates/core/home.html` e parciais do painel,
  `templates/partials/sidebar.html`, novo `static/js/dashboard-charts.js`.
- Dependências: `chart.js` em `package.json`/`package-lock.json`; `scripts/copy-alpine.mjs`
  também copia o Chart.js para `static/dist/js/`.
- Testes: ajuste de `core/tests/test_home.py` (o redirecionamento deixa de existir) e testes novos
  de agregação, isolamento, estados vazios, status do saldo e renderização.
- Documentação: README (seção do painel/front), se citar a página inicial.
- Sem mudança de banco, de rotas além do comportamento de `/`, nem de configuração.
