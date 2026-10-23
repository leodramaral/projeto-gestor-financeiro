# Design

## Context

Hoje o assistente registra duas coisas, ambas em `assistant/views.py`: a falha (`logger.warning` com
`cause`, `status` e `seconds`) e a recusa (`logger.info`). O `service.py` não registra nada: o corpo do erro
do provedor é descartado em `_ask` e a rodada em que a falha ocorreu não chega ao `AssistantError`. O spec
proíbe registrar conteúdo (pergunta, resposta, dados); ver proposal.md para a motivação e a Issue #72.

Já existem o caminho `assistant.service` / `assistant.views` (loggers por módulo, que herdam do
logger `assistant` usado nos testes com `caplog`) e o formato `chave=valor` em uma linha.

## Goals / Non-Goals

**Goals:**
- Diagnosticar uma falha do assistente pelo log, sem reproduzi-la à mão.
- Manter a garantia de que nenhum conteúdo do usuário nem dado financeiro vai para o log.
- Zero dependência nova e zero mudança visível ao usuário.

**Non-Goals:**
- Tracing distribuído (OpenTelemetry), métricas, painel ou coletor de logs.
- Persistir diagnóstico no banco.
- Corrigir a causa da Issue de origem (o repasse da `thought_signature`).

## Decisions

**1. Logs `chave=valor`, não JSON nem OpenTelemetry.** O app é um único serviço Django que fala com um
provedor externo: um trace teria quase os mesmos campos que as linhas já dão, ao custo de SDK, instrumentação e um coletor no
Compose. Mantém-se o formato do log atual, legível no `docker compose logs`. *Alternativas:* JSON (exige
formatter e configuração de `LOGGING` sem ganho com um leitor humano); OpenTelemetry (avaliar em change
própria se o objetivo for estudar observabilidade).

**2. `question_id` = `uuid4().hex[:8]`, criado em `_Question`.** Liga todas as linhas da mesma pergunta
quando várias chegam juntas. Não carrega nada do usuário nem da pergunta. O `AssistantError` e o `Answer`
levam o id, para a view logar a falha e o resumo com o mesmo valor.

**3. Log por chamada em `_ask` e por ferramenta em `_use_tools`, no `service.py`.** São os pontos que sabem
a rodada, o `finish_reason` e os tokens. A view fica com a falha e o resumo, porque é ela que mede a
duração total e conhece o desfecho. O nome da ferramenta só é registrado se for uma das conhecidas
(`SPENDING`, `DECLINE`); qualquer outro nome vindo do modelo vira `unknown`, já que ele é entrada não
confiável.

**4. A mensagem do provedor entra só no 4xx e só pelo campo estruturado.** Lê-se `error.body["error"]
["message"]` (ou `body[0]["error"]["message"]`, que é a forma do Gemini) e nunca `str(error)` nem o corpo
inteiro. Passa por uma função única que: tira quebras de linha e espaços repetidos, mascara a chave
(`settings.LLM_API_KEY`, quando houver) e corta no limite `MAX_PROVIDER_MESSAGE` (`assistant/service.py`). No 5xx e em erros sem status, nada é
registrado, porque a causa é do provedor e o corpo é mais provável de ecoar a requisição.

**5. A rodada vai no `AssistantError`.** `_ask` recebe o número da rodada e o atribui ao erro que levanta;
o laço `_loop` já o conhece. A view o imprime na linha de falha.

**6. Resumo por pergunta, no nível INFO; falha, em WARNING.** Sucesso, recusa e rejeição geram uma linha de
resumo com resultado, rodadas, tokens e duração. A falha continua em WARNING, agora com os campos novos.

## Risks / Trade-offs

- **[A mensagem de um 4xx pode ecoar parte da requisição]** → só o campo `message` do erro, truncado em `MAX_PROVIDER_MESSAGE`
  caracteres, e só em 4xx; o spec e os testes exigem que pergunta e argumentos nunca apareçam. Resíduo
  aceito: um provedor que cite um trecho do prompt do sistema (texto fixo do app, sem dado do usuário).
- **[Mais linhas por pergunta (até ~10)]** → são `info`; o `docker compose logs` fica mais longo, mas
  cada linha é curta e o `question_id` permite filtrar com `grep`.
- **[Formato da mensagem varia por provedor]** → a leitura é tolerante: qualquer falha ao extrair o campo
  resulta em "sem mensagem", nunca em exceção no tratamento de erro.
