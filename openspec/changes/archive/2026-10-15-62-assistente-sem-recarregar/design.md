# Design

## Context

Motivação em `proposal.md`; requisitos em `specs/assistant/spec.md`. Estado atual:

- `ChatView.post` (`assistant/views.py`) valida, reserva créditos, responde e, no sucesso, grava a sessão e
  faz `redirect` para o `GET`. Em validação, falha, recusa e créditos esgotados, renderiza a página com
  status 200, `notice` (caixa cinza ou vermelha acima do campo) e o formulário preenchido. A lógica de
  créditos, histórico e provedor **continua valendo**; muda só **o que a view entrega ao template** (ver
  "Avisos dentro do chat").
- A caixa mostra hoje "Créditos de hoje: X de Y tokens" ao lado da barra (`percent` já existe no contexto).
- `templates/assistant/chat.html` já tem um `x-data="{ sending: false }"` no formulário (trava duplo envio e
  mostra o ícone de carregamento) e `@pageshow.window` para destravar ao voltar do cache. O atalho Enter do
  campo está em `assistant/forms.py` e chama `$el.form.requestSubmit()`.
- Alpine vem de `static/dist/js/alpine.min.js` (`defer`, no `base.html`); há um script próprio em
  `static/js/category-select.js` como precedente de JavaScript do projeto. Não há CSP configurada.
- `fetch` com `POST` seguido de `302` refaz a requisição como `GET` e devolve a página final; `response.redirected`
  distingue o sucesso (houve redirecionamento) dos casos que renderizam direto.

## Goals / Non-Goals

**Goals:**
- Enviar sem recarregar, mantendo **uma única fonte de verdade**: o HTML renderizado pelo servidor.
- Degradar para o fluxo atual quando o JavaScript não roda ou o `fetch` falha.

**Non-Goals:**
- Endpoint JSON, streaming, renderizar mensagens no cliente a partir de dados, ou mudar os textos dos
  avisos e o resto do visual aprovado além do que a proposta lista.

## Decisions

### Avisos dentro do chat: turno efêmero, estado da caixa e medidor
A view deixa de passar `notice`/`notice_is_error` e passa três coisas, todas só para aquela resposta:

- **`ephemeral`**: `{question, kind, text}` com `kind` `"assistant"` (recusa, cortesia, resposta não
  confiável) ou `"error"` (falha do provedor, indisponível, 429). O template o desenha **depois** das
  mensagens da sessão: a pergunta em bolha cinza e, conforme o `kind`, a resposta com a marca "Assistente" ou
  uma linha de erro (ícone, cor de erro, pergunta marcada como não enviada). Não vai para a sessão nem para o
  modelo; some ao recarregar e ao enviar de novo. No `"assistant"` o formulário volta **sem texto** (campo
  limpo); no `"error"` volta com o texto (`data-restore`).
- **`composer_notice`**: texto dentro da caixa, para créditos esgotados e sem chave. Aparece também no `GET`
  quando `used >= limit` ou sem `LLM_API_KEY`, desativa o botão de envio e mantém o texto digitado. Nesses
  casos não há turno efêmero.
- **Medidor**: `percent` (0 a 100) e `tone`, calculado no servidor: `brand` (até 69), `warning` (70 a 89),
  `error` (90 a 99) e `critical` (100). A caixa mostra a barra, "Créditos" e `NN%` na cor do tom; o uso e o
  total ("Usados X de Y") ficam em texto só para leitor de tela e no `title`, e a palavra "tokens" sai da tela.

O erro de validação segue sob o campo. Sem JavaScript, o servidor renderiza tudo isso no próprio `POST`,
então os dois caminhos mostram o mesmo.
*Alternativa descartada:* manter o aviso solto acima da caixa. Fica fora do chat e some do contexto de quem
perguntou.

### Trocar regiões do HTML da página, em vez de criar um endpoint
O JavaScript faz `fetch(form.action, { method: "POST", body: new FormData(form) })`, lê o HTML da resposta com
`DOMParser` e troca o conteúdo de regiões marcadas com `id`: conversa (`#chat-conversation`, com o turno
efêmero), ação do topo (`#chat-actions`, o "Nova conversa" só existe com conversa) e três pontos da
caixa: erro do campo (`#chat-field-errors`), mensagem da caixa (`#chat-composer-notice`) e medidor
(`#chat-credits`). O botão de envio e o `<textarea>` ficam fora das trocas, para o foco e o estado de espera
sobreviverem. Assim escape, `linebreaksbr`, créditos e regras de
histórico ficam num lugar só (o servidor), e um teste Python que confere o HTML do `POST` cobre o conteúdo
trocado. O token CSRF vem no `FormData`; o formulário e o `<textarea>` não são trocados, então o token e o foco permanecem.
*Alternativa descartada:* endpoint JSON ou fragmento HTML dedicado. Duplicaria rota, autenticação e
renderização, e afastaria o fluxo com e sem JavaScript.

### O servidor decide se o texto volta ao campo
Ao enviar, o componente guarda o texto e limpa o campo. Um elemento `#chat-state` (oculto, fora das trocas)
traz dois sinais, lidos **da resposta** a cada envio: `data-restore="true"` quando o texto deve voltar (falha
do provedor, erro de validação, mensagem da caixa) e `data-blocked="true"` quando a caixa está bloqueada
(créditos esgotados, sem chave), o que desativa o botão. O componente apenas obedece: restaura o texto
guardado ou deixa o campo limpo. Não se lê o `<textarea>` do HTML recebido nem se adivinha pelo conteúdo. A pergunta
otimista (bloco cinza + indicador) é só do cliente e é **substituída** pela troca da região da conversa, de
modo que o que fica na tela é sempre o que o servidor renderizou (sessão mais o turno efêmero).

### Falha de rede ou resposta inesperada cai no envio normal
Se o `fetch` rejeita (rede), ou a resposta não é HTML da tela (status ≠ 200 após o redirecionamento, ou sem as
regiões), o componente restaura o campo, remove a pergunta otimista e mostra uma linha de erro local no chat, em
português, como a de falha do provedor; a **resposta com redirecionamento para o login** (sessão expirada, `response.url` fora de
`/assistant/`) faz `window.location = response.url`. Não se reenvia sozinho: o `POST` pode ter consumido
créditos.
*Alternativa:* `form.submit()` nativo como reserva. Descartada: reenviaria uma pergunta que pode já ter sido
processada.

### Componente Alpine em arquivo próprio
`static/js/assistant-chat.js` registra `Alpine.data("assistantChat", ...)` (escuta `alpine:init`). O Alpine
inicia logo depois de ser carregado, então o script precisa vir **antes** dele: o `base.html` ganha o bloco
`component_scripts`, entre o `category-select.js` e o Alpine (o `extra_scripts` vem depois e não serve). O formulário passa a usar
`x-data="assistantChat"`; o `sending` e o `@keydown.enter` do campo continuam, agora lendo do componente. O
HTML do indicador e do bloco otimista é um `<template>` no `chat.html`, para que texto e classes Tailwind
fiquem no template (e o Tailwind os enxergue) e o JavaScript só o clone, inserindo a pergunta com
`textContent` (nunca `innerHTML`). A troca de regiões usa o HTML do **nosso** servidor, já escapado.
*Alternativa:* script inline no template. Descartada: difícil de testar e de manter, e mistura lógica com HTML.

### Acessibilidade
`#chat-conversation` ganha `role="log"` com `aria-live="polite"` e `aria-relevant="additions"`, para anunciar só
mensagens novas, inclusive o turno efêmero; a linha de erro tem `role="alert"`. A mensagem da caixa e o medidor
têm `role="status"`, e a porcentagem tem texto de leitor de tela com o uso e o total. O indicador tem `role="status"` e texto só para leitor de tela ("O assistente está
respondendo"); os pontos animados ficam `aria-hidden` e param com `motion-reduce`. O foco nunca sai do campo:
nenhuma troca de região toca o `<textarea>` nem o botão. Rolagem: o layout rola dentro de um contêiner (não na janela), então o
componente acha o ancestral rolável mais próximo de `#chat-conversation` e o leva ao fim, sem rolagem suave
com `prefers-reduced-motion`.

### Sem JavaScript, o fluxo é o mesmo
O `<form method="post">`, o `csrf_token` e o redirecionamento da view permanecem. O componente só intercepta o
`submit` quando roda; o `:disabled`/ícone de carregamento continuam como reforço. Os `<template>` e as regiões
são inertes sem script.

## Risks / Trade-offs

- [O HTML do servidor muda e os `id` das regiões somem] → teste Python afirma a presença de cada `id`, o
  `data-restore` e o conteúdo de cada região em sucesso, recusa, erro e créditos esgotados.
- [O turno efêmero some ao recarregar a tela] → aceito: ele não faz parte da conversa (não está na sessão).
- [Ao recarregar um `POST` renderizado, o navegador pede para reenviar o formulário] → já era assim; o
  redirecionamento fica só para o sucesso.
- [Cor sozinha não transmite o nível dos créditos] → a porcentagem em texto e o texto de leitor de tela
  acompanham a cor, e o contraste das quatro cores é conferido nos temas claro e escuro.
- [Voltar do histórico do navegador mostra tela antiga] → `@pageshow` já destrava; a conversa vem da sessão ao
  recarregar, então não há estado só do cliente a perder.
- [Pergunta otimista diverge do que a sessão guarda (por ex., CRLF e `strip`)] → a troca da região a
  substitui pelo HTML do servidor assim que a resposta chega.
- [Resposta lenta com a aba em segundo plano] → sem tratamento especial; o `fetch` conclui quando a aba volta.
- [Sessão expirada no meio da conversa] → detectada pelo redirecionamento ao login (ver decisão acima).
- [Não há teste de JavaScript no projeto] → o que é de Python é automatizado; o comportamento do navegador é
  verificado à mão nos temas claro e escuro e no celular (tarefa dedicada), com `playwright` disponível para
  conferir o fluxo.
