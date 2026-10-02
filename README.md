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
([TailAdmin](https://tailadmin.com)), suíte de testes e verificação automática (CI). O domínio financeiro ainda **não foi
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
- Caixa de entrada de e-mail (Mailpit): <http://127.0.0.1:8025/>

**6. Crie sua conta**

Pela tela de cadastro, <http://127.0.0.1:8000/accounts/signup/>: informe nome, e-mail e senha. O
e-mail de confirmação não sai da máquina; abra o Mailpit (<http://127.0.0.1:8025/>), clique no link
da mensagem e depois entre em <http://127.0.0.1:8000/accounts/login/>. Só contas confirmadas
conseguem entrar.

Para o admin (`/admin/`), crie um superusuário (pede e-mail, nome e senha; já nasce confirmado):

```bash
docker compose exec web python manage.py createsuperuser
```

> **Veio de uma versão anterior ao cadastro de usuários?** O modelo de usuário mudou, e o banco
> antigo (com o `User` padrão do Django) é incompatível. Recrie-o: `docker compose down -v` e
> `docker compose up --build` (apaga os dados locais, inclusive o superusuário antigo).

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
docker compose exec web pytest --cov --cov-report=term-missing   # testes + cobertura (igual ao CI)
uvx pre-commit run --all-files                       # lint, formatação e higiene de arquivos (igual ao CI)
docker compose run --rm css npm run build            # recompila o CSS uma vez
docker compose run --rm css npm run watch            # recompila o CSS a cada edição de template/estilo
docker compose exec web python manage.py send_test_email voce@exemplo.com  # e-mail de teste (aparece no Mailpit)
openspec validate --all                              # valida os artefatos do OpenSpec (sem --strict)
```

### Como funciona por baixo (engenharia)

O `docker-compose.yml` define quatro serviços que sobem em ordem:

```
css  ──(termina com sucesso)──┐
                               ├──▶  web  (Django, 127.0.0.1:8000)
db   ──(healthcheck ok)───────┘
```

| Serviço | Imagem | Papel |
|---|---|---|
| `css` | `node:22-alpine` | Roda `npm ci && npm run build`: compila o Tailwind e copia o Alpine.js para `static/dist/`, e **termina**. O `web` só sobe depois que ele conclui. |
| `db` | `postgres:16-alpine` | Banco de dados, com volume nomeado `pgdata` (os dados sobrevivem a `down`). Tem *healthcheck* (`pg_isready`), então o `web` espera o banco aceitar conexões. |
| `mailpit` | `axllent/mailpit` | Caixa de entrada fake para dev: recebe todo e-mail da aplicação (SMTP em `mailpit:1025`, só na rede do Compose) e o exibe em <http://127.0.0.1:8025>. Sem volume: as mensagens somem ao recriar o contêiner. Nada sai da máquina. |
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
- **E-mail por ambiente.** Dev envia por SMTP ao Mailpit (sem variáveis no `.env`); teste usa o
  backend em memória (`mail.outbox`); prod usa SMTP configurado por variável. Em prod a aplicação
  **não sobe** sem `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` e
  `SITE_URL` (base dos links nos e-mails, ex.: `https://app.exemplo.com.br`); `EMAIL_PORT` (587) e
  `EMAIL_USE_TLS` (true) têm padrão. Para enviar e-mail no código, use
  `core.emailing.send_templated_email(to, subject, template, context)`, que renderiza
  `templates/email/<template>.txt` e `.html`. Para validar a configuração:
  `docker compose exec web python manage.py send_test_email voce@exemplo.com`.
- **Contas de usuário.** O app `accounts` define `AUTH_USER_MODEL = "accounts.User"`, com **e-mail
  como login** (único sem diferenciar maiúsculas, também no banco). O cadastro cria a conta como
  *não confirmada* e envia um link por e-mail (vale `PASSWORD_RESET_TIMEOUT`, 3 dias, e só funciona
  uma vez); sem confirmar, o login é recusado. "Lembrar de mim" mantém a sessão por
  `SESSION_REMEMBER_SECONDS` (30 dias); sem ele, a sessão acaba ao fechar o navegador. As páginas do
  painel exigem login (`LoginRequiredMixin`); telas de visitante estendem `templates/base_auth.html`.
  Rotas: `/accounts/{signup,login,logout,confirm/...}/`.
- **Porta só local.** A porta é publicada em `127.0.0.1`, então a aplicação não fica exposta à rede.
  Não há servidor de produção ainda; a hospedagem não foi decidida.

### Estrutura do repositório

```
config/            projeto Django: urls, wsgi/asgi e settings/{base,dev,test,prod}.py
accounts/          usuários: modelo `User`, cadastro, confirmação por e-mail, login/logout e testes
core/              app Django inicial (tela home), envio de e-mail (`emailing.py`) e seus testes
templates/         base.html, parciais (sidebar, header...), telas e e-mails (`email/`)
static/            imagens versionadas; static/dist/ é gerado e não versionado
frontend/          CSS-fonte (Tailwind) e licença do TailAdmin
docker/            Dockerfile da aplicação
openspec/          specs vigentes (specs/) e changes em andamento/arquivadas (changes/)
.claude/ .agents/  comandos e skills dos agentes de IA usados no fluxo
AGENTS.md          convenções, fronteiras e armadilhas (fonte única para agentes)
```

### Modelo de dados

`accounts.User` (tabela `accounts_user`), o único model do projeto por enquanto:

| Campo | Tipo | Observação |
|---|---|---|
| `email` | e-mail, único | Login. Gravado em minúsculas; índice único também sobre `lower(email)`. |
| `name` | texto (150) | Informado no cadastro. |
| `password` | texto | Hash (não é a senha). |
| `email_confirmed_at` | data/hora, nulo | Nulo = conta não confirmada; só contas confirmadas entram. |
| `is_active` | booleano | Falso = conta desativada pelo admin (não entra). |
| `is_staff` / `is_superuser` | booleanos | Acesso ao admin / todos os poderes. |
| `date_joined` / `updated_at` / `last_login` | data/hora | Cadastro, última alteração e último acesso. |

Relações herdadas do Django: `groups` e `user_permissions`.

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
7. **Verificar:** `openspec validate --all` (sem `--strict`), `docker compose exec web pytest`,
   `uvx pre-commit run --all-files` e a verificação manual descrita nas tasks. O CI repete essas
   checagens no PR (ver [Parte 3](#parte-3--qualidade-de-código-e-ci)).
8. **Arquivar** (`openspec archive <id> --yes`), ainda na branch e antes do PR. Isso mescla os
   deltas da change em `openspec/specs/` e move a pasta para `changes/archive/`.
9. **Pull Request** com `Closes #<n>` no corpo, para a Issue fechar sozinha no merge. O PR só deve
   ser mesclado com o **CI verde**.

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

## Parte 3 — Qualidade de código e CI

O código é verificado automaticamente em dois pontos: localmente, a cada `git commit`
(pre-commit), e no GitHub, a cada Pull Request (CI).

### CI

**CI** (*Continuous Integration*, integração contínua) é a execução automática das verificações do
projeto a cada alteração proposta. O resultado de cada verificação é registrado no Pull Request
como aprovado ou reprovado.

A implementação usa o **GitHub Actions**, e está definida em
[`.github/workflows/ci.yml`](.github/workflows/ci.yml).

**Gatilhos:**

- abertura de Pull Request e cada novo commit enviado a ele;
- merge na `main`.

Um novo push na mesma branch cancela a execução anterior.

### Jobs

Um **job** é um conjunto de passos executado em uma máquina virtual limpa, descartada ao final. O
CI tem três jobs, executados em paralelo e independentes entre si.

| Job | Verifica | Execução |
|---|---|---|
| `quality` | Padrão do código | Hooks do pre-commit: lint, formatação e higiene de arquivos |
| `tests` | Testes e cobertura | `pytest` com cobertura, no Docker Compose |
| `openspec` | Formato das specs e changes | `openspec validate --all` |

#### `quality`

- **Lint:** detecta erros prováveis, como variável não utilizada e `import` fora de ordem.
  Ferramenta: [Ruff](https://docs.astral.sh/ruff/).
- **Formatação:** padroniza aspas, espaços e quebras de linha, com no máximo 100 caracteres por
  linha. Ferramenta: Ruff.
- **Complexidade ciclomática:** número de caminhos de execução de uma função; cada `if`, `for` ou
  `and` adiciona um. O limite é 10. Funções acima disso são reprovadas e devem ser divididas.
- **Higiene de arquivos:** espaço ao final da linha, ausência de quebra de linha final, YAML
  inválido, marcador de conflito de merge e chave privada versionada.

#### `tests`

Executa a suíte no Docker Compose do desenvolvimento, com o mesmo PostgreSQL e o mesmo build do CSS,
e mede a **cobertura**: a porcentagem do código executada pelos testes.

- **Cobertura de linha:** proporção das linhas executadas.
- **Cobertura de branch:** em cada `if`, indica se os testes percorreram os dois desvios,
  verdadeiro e falso.

O **piso** (`fail_under`, no `pyproject.toml`) é a cobertura mínima aceita. Com cobertura abaixo
dele, o job é reprovado mesmo que todos os testes passem. O piso é elevado quando a cobertura
aumenta e não é reduzido.

#### `openspec`

Valida se specs e changes seguem o formato exigido; por exemplo, todo requisito deve ter ao menos
um cenário. A versão do OpenSpec é fixada no workflow para que atualizações da ferramenta não
alterem o resultado do CI.

### Resultado no GitHub

1. O estado de cada job aparece na seção de *checks* do Pull Request: em execução, aprovado (✅) ou
   reprovado (❌).
2. O link **Details** do job reprovado abre o log; o erro está próximo ao final.
3. Após a correção, um novo commit enviado ao Pull Request dispara nova execução.

As execuções também ficam listadas na aba **Actions** do repositório. Em Pull Requests de forks, o
GitHub pode exigir aprovação de um mantenedor antes da primeira execução.

### Falhas comuns

| Job | Causa | Correção |
|---|---|---|
| `quality` | Import fora de ordem, formatação, função complexa | `uvx pre-commit run --all-files` aplica as correções automáticas. Funções complexas são divididas manualmente. |
| `tests` (teste) | Teste reprovado | `docker compose exec web pytest`; a mensagem indica o teste e a asserção. |
| `tests` (cobertura) | Cobertura abaixo do piso | Adicionar testes ao código novo. A coluna `Missing` do log lista as linhas sem cobertura. |
| `openspec` | Spec ou change malformada | `openspec validate --all` indica o arquivo e a linha. |

### Pre-commit

O **pre-commit** executa localmente as verificações do job `quality`, no momento do `git commit`.
Se houver problema, o commit é interrompido e as correções automáticas são aplicadas; os arquivos
alterados devem ser revisados e adicionados ao commit.

A instalação é feita uma vez por clone e requer o
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) na máquina, usado somente para esta
ferramenta. A aplicação continua executando apenas no Docker.

```bash
uvx pre-commit install
```

Execução manual, sem commit:

```bash
uvx pre-commit run --all-files
```

As regras estão em [`.pre-commit-config.yaml`](.pre-commit-config.yaml) e, para o Ruff, no
`pyproject.toml`. O CI usa os mesmos arquivos; portanto, o que passa localmente passa no CI.

### Reprodução local do CI

```bash
uvx pre-commit run --all-files                                    # job quality
docker compose exec web pytest --cov --cov-report=term-missing   # job tests
openspec validate --all                                           # job openspec
```

### Perguntas frequentes

**O CI bloqueia o merge?** Somente se a *proteção de branch* exigir os três checks. Por regra do
projeto, não se faz merge com o CI reprovado.

**É possível desativar uma regra do lint?** Apenas com justificativa. A exceção é registrada no
`pyproject.toml`, com comentário explicando o motivo, e avaliada no Pull Request.

**CI aprovado garante código correto?** Não. Indica apenas que as verificações automáticas
passaram. A revisão por outra pessoa e a verificação manual descrita nas tasks continuam
necessárias.

---

## Licenças

O layout usa o [TailAdmin](https://tailadmin.com) (versão gratuita, MIT); a licença está em
`frontend/TAILADMIN-LICENSE`.
