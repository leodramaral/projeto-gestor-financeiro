# Tasks

## 1. Cabeçalho de página no lugar do breadcrumb

- [x] 1.1 Criar `templates/partials/page_title.html` (parâmetro `title`, `h1` com o estilo do título atual) e remover `partials/breadcrumb.html`; verificar que `grep -r breadcrumb templates` não acha nada
- [x] 1.2 Trocar o `include` nos 15 templates (`dashboard_base`, lançamentos, categorias, metas, perfil e as telas de novo, editar, excluir e registrar progresso); verificar que cada tela renderiza com `200` no teste de acesso existente
- [x] 1.3 Escrever testes de que cada tela autenticada tem exatamente um `h1` com o nome dela e nenhum "Trilha de navegação", e de que o título do modal de lançamento não é `h1`; verificar que passam e falhavam antes da troca
- [x] 1.4 Ajustar os testes que dependiam do `h2` ou da trilha, se houver; verificar `docker compose exec web pytest` sem falha nas apps `core`, `transactions`, `goals` e `accounts`

## 2. Cálculo no servidor

- [x] 2.1 Em `transactions/dashboard.py`, somar entradas e despesas em blocos de 7 dias (o último com os dias restantes) e incluir `weeks` no JSON dos gráficos; verificar com teste de unidade em mês de 28, 30 e 31 dias e com o teste de que a soma dos blocos é igual aos totais do mês
- [x] 2.2 Calcular a maior despesa do mês (empate pelo mais recente) e o menor saldo ao fim de um dia (empate pelo dia mais cedo), com o caso de mês sem lançamentos; verificar com testes de unidade dos cenários "Maior despesa", "Mês sem despesas", "Menor saldo negativo" e "Mês sem lançamentos"
- [x] 2.3 Calcular a frase da taxa de economia nos três casos (positiva, negativa, sem entradas); verificar com os três cenários da spec
- [x] 2.4 Expor no contexto da Visão geral o menor saldo, o saldo final e se houve saldo negativo, para o bloco de destaque; verificar no teste da página que os valores batem com os dos cartões

## 3. Seleção do mês e atalho

- [x] 3.1 Em `core/views.py`, montar a lista de meses do primeiro lançamento até o mês atual e o indicador de "mês atual"; verificar com teste de que a lista tem os meses certos e só eles
- [x] 3.2 No `dashboard_base.html`, trocar o intervalo de datas solto por `<select>` de meses (envio automático e `<noscript>` com botão), manter as setas, mostrar "Este mês" só fora do mês atual e dar 44 px aos controles; verificar com testes dos cenários "Escolher o mês no campo" e "Atalho para o mês atual" e com a regressão dos cenários de limite e de mês inválido
- [x] 3.3 Acrescentar o atalho "Novo lançamento" junto do seletor, só quando há lançamentos; verificar com teste de que o link aparece nas quatro abas e não aparece no estado vazio

## 4. Bloco de destaque e indicadores

- [x] 4.1 Criar o bloco de destaque na Visão geral (saldo final, mensagem de status, "Começou o mês com…" com o "i" do saldo inicial, canvas da linha); verificar com os testes de status do saldo (negativo, zero, positivo, mês navegado) adaptados ao novo bloco
- [x] 4.2 Reduzir os cartões a três indicadores (entradas, despesas, taxa de economia com a frase), mantendo variação, "sem base" e os controles "i"; verificar com os testes de cartões e de explicação existentes, reescritos onde cobriam os cartões removidos
- [x] 4.3 Garantir que o bloco mostra saldo final, mensagem e saldo inicial sem o script; verificar com teste que não carrega o JS e inspeciona o HTML
- [x] 4.4 Colocar as frases de maior despesa e de menor saldo sob os gráficos de fluxo e de saldo, também na aba Fluxo e saldo; verificar com os cenários de resumo em texto, incluindo a descrição com `<b>` escapada

## 5. Gráficos

- [x] 5.1 Em `static/js/dashboard-charts.js`, acrescentar o seletor Dias | Semanas ao fluxo de caixa, com abertura em "Semanas" abaixo de 640 px e a visão preservada ao trocar o tema; verificar no navegador em 390 px e em 1440 px
- [x] 5.2 No gráfico de saldo, tirar a suavização, marcar o zero e pintar de vermelho o trecho negativo; verificar no navegador com um mês de saldo que fica negativo e termina positivo
- [x] 5.3 Desenhar a linha do bloco de destaque (`chart-hero`) com o ponto de menor saldo quando houver saldo negativo e o texto alternativo; verificar no navegador nos temas claro e escuro, em 390 px e em 1440 px
- [x] 5.4 Conferir que sem o Chart.js a página continua com saldo, indicadores e frases, e que nenhum script é pedido a domínio externo; verificar com os testes existentes de "Sem CDN" e de página sem gráfico

## 6. Estilo

- [x] 6.1 Em `frontend/style.css`, acrescentar os tokens do bloco jade nos dois temas e das cores novas dos gráficos, e recompilar com `docker compose run --rm css npm run build`; verificar contraste mínimo de 4,5:1 do texto sobre o bloco jade em claro e escuro
- [x] 6.2 Confirmar que o `woff2` servido preservou o `tnum` e aplicar `tabular-nums` aos valores do painel; verificar o recurso no arquivo servido (fonttools) e o alinhamento dos dígitos nas listas no navegador

## 7. Design e documentação

- [x] 7.1 Reduzir `design/dashboard.figcraft` à opção B com frames `dashboard · <viewport> · <tema> · padrão`, ajustando o que diverge do código (o "i" do saldo inicial, a frase da taxa, o texto do menor saldo igual nos dois tamanhos); verificar abrindo o arquivo e conferindo os nomes dos frames
- [x] 7.2 Desenhar o desktop escuro da Visão geral com os tokens escuros do CSS; verificar contra a captura do app em tema escuro
- [x] 7.3 Tirar a trilha dos desenhos de `transactions`, `categories`, `goals` e `profile` e trocar o título pelo `h1`; verificar abrindo cada arquivo e exportando um PNG por tela
- [x] 7.4 Atualizar o `AGENTS.md`: remover "o painel não tem design, por causa dos gráficos" e registrar as divergências conhecidas do desenho do painel (D11); verificar com `grep -n painel AGENTS.md`
- [x] 7.5 Desenhar o estado de saldo negativo do bloco de destaque (fundo claro com valor vermelho, D12) e o "Ver detalhes" no rodapé do cartão de fluxo (D13); verificar contra o app com um mês de saldo negativo
- [x] 7.6 Conferir que a soma das colunas e o último ponto do saldo do desenho batem com os indicadores; verificar somando os dados de exemplo

## 8. Verificação final

- [x] 8.1 Rodar `docker compose exec web pytest --cov --cov-report=term-missing` e verificar que passa sem baixar o `fail_under`
- [x] 8.2 Rodar `uvx pre-commit run --all-files` e verificar que passa, inclusive a complexidade máxima 10
- [x] 8.3 Rodar `openspec validate --all` (sem `--strict`) e verificar que passa
- [x] 8.4 Percorrer o painel no navegador em 390 px e em 1440 px, claro e escuro, em um mês com saldo negativo no meio, em um mês sem lançamentos e na conta nova; verificar que nada quebra e que o saldo final é o primeiro número que se vê
- [x] 8.5 Comparar os frames do `design/dashboard.figcraft` com o app renderizado e registrar qualquer diferença nova no `AGENTS.md`
