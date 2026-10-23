# Tasks

## 1. Identificador e rodada nos erros

- [x] 1.1 Gerar o `question_id` em `_Question` e levá-lo no `AssistantError` e no `Answer`; verificar com um teste de serviço que o id tem 8 caracteres hexadecimais e que erro e resposta da mesma pergunta o compartilham
- [x] 1.2 Passar a rodada de `_loop` para `_ask` e gravá-la no `AssistantError`; verificar com um teste em que o provedor falha na segunda chamada e o erro traz `round == 2`

## 2. Mensagem do provedor

- [x] 2.1 Criar a função que extrai `message` do erro 4xx (formas `{"error": {...}}` e `[{"error": {...}}]`), tira quebras de linha, mascara `LLM_API_KEY` e corta no limite `MAX_PROVIDER_MESSAGE` (`assistant/service.py`); verificar com testes unitários de formato, tamanho, máscara e entrada malformada (sem exceção)
- [x] 2.2 Ligar a função só aos erros com status 4xx (inclui 429) e deixá-la vazia nos demais; verificar com testes de 400, 429, 503 e erro sem status

## 3. Linhas de log

- [x] 3.1 Registrar uma linha por chamada ao modelo em `_ask` (id, rodada, modelo, `finish_reason`, tokens, segundos); verificar com `caplog` que uma pergunta de duas rodadas gera duas linhas com o mesmo id
- [x] 3.2 Registrar uma linha por ferramenta em `_use_tools` (id, nome e resultado, sem argumentos nem dados); nome desconhecido vira `unknown`; verificar com `caplog` que o argumento enviado pelo modelo não aparece
- [x] 3.3 Acrescentar à linha de falha da view o id, a rodada, o modelo e a mensagem do provedor, e registrar o resumo da pergunta (id, resultado, rodadas, tokens, segundos); verificar com `caplog` os campos nos desfechos resposta, recusa, rejeição e falha

## 4. Garantia de privacidade

- [x] 4.1 Estender `test_a_failure_is_logged_with_metadata_only` e `test_a_refusal_is_logged_without_the_question`: a pergunta, a resposta e os argumentos nunca aparecem em nenhuma linha, mesmo quando a mensagem do provedor ecoa a chave; verificar com `docker compose exec web pytest assistant`

## 5. Verificação final

- [x] 5.1 Rodar `docker compose exec web pytest --cov --cov-report=term-missing` e `uvx pre-commit run --all-files`; verificar que passam e que a cobertura não cai abaixo do `fail_under`
- [x] 5.2 Reproduzir a falha da Issue #72 (Gemini 3, resposta 400 na segunda rodada) e verificar no `docker compose logs web` que a causa aparece na linha de falha, com a rodada e a mensagem do provedor
- [x] 5.3 Rodar `openspec validate --all` (sem `--strict`) e verificar que passa
