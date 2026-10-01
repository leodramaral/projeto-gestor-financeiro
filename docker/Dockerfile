FROM python:3.12-slim

# `uv` vem da imagem oficial, sem instalar curl nem compilar nada.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Dependências em camada própria, antes do código: só reinstala quando o lockfile muda.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

COPY manage.py ./
COPY config/ ./config/

# Usuário sem privilégio.
RUN useradd --create-home --uid 1000 app \
    && chown -R app:app /opt/venv
USER app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
