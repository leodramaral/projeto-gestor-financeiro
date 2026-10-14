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
docker compose up --build                             # web + db em 127.0.0.1:8000 (migra ao subir)
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
- **Dependências com `uv`** (`pyproject.toml` + `uv.lock`); nunca `requirements.txt`.
- **O domínio ainda não foi modelado.** Não crie model, regra de negócio nem tela de domínio sem uma
  change que a autorize.
- **`static/dist/` e `node_modules/` não são versionados:** o CSS compilado nasce do serviço `css` do
  Compose, que também copia para `static/dist/` o Alpine, o Chart.js e a fonte Outfit
  (`@fontsource-variable/outfit`, `scripts/copy-alpine.mjs`). Node só existe dentro do contêiner.
- **Qualidade e CI.** Ruff (`E,F,I,UP,B,DJ,C90`, complexidade máxima 10, linha de 100) roda só via
  pre-commit (`.pre-commit-config.yaml`; instale com `uvx pre-commit install`). O CI
  (`.github/workflows/ci.yml`: `quality`, `tests`, `openspec`) repete tudo; **não mescle com o CI
  vermelho**. O piso de cobertura (`fail_under` no `pyproject.toml`) só sobe, nunca é rebaixado para
  fazer um PR passar.
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
  (o app dá foco ao campo Nome no modal) e sem `shadow-theme-*`; o ícone de metas (alvo) e o de tema são
  desenhados à mão; o hambúrguer do cabeçalho é outro; o campo de data mostra `dd/mm/aaaa` (o do navegador
  segue o idioma); o fundo dos modais é a casca da tela só com o título; menu `⋯` aberto não é desenhado;
  o frame é o tamanho da janela, sem a rolagem; o arquivo foi gerado por script e não usa componentes do
  FigCraft; dados fictícios (`Maria Silva`, 5 metas).
- **Divergências conhecidas das demais telas** (login, confirmação de conta, recuperação de senha,
  lançamentos, categorias e perfil; o painel não tem design, por causa dos gráficos): sem estados de foco e de hover
  (o app dá `autofocus` ao primeiro campo) e sem `shadow-theme-*` em cartões, campos, modais e menus; o
  frame é o tamanho da janela (1440×900 ou 390×844), sem a rolagem da página; menu de ações da linha aberto
  só nos frames "menu de ações" e lista do seletor de categoria sempre fechada; o campo de data não mostra o
  ícone de calendário do navegador; o negrito de "Outros" no aviso de exclusão de categoria não é
  reproduzido; os dados são fictícios e coerentes entre as telas (`Maria Silva`, 8 lançamentos), não os do
  app.

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
