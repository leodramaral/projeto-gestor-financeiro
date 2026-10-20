# AGENTS.md

> Como trabalhar neste repositório: convenções, fronteiras e armadilhas. `CLAUDE.md` importa este
> arquivo. O `README.md` diz como rodar o projeto.

## Idioma

- **Código-fonte em inglês:** nome de módulo, classe, função, variável, docstring, comentário,
  mensagem de log e rota.
- **Texto de produto** (o que o usuário lê na tela) em português do Brasil.
- **Tudo o mais em pt-BR:** proposals, specs, design, tasks, commits, Issues e documentação em
  prosa. Requisitos usam **DEVE / NÃO DEVE**; cenários usam `#### Cenário:` com
  `- **QUANDO**` / `- **ENTÃO**` / `- **E**`.
- Única exceção, por ser estrutura de ferramenta: o marcador `### Requirement:` fica em inglês
  (o parser do OpenSpec o reconhece por regex fixa). Por isso a validação roda sem `--strict`.
- Nome de variável de ambiente não muda: é contrato operacional (`.env`, `docker-compose.yml`).

## Entry points

Tudo roda em Docker; o Python do sistema não é usado.

```bash
cp .env.example .env                                  # primeira vez
docker compose up --build                             # web em 127.0.0.1:8000 (migra ao subir), db, css e Mailpit (e-mails em :8025)
docker compose exec web python manage.py <comando>    # qualquer comando do Django
docker compose exec web pytest                        # testes (settings de teste, banco próprio)
docker compose exec web pytest --cov --cov-report=term-missing   # com cobertura (como o CI; piso em `fail_under`)
uvx pre-commit run --all-files                        # lint (Ruff, inclui complexidade), formatação e higiene
docker compose run --rm css npm run build             # recompila o CSS (`watch` para acompanhar)
openspec validate --all                               # SEM --strict
```

`DJANGO_SETTINGS_MODULE` escolhe o ambiente: `config.settings.dev` (local), `.test` ou `.prod`.
`config.settings.base` é só o módulo comum, não um ambiente.

## Regras

- **Não versione segredos.** `.env` está no `.gitignore`; só `.env.example` é versionado, sem valores
  reais. `SECRET_KEY` e `DATABASE_URL` não têm valor padrão: a aplicação deve falhar sem elas.
- **Ícones são da Lucide.** Todo ícone novo da interface vem da [Lucide](https://lucide.dev) (`lucide-static`
  1.52.0, ISC): copie o SVG para `core/icons/<nome-lucide>.svg` e use `{% load icon_tags %}{% lucide "nome" "h-5 w-5" %}`;
  os ícones das categorias ficam em `transactions/icons/` (`category_icon`). Não desenhe SVG à mão; só o
  indicador de espera do assistente (pontos animados) e as marcas (logo) são desenho próprio. Toda a
  interface já usa a Lucide, e assim deve seguir. Nos `.figcraft` o ícone é o caminho do próprio SVG de
  `core/icons/` (traço de 2 px, pontas e junções arredondadas, na cor do estado), não um redesenho.
- **Dependências com `uv`** (`pyproject.toml` + `uv.lock`); nunca `requirements.txt`.
- **Todo model, regra de negócio e tela de domínio nasce de uma change.** O domínio já existe (contas,
  lançamentos, categorias, metas, painel e assistente de IA; ver `openspec/specs/`): não amplie nem
  crie nada dele fora de uma change que autorize.
- **`static/dist/` e `node_modules/` não são versionados:** o CSS compilado nasce do serviço `css` do
  Compose, que também copia para `static/dist/` o Alpine, o Chart.js e a fonte Outfit
  (`@fontsource-variable/outfit`, `scripts/copy-alpine.mjs`). Node só existe dentro do contêiner.
- **Qualidade e CI.** Ruff (`E,F,I,UP,B,DJ,C90,S`, complexidade máxima 10, linha de 100; `S` é a checagem de segurança do
  Bandit, isenta só em `**/tests/**`) roda só via
  pre-commit (`.pre-commit-config.yaml`; instale com `uvx pre-commit install`). O CI
  (`.github/workflows/ci.yml`: `quality`, `tests`, `openspec`) repete tudo, e o CodeQL
  (`codeql.yml`, a cada PR e semanalmente) analisa a segurança; **não mescle com o CI
  vermelho**. O piso de cobertura (`fail_under` no `pyproject.toml`) só sobe, nunca é rebaixado para
  fazer um PR passar.
- **Dependabot** (`.github/dependabot.yml`, semanal) mantém as linhas Django 5.2, Node 22, PostgreSQL 16 e
  Python 3.12 por `ignore`: para adotar outra versão, remova a entrada e migre numa change própria.
- **O assistente de IA é opcional.** As variáveis `LLM_*` (`.env.example`) o configuram; sem
  `LLM_API_KEY` a aplicação roda normalmente e só a tela do assistente fica indisponível.
- `environment` vence `env_file` no Compose: ao acrescentar variável, confira que nada a sobrescreve.
- **Worktrees ficam em `worktrees/<nome>`, dentro do repositório** (pasta já ignorada pelo
  `.gitignore` e pelo `.dockerignore`), nunca como pasta irmã fora dele. Use `scripts/worktree`
  (o `db` precisa estar de pé); o nome pode seguir o id da change (`3-registrar-lancamentos`):
  - `scripts/worktree new <nome> [branch]`: cria a worktree, copia o `.env` (lista `COPY_FILES` no
    topo do script), define `APP_DB_NAME=gestor_<nome>` nele e cria esse banco como cópia do
    principal. Sem `[branch]`, a branch tem o nome da worktree.
  - `scripts/worktree resync <nome>`: refaz o banco da worktree a partir do principal (a cópia não
    o acompanha depois de criada; apaga o que houver no banco da worktree).
  - `scripts/worktree remove <nome>`: remove a worktree e apaga o banco dela; recusa o principal.
  - O Compose fixa `name: projeto-gestor-financeiro`: todas as worktrees compartilham o contêiner
    `web`, a rede e o servidor Postgres, mas cada uma usa **o seu banco** (`APP_DB_NAME`); o do
    pytest vira `test_gestor_<nome>`, então rodadas em worktrees diferentes não colidem.
  - Para validar a worktree no navegador (porta 8000), rode `docker compose up -d` **nela**: recria o
    `web` apontando para ela, o `css` recompila `static/dist/` e o `migrate` roda no banco **da
    worktree**. Só uma worktree por vez na 8000. `--build` só se `pyproject.toml` ou `uv.lock`
    mudaram. Para voltar ao checkout principal, rode `docker compose up -d` nele.
  - Testes sem trocar o `web`: `docker compose run --rm --no-deps web pytest` (o `db` de pé).

## Design (FigCraft)

O design das telas mora em `design/`, versionado. A ferramenta é o FigCraft (alpha; app desktop, CLI e
servidor MCP). Não é preciso para rodar nem para desenvolver o app, só para editar ou exportar design.

- **Arquivos.** `design/<tela>.figcraft` é o **artefato de design**: a fonte editável, um zip com
  `document.json` (binário para o git; o PR não mostra o diff).
  `design/png/` recebe os PNGs exportados do `.figcraft` e **não é versionado** (`.gitignore`): PNG não
  tem diff e cada ajuste criaria um binário novo no histórico; exporte quando precisar ver. `design/fonts/` tem a fonte do design
  (`Outfit[wght].ttf` e a `OFL.txt`). `design/` fica fora da imagem Docker (`.dockerignore`).
- **Nomes.** Frame: `<tela> · <viewport> · <tema> · <estado>`, como `signup · desktop · claro · com
  erros`: tela é o nome da rota em inglês, viewport é `desktop` ou `mobile`, tema é `claro` ou `escuro`
  e o estado é em português (`padrão`, `com erros`, `senha válida`). O PNG leva o mesmo nome em
  minúsculas, sem acento e com `-`: `signup-desktop-claro-com-erros.png`.
- **Fiel ao código.** Cores e tamanhos vêm de `frontend/style.css` (inclusive a altura de linha de cada
  classe `text-*`), e textos, rótulos e mensagens vêm dos templates e de `accounts/forms.py`; dado de
  exemplo é claramente fictício (`Maria Silva`, `maria@exemplo.com`). Quem muda uma tela atualiza o
  design na mesma change.
- **Fonte.** O app serve a Outfit pelo build, para qualquer visitante. O FigCraft só desenha com fontes
  **instaladas no sistema** (`.ttf`): antes de editar ou exportar, instale `design/fonts/Outfit[wght].ttf`
  (Linux: copie para `~/.local/share/fonts/` e rode `fc-cache -f`; Windows: botão direito → Instalar).
  Sem ela o texto sai numa fonte substituta, sem aviso, e os PNGs exportados saem com a tipografia errada.
- **Instalar e atualizar o FigCraft** (CLI, servidor MCP e app Linux): `scripts/figcraft-upgrade`
  (precisa do `gh` logado) baixa a release, confere o `SHA256SUMS` (recusa e não instala nada se não
  bater) e mantém o caminho `~/.local/share/figcraft/current/bin/figcraft-cli`, que não muda entre
  versões. `scripts/figcraft-upgrade --list` mostra as versões; `scripts/figcraft-upgrade <versão>`
  instala uma específica; para voltar, `ln -sfn ~/.local/share/figcraft/<versão> ~/.local/share/figcraft/current`.
  O app do Windows é o `.msi` da página de releases do FigCraft, que não passa pelo script.
- **MCP, por usuário e nunca em `.mcp.json`** (o caminho do binário é da máquina de cada pessoa):

  ```bash
  claude mcp add figcraft --scope local -- "$HOME/.local/share/figcraft/current/bin/figcraft-cli" mcp
  ```

  Sem `--no-system-fonts`, senão a Outfit instalada não aparece. Reinicie a sessão do Claude Code
  depois de registrar ou de atualizar.
- **Exportar os PNGs** (opcional, não vão para o git) a partir do `.figcraft`; o export nomeia `signup _ desktop _ …`, então renomeie
  pela convenção acima:

  ```bash
  ~/.local/share/figcraft/current/bin/figcraft-cli export design/signup.figcraft -o design/png/ --format png
  ```

  A pasta `design/png/` é ignorada pelo git.
- **Divergências conhecidas** entre o design do cadastro e o app: só o mobile claro existe; sem estados
  de foco (o app dá `autofocus` ao campo Nome) nem `shadow-theme-xs` nos campos; sem a caixa de erro
  geral (`form_errors`). O `-mt-2` do Tailwind não existe no auto layout: o design o reproduz com um
  grupo de 8 px entre o campo e o item abaixo dele.
- **Divergências conhecidas do design de metas** (`design/goals.figcraft`): sem estados de foco e de hover
  (o app dá foco ao campo Nome no modal) e sem `shadow-theme-*`; o campo de data mostra `dd/mm/aaaa` (o do navegador
  segue o idioma); o fundo dos modais é a casca da tela só com o título; menu `⋯` aberto não é desenhado;
  o frame é o tamanho da janela, sem a rolagem; o arquivo foi gerado por script e não usa componentes do
  FigCraft; dados fictícios (`Maria Silva`, 5 metas).
- **Divergências conhecidas do design do assistente** (`design/assistant.figcraft`, desktop claro e escuro, mobile
  claro; o visual segue o chat da demo do TailAdmin Pro, reproduzido em Tailwind próprio): sem estados de foco e de hover e sem `shadow-theme-*`; o frame é o tamanho da janela (1440×900 ou
  390×844), sem a rolagem; os ícones do assistente (menu, marca nas mensagens e erro) são da Lucide, redesenhados em traço; o botão de envio
  aparece só no estado normal (sem o indicador de carregamento) e o campo, sem o anel de foco; só o desktop claro tem os estados aguardando (pergunta enviada com o
  indicador de espera, que no app salta), com erro (falha do provedor: pergunta marcada como não enviada e linha
  de erro no chat), com recusa, com cortesia, não confiável e sem créditos (mensagem dentro da caixa, envio
  desativado), além de um quadro à parte com as quatro faixas do medidor de créditos (`assistant · medidor de
  créditos · claro · faixas`); o cabeçalho e a barra lateral são cópias de `goals.figcraft` (o item "Assistente" ativo e "Metas"
  inativo), e o arquivo foi gerado por script, sem componentes do FigCraft; dados fictícios (`Maria Silva`, uma
  pergunta e uma resposta de exemplo, medidor de créditos em 3%).
- **Divergências conhecidas das demais telas** (login, confirmação de conta, recuperação de senha,
  lançamentos, categorias e perfil; o painel tem a lista abaixo): sem estados de foco e de hover
  (o app dá `autofocus` ao primeiro campo) e sem `shadow-theme-*` em cartões, campos, modais e menus; o
  frame é o tamanho da janela (1440×900 ou 390×844), sem a rolagem da página; menu de ações da linha aberto
  só nos frames "menu de ações" e lista do seletor de categoria sempre fechada; o campo de data não mostra o
  ícone de calendário do navegador; o negrito de "Outros" no aviso de exclusão de categoria não é
  reproduzido; os dados são fictícios e coerentes entre as telas (`Maria Silva`, 8 lançamentos), não os do
  app.
- **Divergências conhecidas do design do painel** (`design/dashboard.figcraft`, só a Visão geral; as abas
  Categorias, Fluxo e saldo e Lançamentos e o estado vazio não têm desenho): os gráficos e a linha do
  saldo são **desenhados à mão** a partir dos dados de exemplo, porque o FigCraft não executa o Chart.js,
  e por isso têm menos marcas no eixo e o cruzamento do zero é exato (no app, o segmento que cruza fica todo
  vermelho); sem estados de foco e de hover e sem `shadow-theme-*`; o frame mostra a página inteira, não só a
  janela; o campo de mês é o `<select>` fechado, o atalho "Este mês" aparece desativado e o "Novo lançamento" fica na linha da data (no app, no celular, sobe para a linha do título); o ícone de tema do
  cabeçalho escuro continua sendo a lua; o estado de saldo negativo é só o bloco de destaque
  (`saldo negativo`), com números próprios; abaixo dos gráficos aparece uma nota no lugar de "Gastos por
  categoria" e "Últimos lançamentos", que não mudaram; o menu lateral tem três itens, sem "Metas"; os dados
  batem com os lançamentos só no saldo final (R$ 2.628,75) e nos lançamentos de outubro, e o painel tem
  lançamentos a mais.

## Impeccable (opcional)

Skill de design para o Claude Code (`/impeccable ...`: critique, audit, polish etc.). Não é preciso
para rodar nem para desenvolver o app.

- **Não é versionada.** Instale na sua máquina com `npx impeccable install` e ignore localmente, sem
  tocar no `.gitignore` do projeto, acrescentando ao `.git/info/exclude`:

  ```
  .claude/skills/impeccable/
  .claude/agents/impeccable-*
  ```

- **Binário.** Na primeira execução a skill baixa um binário de `github.com/pbakaus/impeccable`
  para `~/.impeccable/` (precisa de rede e de `curl` ou `wget`).
- **`PRODUCT.md` é versionado:** é o contexto de produto (usuários, propósito, restrições) que a skill
  lê. Quem muda o produto atualiza esse arquivo.
- **Não muda o fluxo do projeto.** Mudança de tela continua exigindo uma change do OpenSpec e a
  atualização do design em `design/` (ver acima); a skill não substitui nenhum dos dois.

## Fluxo de trabalho: Issues + OpenSpec

Spec-Driven Development. **Não implemente sem uma change.**

1. A Issue existe (`gh issue create`) e aponta para o trabalho.
2. `/opsx:explore` quando a intenção tem mais de uma leitura.
3. Branch com o id da change: `git checkout -b 2-login-por-email`.
4. `/opsx:propose`. O id da change é `<n>-<nome>`: o número da Issue seguido de um nome em
   kebab-case (`2-login-por-email`). Ao arquivar, a pasta ganha a data na frente
   (`2026-10-01-2-login-por-email`). Exceção histórica: `1-boilerplate` e `1-frontend-testes`
   repetem o `1`, porque ambas atendem à Issue #1.
5. `/opsx:apply`. Marque cada task só depois de **concluída e verificada**.
6. O que surgir no caminho: dentro do escopo vira task **antes** de ser feito; fora do escopo vira
   Issue nova, e o trabalho corrente não desvia.
7. Verificar (`openspec validate --all` e a verificação manual descrita nas tasks).
8. `openspec archive <id> --yes` ainda na branch, antes do PR.
9. PR com `Closes #<n>`.

## Commits

Conventional Commits, em português, com o **número da Issue** da change como escopo:
`feat(#2): login por e-mail`, `chore(#1): base Django + PostgreSQL em Docker`.
Trabalho fora de change usa a área como escopo: `docs: ...`, `chore(docker): ...`.
O título do PR segue o mesmo padrão.
