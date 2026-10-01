# Gestor Financeiro

> **Projeto acadêmico.** Este repositório é um trabalho de estudo, desenvolvido para fins
> educacionais. Não é um produto comercial, não tem garantia de funcionamento e **não deve ser
> usado para gerir dinheiro real**.

## Sobre o projeto

O Gestor Financeiro é uma aplicação web para controle de finanças pessoais. A meta é permitir que
uma pessoa se cadastre, registre seu saldo e suas despesas e acompanhe a própria situação
financeira. O escopo está dividido em duas fases, acompanhadas pelas Issues do repositório:

- **MVP** (label `mvp`): configuração do ambiente, login e cadastro, registro de lançamentos
  (saldo e despesas) e resumo de status financeiro.
- **Pós-MVP** (label `pos-mvp`): categorização de custos, painel com gráficos, tarefas e metas,
  previsão de orçamento, assistente de gestão com IA, planos de serviço, relatórios e exportação,
  deploy em cloud, documentação final e pitch.

**Estado atual:** só a fundação está pronta — projeto Django, PostgreSQL, Docker, layout
([TailAdmin](https://tailadmin.com)) e suíte de testes. O domínio financeiro ainda **não foi
modelado**: a tela inicial é um esqueleto. As funcionalidades entram uma a uma, cada uma como uma
*change* do OpenSpec (ver [Fluxo de desenvolvimento](#fluxo-de-desenvolvimento)).

**Stack:** Python 3.12, Django 5.2 (templates no servidor, sem SPA), PostgreSQL 16, Tailwind CSS 4
e Alpine.js. Tudo roda em Docker.

---

## Parte 1 — Rodar a aplicação do zero

### Pré-requisitos

Só duas coisas na máquina:

- [Docker](https://docs.docker.com/get-docker/) com o plugin **Docker Compose v2** (`docker compose`).
- [Git](https://git-scm.com/).

Python, `uv`, Node e PostgreSQL **não** precisam estar instalados: vivem dentro dos contêineres.

### Passo a passo

**1. Clone o repositório**

```bash
git clone git@github.com:leodramaral/projeto-gestor-financeiro.git
cd projeto-gestor-financeiro
```

**2. Crie o arquivo de ambiente**

```bash
cp .env.example .env
```

O `.env` guarda a configuração e os segredos locais. Ele está no `.gitignore` e nunca é
versionado; só o `.env.example` (sem valores reais) vai para o Git.

**3. Preencha os valores obrigatórios no `.env`**

| Variável | O que fazer |
|---|---|
| `SECRET_KEY` | Gere uma chave (comando abaixo) e cole. |
| `POSTGRES_PASSWORD` | Escolha qualquer senha. Evite `@`, `:` e `/`, que quebram a URL do banco. |
| `POSTGRES_DB`, `POSTGRES_USER` | Já vêm com `app`; pode manter. |
| `DJANGO_SETTINGS_MODULE` | Mantenha `config.settings.dev`. |

Para gerar a `SECRET_KEY` sem instalar nada, use o próprio contêiner do Python:

```bash
docker run --rm python:3.12-slim python -c "import secrets; print(secrets.token_urlsafe(50))"
```

As variáveis `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `SECURE_SSL_REDIRECT` são só de produção e
podem ficar como estão.

**4. Suba tudo**

```bash
docker compose up --build
```

Na primeira vez leva alguns minutos (baixa imagens, instala dependências Python e Node).

**5. Acesse**

- Aplicação: <http://127.0.0.1:8000/>
- Admin do Django: <http://127.0.0.1:8000/admin/>

**6. (Opcional) Crie um superusuário para entrar no admin**

```bash
docker compose exec web python manage.py createsuperuser
```

**7. Confirme que está tudo certo rodando os testes**

```bash
docker compose exec web pytest
```

Para parar: `Ctrl+C` no terminal do `up`, ou `docker compose down` (mantém os dados do banco).
Para apagar também o banco e o cache do Node: `docker compose down -v`.

### Comandos do dia a dia

```bash
docker compose exec web python manage.py <comando>   # qualquer comando do Django (migrate, shell...)
docker compose exec web pytest                       # testes
docker compose run --rm css npm run build            # recompila o CSS uma vez
docker compose run --rm css npm run watch            # recompila o CSS a cada edição de template/estilo
openspec validate --all                              # valida os artefatos do OpenSpec (sem --strict)
```

### Como funciona por baixo (engenharia)

O `docker-compose.yml` define três serviços que sobem em ordem:

```
css  ──(termina com sucesso)──┐
                               ├──▶  web  (Django, 127.0.0.1:8000)
db   ──(healthcheck ok)───────┘
```

| Serviço | Imagem | Papel |
|---|---|---|
| `css` | `node:22-alpine` | Roda `npm ci && npm run build`: compila o Tailwind e copia o Alpine.js para `static/dist/`, e **termina**. O `web` só sobe depois que ele conclui. |
| `db` | `postgres:16-alpine` | Banco de dados, com volume nomeado `pgdata` (os dados sobrevivem a `down`). Tem *healthcheck* (`pg_isready`), então o `web` espera o banco aceitar conexões. |
| `web` | build de `docker/Dockerfile` | Aplica as migrações (`migrate`) e inicia o `runserver`. O código é montado em `/app`, então editar um arquivo recarrega a aplicação sem rebuild. |

Decisões que valem conhecer:

- **Imagem do `web`.** Parte de `python:3.12-slim` e instala as dependências com
  [`uv`](https://docs.astral.sh/uv/) a partir de `pyproject.toml` + `uv.lock` (`--locked`: build
  reprodutível). As dependências ficam numa camada própria, *antes* do código, e só são
  reinstaladas quando o lockfile muda. O processo roda como usuário sem privilégio (`app`, uid 1000).
  Não existe `requirements.txt`.
- **Configuração por ambiente.** `config/settings/` tem `base` (comum, **não** é um ambiente),
  `dev`, `test` e `prod`; a variável `DJANGO_SETTINGS_MODULE` escolhe qual vale. Segredos entram
  só por variável de ambiente (via `django-environ`).
- **Falha rápida.** `SECRET_KEY` e `DATABASE_URL` não têm valor padrão: sem elas a aplicação se
  recusa a subir, em vez de rodar insegura. O Compose monta a `DATABASE_URL` a partir das três
  variáveis `POSTGRES_*`.
- **Front-end sem Node na máquina.** O CSS-fonte é `frontend/style.css`; o resultado compilado fica
  em `static/dist/` (não versionado, assim como `node_modules/`, que é um volume nomeado). O layout
  é o TailAdmin: `templates/base.html` e as parciais em `templates/partials/`. Telas novas estendem
  `base.html` e preenchem `{% block content %}`.
- **Testes isolados.** `pytest` + `pytest-django` forçam `config.settings.test`, mesmo com
  `dev` no `.env`, e usam um banco `test_<POSTGRES_DB>` próprio, criado e removido a cada execução.
  O banco de desenvolvimento nunca é tocado. Os testes ficam em `<app>/tests/test_*.py`.
- **Porta só local.** A porta é publicada em `127.0.0.1`, então a aplicação não fica exposta à rede.
  Não há servidor de produção ainda; a hospedagem não foi decidida.

### Estrutura do repositório

```
config/            projeto Django: urls, wsgi/asgi e settings/{base,dev,test,prod}.py
core/              app Django inicial (tela home) e seus testes
templates/         base.html, parciais (sidebar, header...) e telas
static/            imagens versionadas; static/dist/ é gerado e não versionado
frontend/          CSS-fonte (Tailwind) e licença do TailAdmin
docker/            Dockerfile da aplicação
openspec/          specs vigentes (specs/) e changes em andamento/arquivadas (changes/)
.claude/ .agents/  comandos e skills dos agentes de IA usados no fluxo
AGENTS.md          convenções, fronteiras e armadilhas (fonte única para agentes)
```

### Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Erro `Set the SECRET_KEY environment variable` ao subir | `SECRET_KEY` vazia no `.env`. |
| `password authentication failed` no `web` depois de mudar a senha | O volume `pgdata` guarda a senha antiga. Rode `docker compose down -v` (apaga os dados locais) e suba de novo. |
| Página sem estilo | O serviço `css` falhou. Veja `docker compose logs css` ou rode `docker compose run --rm css npm run build`. |
| `port is already allocated` | Algo já usa a porta 8000 local. |

---

## Parte 2 — Fluxo de desenvolvimento

O projeto adota **Spec-Driven Development** com [OpenSpec](https://github.com/Fission-AI/OpenSpec):
primeiro se descreve e se aprova *o que* será feito, depois se implementa. **Não se implementa
nada sem uma change.** Parte do trabalho é feita com agentes de IA (Claude Code e outros), e as
specs são o contrato que os mantém alinhados com o que foi planejado.

### Os três artefatos

| Artefato | Onde vive | Para que serve |
|---|---|---|
| **Issue** | GitHub | A demanda: *por que* o trabalho existe. Labeladas `mvp` ou `pos-mvp`. |
| **Change** | `openspec/changes/<n>-<nome>/` | A proposta de mudança: `proposal.md` (o quê e por quê), `design.md` (como), `specs/` (requisitos como deltas) e `tasks.md` (checklist verificável). |
| **Spec** | `openspec/specs/` | A verdade vigente do sistema, formada pelas changes já arquivadas. |

Uma change tem id `<n>-<nome>`: o número da Issue seguido de um nome em kebab-case
(ex.: `2-login-por-email`). Ao ser arquivada, a pasta ganha a data na frente
(`2026-10-01-2-login-por-email`).

### O ciclo, passo a passo

```
Issue ─▶ explore ─▶ branch ─▶ propose ─▶ apply ─▶ verificar ─▶ archive ─▶ PR (Closes #n)
```

1. **Issue.** O trabalho começa numa Issue (`gh issue create`) que o descreve.
2. **Explorar** (`/opsx:explore`), quando a intenção admite mais de uma leitura. Investiga-se antes
   de propor.
3. **Branch** com o id da change, a partir da `main`:
   `git checkout -b 2-login-por-email`.
4. **Propor** (`/opsx:propose`). Gera `proposal`, `design`, specs e `tasks` de uma vez. Ajustes
   posteriores no plano usam `/opsx:update`.
5. **Implementar** (`/opsx:apply`). Executa as tasks do `tasks.md`; cada uma só é marcada depois de
   **concluída e verificada**.
6. **O que surgir no caminho:** se está dentro do escopo, vira task *antes* de ser feito; se está
   fora, vira Issue nova e o trabalho corrente não desvia.
7. **Verificar:** `openspec validate --all` (sem `--strict`), `docker compose exec web pytest` e a
   verificação manual descrita nas tasks.
8. **Arquivar** (`openspec archive <id> --yes`), ainda na branch e antes do PR. Isso mescla os
   deltas da change em `openspec/specs/` e move a pasta para `changes/archive/`.
9. **Pull Request** com `Closes #<n>` no corpo, para a Issue fechar sozinha no merge.

A skill `fechar-change` automatiza os passos 7–9: verifica, decide se já dá para arquivar,
commita, faz o push e abre o PR.

### Comandos do OpenSpec

| Comando | Uso |
|---|---|
| `/opsx:explore` | Investiga antes de propor |
| `/opsx:propose` | Cria uma change nova com todos os artefatos |
| `/opsx:update` | Ajusta artefatos de uma change em andamento |
| `/opsx:apply` | Implementa as tasks pendentes |
| `/opsx:sync` | Sincroniza specs sem arquivar |
| `/opsx:archive` | Arquiva a change e mescla os deltas em `openspec/specs/` |

Se os comandos não aparecerem no Claude Code, rode `openspec update` e reinicie-o.

### Commits e Pull Requests

- **Conventional Commits, em português**, com o **número da Issue** como escopo:
  `feat(#2): login por e-mail`, `chore(#1): base Django + PostgreSQL em Docker`.
- Trabalho fora de change usa a área como escopo: `docs: ...`, `chore(docker): ...`.
- O título do PR segue o mesmo padrão e o corpo traz `Closes #<n>`.
- Nunca se versionam segredos: só o `.env.example`, sem valores reais.

### Convenções de idioma

| O quê | Idioma |
|---|---|
| Código-fonte: módulos, classes, funções, variáveis, comentários, logs, rotas | Inglês |
| Texto que o usuário lê na tela | Português do Brasil |
| Proposals, specs, design, tasks, commits, Issues e documentação | Português do Brasil |

Nas specs, requisitos usam **DEVE / NÃO DEVE** e cenários usam `#### Cenário:` com
`- **QUANDO**` / `- **ENTÃO**` / `- **E**`. A única exceção é o marcador `### Requirement:`, que fica
em inglês porque o parser do OpenSpec o reconhece por regex fixa — por isso a validação roda sem
`--strict`.

### Onde ler mais

- [`AGENTS.md`](AGENTS.md) — convenções, fronteiras e armadilhas (fonte única, também lida pelos agentes).
- [`openspec/specs/`](openspec/specs/) — o que o sistema promete hoje.
- [`openspec/changes/archive/`](openspec/changes/archive/) — o histórico de decisões, change a change.
- [`openspec/config.yaml`](openspec/config.yaml) — o contexto e as regras que guiam a geração dos artefatos.

---

## Licenças

O layout usa o [TailAdmin](https://tailadmin.com) (versão gratuita, MIT); a licença está em
`frontend/TAILADMIN-LICENSE`.
