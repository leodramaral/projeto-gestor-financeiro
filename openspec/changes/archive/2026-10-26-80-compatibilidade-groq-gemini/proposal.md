# Proposal

## Why

O requisito "Provedor configurável por ambiente" promete que trocar de provedor compatível com a API da
OpenAI não exige mudança de código, mas isso não vale para o Gemini: toda pergunta que consulta dados
falha na segunda chamada ao modelo com HTTP 400 (*"Function call is missing a thought_signature"*). O
Gemini devolve, em cada chamada de ferramenta, um dado opaco que precisa voltar na rodada seguinte, e o
serviço reenvia a mensagem do assistente reconstruindo só os campos que conhece. A Groq, padrão do
projeto, não manda esse dado, por isso o defeito nunca apareceu. As dependências do assistente (provedores,
endereços, modelos, limites) também não estão documentadas além de uma frase no README.

## What Changes

- **Devolver o estado opaco do provedor:** a mensagem do assistente com chamadas de ferramenta, reenviada
  na rodada seguinte, passa a levar os campos extras que o provedor mandou em cada chamada. Sem campo
  extra, a mensagem fica idêntica à de hoje.
- **Compatibilidade declarada e verificada:** o assistente DEVE funcionar com **Groq** e **Gemini**,
  verificados com o provedor real; outro provedor só entra depois de testado, antes de qualquer mudança
  que o assuma.
- **README (seção de configuração) e `.env.example`:** documentam, de forma curta, os provedores testados
  (Groq e Gemini), com o `LLM_BASE_URL`, o `LLM_MODEL` e onde criar a chave de cada um.
- **Label do modelo na caixa do chat:** a caixa de pergunta mostra, junto dos créditos, o nome do modelo em
  uso (`LLM_MODEL`), sem rótulo, para quem testa ver de relance com qual provedor responde; some sem `LLM_API_KEY`.
  Muda tela: o quadro entra em `design/assistant.figcraft` e é validado antes do código.
- Não troca o SDK `openai` por chamada REST direta.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `assistant`: o requisito "Provedor configurável por ambiente" passa a exigir a devolução do estado
  opaco do provedor, a lista de provedores verificados e a documentação deles; o requisito "Tela do
  assistente protegida por login" passa a exigir a label do modelo em uso na caixa de pergunta.

## Impact

- Código: `assistant/service.py` (`_assistant_message`), `assistant/views.py` e
  `templates/assistant/chat.html` (label do modelo) e os testes em `assistant/tests/` (`fakes.py`,
  `test_service.py`, `test_views.py`).
- Design: `design/assistant.figcraft` (a caixa de pergunta em todos os quadros do assistente).
- Documentação: `README.md` (seção de configuração), `.env.example` e a menção ao assistente no
  `AGENTS.md`.
- Sem migração, sem dependência nova, sem mudança de rota, de model nem de texto de tela.
- Fora do escopo: nova tentativa automática em 503 ou timeout, ajuste de latência do plano gratuito e os
  assuntos das Issues #68, #78 e #79.
