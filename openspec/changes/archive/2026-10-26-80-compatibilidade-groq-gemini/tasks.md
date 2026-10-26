# Tasks

## 1. Design da label do modelo (validar antes do código)

- [x] 1.1 Desenhar a label com o nome do modelo (sem a palavra "Modelo") na caixa de pergunta do quadro `assistant · desktop · claro · vazio`, no mobile claro e no desktop escuro de `design/assistant.figcraft` (FigCraft, fiel ao `frontend/style.css`, Outfit instalada, ícones só da Lucide se houver); o quadro mostra `openai/gpt-oss-120b` e a variação com `gemini-3.1-flash-lite`; exportar os PNGs para conferência
- [x] 1.2 **PARADA:** mostrar o quadro ao usuário (nomeando o quadro do `.figcraft` e a posição) e esperar a validação ou o ajuste; não tocar em view, template nem texto da tela antes da resposta

## 2. Devolver o estado opaco do provedor

- [x] 2.1 Em `assistant/tests/fakes.py`, permitir que `tool_response` crie chamadas com campos extras (como o SDK, em `model_extra`) e verificar que os testes existentes continuam passando sem alterar suas chamadas
- [x] 2.2 Escrever em `assistant/tests/test_service.py` o teste de que um campo extra do `tool_call` (ex.: `extra_content`) volta, igual, na mensagem do assistente da rodada seguinte, e o de que sem campo extra a mensagem é só `id`, `type` e `function`; ver o primeiro falhar antes da correção
- [x] 2.3 Ajustar `_assistant_message` em `assistant/service.py` para acrescentar os campos de `model_extra` de cada chamada, sem sobrescrever `id`, `type` nem `function`; os dois testes da 2.2 e a suíte do assistente passam
- [x] 2.4 Teste de que o campo extra não entra no histórico da conversa (a sessão guarda só texto)

## 3. Label do modelo na tela (só depois da validação da 1.2)

- [x] 3.1 Escrever em `assistant/tests/test_views.py` os testes da label: mostra o valor de `LLM_MODEL` e não mostra a palavra "Modelo", muda com `settings.LLM_MODEL`, some sem `LLM_API_KEY`, traz o texto "Modelo em uso: <nome>" para leitor de tela e não contém a chave nem `LLM_BASE_URL`; ver falharem antes do código
- [x] 3.2 Passar `model` no contexto de `assistant/views.py` e acrescentar a label em `templates/assistant/chat.html`, como no quadro validado (`truncate`, `title`, `sr-only`, claro e escuro); os testes da 3.1 e a suíte do assistente passam
- [x] 3.3 Conferir no navegador (Playwright), em desktop e celular, claro e escuro, que a label aparece, o nome longo é cortado sem quebrar a linha e a label continua certa depois de enviar uma pergunta com JavaScript
- [x] 3.4 Atualizar a caixa de pergunta nos demais quadros do assistente em `design/assistant.figcraft` e a lista de divergências do assistente no `AGENTS.md`

## 4. Documentação das dependências

- [x] 4.1 Acrescentar ao `README.md`, na Parte 1, a subseção "Provedores do assistente", curta: uma tabela com Groq e Gemini (endereço-base, modelo de exemplo, onde criar a chave) e a frase de que só esses dois foram testados; conferir que cada endereço e link citado está certo
- [x] 4.2 Atualizar o `.env.example` com as linhas do Gemini comentadas ao lado das da Groq, sem chave real, e conferir que `LLM_API_KEY` continua em branco
- [x] 4.3 Apontar para a nova seção do README na regra "O assistente de IA é opcional" do `AGENTS.md`

## 5. Verificação com os provedores reais

- [x] 5.1 Com o Gemini (chave do `.env`), dados fictícios em transação desfeita e `LLM_TIMEOUT_SECONDS` ajustado só no processo: rodar pergunta com consulta do mês atual, com mês informado, recusa, mês futuro e cortesia; todas completam sem 400, e o resultado entra em "Verificação com os provedores reais" do `design.md`
- [x] 5.2 Com a Groq (chave fornecida por quem tem a conta), o mesmo roteiro; registrar o resultado em `design.md` e, se algum item falhar, parar e abrir a discussão antes de seguir
- [x] 5.3 Conferir que o banco não ficou com usuário nem lançamento fictício depois das rodadas

## 6. Spec e fechamento

- [x] 6.1 `openspec validate --all` passa (sem `--strict`)
- [x] 6.2 `docker compose exec web pytest --cov --cov-report=term-missing` passa sem rebaixar `fail_under`, e `uvx pre-commit run --all-files` passa
