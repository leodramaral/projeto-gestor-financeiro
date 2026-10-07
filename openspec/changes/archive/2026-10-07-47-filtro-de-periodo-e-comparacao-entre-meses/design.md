# Design

## Context

- `build_dashboard(user, today)` (`transactions/dashboard.py`) calcula tudo e `core.HomeView` só
  chama e renderiza. Hoje o mês corrente é implícito: `_month_points` devolve a janela de 6 meses,
  os cartões usam `months[-1]`/`months[-2]` e `_category_slices` recorta `today.replace(day=1)`.
- O saldo atual vem de `current_balance(user)`; o Chart.js 4 já é servido localmente e
  `static/js/dashboard-charts.js` lê um `json_script` e só cria o gráfico cujo `<canvas>` existe.
- A listagem de lançamentos já filtra por querystring (`?category=`): filtro via `GET` é padrão do
  projeto. O painel é renderizado no servidor, sem SPA.
- O mockup aprovado (artefato "Painel por Abas") é a referência visual e de comportamento. Ele é
  ilustrativo em duas coisas: usa caminhos em português (`/painel/categorias/`) e mostra uma faixa
  de "verificações de consistência" no rodapé. Aqui, as rotas seguem o `AGENTS.md` (em inglês) e as
  verificações viram testes.
- Sem mudança de modelo, migração ou dependência. Convenção: código em inglês, texto de produto em
  pt-BR, Ruff com complexidade máxima 10, piso de cobertura que só sobe.

## Goals / Non-Goals

**Goals:**
- Um único conceito de período, o mês calendário, resolvido num só lugar e usado por todas as abas,
  de modo que os números fechem entre si.
- Cada aba calcula só o que mostra (uma rota por aba, sem endpoint JSON).

**Non-Goals:**
- Semana, período personalizado e comparação entre dois meses escolhidos.
- JavaScript de roteamento, HTMX, cache ou endpoint JSON.
- Filtro de mês na listagem de lançamentos.

## Decisions

**1. O mês é resolvido por `resolve_month(raw, today, first_month)`, em `transactions/periods.py`.**
Entrada: o valor cru de `?month=`, `today` (injetável, vindo de `timezone.localdate()`) e o primeiro
mês com lançamento do usuário (`earliest`, ou `today` sem lançamentos). Regras: ausente, mal
formado (`date.fromisoformat(f"{raw}-01")` falhando) ou inexistente → mês atual; acima do mês
atual → mês atual; abaixo de `earliest` → `earliest`. Devolve o mês e `has_prev`/`has_next` para
os controles. Reaproveita `shift_month`. Nunca levanta exceção nem devolve erro ao usuário (a
resposta é sempre `200`). *Alternativa:* um `forms.Form` — rejeitada: é um único campo opcional
com fallback silencioso.

**2. `Summary` (`build_summary`) como base de todas as abas.**
Dataclass com `month`, `opening`, `income`, `expense`, `final`, `savings_rate` e, para o mês
anterior, `income_change`/`expense_change` (`None` = "sem base"). Saldo inicial: uma `Sum`
condicional dos lançamentos com `date < início do mês` (`_net`). Totais do mês e do anterior: uma
`Sum` condicional por intervalo, duas consultas simples. Tudo em `Decimal`; `float` só ao
serializar para o gráfico. As cinco explicações dos cartões usam esses mesmos campos, então número
e texto não podem divergir.

**3. Agregações por aba, em funções puras sobre o ORM.**
- `daily_series(user, month, opening)`: uma consulta `values("date", "kind")` + `Sum` filtrada pelo
  mês; preenche os dias sem lançamento com zero e acumula o saldo em Python, partindo de `opening`.
  O último ponto é o saldo final por construção; um teste confirma contra `Summary`.
- `category_slices(user, month, top=None)`: a atual, parametrizada por mês; `top=5` na Visão geral
  (agrupa em "Outras") e `top=None` na aba Categorias.
- `month_transactions(user, month, limit=None)`: `limit=5` na Visão geral, sem limite na aba
  Lançamentos, na mesma ordem da listagem (`-date`, `-id`).
O mês exibido inclui dias futuros (decisão: o saldo final conta tudo do mês, e o gráfico vai até o
último dia). `_month_points`, `WINDOW_MONTHS` e `current_balance` no painel saem.

**4. Uma view por aba, sobre uma view-base que resolve o mês.**
`DashboardTabView` (`LoginRequiredMixin` + `TemplateView`) lê `request.GET["month"]`, chama `resolve_month`, monta o
`Summary` e injeta no contexto o mês, os links ‹ › e os links das abas, todos com `?month=`.
As quatro views (`HomeView`, categorias, fluxo, lançamentos) só acrescentam o que a aba mostra.
Rotas em inglês: `/` (`home`), `/dashboard/categories/`, `/dashboard/flow/` e
`/dashboard/transactions/`, em `core/urls.py`. O item "Painel" da barra lateral fica ativo quando
`resolver_match.url_name` é qualquer um dos quatro. Sem lançamentos, as quatro rotas mostram o
mesmo estado vazio atual, sem seletor nem abas. *Alternativa:* uma única view com `?tab=` —
rejeitada: cada aba calcularia tudo, e a rota própria é o que a spec pede.

**5. Navegação ‹ › e abas são links, sem JavaScript.**
Os controles de mês são `<a>` (ou `<span aria-disabled>` nos limites). As abas também, com
`aria-current="page"` na atual; o container usa `overflow-x: auto` **e** `overflow-y: hidden`, para
não criar rolagem vertical por arredondamento. Cada navegação é uma página nova; por isso não há
estado de aba no cliente.

**6. Cartões com "i" abertos por Alpine.js.**
O parcial `core/partials/cards.html` monta os cinco cartões e `info_button.html` desenha o botão:
`<button type="button">` com `aria-label`, `aria-describedby` apontando para o `role="tooltip"` e,
com o Alpine.js que o layout já carrega, abre em `mouseenter`, `focus` e `click` e fecha em
`mouseleave`, `blur`, `Esc` e clique fora. O texto vem do template com os valores do resumo
(fórmula com números reais). *Alternativas:* (a) `title` nativo — rejeitada: não aparece no
teclado nem no toque; (b) CSS puro com `group-hover`/`focus-within` — rejeitada: não cobre toque
nem Esc, e o Alpine já está no projeto.

**7. Gráficos por dia no mesmo `dashboard-charts.js`.**
O `json_script` passa a trazer `days` (rótulos), `income`, `expense`, `balance` e `categories`. O
script cria cada gráfico só se o `<canvas>` existe (Visão geral: os três; Fluxo: colunas e área;
Categorias: rosca). Rótulo do eixo a cada 5 dias; barras finas; ponto final do saldo destacado;
mesmo tema claro/escuro e mesmo formato de reais que hoje.

**8. Mensagem de status sobre o saldo final.**
As duas mensagens da #6 continuam, agora ligadas ao saldo final do mês exibido (e não ao saldo de
hoje): `Summary.status` (`negative`, `zero`, `positive`) decide o destaque vermelho e o texto.

**9. Decisão de produto registrada: sem semana, sem personalizado, sem comparação livre.**
A Issue #47 pedia semana e período personalizado; o painel mensal os dispensa, por decisão do
usuário, e nenhuma Issue nova é aberta para eles. O PR fecha a #47 com o escopo reduzido que esta
change descreve.

## Risks / Trade-offs

- [Mês errado na virada de mês/ano ou perto da meia-noite] → `today` injetável, `timezone.localdate()`
  na view e testes em janeiro, dezembro, 29/02 e primeiro/último dia do mês.
- [Número do cartão divergir do gráfico ou da categoria] → testes de consistência (a faixa do
  mockup): saldo inicial + entradas − despesas = saldo final = último ponto do saldo; soma das
  categorias = despesas; soma das colunas = cartões; saldo inicial de um mês = saldo final do
  anterior.
- [Altura da página mudar ao trocar de aba e piscar] → cada aba é uma página completa; se a
  piscada persistir na verificação visual, fixar `min-height` no contêiner do painel.
- [Muitas consultas por página] → Visão geral: ~7 consultas agregadas, todas por `user` e `date`,
  sem N+1 (categorias por `values`, lançamentos com `select_related("category")`).
- [Perda de funcionalidade da #6] → decisão explícita da spec (REMOVED com `Migration`); os testes
  dos requisitos removidos são trocados, não apagados sem substituto.
- [Complexidade ciclomática do Ruff (10)] → uma função por agregação; `resolve_month` curta.

## Migration Plan

Sem migração nem mudança de dados. `docker compose up --build` já recompila o CSS. Reverter é
voltar o commit: o painel volta à janela de 6 meses.
