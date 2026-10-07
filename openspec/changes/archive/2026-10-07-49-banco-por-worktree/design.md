## Context

O Compose fixa `name: projeto-gestor-financeiro`; o `web` monta só a pasta onde `docker compose up`
rodou e usa a `DATABASE_URL` montada no próprio `docker-compose.yml`. Todas as worktrees compartilham
`db`, rede e banco. O `db` é Postgres 16 e `POSTGRES_USER` é superusuário (cria bancos). A interpolação
do Compose lê o `.env` da pasta do projeto, ou seja, o da worktree, então `APP_DB_NAME` lá basta.

## Goals / Non-Goals

**Goals:** um banco por worktree, criado e removido por um script; `docker compose up -d` na worktree
valida o painel na 8000; sem `APP_DB_NAME`, tudo como hoje.

**Non-Goals:** Postgres por worktree, sincronização contínua, várias worktrees simultâneas no ar.

## Decisions

- **Mesmo servidor, um banco por worktree.** Isolamento suficiente com custo de memória zero. O banco
  de teste vira `test_gestor_<nome>` sem mexer em settings (pytest-django prefixa `test_` ao `NAME`).
- **`${APP_DB_NAME:-${POSTGRES_DB}}` na `DATABASE_URL`.** Retrocompatível. O `healthcheck` do `db` e
  o `POSTGRES_DB` do serviço `db` seguem o banco principal, que é o que o contêiner cria na inicialização.
- **Cópia por `pg_dump | psql`, não `CREATE DATABASE ... TEMPLATE`.** O `TEMPLATE` falha se há conexões
  no banco de origem (o `web` está conectado). Forma: `docker compose exec -T db pg_dump -U "$POSTGRES_USER"
  --no-owner --no-privileges "$MAIN" | docker compose exec -T db psql -U "$POSTGRES_USER" -v ON_ERROR_STOP=1
  --single-transaction -d "gestor_<nome>"`, com `set -o pipefail`. Se a cópia falhar, o banco recém-criado é
  apagado (rollback do `new`).
- **Nome do banco:** `gestor_` + `<nome>` em minúsculas com `[^a-z0-9]` trocado por `_`; recusa vazio ou
  mais de 63 caracteres. Dois nomes distintos podem colidir após a troca (`a-b` e `a_b`): a checagem de
  "já existe" recusa o segundo.
- **`remove` seguro:** só apaga o banco se o nome começa com `gestor_` e é diferente de `POSTGRES_DB`
  lido do `.env`; imprime o nome e apaga com `DROP DATABASE ... WITH (FORCE)` (PG 13+), porque o `web` pode
  estar conectado.
- **`resync`:** `DROP DATABASE ... WITH (FORCE)` + recriação + cópia, pelo mesmo caminho do `new`. Fica
  sem rollback: se a cópia falhar, o banco fica vazio e o erro manda rodar `resync` de novo.
- **Arquivos locais: cópia, sem link simbólico.** Só o `.env` hoje; `COPY_FILES=(.env)` no topo permite
  estender. Link simbólico fica para quando houver arquivo pesado.
- **Ordem do `new`:** valida tudo (nome, `db` no ar, worktree e banco inexistentes) antes de criar algo;
  cria worktree, copia arquivos, cria e popula banco. Falha após `git worktree add` desfaz a worktree.
- **CSS:** sem passo no script; o serviço `css` recompila `static/dist/` em todo `up`.

## Risks / Trade-offs

- `docker compose up -d` na worktree recria o `web` apontando para ela: só uma worktree por vez na 8000.
  Documentado no `AGENTS.md`.
- O banco copiado envelhece; `resync` existe para isso e apaga alterações locais dele.
- O script depende do `db` no ar e do `.env` do checkout principal; falha com mensagem clara se faltarem.

## Open Questions

Nenhuma: os pontos deixados à change na Issue estão decididos acima.
