# Tasks

## 1. View e mensagens (servidor)

- [x] 1.1 Em `assistant/views.py`, trocar `notice`/`notice_is_error` por `ephemeral` (`question`, `kind` `assistant` ou `error`, `text`), `composer_notice` e `restore` no contexto: recusa, cortesia e resposta não confiável → turno `assistant` com formulário limpo; falha do provedor → turno `error` com o texto de volta; créditos esgotados e sem chave → `composer_notice`, inclusive no `GET`; verificar com `docker compose exec web pytest assistant`, ajustando os testes que liam `notice`
- [x] 1.2 Calcular `percent` e `tone` (`brand` até 69, `warning` 70 a 89, `error` 90 a 99, `critical` em 100) e entregar ao template; verificar com teste de unidade nos limites 0, 69, 70, 89, 90, 99 e 100

## 2. Template

- [x] 2.1 Em `templates/assistant/chat.html`, dar `id` às regiões `#chat-conversation` (com `role="log"`, `aria-live="polite"`, `aria-relevant="additions"`), `#chat-actions`, `#chat-field-errors`, `#chat-composer-notice` e `#chat-credits`, mais o `#chat-state` com `data-restore` e `data-blocked`, e remover a caixa de aviso solta; verificar que a suíte do assistente segue verde e que nenhuma caixa aparece acima do campo
- [x] 2.2 Desenhar o turno efêmero depois das mensagens da sessão: pergunta em bolha cinza e resposta com a marca "Assistente" (`assistant`) ou linha de erro com `role="alert"` e a pergunta marcada como não enviada (`error`); verificar com teste que o texto vai escapado
- [x] 2.3 Trocar o medidor da caixa por barra, "Créditos" e `NN%` na cor do `tone`, com o uso e o total só em texto de leitor de tela e no `title`, sem a palavra "tokens"; mostrar a mensagem da caixa e desativar o botão de envio em `composer_notice`; verificar no navegador as quatro cores nos temas claro e escuro
- [x] 2.4 Acrescentar ao `chat.html` o `<template>` do bloco da pergunta otimista e do indicador de espera (`role="status"`, texto só para leitor de tela, pontos `aria-hidden` com `motion-reduce`); verificar no navegador que, sem o componente, nada novo aparece

## 3. Componente Alpine

- [x] 3.1 Criar `static/js/assistant-chat.js` com `Alpine.data("assistantChat")`: intercepta o `submit`, trava duplo envio, insere a pergunta com `textContent` e o indicador, limpa o campo mantendo o foco e rola até a última mensagem; verificar no navegador que a pergunta aparece na hora e a página não recarrega
- [x] 3.2 Fazer o `fetch` do mesmo `POST` e trocar as cinco regiões (`#chat-conversation`, `#chat-actions`, `#chat-field-errors`, `#chat-composer-notice` e `#chat-credits`) a partir do HTML da resposta; verificar que a resposta aparece, a porcentagem e a cor do medidor mudam e o "Nova conversa" aparece
- [x] 3.3 Restaurar o texto digitado só quando o `#chat-state` da resposta traz `data-restore="true"`, e bloquear o envio com `data-blocked`; tratar rede caída, resposta inesperada e redirecionamento ao login com uma linha de erro local em português, sem reenviar; verificar cada caso no navegador (erro do provedor, recusa, cortesia, créditos esgotados, 501 caracteres, servidor parado, sessão expirada)
- [x] 3.4 Ligar o formulário e o campo ao componente (`x-data="assistantChat"`, atalho Enter em `assistant/forms.py`) e carregar o script no `chat.html` antes do Alpine (bloco `component_scripts` no `base.html`); verificar Enter, Shift+Enter e clique no botão, e que `docker compose exec web pytest assistant` segue verde

## 4. Testes automatizados

- [x] 4.1 Em `assistant/tests/test_views.py`, testar que a página traz o `x-data`, o `<template>`, o script e cada `id` de região, e que o `POST` sem JavaScript continua redirecionando e gravando o histórico; verificar com `pytest assistant/tests/test_views.py`
- [x] 4.2 Testar o HTML do `POST` em cada caso: recusa, cortesia e resposta não confiável (turno do assistente, campo limpo, fora do histórico), falha do provedor (linha de erro, texto de volta, fora do histórico), pergunta longa demais (erro sob o campo), créditos esgotados e sem chave (mensagem na caixa, botão desativado, também no `GET`), `data-restore` em cada um e nenhuma caixa de aviso fora do chat; verificar com `pytest assistant`
- [x] 4.3 Testar o medidor: porcentagem e tom nos limites, "Créditos" presente e a palavra "tokens" ausente do HTML; conferir `pytest --cov --cov-report=term-missing` sem baixar o `fail_under`

## 5. Design e documentação

- [x] 5.1 Atualizar `design/assistant.figcraft` (desktop claro) com os estados: pergunta enviada aguardando, recusa em bolha, falha do provedor em linha de erro, créditos esgotados na caixa e o medidor nas quatro cores; exportar os PNGs para conferir (`design/png/` não é versionada); mostrar o design ao usuário e esperar a validação antes de implementar a tela
- [x] 5.2 Atualizar a nota de divergências do assistente no `AGENTS.md` (turnos, medidor e o que o design não reproduz) e conferir com `openspec validate --all`

## 6. Verificação final

- [x] 6.1 Verificar à mão no navegador (`docker compose up`), nos temas claro e escuro e no celular (390 px): envio sem recarregar, indicador, foco, rolagem, cada aviso no lugar certo (chat, campo ou caixa) com o texto de volta só nos erros, medidor nas quatro cores sem a palavra "tokens", "Nova conversa" aparecendo e sumindo, leitor de tela anunciando a resposta (`aria-live`) e `prefers-reduced-motion`; confirmar sem JavaScript (desativado nas ferramentas do navegador) o fluxo post/redirect/get
- [x] 6.2 Rodar `uvx pre-commit run --all-files`, `docker compose exec web pytest --cov --cov-report=term-missing` e `openspec validate --all`, todos verdes

## 7. Ícones da Lucide (pedido durante a change)

- [x] 7.1 Criar o template tag `lucide` e a pasta `core/icons/` (SVGs da Lucide 1.52.0 com a licença) e verificar com `core/tests/test_icon_tags.py` (nome desconhecido falha, cada arquivo é um SVG limpo)
- [x] 7.2 Trocar os ícones do assistente (menu, marca nas mensagens, erro, "Nova conversa", enviar e carregamento) pelos da Lucide e redesenhar os mesmos no `design/assistant.figcraft`; verificar no navegador e nos PNGs exportados
- [x] 7.3 Trocar os demais ícones da interface (barra lateral, cabeçalho, alternar tema, metas, lançamentos, categorias, campo de data, alerta, setas do calendário, paginação, seletor de mês, links "Voltar" e marcas das regras de senha) pelos da Lucide, mantendo só os logos; verificar com `grep "<svg" templates static/js` (sobram os dois logos e o do calendário em JS), a suíte verde e as telas no navegador (claro, escuro, celular)
