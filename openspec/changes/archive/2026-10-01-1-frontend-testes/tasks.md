# Tasks

## 1. Testes (infraestrutura)

- [x] 1.1 Adicionar `pytest` e `pytest-django` ao grupo `dev` do `pyproject.toml`, atualizar `uv.lock` e ajustar o `docker/Dockerfile` para instalá-lo; verificar com `docker compose build` e `docker compose run --rm web pytest --version`
- [x] 1.2 Configurar `[tool.pytest.ini_options]` com `--ds=config.settings.test`; verificar que `docker compose exec web pytest` usa as settings de teste mesmo com `DJANGO_SETTINGS_MODULE=config.settings.dev` no `.env`
- [x] 1.3 Verificar que a suíte cria e remove `test_<db>` e não altera o banco de desenvolvimento (conferir com `psql` antes e depois)

## 2. Front-end

- [x] 2.1 Criar o app `core` (view `home`, rota `/` com `name="home"`), registrar em `INSTALLED_APPS` e `config/urls.py`; verificar que `/` responde `200`
- [x] 2.2 Adicionar `package.json` e lockfile com `tailwindcss` e `@tailwindcss/cli`, a entrada CSS do Tailwind (fontes e tokens do TailAdmin) e scripts `build` e `watch`; verificar que `npm run build` gera `static/dist/`
- [x] 2.3 Criar o serviço `css` no `docker-compose.yml` (volume nomeado para `node_modules`) e `depends_on` no `web` com `service_completed_successfully`; verificar que `docker compose up --build` num clone limpo compila o CSS antes de o `web` iniciar e que uma falha de build impede o `web` de subir
- [x] 2.4 Ajustar `.gitignore` e `.dockerignore` (`static/dist/`, `node_modules/`) e `STATICFILES_DIRS` em `config/settings/base.py`; verificar com `git status` que nenhum artefato compilado aparece
- [x] 2.5 Criar `templates/base.html` e as parciais `templates/partials/sidebar.html` e `header.html` a partir do TailAdmin (texto em pt-BR, Alpine.js estático local, origem e licença citadas em comentário) e `templates/core/home.html` estendendo o base; verificar abrindo `http://127.0.0.1:8000/` e conferindo barra lateral, cabeçalho, área de conteúdo e estilos aplicados
- [x] 2.6 Criar as parciais `partials/breadcrumb.html` e `partials/alert.html` (componentes TailAdmin, parametrizadas) e usá-las em `core/home.html` com "Olá, mundo" e uma mensagem de sucesso estática; verificar no navegador, em largura de desktop e de celular, que ambos aparecem estilizados e que a barra lateral recolhe no celular

## 3. Teste de fumaça

- [x] 3.1 Escrever em `core/tests/` o teste que confirma `200` em `/`, uso do template base e presença dos blocos de layout e do texto "Olá, mundo"; verificar que `docker compose exec web pytest` passa e que o teste falha ao remover a rota (reverter em seguida)

## 4. Documentação

- [x] 4.1 Atualizar o `README.md` (front-end e build do CSS, `watch`, rodar testes) e o `AGENTS.md` (novos comandos de entrada e a regra de não versionar `static/dist/`); verificar que os comandos documentados funcionam copiados e colados

## 5. Verificação final

- [x] 5.1 Percorrer os critérios de aceitação da Issue #1 num clone limpo (`cp .env.example .env`, `docker compose up --build`, página com layout, `pytest` verde) e rodar `openspec validate --all`
