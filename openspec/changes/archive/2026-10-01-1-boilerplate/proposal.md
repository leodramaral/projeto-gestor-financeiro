# Proposal

## Why

O repositório está vazio. Antes de modelar qualquer domínio é preciso uma fundação reproduzível:
um projeto Django com PostgreSQL que suba com um comando, em qualquer máquina, e um fluxo de
trabalho guiado por OpenSpec.

## What Changes

- Projeto Django (LTS) gerenciado com `uv`, com configuração separada por ambiente: `base`, `dev`
  (local), `test` e `prod`.
- Ambiente 100% em Docker: serviço `web` e serviço `db` (PostgreSQL) via `docker compose`; as
  migrações pendentes são aplicadas na subida do `web`.
- Documentação base: `AGENTS.md`, `CLAUDE.md`, `README.md`, `.env.example`, `.gitignore`.
- Estrutura do OpenSpec com contexto do projeto em `openspec/config.yaml`.

Fora do escopo: suíte de testes, quality gate (lint, pre-commit, CI), UI, regras e modelagem de
domínio, deploy automático. Cada um entra como change própria.

## Capabilities

### New Capabilities
- `project-configuration`: configuração por ambiente e validação de variáveis obrigatórias.
- `runtime-environment`: execução da aplicação e do banco em contêineres.

### Modified Capabilities

## Impact

Cria a estrutura inicial do repositório (`config/`, `docker/`, `docker-compose.yml`,
`pyproject.toml`, documentação). Dependências de execução: `django`, `psycopg[binary]`,
`django-environ`.
