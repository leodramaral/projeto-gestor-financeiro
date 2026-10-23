# Tasks

## 1. Design (validar antes do código)

- [x] 1.1 Criar `design/toast.figcraft` com os quadros de sucesso, erro, aviso e info em desktop claro, desktop escuro e mobile claro (`toast · <viewport> · <tema> · níveis`) e a pilha recolhida (toast mais novo à frente e as cartas de trás), e acrescentar a `design/transactions.figcraft` o toast de sucesso em contexto nos mesmos três casos, com o texto real "Lançamento registrado." e os ícones da Lucide (`circle-check`, `circle-alert`, `triangle-alert`, `info` e `x`, traço de 2 px de `core/icons/`); exportar os PNGs só para conferir (`design/png/` não é versionada)
- [x] 1.2 Mostrar ao usuário os quadros pelo nome e posição no `.figcraft` e esperar a validação; não começar o grupo 2 antes dela
- [x] 1.3 Registrar no `AGENTS.md` o `design/toast.figcraft` e as divergências do design do toast (animação, pausa ao passar o mouse, pilha expandida sem quadro, quadros por nível como recortes sobre o fundo da página, nome `toast · …` por ser componente e não rota, arquivo gerado por script) e verificar com `openspec validate --all`
- [x] 1.4 Remover do design os quadros que ainda mostram o alerta estático (`lançamento registrado` em `transactions.figcraft` e `categoria criada` em `categories.figcraft`) e conferir que nenhum `.figcraft` mantém o alerta, com varredura por "Alerta de sucesso" e "Título do alerta" (0 resultados)

## 2. Ícones e licença

- [x] 2.1 Copiar da Lucide 1.52.0 os ícones `triangle-alert` e `info` para `core/icons/`; verificar com `docker compose exec web pytest core/tests/test_icon_tags.py` (cada arquivo é um SVG limpo)
- [x] 2.2 Versionar `frontend/PINES-LICENSE` com o texto MIT do Pines UI (copyright DevDojo), como o `frontend/TAILADMIN-LICENSE`, e citar o Pines no `AGENTS.md`; verificar que o arquivo existe com o aviso de copyright e que `git diff --stat` não toca `package.json`, `uv.lock` nem `scripts/copy-alpine.mjs`

## 3. Servidor e templates

- [x] 3.1 Definir `MESSAGE_TAGS` em `config/settings/base.py` (`success`, `error`, `warning`, `info`; `debug` cai em `info`); verificar com teste de unidade dos quatro níveis do Django e de um nível desconhecido
- [x] 3.2 Dar variantes de nível ao `partials/alert.html` (cor, ícone, `role` e título por nível; "Tudo certo", "Algo deu errado", "Atenção", "Informação"); verificar com teste que renderiza os quatro e confere o ícone e o `role` de cada um
- [x] 3.3 Criar `partials/toast_templates.html` (um `<template data-toast-level>` por nível, com ícone Lucide, título, texto e botão de fechar "Fechar" com o `x` da Lucide) e `partials/toast_messages.html` (elemento `[data-toast]` por mensagem, oculto, mais o `alert.html` em `<noscript>`); verificar com teste do HTML renderizado
- [x] 3.4 Incluir os dois parciais, o contêiner da pilha (`x-data="toastStack"`, `aria-label="Notificações"`) e o `toast.js` (com `defer`, antes do Alpine) em `base.html` e `base_auth.html`, e remover o laço de `messages` de `transaction_list`, `category_list`, `goal_list` e `accounts/login`; verificar com `grep "partials/alert.html" templates` (só o `<noscript>` do parcial novo sobra) e `docker compose exec web pytest` verde, ajustando os testes que liam o alerta
- [x] 3.5 Testar que as quatro telas e uma tela futura (que só estende o layout) exibem a mensagem emitida, que várias mensagens geram vários `[data-toast]`, que o texto sai escapado e que nenhuma página referencia domínio externo para o toast; verificar com `pytest`

## 4. Componente de front-end

- [x] 4.1 Criar `static/js/toast.js` com o cabeçalho de atribuição ao Pines (MIT, DevDojo) e `window.toast.success|error|warning|info` e `show(nivel, texto)`: dispara `toast:show`, com fila para chamadas anteriores ao Alpine; verificar no navegador chamando cada nível no console, inclusive antes de o Alpine iniciar e com `<b>x</b>`, que sai literal
- [x] 4.2 Registrar `Alpine.data("toastStack")` em `alpine:init`: array `toasts` com `x-for`, clone do `<template>` do nível preenchido com `textContent`, `role` por nível, duração de 5 000 ms (erro sem temporizador), botão de fechar que remove só o toast dele, e leitura dos `[data-toast]` no `init`, com nível desconhecido tratado como `info`; verificar no navegador registrando um lançamento, uma categoria, uma meta e redefinindo a senha (toast no topo à direita, texto igual ao de antes, sem alerta no fluxo da página)
- [x] 4.3 Implementar o empilhamento em cartas (mais novo à frente, até três cartas), a expansão com `mouseenter`/`focusin` e a pausa dos temporizadores enquanto expandida; verificar no navegador com quatro toasts seguidos (pilha recolhida, expandida ao passar o mouse e ao tabular até o botão de fechar, fechar um sem fechar os outros)
- [x] 4.4 Em `frontend/style.css`, definir a geometria e a `transition` da pilha por variáveis CSS, o contêiner `fixed` no topo à direita (`width: min(24rem, calc(100vw - 2rem))`, `z-index` acima do cabeçalho, abaixo dele no desktop pelo deslocamento) e desativar a `transition` sob `prefers-reduced-motion`; verificar nos temas claro e escuro, em 1440 px e 390 px, e com a preferência de movimento reduzido ligada

## 5. Documentação

- [x] 5.1 Atualizar o `AGENTS.md`: o `toast.js` e o uso do toast (`messages.*` no servidor, `window.toast` no JS) para quem criar tela nova, e conferir com `openspec validate --all`
- [x] 5.2 Conferir o `README.md` e, se citar o alerta de sucesso, atualizar; verificar com `grep -n "alerta" README.md`

## 6. Verificação final

- [x] 6.1 Verificar à mão no navegador (`docker compose up`), nos temas claro e escuro e em 390 px: sumir sozinho em cerca de 5 s, pausa ao passar o mouse e ao focar o botão, fechar por clique e por teclado, erro que não some, empilhamento e expansão com quatro toasts, toast acima do cabeçalho e do modal, leitor de tela anunciando (`role`) sem mover o foco e, com o JavaScript desativado, o alerta no topo do conteúdo
- [x] 6.2 Confirmar que os erros de formulário e os do chat do assistente seguem inline e sem toast, e que `git diff --stat` não toca `form_errors.html` nem os templates do assistente
- [x] 6.3 Rodar `uvx pre-commit run --all-files`, `docker compose exec web pytest --cov --cov-report=term-missing` (sem baixar o `fail_under`) e `openspec validate --all`, todos verdes
