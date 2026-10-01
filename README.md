# projeto-gestor-financeiro

Aplicação web em Django com PostgreSQL, executada em Docker.

## Subir localmente

```bash
cp .env.example .env
docker compose up --build
```

A aplicação responde em <http://127.0.0.1:8000/> e o admin em `/admin/`.

## Front-end

O layout é o [TailAdmin](https://tailadmin.com) (versão gratuita, MIT) sobre Tailwind CSS 4, em
templates Django: `templates/base.html` e as parciais em `templates/partials/` (barra lateral,
cabeçalho, breadcrumb, alerta). Telas novas estendem `base.html` e preenchem `{% block content %}`.

O CSS e o Alpine.js são gerados pelo serviço `css` do Compose, que roda antes do `web` e termina;
o resultado fica em `static/dist/` (não versionado). Não é preciso ter Node na máquina.

```bash
docker compose run --rm css npm run build   # recompila uma vez
docker compose run --rm css npm run watch   # recompila ao editar templates/estilos
```

O CSS-fonte é `frontend/style.css`. A licença do TailAdmin está em `frontend/TAILADMIN-LICENSE`.

## Testes

```bash
docker compose exec web pytest
```

Usam `pytest` + `pytest-django` com `config.settings.test` (forçado pelo `pytest`, mesmo com
`DJANGO_SETTINGS_MODULE=config.settings.dev` no `.env`) e um banco `test_<POSTGRES_DB>` próprio, criado
e removido a cada execução. O banco de desenvolvimento não é tocado. Os testes ficam em
`<app>/tests/test_*.py`. O CI (GitHub Actions) ainda não existe e será uma change própria.

## Ambientes

`DJANGO_SETTINGS_MODULE` define o ambiente: `config.settings.dev` (local), `config.settings.test` e
`config.settings.prod`. O módulo `base` é comum aos três.

## Como trabalhamos

Mudanças passam por OpenSpec (`openspec/`). Ver `AGENTS.md` para convenções e fluxo.
