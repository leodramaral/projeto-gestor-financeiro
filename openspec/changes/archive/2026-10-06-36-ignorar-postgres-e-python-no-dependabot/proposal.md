# Proposal

## Why

Depois da correção anterior, o Dependabot abriu o PR #45 (Postgres 16 → 18), e o CI falhou: a
imagem 18 do Postgres guarda os dados num diretório por versão e se recusa a subir com o volume
montado em `/var/lib/postgresql/data`. Mesmo com o caminho corrigido, quem tem dados num volume 16
não os abre na 18 sem `pg_upgrade` ou dump e restore. É a mesma família do Django e do Node: uma
major é uma migração, não uma atualização. A imagem base do Python (`python:3.12-slim`) é o
próximo candidato (o `pyproject.toml` aceita `>=3.12`). Origem: Issue #36 (mesma da change anterior).

## What Changes

- `.github/dependabot.yml` passa a ignorar a **major do Postgres** (imagem do serviço `db`) e
  **major e minor do Python** (imagem base do `docker/Dockerfile`).
- A spec `security-scanning` estende o requisito de atualização automatizada e ganha dois cenários.
- O comentário do `dependabot.yml` e o README listam as quatro linhas fixadas (Django 5.2, Node 22,
  Postgres 16, Python 3.12).

Fora do escopo: migrar o Postgres ou o Python, e fechar o PR #45 dentro desta change (ele é fechado
à mão depois do merge).

## Capabilities

### New Capabilities

### Modified Capabilities
- `security-scanning`: o requisito de atualização automatizada passa a excluir também a major do
  Postgres e major e minor do Python da imagem base.

## Impact

- `.github/dependabot.yml` e `README.md`.
- O PR #45 deixa de ter versão aceita. Patches do Postgres 16 e do Python 3.12 vêm nas próprias tags.
