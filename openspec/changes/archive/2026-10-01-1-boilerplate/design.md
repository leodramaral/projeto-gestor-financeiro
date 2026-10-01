## Context

Repositório vazio; a fundação segue a convenção do projeto de referência (`analytics`): `uv`,
Dockerfile enxuto com usuário não-root, `docker compose` com perfis.

## Goals / Non-Goals

**Goals:** projeto Django rodando em Docker com Postgres; settings por ambiente; fluxo OpenSpec.
**Non-Goals:** testes, lint, CI, UI, domínio, deploy.

## Decisions

1. **Django completo, sem SPA.** HTML renderizado no servidor; uma única aplicação a manter.
2. **Settings em pacote:** `base.py` comum + `dev.py`, `test.py`, `prod.py`. Escolha por
   `DJANGO_SETTINGS_MODULE`. Alternativa descartada: um único arquivo com `if ENV` — mistura
   ambientes e dificulta teste.
3. **`django-environ` para variáveis**, com `SECRET_KEY` e `DATABASE_URL` obrigatórias (sem valor
   padrão), para falhar cedo.
4. **`uv` + `pyproject.toml`**, instalação em camada cacheável no Docker (`uv sync --locked`).
5. **Compose:** `web` + `db` (postgres:16-alpine, healthcheck, volume nomeado). Porta só em
   `127.0.0.1`. `web` roda `migrate && runserver`: `migrate` é idempotente (no-op sem migração
   pendente), e se falhar o servidor não sobe. Serviço de migração separado foi descartado — só se
   justifica com várias réplicas ou credenciais distintas, e nada disso existe aqui. `web` roda `runserver` com o código montado. Servidor de
   produção (gunicorn, estáticos, proxy) fica de fora: a hospedagem ainda não existe, e decidir
   agora só aumentaria o que é preciso entender do projeto.

## Risks / Trade-offs

- `env_file` do compose vence a imagem: nenhuma variável é sobrescrita hoje; revisar ao
  acrescentar novas.
- Sem testes nesta change, a verificação é manual (ver tasks).
