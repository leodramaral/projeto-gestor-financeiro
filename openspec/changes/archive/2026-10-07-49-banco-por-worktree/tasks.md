## 1. Compose e configuração

- [x] 1.1 `docker-compose.yml`: `DATABASE_URL` com `${APP_DB_NAME:-${POSTGRES_DB}}`
- [x] 1.2 `.env.example`: documentar `APP_DB_NAME` (opcional, um banco por worktree, definido pelo script)
- [x] 1.3 Verificar que, sem `APP_DB_NAME`, `docker compose config` produz a mesma `DATABASE_URL` de antes

## 2. Script `scripts/worktree`

- [x] 2.1 Esqueleto: `set -euo pipefail`, `COPY_FILES=(.env)` no topo, uso/ajuda, checagem de `db` no ar
- [x] 2.2 Derivação e validação do nome do banco (minúsculas, `_`, vazio, limite de 63)
- [x] 2.3 `new`: validações prévias, `git worktree add`, cópia de arquivos, `APP_DB_NAME` no `.env`, criação do banco por `pg_dump | psql`, rollback em falha
- [x] 2.4 `remove`: recusa o banco principal e nome sem prefixo `gestor_`, `git worktree remove`, `DROP DATABASE ... WITH (FORCE)`
- [x] 2.5 `resync`: recria o banco da worktree a partir do principal, com conexões abertas
- [x] 2.6 `shellcheck` limpo (rodar via contêiner) e executável no git (`chmod +x`)

## 3. Documentação

- [x] 3.1 `AGENTS.md`: trocar a regra de evitar `up` na worktree pelo fluxo novo (`up -d`, `--build` só se `pyproject.toml`/`uv.lock` mudaram, `scripts/worktree`, `run --rm --no-deps web pytest`) e remover o passo manual do CSS
- [x] 3.2 `README.md`: sem trecho sobre worktrees; nada a ajustar

## 4. Verificação

- [x] 4.1 `scripts/worktree new x`: worktree, `.env` com `APP_DB_NAME=gestor_x` e banco com os dados do principal
- [x] 4.2 `docker compose up -d` na worktree: painel na 8000 com o banco dela; migração nova na worktree não aparece no principal
- [x] 4.3 `pytest` em duas worktrees ao mesmo tempo, sem colisão
- [x] 4.4 `resync` reflete dado novo do principal; `remove x` apaga pasta e banco; recusa apagar o principal
- [x] 4.5 `uvx pre-commit run --all-files` e `openspec validate --all`
