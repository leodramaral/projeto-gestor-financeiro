# projeto-gestor-financeiro

Aplicação web em Django com PostgreSQL, executada em Docker.

## Subir localmente

```bash
cp .env.example .env
docker compose up --build
```

A aplicação responde em <http://127.0.0.1:8000/> e o admin em `/admin/`.

## Ambientes

`DJANGO_SETTINGS_MODULE` define o ambiente: `config.settings.dev` (local), `config.settings.test` e
`config.settings.prod`. O módulo `base` é comum aos três.

## Como trabalhamos

Mudanças passam por OpenSpec (`openspec/`). Ver `AGENTS.md` para convenções e fluxo.
