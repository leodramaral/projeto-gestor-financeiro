# Proposal

## Why

Na Issue #72: ao testar o assistente com o Gemini, toda pergunta falhou com "O assistente está indisponível"
e o log trazia só `cause=BadRequestError status=400 seconds=1.90`. O motivo (o provedor exigia de volta a
`thought_signature` do tool call) só apareceu reproduzindo a chamada à mão, porque o app descarta o corpo do
erro e não diz em qual das até quatro rodadas a falha ocorreu. Hoje diagnosticar uma falha do assistente
exige código de depuração fora do app.

## What Changes

- Cada pergunta ganha um **identificador curto** (`question_id`), que aparece em todas as linhas de log dela.
- Cada **chamada ao modelo** registra rodada, modelo, `finish_reason`, tokens e duração; cada **ferramenta**
  registra o nome e o resultado (ok, recusa ou erro), sem argumentos e sem dados.
- A **falha** passa a registrar também a rodada em que ocorreu e, nos erros 4xx do provedor, a **mensagem de
  erro dele**, truncada e com a chave mascarada. É o dado que teria mostrado a causa da Issue de uma só vez.
- Uma linha de **resumo** por pergunta concluída (resultado, rodadas, tokens, duração).
- O requisito "Falha amigável do provedor" é emendado: a lista de metadados permitidos cresce, e a proibição
  de registrar pergunta, resposta, argumentos e valores financeiros continua inteira.
- Formato `chave=valor` em uma linha, como o que já existe. Sem dependência nova.

### Fora do escopo

- **OpenTelemetry** e qualquer coletor ou painel: pode ser avaliado depois, em change própria.
- **Corrigir o repasse da `thought_signature`** para o Gemini: change própria; esta só torna a causa visível.
- Mudar o que o usuário vê na tela (as mensagens amigáveis não mudam).
- Persistir logs no banco ou criar tela de diagnóstico.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `assistant`: o requisito "Falha amigável do provedor" passa a permitir, além do tipo da falha, status e
  duração, o identificador da pergunta, a rodada, o modelo, os tokens e a mensagem de erro do provedor nos
  erros 4xx, e exige o log por chamada ao modelo e por ferramenta, sempre sem conteúdo.

## Impact

- Código: `assistant/service.py` (log por chamada e por ferramenta, rodada e mensagem do provedor nos
  erros) e `assistant/views.py` (a linha de falha e o resumo).
- Testes: `assistant/tests/` (o cenário "Log sem conteúdo" é estendido; novos para o log por rodada, a
  mensagem do provedor, a máscara da chave e a ausência de conteúdo).
- Sem migração, sem mudança de interface, sem variável de ambiente nova. Origem: Issue #72.
