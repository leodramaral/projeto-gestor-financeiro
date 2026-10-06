# Design

## Context

- `/` é `core.views.HomeView`, um `RedirectView` para `transactions:list`. O saldo já existe em
  `transactions.models.current_balance(user)`; a listagem o exibe num cartão.
- `Transaction` (valor sempre positivo, `kind` income/expense, `date`, FK `category` nula só para
  entradas) e `Category` (cor por chave em `transactions/appearance.py`, com hex claro e escuro)
  bastam: **não há mudança de modelo nem migração**.
- Front: Tailwind compilado + Alpine.js copiado de `node_modules` para `static/dist/js/` por
  `scripts/copy-alpine.mjs`, tudo dentro do serviço `css` do Compose. Sem CDN, sem SPA. O tema é
  controlado por `darkMode` no `<body>` e `setTheme` em `partials/theme_init.html`.
- Nenhuma biblioteca de gráficos está no repositório (só o layout do TailAdmin foi trazido). A Issue
  sugeria ApexCharts, mas ele só é MIT até a 5.0.0; da 5.1.0 em diante (incluindo a 7.x atual) a
  licença é própria (Community < US$ 2 mi, OEM para terceiros). Como o projeto é público e deve ser
  100% open source, a biblioteca é outra.
- Convenção do projeto: código em inglês, texto de produto em pt-BR, cobertura com piso que só sobe.

## Goals / Non-Goals

**Goals:**
- Painel fiel à linguagem visual da demo Finance do TailAdmin (cartões de métrica, cartão de
  gráfico de rosca, colunas, área), reaproveitando as classes do tema já compilado.
- Agregação correta, testável sem navegador e isolada por usuário.

**Non-Goals:**
- Filtro de período e comparação entre meses (Fases C e D da #6) → Issue nova.
- Endpoint JSON, HTMX/atualização parcial, cache, ou qualquer mudança de modelo.
- Widgets da demo sem domínio aqui (cartões, Quick Send, moedas).

## Decisions

**1. Agregação em `transactions/dashboard.py`, funções puras sobre o ORM.**
`build_dashboard(user, today)` devolve um dataclass com: saldo, totais do mês e do anterior,
gastos por categoria, 6 meses de fluxo e saldo, e últimos 5 lançamentos. `today` é parâmetro
(a view passa `timezone.localdate()`), o que torna os testes determinísticos. Fica em
`transactions/` (dono de `Transaction`), e `core.HomeView` só chama e renderiza. *Alternativa:*
colocar tudo na view — rejeitada: a lógica ficaria presa a requisição e ao limite de complexidade
10 do Ruff.

**2. Poucas consultas, agregadas no banco.**
- Fluxo de 6 meses: uma consulta com `TruncMonth("date")` + `values("month","kind")` + `Sum`,
  filtrada por `user` e `date` entre o 1º dia da janela e o último dia do mês corrente.
- Saldo inicial da janela: uma `Sum` com filtro por tipo para `date < início da janela`; o saldo de
  cada mês é esse valor mais o acumulado (entradas − despesas) mês a mês, em Python.
- Rosca: `filter(kind=expense, date no mês)` + `values("category")` + `Sum`, juntando nome e cor da
  categoria; ordenado por valor decrescente. Totais do mês e do anterior saem do fluxo (a janela já
  contém o mês anterior). Variação = (atual − anterior) / anterior; `None` se anterior é zero.
- Saldo atual: reutiliza `current_balance` (uma fonte de verdade — o teste compara com a listagem).
Valores ficam em `Decimal` até a borda; só ao serializar para o gráfico viram `float` com duas casas.

**3. Meses da janela calculados por aritmética de (ano, mês), preenchendo lacunas.**
Uma lista de 6 `date` (dia 1) gerada a partir de `today`; o resultado do banco é indexado por mês e
os ausentes entram com zero. *Alternativa:* `generate_series` do Postgres — rejeitada por prender o
código a SQL específico sem ganho.

**4. Lançamentos futuros.** Os gráficos cortam no fim do mês corrente; o saldo do último ponto é o
saldo "até o fim do mês corrente". O cartão de saldo usa `current_balance` (todos os lançamentos,
como a listagem), então os dois só divergem se houver lançamento datado depois do mês corrente.
Registrado como comportamento aceito e coberto por teste.

**5. Chart.js 4 local, igual ao Alpine.** Dependência `chart.js` (MIT) no `package.json`;
`copy-alpine.mjs` passa a copiar também `node_modules/chart.js/dist/chart.umd.min.js` para
`static/dist/js/chart.umd.min.js` (~208 KB; o comentário do script é atualizado). O build já roda no
`docker compose up`, e `static/dist/` continua fora do Git.
*Alternativas:* (a) ApexCharts — visual idêntico ao TailAdmin, mas licença própria desde a 5.1.0; a
5.0.0 (MIT) está congelada desde jul/2025 e ficaria sem correções; (b) Apache ECharts 6 — Apache-2.0,
porém ~1,1 MB para três gráficos; (c) CDN — rejeitada (o projeto serve tudo localmente).
O visual da demo Finance (rosca fina, colunas arredondadas, área com gradiente, grade discreta,
fonte do tema) é reproduzido por configuração: `cutout`, `borderRadius`, `fill`/gradiente via
`scriptable options`, `grid`/`ticks` e legenda própria em HTML.

**6. Dados via `json_script`; um único `static/js/dashboard-charts.js`.**
O template emite `{{ chart_data|json_script:"dashboard-data" }}` (escapa `<`/`>`/`&`, então nomes de
categoria digitados pelo usuário não quebram o HTML) e o script lê esse JSON, cria os três gráficos
e só roda se o elemento existir. Carregado com `defer` apenas na página do painel (bloco
`extra_scripts` novo em `base.html`), depois de `chart.umd.min.js`. Configuração visual segue a
demo: rosca com legenda própria em HTML, colunas arredondadas, área com gradiente, fonte e cores
do tema (brand `#0f766e` para entradas/saldo, `error` para despesas, cor de cada categoria vinda
de `appearance.py`, na variante clara ou escura). *Alternativa:* endpoint JSON + fetch — rejeitada:
mais uma rota, mais superfície de segurança e o "reflexo imediato" já vem de graça no servidor.

**6b. Regras do Chart.js 4 a seguir.** `new Chart(canvas, {type, data:{labels, datasets}, options})`;
rosca: `type: "doughnut"` com um dataset (`data` + `backgroundColor` por fatia); colunas: `type: "bar"`
com dois datasets; área: `type: "line"` com `fill: true`. Cada gráfico fica num `<canvas>` com
contêiner de altura fixa e `maintainAspectRatio: false`. Para recriar, `chart.destroy()` antes; para
mudar tema, alterar as cores nas opções e chamar `chart.update()`. Tooltips usam `callbacks.label`
devolvendo string. A versão fixada no `package-lock.json` é a 4.x.

**7. Tema escuro.** O script lê `document.documentElement.classList.contains("dark")` para escolher
a paleta e observa a mudança da classe `dark` com um `MutationObserver`, atualizando as cores das opções e
chamando `chart.update()` em cada gráfico. Isso evita acoplar ao `setTheme` existente.

**8. Formatação em reais no cliente.** Tooltips e eixos usam `Intl.NumberFormat("pt-BR",
{style:"currency", currency:"BRL"})`; meses por rótulo curto em pt-BR (`jan`, `fev`…) montado no
servidor com `django.utils.dates.MONTHS_3` já em português (o projeto usa `pt-br`), para não depender
do locale do navegador. Os valores da lista, dos cartões e do saldo são renderizados no servidor
com `floatformat:"2g"`, como a listagem.

**9. Estados vazios decididos no servidor.** `has_transactions` (qualquer lançamento do usuário) e
`has_expenses_this_month` controlam o que é renderizado; sem dados, o HTML nem inclui o
`<div>` do gráfico nem o `json_script`, e o JS sai cedo. Os fluxos de 6 meses só aparecem quando há
algum lançamento.

**10. Navegação.** Item "Painel" (ícone de grade do TailAdmin) vira o primeiro do menu, ativo quando
`request.resolver_match.url_name == "home"`. Após criar/editar/excluir lançamento o fluxo
existente continua voltando à listagem; o painel não guarda estado, então reflete tudo ao abrir.

## Risks / Trade-offs

- [Janela de meses errada na virada de mês/ano ou fuso] → `today` injetável + testes em janeiro,
  dezembro, dia 31 e meses sem lançamentos; `timezone.localdate()` na view.
- [Soma de `float` no gráfico divergir da listagem] → somar sempre em `Decimal` no servidor; só
  converter na serialização; teste compara com a soma da listagem filtrada.
- [Nome de categoria malicioso no gráfico/legenda] → `json_script` para dados; a legenda é HTML
  renderizado pelo template (autoescape), nunca montada com `innerHTML` no JS.
- [Peso do Chart.js: ~208 KB minificado] → só carregado na página do painel, com `defer`.
- [Aparência menos pronta que a do ApexCharts] → opções de estilo explícitas (rosca fina, colunas arredondadas, área com gradiente) e verificação visual contra a demo Finance no tema claro e no escuro.
- [Cobertura: o JS não entra no pytest] → a lógica fica no servidor (testada); o JS é verificado
  manualmente e por checagem de que o HTML traz o JSON esperado.
- [Fatias demais na rosca] → mostrar as 5 maiores categorias e agrupar o resto em "Outras" na
  lista e no gráfico, como a demo faz com "Others".

## Migration Plan

Sem migração de dados. Basta `docker compose up --build` (o serviço `css` baixa o Chart.js e o
copia). Reverter é voltar o commit: `/` volta a redirecionar para a listagem.

## Open Questions

- Nenhuma que bloqueie. A mensagem motivacional exata do saldo positivo é texto de produto e pode ser
  ajustada na revisão sem mudar spec, abordagem ou tasks.
