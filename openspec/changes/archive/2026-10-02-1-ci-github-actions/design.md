# Design

## Context

O projeto roda inteiramente em Docker (ver `AGENTS.md`). Os testes usam `config.settings.test`, que
exige `SECRET_KEY` e `DATABASE_URL`; o Compose monta `DATABASE_URL` a partir de `POSTGRES_*` do
`.env`, que não é versionado (só `.env.example`). O serviço `web` depende de `css`
(`npm ci && npm run build`) e de `db` saudável. O OpenSpec CLI é um pacote npm
(`@fission-ai/openspec`, local: 1.13.1). Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**
- O CI reproduz o fluxo local (`docker compose`), não um segundo caminho de execução.
- Testes e validação do OpenSpec reprovam o PR de forma independente e legível.

**Non-Goals:**
- CD, matriz de versões, cache avançado, checagem de tipos, lint de templates.
- Configurar proteção de branch (é ajuste no GitHub, feito pela equipe depois).

## Decisions

1. **Testes via `docker compose`, não `setup-python` + serviço Postgres do Actions.** Garante a
   mesma imagem, versão do Postgres e build do CSS do desenvolvimento, e ainda valida que o serviço
   `css` compila. Alternativa (Python nativo no runner) é mais rápida, mas duplica a configuração e
   deixa o build do CSS sem cobertura. Execução: `docker compose up -d --wait db` e
   `docker compose run --rm web pytest --cov --cov-report=term-missing`
   (o `run` sobe o `css` por dependência).
2. **`.env` gerado no job** a partir de `.env.example`, com `SECRET_KEY` e `POSTGRES_PASSWORD`
   aleatórios (`openssl rand`). Nenhum secret do repositório, então PRs de fork funcionam.
3. **Três jobs paralelos** (`quality`, `tests` e `openspec`): `openspec` só precisa de Node e
   `quality` só de `uv`; falhas aparecem separadas na aba do PR.
3a. **Ruff para lint e formatação** (substitui flake8+isort+black numa ferramenta só). Regras:
   `E, F, I, B, UP, DJ, C90`, `line-length = 100`, alvo `py312`, migrações excluídas, em
   `[tool.ruff]` do `pyproject.toml`. `C90` (McCabe) limita a complexidade ciclomática a 10
   (`max-complexity = 10`) e **bloqueia**, igual ao projeto analytics; por ser regra do Ruff,
   não há ferramenta extra (radon/xenon).
3b. **pre-commit como fonte única.** `.pre-commit-config.yaml` fixa por `rev` o `ruff-pre-commit`
   (`ruff` com `--fix` e `ruff-format`) e o `pre-commit-hooks` (espaço no fim da linha, nova linha no
   fim do arquivo, `check-yaml`, `check-merge-conflict`, `detect-private-key`, `check-added-large-files`).
   O job `quality` roda `uvx pre-commit run --all-files`, então CI e máquina local aplicam as mesmas
   regras e o Ruff não precisa estar no grupo `dev` nem na imagem. Alternativa (Ruff em `dev` +
   `ruff check` direto no CI) duplicaria a versão em dois lugares. Custo: o pre-commit roda no
   host e exige `uv` instalado ali, aceito porque é só ferramenta de desenvolvimento de commit;
   a execução da aplicação continua só em Docker. `uv.lock`, `package-lock.json`, `openspec/` e
   `static/dist/` ficam excluídos dos hooks de texto.
3c. **Formatação do código existente num commit separado**, antes de ligar o CI, para o diff de
   revisão não misturar reformatação com funcionalidade.
4. **OpenSpec fixado em `1.13.1`** via `npm install -g @fission-ai/openspec@1.13.1`, a versão usada
   localmente; a atualização é uma decisão consciente (edição do workflow).
5. **Cobertura com piso, configurada no `pyproject.toml`.** `pytest-cov` com
   `[tool.coverage.run] branch = true` e `source = ["config", "core"]` (omitindo `migrations`), e
   `[tool.coverage.report] show_missing = true` e `fail_under = <valor medido>`. O piso é o valor
   **medido** na task 2.1, sem arredondar para cima nem margem, e só sobe quando a cobertura real sobe
   (mesma disciplina do analytics). Assim uma regressão é barrada desde o primeiro dia, sem escolher
   um número arbitrário. Os parâmetros ficam no `pyproject.toml`, não em `addopts`: o CI e o uso local
   leem a mesma fonte, e a execução rápida de um teste isolado continua sem cobertura (`--cov`
   explícito na linha de comando ativa a medição). O `fail_under` só vale quando `--cov` é usado.
6. **Gatilhos:** `pull_request` e `push` em `main`, com `concurrency` cancelando execuções antigas
   da mesma ref, e `permissions: contents: read`.
7. **Permissão de `static/dist` no runner.** O `css` grava no checkout montado em `/app` como `node`
   (uid 1000), mas o checkout do runner pertence ao uid 1001. O `web` também grava no checkout (`.coverage`,
   `.pytest_cache`) como `app` (uid 1000). O workflow libera escrita no workspace inteiro
   (`chmod -R a+rwX .`) antes do Compose. Preferível a rodar o `css` como root (deixaria `static/dist/`
   com dono root no host, o que o `docker-compose.yml` evita de propósito) ou a parametrizar o uid no
   Compose (mudança maior, fora do escopo). Detectado no primeiro PR; não aparecia localmente
   porque o uid do desenvolvedor é 1000.
8. **Actions por tag major** (`actions/checkout@v4`, `actions/setup-node@v4`); fixar por SHA fica
   fora de escopo.

## Risks / Trade-offs

- [Piso fixado sobre uma base minúscula (só a `home`) oscila a cada código novo sem teste] →
  esperado: o piso é a rede de segurança; ao adicionar código com testes ele sobe junto, em
  commit explícito.
- [`docker compose run` demora (build da imagem + `npm ci`)] → aceitável para o tamanho do
  projeto; cache de camadas/npm pode vir depois se o tempo incomodar.
- [Porta 8000 e `restart` do Compose irrelevantes no CI, mas o `run` não publica portas] → usar
  `run --rm` (sem `up` do `web`), evitando conflito.
- [Versão fixa do OpenSpec envelhece] → atualizar junto com `openspec update` local.
- [Hooks de texto reescrevendo arquivos gerados ou de terceiros] → `exclude` explícito e conferir
  `git diff --stat` após a primeira execução.
- [Não dá para validar o workflow sem o GitHub] → verificar localmente com `act` se disponível;
  a verificação definitiva é a aba Actions do PR (por isso a change só pode ser arquivada com o
  CI verde, ver skill `fechar-change`).
