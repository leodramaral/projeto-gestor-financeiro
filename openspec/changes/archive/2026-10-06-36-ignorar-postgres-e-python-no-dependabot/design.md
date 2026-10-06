# Design

## Context

A change `36-ignorar-django-e-node-no-dependabot` fixou o Django e o Node, mas deixou de fora o
Postgres. O PR #45 (`postgres:16-alpine` → `18-alpine`) falhou no job `tests`: o log do contêiner
`db` diz que, na 18+, a imagem usa diretórios por versão e não aceita o volume em
`/var/lib/postgresql/data`, que é como o `docker-compose.yml` monta o `pgdata`. O serviço `db`
guarda dados, então a major exige migração. O `docker/Dockerfile` usa `python:3.12-slim` e o
`pyproject.toml` aceita `requires-python = ">=3.12"`, o que deixa a imagem sujeita a PR de 3.13
ou 3.14.

## Goals / Non-Goals

**Goals:**
- Versionar a decisão de ficar no Postgres 16 e no Python 3.12 até haver uma migração planejada.

**Non-Goals:**
- Migrar para Postgres 18 (ajuste do volume e `pg_upgrade`) ou para outro Python.

## Decisions

- **Postgres: `semver-major` no ecossistema `docker-compose`.** A tag `16-alpine` já acompanha os
  patches da 16, então só a major gera PR.
- **Python: `semver-major` e `semver-minor` no ecossistema `docker`** (`/docker`), porque no
  Python cada minor (3.12 → 3.13) é uma versão de linguagem nova, com depreciações e remoções.
- **Mesmo padrão das entradas existentes:** `ignore` no arquivo, não `@dependabot ignore` por PR.
- **O PR #45 é fechado à mão depois do merge**, para o `ignore` já estar valendo e o Dependabot não
  reabri-lo.

## Risks / Trade-offs

- [O Postgres 16 sai de suporte e ninguém lembra de migrar] → o comentário do `dependabot.yml` e o
  README dizem que a major é uma migração planejada; o fim de vida da 16 deve ser acompanhado à parte.
- [Ignorar o Python esconde uma correção de segurança da imagem] → os patches (3.12.x) seguem
  chegando com a tag `3.12-slim`, e os alertas de segurança continuam ligados.
