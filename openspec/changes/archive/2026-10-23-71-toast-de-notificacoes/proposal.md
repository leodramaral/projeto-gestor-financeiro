# Proposal

## Why

O aviso de sucesso (Issue #71) é um alerta estático (`partials/alert.html`) renderizado no fluxo da
página: empurra o conteúdo para baixo, nunca some sozinho e o mesmo laço de `messages` está copiado em
quatro telas (Lançamentos, Categorias, Metas e Login). Não há um mecanismo de notificação reutilizável:
cada tela nova teria de repetir o laço, e qualquer aviso sem recarregar a página não tem onde aparecer.

## What Changes

- Novo **toast global**, dinâmico e reutilizável, como **componente Alpine próprio** (`static/js/toast.js`),
  **sem dependência nova**. A lógica de empilhar os toasts em cartas, com expansão ao passar o mouse, é
  adaptada do toast do [Pines UI](https://devdojo.com/pines) (MIT, DevDojo), com atribuição no arquivo e a
  licença versionada. O Toastify-js e as demais bibliotecas foram avaliados e descartados: o Toastify está sem
  release desde 2022, e as ativas (Notiflix, SweetAlert2) trazem visual e ícones próprios que teríamos de
  neutralizar.
- Componente **geral**, não só de sucesso: quatro níveis (sucesso, erro, aviso e info), cada um com ícone
  da Lucide e cor do TailAdmin, em claro e escuro. Hoje só o sucesso é emitido; os demais ficam prontos
  para qualquer caso de uso futuro.
- Dois canais de entrada: o **servidor** (`messages.*` do Django, com `MESSAGE_TAGS`) e uma **API JS**
  (`window.toast.<nível>(texto)`) para avisar sem recarregar a página.
- O laço de `messages` sai das quatro telas e vai para `base.html` e `base_auth.html`: toda tela, atual ou
  futura, já nasce com toast. O `partials/alert.html` vira o modelo visual do toast e o fallback sem
  JavaScript (`<noscript>`).
- Comportamento: topo à direita, cerca de 5 s, botão de fechar (ícone Lucide) e pausa ao passar o mouse ou
  focar o toast; vários toasts empilham em cartas e a pilha expande ao passar o mouse; o erro não some
  sozinho; `role` por nível e respeito a `prefers-reduced-motion`.
- Design: arquivo próprio `design/toast.figcraft` (quatro níveis, claro e escuro, desktop e mobile, e a pilha
  recolhida), porque o toast é global e não pertence a uma tela; o toast de sucesso em contexto fica em
  `design/transactions.figcraft`. **Validado pelo usuário antes do código**.

### Fora do escopo

- Erros de formulário (`partials/form_errors.html`, erros por campo) e erros do chat do assistente:
  continuam inline, **sem nenhuma mudança**.
- Emitir erro, aviso ou info em algum ponto do app: o componente os suporta, mas nenhuma tela passa a
  emiti-los nesta change.
- Notificações persistentes, histórico de notificações e e-mail.
- Trocar o texto de qualquer mensagem de sucesso existente.

## Capabilities

### New Capabilities
- `notifications`: toast global de notificações (níveis, canais servidor e JS, comportamento,
  acessibilidade, fallback sem JavaScript e carregamento nos dois layouts).

### Modified Capabilities
- `screen-design`: o design passa a documentar o toast (níveis, temas e viewports).

Os cenários de "mensagem de sucesso" de `transactions`, `categories`, `goals` e `password-recovery` não
mudam: a mensagem continua exibida, só o apresentador troca.

## Impact

- **Dependências:** nenhuma nova (`package.json`, `uv.lock` e `scripts/copy-alpine.mjs` não mudam). O código
  adaptado do Pines entra com `frontend/PINES-LICENSE` (MIT, copyright DevDojo), como já é feito com o
  TailAdmin.
- **Templates:** `base.html`, `base_auth.html`, `partials/alert.html`, novos parciais do toast; remoção do
  laço em `transaction_list`, `category_list`, `goal_list` e `accounts/login`.
- **JS/CSS:** novo `static/js/toast.js` (`Alpine.data`); ajustes em `frontend/style.css` (animação do
  empilhamento e `prefers-reduced-motion`).
- **Backend:** `MESSAGE_TAGS` em `config/settings/base.py`. Views e textos não mudam.
- **Testes:** testes do markup e das tags; os testes de `messages` existentes seguem valendo.
- **Design e docs:** `design/toast.figcraft` (novo), `design/transactions.figcraft` e notas no `AGENTS.md` (divergências do design e o uso do toast).
