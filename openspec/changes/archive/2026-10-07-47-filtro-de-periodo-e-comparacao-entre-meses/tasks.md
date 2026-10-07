# Tasks

## 1. Mês e resumo

- [x] 1.1 Criar `resolve_month(raw, today, first_month)` em `transactions/periods.py` devolvendo o mês e `has_prev`/`has_next`; verificar com testes parametrizados: ausente, `abc`, `2026-13`, vazio, futuro (ajusta ao atual), anterior ao primeiro lançamento (ajusta ao primeiro), janeiro/dezembro e 29/02
- [x] 1.2 Criar `Summary` (`build_summary`) (saldo inicial, entradas, despesas, saldo final, taxa de economia, variações contra o mês anterior com `None` = "sem base"); verificar com testes de saldo inicial só com lançamentos anteriores, mês sem entradas (taxa `None`), mês anterior zerado e encadeamento (saldo inicial de um mês = saldo final do anterior)

## 2. Agregações

- [x] 2.1 Implementar `daily_series(user, month, opening)` com todos os dias do mês (inclusive futuros), dias vazios em zero e saldo acumulado; verificar com testes de mês com lacunas, 28/29/30/31 dias e último ponto = saldo final
- [x] 2.2 Parametrizar `category_slices` por mês e por `top` (5 + "Outras" na Visão geral, todas na aba Categorias); verificar com testes de soma das fatias = despesas do mês, mais de 5 categorias e mês sem despesas
- [x] 2.3 Implementar `month_transactions(user, month, limit)` na ordem da listagem; verificar com testes de limite 5, sem limite e mês vazio
- [x] 2.4 Remover `_month_points`, `WINDOW_MONTHS` e o cálculo fixo no mês corrente; verificar que nenhum import quebrado resta (`pytest` coleta tudo)
- [x] 2.5 Isolamento por usuário em todas as agregações; verificar com teste de dois usuários nos mesmos meses (totais, categorias, dias e lista só do usuário logado)

## 3. Views e rotas

- [x] 3.1 Criar `DashboardTabView` (login obrigatório, resolve o mês, injeta resumo e links de ‹ ›, de abas e de atalhos com `?month=`); verificar com testes de view: `200` sem e com `month`, `month` inválido, limites e redirecionamento do visitante anônimo
- [x] 3.2 Criar as views das quatro abas (`OverviewView`, `CategoriesView`, `FlowView`, `TransactionsTabView`) e as rotas `/`, `/dashboard/categories/`, `/dashboard/flow/` e `/dashboard/transactions/` em `core/urls.py`; verificar que cada rota responde `200` e que as quatro mostram o estado vazio sem seletor nem abas quando o usuário não tem lançamentos
- [x] 3.3 Marcar "Painel" ativo na barra lateral em qualquer aba; verificar com teste em `core/tests/test_sidebar_state.py` para as quatro rotas

## 4. Telas

- [x] 4.1 Criar o seletor de mês (‹ rótulo por extenso + intervalo ›, desativado nos limites) e a barra de abas (`aria-current`, `overflow-x: auto` e `overflow-y: hidden`) em parciais; verificar com teste de HTML (rótulo em português, links com `month`, controle desativado nos limites)
- [x] 4.2 Criar os parciais dos cartões e do botão "i" acessível (`button`, `aria-label`, `aria-describedby`, `role="tooltip"`, abertura por ponteiro, foco, clique e Esc via Alpine.js), com a fórmula e os valores reais do mês; verificar com teste de HTML que as cinco explicações existem, trazem os números do mês e o texto de "taxa indisponível" sem entradas
- [x] 4.3 Montar o template da Visão geral (cartões, fluxo, saldo, categorias e 5 lançamentos, cada bloco com "Ver detalhes") e os das abas Categorias, Fluxo e saldo e Lançamentos (tabela do mês + link para a listagem completa); verificar com testes de HTML por aba, incluindo mês sem lançamentos e sem despesas (mensagem no lugar do gráfico)
- [x] 4.4 Ligar as mensagens de status ao saldo final do mês exibido (vermelho e "no vermelho, cuidado" se negativo; "no verde" se positivo; nada se zero); verificar com teste de saldo negativo, zero, positivo e que a mensagem acompanha o mês navegado
- [x] 4.5 Recompilar o CSS (`docker compose run --rm css npm run build`) para as classes novas

## 5. Gráficos

- [x] 5.1 Adaptar `static/js/dashboard-charts.js` e o `json_script` aos dados diários (`days`, `income`, `expense`, `balance`, `categories`), criando cada gráfico só se o `<canvas>` existe; verificar com teste que o JSON embutido bate com o cálculo do servidor
- [x] 5.2 Verificação visual no navegador, nos temas claro e escuro e em tela estreita: seletor, abas sem rolagem vertical, ⓘ por mouse e por teclado, gráficos diários, troca entre abas sem piscar e sem rolagem horizontal da página

## 6. Fechamento

- [x] 6.1 Reescrever os testes de `transactions/tests/test_dashboard.py` e `core/tests/test_home.py` que cobriam os requisitos removidos (6 meses e saldo atual solto); verificar que a cobertura não cai e que cada requisito novo da spec tem teste
- [x] 6.2 Escrever os testes de consistência da faixa do mockup: saldo inicial + entradas − despesas = saldo final = último ponto do saldo; soma das categorias = despesas; soma das colunas = cartões; mesmo conjunto de lançamentos em todas as abas
- [x] 6.3 Rodar `docker compose exec web pytest --cov --cov-report=term-missing` (acima do `fail_under`), `uvx pre-commit run --all-files` e `openspec validate --all`, sem erros
