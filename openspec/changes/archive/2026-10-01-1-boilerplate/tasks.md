## 1. Documentação base

- [x] 1.1 Criar `.gitignore`, `AGENTS.md`, `CLAUDE.md` (importa `AGENTS.md`) e `README.md`
- [x] 1.2 Configurar a identidade git local (`user.email`)

## 2. Projeto Django

- [x] 2.1 `uv init` e dependências de execução (`django`, `psycopg[binary]`, `django-environ`)
- [x] 2.2 `startproject config .` e settings em `base.py`, `dev.py`, `test.py`, `prod.py`
- [x] 2.3 `SECRET_KEY` e `DATABASE_URL` obrigatórias; `.env.example` sem segredos
- [x] 2.4 Verificar `manage.py check` nos três ambientes

## 3. Docker

- [x] 3.1 `docker/Dockerfile` (Python slim, `uv sync --locked`, usuário não-root)
- [x] 3.2 `docker-compose.yml` com `web` (migra ao subir) e `db` (healthcheck, volume nomeado)
- [x] 3.3 Verificar `docker compose up --build`: `/` e `/admin/` respondem em `127.0.0.1:8000`
- [x] 3.4 Verificar que um banco vazio é migrado na subida e que um reinício sem migração pendente sobe normalmente
- [x] 3.5 Verificar `manage.py check --deploy` com `config.settings.prod`

## 4. Fechamento

- [x] 4.1 `openspec validate --all` sem erro
- [x] 4.2 Arquivar a change (commit direto na `main`, sem PR: o repositório ainda não tinha histórico)
