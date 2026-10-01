# Design

## Context

O projeto roda só em Docker: `web` (Django com `runserver`, código montado em `/app`) e `db`
(PostgreSQL 16). A imagem é Python 3.12 + `uv`, instala com `--no-dev` e não tem Node. Não há app
Django próprio, `templates/` (já listado em `TEMPLATES["DIRS"]`) nem `static/`; `config/urls.py`
só expõe `/admin/`. `config/settings/test.py` já existe. `AGENTS.md` proíbe modelo e tela de domínio
sem change, então a página inicial é só moldura. Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**
- Um comando (`docker compose up --build`) entrega a página com layout e CSS compilado.
- `pytest` roda no contêiner com o mesmo PostgreSQL do ambiente, sem depender da máquina.

**Non-Goals:**
- Copiar o TailAdmin inteiro: só entram os componentes que o layout base usa.
- CI (GitHub Actions): change própria, depois; a decisão de rodar tudo via Compose já permite reaproveitar os comandos.
- Imagem de produção, `collectstatic`, CDN ou cache de assets.

## Decisões

**1. TailAdmin gratuito, adaptado a templates Django.** Parte-se do template HTML/Tailwind do
TailAdmin e extrai-se: `base.html` (estrutura + blocos `title`, `content`), parciais `sidebar` e
`header` em `templates/partials/`. Mantém-se Alpine.js (que o TailAdmin usa para menu e tema), servido
copiado do `node_modules` para `static/dist/js` no build (não versionado), não por CDN. Alternativa descartada: React/Next do TailAdmin —
contraria "templates renderizados no servidor; sem SPA". Verificar a licença (MIT) e registrar a
origem num comentário do `base.html`.

**1b. Conteúdo "Olá, mundo".** A página inicial exibe só dois componentes do TailAdmin, para o
desenvolvedor validar visualmente que o layout e o CSS funcionam: breadcrumb (parcial reutilizável
`partials/breadcrumb.html`, recebe o título) e alerta de sucesso (`partials/alert.html`, recebe tipo e
mensagem). Texto estático, sem dado nem modelo. Foram escolhidos por serem genéricos: cards de
métrica e tabelas sugeririam dados financeiros e pertencem às changes de domínio. A validação da UI é
manual (navegador); não há teste de navegador nesta change.

**2. Build do CSS por serviço `css` no Compose.** Imagem `node:22-alpine`, código montado, executa
`npm ci && npm run build` (Tailwind CLI, `--minify`) e termina; `web` declara
`depends_on: css: condition: service_completed_successfully`. Saída em `static/dist/` (no
`.gitignore`). Isso atende "sem Node na máquina" e, como o `./` está montado em `/app`, o resultado
aparece no `web` sem rebuild da imagem. Para editar estilos há `docker compose run --rm css npm run
watch`. Alternativas descartadas: (a) estágio Node no Dockerfile — o volume `./:/app` esconderia o
CSS gerado na imagem; (b) versionar o CSS compilado — gera diff ruidoso e risco de ficar defasado;
(c) CDN do Tailwind — não serve para o TailAdmin e quebra offline.

**3. App `core` para a rota `/`.** `TemplateView` simples em `core/views.py`, URL `name="home"`.
Sem modelo. É o lugar natural das telas transversais futuras. Os templates ficam em `templates/` na
raiz (já configurado), não dentro do app, por serem compartilhados.

**4. Estáticos.** `STATICFILES_DIRS = [BASE_DIR / "static"]`; `runserver` serve em desenvolvimento
via `staticfiles`. No teste, a página referencia `static/dist/...` por `{% static %}`; o
`StaticFilesStorage` padrão não exige o arquivo existir, então a suíte não depende do build do CSS.

**5. pytest.** Grupo `dev` em `pyproject.toml` (`pytest`, `pytest-django`), instalado pelo Dockerfile
(remove-se `--no-dev`: a imagem hoje só serve desenvolvimento). Configuração em
`[tool.pytest.ini_options]` com `addopts = "--ds=config.settings.test"`: a opção de linha de comando
vence a variável `DJANGO_SETTINGS_MODULE=dev` vinda do `.env`. `pytest-django` cria `test_<db>` no
mesmo servidor; o usuário do compose é dono do banco e tem `CREATEDB`. Testes ficam em
`core/tests/`.

## Riscos / Trade-offs

- [Build do CSS adiciona tempo à primeira subida] → `npm ci` usa cache de volume nomeado
  (`node_modules`) para não reinstalar a cada `up`.
- [`node_modules` no volume `./:/app` polui a árvore e quebra por divergência de SO] → volume nomeado
  só para `node_modules` e entrada no `.gitignore`/`.dockerignore`.
- [Template TailAdmin atualiza e diverge] → versão e origem registradas; adaptação é nossa, sem
  tentativa de acompanhar o upstream.
- [Página inicial pública] → intencional por ora, sem dado algum; rotas protegidas entram com o
  login, em change própria.
