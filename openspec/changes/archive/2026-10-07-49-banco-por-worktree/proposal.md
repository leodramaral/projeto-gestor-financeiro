## Why

Validar uma worktree no navegador hoje esbarra no banco compartilhado: o Compose fixa o nome do
projeto, então todas as worktrees usam o mesmo contêiner `web`, a mesma rede e **um único banco**.
Subir uma worktree migra esse banco; voltar para outra deixa o esquema à frente do código. Duas
rodadas de pytest em worktrees diferentes também colidem no mesmo `test_<banco>`. E a worktree nova
não tem `.env`, o que hoje é um passo manual. Origem: a validação da #47 (Issue #49).

## What Changes

- Um banco por worktree no mesmo servidor Postgres (contêiner `db`, volume `pgdata`): `gestor_<nome>`.
- Variável `APP_DB_NAME`: o `docker-compose.yml` monta a `DATABASE_URL` com
  `${APP_DB_NAME:-${POSTGRES_DB}}`; sem a variável, nada muda. Documentada no `.env.example`.
- Script versionado `scripts/worktree` (shell, sem IA) com `new`, `remove` e `resync`:
  cria/remove a worktree **e** o banco dela, copia os arquivos locais (`.env`) e refaz o banco a
  partir do principal.
- `AGENTS.md`: a regra "evite `docker compose up` dentro da worktree" é trocada pelo fluxo
  `docker compose up -d` na worktree (porta 8000, banco da worktree); sai o passo manual de gerar o
  CSS, porque o serviço `css` já recompila em todo `up`.

## Capabilities

### New Capabilities
- `worktree-workflow`: ciclo de vida de uma worktree de desenvolvimento (criação, remoção,
  ressincronização) com banco isolado.

### Modified Capabilities
- `runtime-environment`: o banco usado pelo `web` passa a poder ser escolhido por `APP_DB_NAME`.

## Impact

- `docker-compose.yml`, `.env.example`, `AGENTS.md` e o novo `scripts/worktree`.
- Nenhum código Python, model ou migração. Bancos de teste passam a ser `test_gestor_<nome>`.
- Fora do escopo: uma instância Postgres por worktree, sincronização contínua entre bancos e várias
  worktrees no ar ao mesmo tempo em portas diferentes.
