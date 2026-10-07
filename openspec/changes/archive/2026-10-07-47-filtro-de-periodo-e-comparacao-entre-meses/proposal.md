# Proposta: painel mensal com abas

## Why

O painel entregue na #6 só olha para o mês corrente, mistura janelas diferentes (cartões do mês,
gráficos de 6 meses, saldo de hoje) e não deixa ver o mês passado. Filtrar só parte dele geraria
números que não fecham entre si. Esta change torna o painel inteiro **mensal**: um seletor de mês
vale para a página toda, e a página se divide em abas que detalham cada segmento.

Origem: Issue #47 (continuação da #6). A #47 também pedia filtro por semana e por período
personalizado, que saem desta change por decisão de produto: o painel é mensal e esses dois
filtros não serão feitos.

## What Changes

- **Seletor de mês** no topo do painel, com navegação ‹ › entre meses. O padrão é o mês atual, e o
  mês escolhido fica na URL (`?month=AAAA-MM`).
- **Tudo é do mês escolhido**: cartões, gráficos, categorias e lançamentos. Acabam as janelas fixas
  de 6 meses e o "saldo atual" solto.
- **Saldo por mês**: saldo inicial (tudo antes do mês), entradas, despesas, saldo final (inicial +
  entradas − despesas) e taxa de economia. As entradas e as despesas mostram a variação contra o
  mês anterior.
- **Cartões com explicação**: cada cartão tem um "i" que mostra como o número é calculado, com os
  valores do mês (ponteiro, foco do teclado ou toque; Esc fecha).
- **Quatro abas**, cada uma com rota própria e o mesmo mês na URL:
  - **Visão geral** (a rota `/`): cartões, fluxo de caixa e evolução do saldo por dia, gastos por
    categoria e últimos lançamentos, cada bloco com "Ver detalhes" para a aba do segmento;
  - **Categorias**: rosca e tabela completa de despesas por categoria;
  - **Fluxo e saldo**: entradas, despesas e saldo dia a dia;
  - **Lançamentos**: todos os lançamentos do mês, com link para a listagem completa.
- **Removido**: os gráficos de 6 meses, os cartões "do mês atual" fixos e o saldo atual solto. As
  mensagens de status ("Você está no vermelho…" e "no verde…") continuam, agora sobre o saldo final
  do mês exibido.

Fora do escopo:
- Filtro por semana e por período personalizado (descartados por decisão de produto).
- Comparação entre dois meses escolhidos: o painel só compara com o mês anterior, nos cartões.
- Filtro de mês na listagem de lançamentos, exportação, mudança de modelo ou migração, e
  dependências novas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `dashboard`: o painel passa a ser mensal, com seletor de mês, saldo inicial e final, cartões com
  explicação do cálculo e quatro abas. Substitui os requisitos de saldo atual, cartões do mês
  atual e fluxo de 6 meses, e ajusta os de página inicial, categorias e últimos lançamentos.

## Impact

- Código: `transactions/dashboard.py` (agregação por mês, em vez da janela de 6 meses),
  `transactions/periods.py` (resolução do mês), `core/views.py` e `core/urls.py` (uma view por
  aba, sobre uma view-base que resolve o mês),
  templates em `templates/core/` (abas, seletor, cartões com ⓘ), `static/js/dashboard-charts.js`
  (gráficos por dia) e os testes do painel, que precisam ser reescritos onde cobriam os requisitos
  removidos.
- O item "Painel" da barra lateral continua ativo em qualquer aba.
- Sem mudança de modelo, migração ou dependência nova. O Chart.js já está no projeto.
