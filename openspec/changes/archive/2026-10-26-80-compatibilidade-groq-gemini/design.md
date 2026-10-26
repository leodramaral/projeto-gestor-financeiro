# Design

## Context

O assistente usa o SDK `openai` (`pyproject.toml`, `assistant/client.py`) contra um endereço compatível
com a API da OpenAI; a chamada é `client.chat.completions.create` em `assistant/service.py`. Na rodada
seguinte à de uma chamada de ferramenta, `_assistant_message` reconstrói a mensagem do assistente com
`id`, `type`, `function.name` e `function.arguments`.

Observado (chamada real, dados fictícios, sem alterar o repositório):
- o Gemini devolve em cada `tool_call` o campo extra `extra_content.google.thought_signature`, que o SDK
  guarda em `tool_call.model_extra` (e o `model_dump` inclui);
- reenviando a mensagem **sem** o campo, a segunda chamada responde HTTP 400 ("Function call is missing a
  thought_signature"); reenviando **com** o `extra_content` do `tool_call`, a resposta sai correta;
- a Groq (padrão do `.env.example`) não manda campo extra no `tool_call`.

Ver proposal.md para a motivação.

## Goals / Non-Goals

**Goals:**
- O assistente funciona de ponta a ponta com Groq e Gemini, trocando só as variáveis `LLM_*`.
- A correção é genérica: não conhece o nome de um provedor nem de um campo específico.
- As dependências do assistente ficam documentadas onde quem configura o projeto olha (README).

**Non-Goals:**
- Trocar o SDK por REST direto (o SDK já preserva os campos extras e mapeia os erros que o app usa).
- Tentar de novo em 503 ou timeout, ou ajustar a latência do plano gratuito.
- Garantir compatibilidade com provedores não testados.
- Mostrar o provedor, o endereço-base ou a chave na tela; trocar o modelo pela tela.

## Decisions

### 1. Repassar os campos extras do `tool_call`, não uma lista fixa

`_assistant_message` continua montando `id`, `type` e `function` e acrescenta, em cada chamada, os campos
de `tool_call.model_extra` que não colidam com esses três. Sem `model_extra` (ou vazio), o resultado é
idêntico ao de hoje.

Alternativas descartadas:
- *Lista fixa (`extra_content`)*: previsível, mas cada provedor novo que exija devolver outro dado pediria
  código novo, contra "trocar de provedor não exige mudança de código".
- *Reenviar `message.model_dump(exclude_none=True)` inteiro*: mais curto, mas devolve também campos de nível
  de mensagem que o app não controla e que um provedor pode rejeitar ao receber de volta; e os
  testes usam objetos simples sem `model_dump`.
- *Trocar para REST direto*: reescreve timeout, mapeamento de erro e leitura de `usage` sem ganho, porque o
  SDK já entrega o campo.

O repasse só vale dentro da pergunta em andamento (a mensagem fica em `self.messages`); o histórico da
conversa guarda só texto, então o dado opaco nunca vai para a sessão.

### 2. Compatibilidade provada com o provedor real, não por suposição

Cada provedor listado como compatível passa pela mesma verificação com dados fictícios, em transação
desfeita (nada fica no banco): pergunta com consulta do mês atual, com mês informado, recusa de assunto,
mês futuro e cortesia. O resultado de cada provedor (quantas perguntas completaram, e a latência
observada) é registrado em "Verificação com os provedores reais" abaixo. Um provedor que falhe na
verificação sai da lista do README.

### 3. Label do modelo na caixa do chat

A view passa ao template `model` (valor de `settings.LLM_MODEL`) e o template o mostra na linha de baixo da
caixa, depois do medidor de créditos e de um divisor fino, só o nome em `text-xs` (sem rótulo visível:
a posição ao lado dos créditos e o nome do modelo já dizem o que é), com `truncate` e `title` com o nome
completo e `sr-only` "Modelo em uso: <nome>" para leitor de tela. No celular, onde o rodapé não comporta
os créditos, o nome e o botão na mesma linha, o nome desce para uma segunda linha, abaixo dos créditos. Some quando `LLM_API_KEY` está vazia (nesse caso nada está rodando e a caixa já mostra a
mensagem de indisponibilidade). É dado de configuração do servidor, não do usuário: o Django escapa o texto
e a tela nunca recebe a chave nem `LLM_BASE_URL`.

Alternativas descartadas: *mostrar o nome do provedor* (o app só conhece o modelo; o endereço é detalhe de
infraestrutura); *mostrar na resposta de cada mensagem* (repete a informação e entra no histórico).

Por ser mudança de tela, o quadro entra **antes** do código: um quadro novo (ou ajuste do `vazio` claro, com
a variação do celular e do escuro) é mostrado e **validado pelo usuário** antes de tocar na view e no
template; só depois a caixa dos demais quadros do assistente é atualizada. Nome do modelo longo,
`openai/gpt-oss-120b` e `gemini-3.1-flash-lite` são os textos de exemplo do design.

### 4. Documentação curta no README

Uma subseção "Provedores do assistente" na Parte 1 do `README.md`, só com o essencial: uma tabela (provedor,
`LLM_BASE_URL`, `LLM_MODEL` de exemplo, onde criar a chave) para a Groq e o Gemini, e a frase de que só esses
dois foram testados. Nada de roteiro de teste, limites de plano nem histórico de verificação: a regra de que um
provedor novo só entra depois de testado com a chamada real fica no `AGENTS.md`, que é de quem desenvolve. O
`.env.example` ganha as linhas do Gemini comentadas, ao lado das da Groq, e o `AGENTS.md` aponta para a seção do
README na regra "O assistente de IA é opcional".

## Risks / Trade-offs

- **Provedor que rejeita um campo extra devolvido** → só repassamos o que o próprio provedor mandou; a
  verificação nos dois provedores cobre o caso e fica registrada. Um provedor novo passa pela mesma
  verificação antes de ser documentado como compatível.
- **Dependência de a verificação com a Groq exigir uma chave** → a tarefa 5.2 precisa de `LLM_API_KEY` da
  Groq fornecida por quem tem a conta; sem ela, a Groq fica "não verificada nesta change" e não entra
  na tabela do README como compatível. É a única decisão que depende de fora do repositório.
- **Latência e 503 do plano gratuito do Gemini** → fora do escopo; documentados como particularidade, com
  o timeout configurável.
- **Nomes de modelo que o provedor aposenta** (o `gemini-2.5-flash` já responde 404 para contas novas) → o
  exemplo da tabela do README é o modelo verificado na data.

## Verificação com os provedores reais

**Gemini** (`gemini-3.1-flash-lite`, 2026-10-26, dados fictícios em transação desfeita, timeout de 90 s só no
processo): 6 de 6 perguntas completaram de primeira, sem erro do provedor.

| Pergunta | Resultado | Rodadas | Tempo |
|---|---|---|---|
| gasto com transporte no mês atual | resposta com valor e percentual | 2 | 11,5 s |
| gasto com alimentação em agosto de 2026 | resposta com o valor | 2 | 9,2 s |
| categoria que mais pesou no mês | resposta com valor, percentual e total | 2 | 6,9 s |
| gasto em janeiro de 2099 | recusa de assunto (mês futuro ainda cai em `no_query`; muda com a Issue #78) | 2 | 7,0 s |
| "oi" | ajuda de cortesia | 1 | 2,8 s |
| "Onde devo investir?" | recusa de assunto | 1 | 3,9 s |

Antes da correção, a mesma pergunta com consulta falhava na rodada 2 com HTTP 400
(*"Function call is missing a thought_signature"*), reproduzido na investigação desta change.

**Groq** (`openai/gpt-oss-120b`, 2026-10-26, mesmo roteiro e mesmo método): 6 de 6 completaram de primeira, sem erro
do provedor e sem mudança de comportamento (a Groq não manda campo extra, então a mensagem reenviada é a de sempre).

| Pergunta | Resultado | Rodadas | Tempo |
|---|---|---|---|
| gasto com transporte no mês atual | resposta com o valor | 2 | 1,7 s |
| gasto com alimentação em agosto de 2026 | resposta com o valor | 2 | 1,6 s |
| categoria que mais pesou no mês | resposta com categoria e valor | 2 | 1,5 s |
| gasto em janeiro de 2099 | recusa de assunto (mês futuro; muda com a Issue #78) | 2 | 1,3 s |
| "oi" | ajuda de cortesia | 1 | 0,9 s |
| "Onde devo investir?" | recusa de assunto | 1 | 0,8 s |

Observação sem relação com esta change: uma resposta da Groq veio com Markdown (`**Moradia**`) apesar de o prompt
pedir texto simples; a tela exibe como texto escapado, então aparecem os asteriscos.
