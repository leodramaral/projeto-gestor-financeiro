# Proposal

## Why

Só o cadastro tem design em `design/` (Issue #53). As demais telas já implementadas — entrar,
confirmação de conta, recuperação de senha, lançamentos, categorias e perfil — existem só no
código: não há registro visual delas nem dos estados (vazio, erro, sucesso), e a regra de que quem muda
uma tela atualiza o design na mesma change não tem como valer para elas. Origem: Issue #55.

## What Changes

- Um `.figcraft` por tela ou fluxo em `design/`, seguindo a convenção e a spec `screen-design` já
  existentes: `login`, `account-confirmation`, `password-reset`, `transactions`,
  `categories` e `profile`. **O painel fica de fora por inteiro**: o FigCraft não executa o Chart.js e, sem os
  gráficos, as telas do painel (visão geral, categorias, fluxo e lançamentos, com o estado vazio que fala de
  gráficos) não mostrariam o que o painel é; a lista de lançamentos já está em `transactions`.
- Cada tela em **desktop claro, desktop escuro e mobile claro**, mais os estados que o código tem
  (erro de formulário, vazio, sucesso, modal aberto, confirmação de exclusão), fiéis a
  `frontend/style.css`, aos templates e aos formulários, com a Outfit e dado de exemplo fictício.
- Frames nomeados `<tela> · <viewport> · <tema> · <estado>`, com `<tela>` no nome da rota em inglês.
- Divergências por limite da ferramenta (foco, sombras, menus abertos) registradas no
  `AGENTS.md`.
- A spec `screen-design` ganha o requisito de cobrir as telas implementadas e de cada uma ter seu
  `.figcraft`.

- **Correção do cartão de visitante:** `templates/base_auth.html` tem a classe `relativeflex` (sem espaço entre
  `relative` e `flex`), então o cartão de confirmação de conta, reenvio e mensagens de recuperação de senha aparece
  encostado no canto superior esquerdo, em vez de centralizado. O design foi desenhado centralizado, como o
  template pretende; o app é corrigido nesta change para bater com ele, em vez de registrar a diferença.

Fora do escopo: o painel (todas as abas e o estado vazio; viram Issue
nova se forem desejadas); telas ainda não implementadas; e-mails transacionais (não são telas do app); alterar
template, view ou model além da correção do cartão de visitante; versionar PNGs; protótipo
com transições.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities
- `visual-identity`: novo requisito de que o cartão das telas de visitante sem painel de marca apareça
  centralizado.
- `screen-design`: novo requisito de que toda tela implementada tenha design no `.figcraft`, com os
  temas, viewports e estados mínimos de cada uma.

## Impact

- Arquivos novos: seis `.figcraft` em `design/`. O `.gitignore` e o `.dockerignore` já cobrem `design/png/`
  e `design/`; o `.gitattributes` já marca `design/*.figcraft` como binário.
- Alterados: `AGENTS.md` (divergências conhecidas das novas telas) e `README.md` (uso do FigCraft na Parte 2).
- Um ajuste de classe em `templates/base_auth.html` e um teste em `accounts/tests/test_guest_layout.py`; nenhum
  model nem view muda. `check-added-large-files` (500 KB) vale para cada `.figcraft`.
- Depende de ferramenta fora do repositório: FigCraft instalado, MCP registrado e a Outfit instalada
  (`design/fonts/`), como na Issue #53.
