# Tasks

## 1. Dependência e esqueleto do front

- [x] 1.1 Adicionar `chart.js` (4.x, MIT) ao `package.json`/`package-lock.json` e fazer `scripts/copy-alpine.mjs` copiar `chart.umd.min.js` para `static/dist/js/`; verificar com `docker compose run --rm css npm run build` e a existência do arquivo em `static/dist/js/`
- [x] 1.2 Adicionar o bloco `extra_scripts` em `templates/base.html` e verificar que as demais telas renderizam igual (`docker compose exec web pytest` passando)

## 2. Agregação no servidor (`transactions/dashboard.py`)

- [x] 2.1 Implementar a janela de 6 meses a partir de `today`, preenchendo meses sem lançamentos, e verificar com testes em janeiro, dezembro e meses vazios
- [x] 2.2 Implementar totais do mês e do anterior, variação percentual (`None` sem base) e taxa de economia (`None` sem entradas); verificar com testes de valores, variação de 50% e divisão por zero
- [x] 2.3 Implementar gastos por categoria do mês (cor da categoria, 5 maiores + "Outras", percentual); verificar que a soma das fatias é igual ao total de despesas e bate com a listagem filtrada por categoria
- [x] 2.4 Implementar fluxo mensal e saldo ao fim de cada mês (saldo inicial da janela vindo dos lançamentos anteriores) e verificar com testes de acúmulo, lacunas e lançamento futuro
- [x] 2.5 Implementar os 5 últimos lançamentos (mesma ordem da listagem) e `build_dashboard(user, today)` reunindo tudo; verificar o isolamento com dois usuários (nada do outro aparece em nenhuma agregação)

## 3. Página do painel

- [x] 3.1 Trocar `HomeView` por uma view renderizada (`LoginRequiredMixin`, `today = timezone.localdate()`) e atualizar `core/tests/test_home.py` (não há mais redirecionamento; anônimo continua indo ao login); verificar com pytest
- [x] 3.2 Criar `templates/core/home.html` e parciais: cartão de saldo com mensagem de status, cartões de entradas/despesas/taxa de economia com variação, lista de últimos lançamentos; verificar com testes de saldo negativo (vermelho + "Você está no vermelho, cuidado"), zero (sem mensagem) e positivo, e de saldo igual ao da listagem
- [x] 3.3 Implementar os estados vazios (sem lançamentos; mês sem despesas) sem emitir `json_script` nem contêiner de gráfico; verificar com testes de resposta 200 e das mensagens
- [x] 3.4 Emitir os dados dos gráficos com `json_script` e verificar que um nome de categoria com `<script>` sai escapado
- [x] 3.5 Adicionar o item "Painel" como primeiro do menu em `templates/partials/sidebar.html`, com `aria-current="page"` no painel e sem ele nas outras telas; verificar com teste e ajustar `core/tests/test_sidebar_state.py` se necessário

## 4. Gráficos (Chart.js)

- [x] 4.1 Criar `static/js/dashboard-charts.js` com a rosca de gastos por categoria (cores das categorias, legenda em HTML escapado, "Outras"); verificar manualmente no navegador (valores = listagem)
- [x] 4.2 Acrescentar o gráfico de colunas de fluxo de caixa (entradas × despesas, 6 meses) e o de área de evolução do saldo; verificar manualmente com dados de vários meses, incluindo lacunas e saldo negativo
- [x] 4.3 Formatar tooltips/eixos em reais (`pt-BR`) e rótulos de mês em português; verificar manualmente
- [x] 4.4 Fazer os gráficos acompanharem o tema claro/escuro, inclusive ao alternar com a página aberta (`MutationObserver` na classe `dark` + `chart.update()`); verificar manualmente nos dois temas e em tela estreita (responsivo)
- [x] 4.5 Confirmar que o painel não requisita nenhum domínio externo e que sem o script a página ainda mostra saldo, cartões e lista (aba Rede / bloqueio do script)

## 5. Fechamento

- [x] 5.1 Rodar `docker compose exec web pytest --cov --cov-report=term-missing`, conferir que a cobertura não caiu abaixo do piso e, se subiu, elevar `fail_under` (truncando para baixo)
- [x] 5.2 Rodar `uvx pre-commit run --all-files` (Ruff, complexidade ≤ 10) sem erros
- [x] 5.3 Atualizar o README (painel e Chart.js no build do front) e criar a Issue nova para as Fases C e D (filtro de período e comparação entre meses), citando a #6 (Issue #47)
- [x] 5.4 Rodar `openspec validate --all` (sem `--strict`) e a verificação manual completa do painel com uma conta nova e uma com dados
