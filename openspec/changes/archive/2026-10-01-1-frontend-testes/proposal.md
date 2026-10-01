# Proposal

## Why

A change `boilerplate` entregou Docker, Django e PostgreSQL, mas o projeto ainda não tem front-end nem
suíte de testes. Sem isso cada integrante valida o trabalho do seu
jeito, e todos os itens seguintes dependem de um layout base e de uma infraestrutura de testes.
Origem: Issue #1 — "Item 0 — Configuração do ambiente".

## What Changes

- Integrar o TailAdmin (versão gratuita, Tailwind CSS) como layout base em templates Django: um
  `base.html` com barra lateral, cabeçalho e área de conteúdo, e uma página inicial em `/` que o usa.
- Compilar o CSS do Tailwind dentro do fluxo Docker, por um serviço `css` do Compose que roda antes
  do `web`, sem exigir Node na máquina do desenvolvedor.
- Configurar `pytest` + `pytest-django` no contêiner, com settings de teste e ao menos um teste de
  fumaça da página inicial.
- Atualizar o `README.md` com front-end e testes, e o `AGENTS.md` com os novos comandos.

**Fora do escopo:** modelos, regras de negócio e telas de domínio; autenticação e login (a página
inicial é pública e sem dados); lint, formatação e pre-commit; CI (GitHub Actions), que fica para change própria; deploy e imagem de produção; testes
de front-end no navegador.

## Capabilities

### New Capabilities
- `frontend-layout`: página base com o layout TailAdmin servida pela aplicação, com o CSS compilado
  no fluxo Docker.
- `automated-testing`: suíte `pytest` executável no contêiner, com teste de fumaça.

### Modified Capabilities
<!-- Nenhuma: os requisitos de runtime-environment e project-configuration não mudam. -->

## Impact

- Código: novo app `core` (view e rota de `/`), `templates/`, `static/`, `config/settings/base.py`
  (app instalado, `STATICFILES_DIRS`), `config/urls.py`.
- Dependências: Python — `pytest` e `pytest-django` em grupo `dev` (`pyproject.toml`/`uv.lock`);
  Node — `tailwindcss` e `@tailwindcss/cli` (`package.json`/lockfile), usados só no build do CSS.
- Infra: `docker-compose.yml` (serviço `css`), `docker/Dockerfile` (instala o grupo `dev`).
- Documentação: `README.md`, `AGENTS.md`.
