# Tasks

## 1. Mensagens de erro das ferramentas

- [x] 1.1 Reescrever em `assistant/tools.py` as mensagens de erro conforme a tabela do `design.md` (exemplo de formato, último mês consultável, argumentos aceitos, ferramentas disponíveis); verificar com `docker compose exec web pytest assistant/tests/test_tools.py`
- [x] 1.2 Reforçar `assistant/tests/test_tools.py`: cada erro confere a parte orientadora (`2026-08` no formato, o mês atual em `YYYY-MM` no futuro e no piso, `month` na lista de argumentos aceitos, os dois nomes de ferramenta na desconhecida), e não só `"error" in …`; verificar com o mesmo comando
- [x] 1.3 Criar `PeriodError` (subclasse de `ToolError`) para mês futuro e anterior ao piso, e `ToolOutcome.period` verdadeiro nesses casos, sem consulta ao banco; verificar com testes em `test_tools.py` (`django_assert_num_queries(0)`)

## 2. Fatos declarados pela ferramenta

- [x] 2.1 Criar `Term` e `Facts` (valores, percentuais e nomes) em `assistant/facts.py` e acrescentar `ToolOutcome.facts` ao lado de `data`, montado a partir do resultado de gastos sem mudar o JSON devolvido ao modelo; verificar com testes que conferem os termos para um mês com 2 categorias, com "Outras" (mais de 20 categorias) e sem despesas
- [x] 2.2 Ajustar `assistant/service.py` para guardar os `Facts` das consultas bem-sucedidas da pergunta no lugar dos dicionários; verificar com `docker compose exec web pytest assistant/tests/test_service.py`

## 3. Guard

- [x] 3.1 Reescrever `assistant/guard.py` para receber `Facts` (sem ler `total` nem `categories`), mantendo `NO_QUERY`, `TOO_LONG`, a regra da escala e a retirada dos nomes antes de ler os números; verificar com os testes existentes de `test_guard.py` adaptados aos fatos
- [x] 3.2 Aceitar valor em reais que seja soma de 2 ou 3 termos distintos ou diferença de 2, com os termos à vista (valor ou nome no texto; "total" para o total); verificar com testes: soma de 2, soma de 3, diferença, conta que não confere, termos fora de vista, nome em outra caixa e a mesma coincidência de valores com 20 categorias
- [x] 3.3 Conferir percentuais (`55%`, `55 %`, `55,5%`): citado, soma de 2 ou 3 percentuais à vista com 1 ponto de tolerância por termo, ou razão entre dois valores à vista a até 1 ponto; verificar com testes para os três caminhos, para `80%` rejeitado e para um nome de categoria com `%` que não conta
- [x] 3.4 Cobrir o guard com um resultado de **outro formato de fatos** (termos inventados no teste), provando que ele não depende de `total` nem de `categories`; verificar com `pytest assistant/tests/test_guard.py`

## 4. Serviço: período sem dados

- [x] 4.1 Acrescentar `messages.period_unavailable(label)` com o texto do `design.md`, usando o rótulo do mês atual; verificar com teste do texto exato para um mês fixo (hora simulada)
- [x] 4.2 Em `assistant/service.py`, ao fim de cada rodada de ferramentas, encerrar a pergunta com `Answer(REJECTED, texto, tokens, reason="period")`, sem nova chamada, quando houve erro de período e nenhuma consulta da pergunta teve sucesso; verificar com testes com o cliente falso: mês futuro (1 chamada ao modelo e tokens contados), mês antes do piso, um mês válido e um futuro na mesma rodada (não encerra), mês em formato inválido (volta ao modelo, vale `NO_QUERY`)
- [x] 4.3 Teste de view em `assistant/tests/test_views.py`: pergunta sobre mês futuro mostra o texto fixo como resposta do assistente, com o campo limpo, fora do histórico da sessão e com os créditos descontados; verificar com `docker compose exec web pytest assistant/tests/test_views.py`

## 5. Prompt

- [x] 5.1 Trocar a regra 4 de `assistant/prompts.py` pela que permite calcular com os valores devolvidos e pede para mostrar os termos; verificar com `assistant/tests/test_client_and_prompt.py` (o prompt contém a nova regra e não contém mais a proibição de somar)

## 6. Verificação com o provedor real

- [x] 6.1 Com `LLM_API_KEY` própria e **dados fictícios**, fazer em ritmo baixo (cota de 8 mil tokens por minuto) cerca de 8 perguntas pela tela: valor citado, soma de duas categorias, diferença, percentual citado, percentual calculado, mês futuro, mês antes de 2000 e uma fora do escopo; conferir que nenhuma resposta correta é barrada e que a mensagem de período aparece sem texto do modelo; anotar no `design.md` (seção "Verificação com o provedor real", criada nesta task) os resultados, os tokens por pergunta e qualquer ajuste de prompt; remover os dados fictícios depois

## 7. Design e documentação

- [x] 7.1 Acrescentar a `design/assistant.figcraft` o quadro `assistant · desktop · claro · período sem dados` (resposta do assistente com o texto fixo, campo limpo), seguindo o quadro "com recusa", e exportar o PNG para conferir; mostrar o PNG ao usuário e só então dar a task por feita
- [x] 7.2 Atualizar a nota de divergências do assistente em `AGENTS.md` com o novo estado; verificar relendo a nota e conferindo que lista o estado "período sem dados"

## 8. Verificação final

- [x] 8.1 Rodar `docker compose exec web pytest --cov --cov-report=term-missing` e conferir que passa acima do piso de `fail_under`
- [x] 8.2 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` (sem `--strict`) e conferir que passam
