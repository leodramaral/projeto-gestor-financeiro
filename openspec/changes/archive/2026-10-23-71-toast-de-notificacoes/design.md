# Design

## Context

Hoje cada tela repete `{% for message in messages %}{% include "partials/alert.html" ... %}`
(`transaction_list`, `category_list`, `goal_list` e `accounts/login`); o `login` usa `base_auth.html`, as demais
`base.html`. Só `messages.success` é emitido. O modal de lançamentos redireciona e recarrega a página, então o
toast nasce no carregamento da página seguinte. Os componentes Alpine do projeto vivem em `static/js/*.js`,
registrados com `Alpine.data` em `alpine:init` (`category-select.js`, `assistant-chat.js`), e o Alpine é carregado
com `defer`. Não há CSP configurada e não há testes de JavaScript no projeto (teste no navegador está fora do
escopo desde a change `1-frontend-testes`). Ver `proposal.md` (Why).

Bibliotecas avaliadas (npm e GitHub, out/2026): Toastify-js (release de jul/2022), Notyf, iziToast e toastr
(paradas), Notiflix e SweetAlert2 (ativas, mas com visual, ícones e API próprios e muito maiores que o necessário),
sonner-js (port de uma pessoa) e Basecoat (kit de UI inteiro). Nenhuma justifica uma dependência: o que o
Toastify faria aqui (posição, empilhamento, animação) o Alpine com Tailwind faz, e o conteúdo do toast já era
nosso. O toast do [Pines UI](https://devdojo.com/pines) (MIT, DevDojo; `elements/toast.html`) tem o efeito de
empilhar em cartas que se expandem ao passar o mouse, e é a base da lógica de empilhamento. Lido no código dele,
é código de demonstração e não serve colado: sem `role` nem `aria-live`; cinco SVGs desenhados à mão; só tema
claro; sem `prefers-reduced-motion`; `x-html` com HTML livre; níveis `danger`/`default`; seis posições e textos em
inglês; JS em string dentro de atributo, com `getElementById`/`classList` e variáveis globais sem declaração.

## Goals / Non-Goals

**Goals:**
- Um único ponto de verdade para o conteúdo e o visual do toast, reaproveitado pelo canal do servidor e pela
  API JS, em vez de duas implementações.
- Toda tela, atual ou futura, ganha toast só por estender um dos dois layouts.
- Nenhuma dependência nova de runtime nem de build.

**Non-Goals:**
- Teste automatizado do JavaScript (sem infraestrutura no projeto): a verificação do comportamento é manual,
  descrita nas tasks. Os testes automatizados cobrem o servidor e o markup.
- Reproduzir as seis posições, o campo de HTML livre ou o tipo "custom" do Pines: só o topo à direita e texto.

## Decisions

### 1. Componente Alpine próprio, com o empilhamento adaptado do Pines
`static/js/toast.js` registra `Alpine.data("toastStack")`, na convenção dos outros componentes. O estado é um
array `toasts` renderizado com `x-for` (sem `getElementById` nem `classList`): cada toast ganha, por posição na
pilha, variáveis CSS (`--toast-index`, escala e deslocamento) e a animação é CSS (`transition`) em
`frontend/style.css`. Fechado, a pilha mostra o mais novo à frente e até três cartas; ao passar o mouse ou
focar dentro dela (`mouseenter`/`focusin`), expande e mostra todos os toasts inteiros. O que se aproveita do
Pines é a ideia e a geometria do empilhamento; o código é reescrito. O arquivo leva no cabeçalho a atribuição ao
Pines (MIT, DevDojo) e a licença vai em `frontend/PINES-LICENSE`, como `frontend/TAILADMIN-LICENSE`.
*Alternativas:* (a) Toastify-js: sem release desde 2022, e traz `✖` em inglês e gradiente que teríamos de
neutralizar; (b) Notiflix ou SweetAlert2: ativas, porém grandes, com visual e ícones próprios que conflitam com a
Lucide e o TailAdmin; (c) colar o toast do Pines sem reescrever: sem `role`, sem dark mode, com `x-html` e
variáveis globais, pelos pontos listados no Context.

### 2. Um `<template>` por nível, renderizado pelo servidor, é a fonte do markup
Um parcial `partials/toast_templates.html`, incluído nos dois layouts, emite quatro `<template data-toast-level>`
(`success`, `error`, `warning`, `info`) com ícone, título, texto e botão de fechar. O `toast.js` clona o do nível
pedido e preenche o texto com `textContent`. Assim o canal do servidor e a API JS usam exatamente o mesmo
markup, o ícone Lucide sai do `{% lucide %}` (nenhum SVG em JS) e o Tailwind enxerga as classes nos templates.
Os ícones novos (`triangle-alert`, `info`) entram em `core/icons/` copiados da Lucide 1.52.0. Títulos por nível:
"Tudo certo", "Algo deu errado", "Atenção" e "Informação".
*Alternativa:* montar o markup em JS: duplicaria o visual e exigiria SVG no script.

### 3. Canal do servidor: mensagens viram dados, lidas uma vez pelo JS
Em `base.html` e `base_auth.html`, um parcial `partials/toast_messages.html` percorre `messages` e emite, por
mensagem, um elemento oculto `<div hidden data-toast data-level="{{ message.level_tag }}">texto</div>` mais, dentro de um
`<noscript>`, o `alert.html` correspondente. O componente varre `[data-toast]` no `init` e exibe um toast por
item; o `<noscript>` é o fallback sem JavaScript (o alerta estático de hoje, agora com variantes de nível).
`MESSAGE_TAGS` em `config/settings/base.py` mapeia os níveis do Django para `success`, `error`, `warning` e
`info`; nível ausente ou desconhecido cai em `info`. As views e os textos não mudam.
*Alternativa:* `json_script`: serve, mas o elemento por mensagem é mais simples de testar no HTML e não precisa
de parse.

### 4. API JS global e pequena, segura antes do Alpine iniciar
`toast.js` define, ao carregar, `window.toast.success|error|warning|info(texto)` e `toast.show(nivel, texto)`.
Cada chamada dispara o evento de janela `toast:show`; o componente o escuta. Chamadas feitas antes de o Alpine
iniciar ficam numa fila que o componente esvazia no `init`, então nenhuma se perde. O texto sempre entra por
`textContent`; não há opção de HTML. O script é carregado com `defer`, antes do Alpine, nos dois layouts.

### 5. Duração, pausa e fechar
Sucesso, aviso e info somem após 5 000 ms; o erro não tem temporizador. Cada toast tem o seu temporizador, e
a pilha inteira pausa enquanto está expandida (mouse sobre ela ou foco dentro dela) e retoma ao sair, o que cobre
o teclado, ao contrário do Pines. O botão de fechar é do nosso markup (`x` da Lucide, rótulo "Fechar") e remove
só o toast dele.

### 6. Acessibilidade por nível
Sucesso e info: `role="status"` (educado); erro e aviso: `role="alert"` (assertivo). O `role` fica em cada
toast, que é inserido depois do carregamento e por isso é anunciado, sem mover o foco. O contêiner da pilha leva
`aria-label="Notificações"`. A ordem do DOM é a cronológica, e a ordem visual das cartas é só CSS.

### 7. Movimento e layout responsivo
Sob `prefers-reduced-motion: reduce`, `frontend/style.css` remove a `transition` e a pilha aparece e some sem
deslizar (a expansão continua, sem animação). O contêiner é `fixed` no topo à direita, com largura
`min(24rem, calc(100vw - 2rem))` e `z-index` acima do cabeçalho (`z-99999`); o deslocamento vertical põe o
toast abaixo do cabeçalho fixo (97 px no desktop, 77 px no celular; 72 px nas telas de visitante, abaixo do
botão de tema). O modal de lançamentos é um `<dialog>` modal, que vai para a camada superior do navegador, e
nenhum `z-index` o vence (verificado: o toast ficava atrás do fundo escurecido). Por isso o contêiner é um
`popover="manual"`, que o componente reabre a cada toast novo (`showPopover()`) para ficar acima do que abriu
depois; sem suporte à API Popover, ele segue como caixa `fixed`. Limite que o navegador impõe: com um modal
aberto, o resto da página fica inerte, então o toast aparece por cima mas só recebe mouse e teclado quando o
modal fecha (um toast de erro espera até lá; os que somem sozinho seguem o tempo normal).

### 8. Sem dependência nem build novos
`package.json`, `uv.lock` e `scripts/copy-alpine.mjs` não mudam: `static/js/toast.js` é servido como os demais
scripts do projeto, por `static/`, sem rede externa.

## Risks / Trade-offs

- [O componente passa a ser manutenção nossa] → ~100 linhas num arquivo só, atrás de `window.toast`, com a mesma
  convenção dos outros componentes Alpine.
- [Sem teste automatizado de JS] → testes de servidor (tags, markup, fallback, ausência de CDN) e verificação
  manual descrita nas tasks, em linha com o resto do projeto.
- [A geometria da pilha depende de CSS e pode quebrar com tema ou altura variável] → alturas medidas pelo
  navegador (as cartas de trás reaproveitam a altura do toast da frente) e conferidas nos dois temas e em 390 px.
- [Mensagem perdida se o JS falhar depois de carregar] → o `<noscript>` só cobre JS desativado, não JS quebrado;
  aceito: o elemento `[data-toast]` segue no HTML e o componente é pequeno e sem rede.
- [Atribuição ao Pines esquecida] → `frontend/PINES-LICENSE` e o cabeçalho do `toast.js` são tasks verificáveis.
- [Toast sobre o cabeçalho fixo no celular] → deslocamento e `z-index` conferidos em 390 px.
- [Toast inerte enquanto um modal está aberto] → aceito: hoje só mensagens do servidor geram toast, e elas
  chegam depois do redirecionamento, com o modal já fechado; a API JS é que pode acionar um toast com o modal
  aberto, e o erro fica na tela até ele fechar.
- [`this.$root` do Alpine some quando o card sai da lista, pois é resolvido a partir do elemento que roda a
  diretiva] → o componente guarda a raiz numa variável de fechamento, capturada no `init`.

## Migration Plan

Não há dados nem migração. Entrega em um PR: o laço sai das quatro telas e os layouts passam a renderizar o
toast ao mesmo tempo, então não há estado intermediário com dois avisos. Reversão: reverter o PR devolve o
alerta estático; nada de dependência a desfazer.
