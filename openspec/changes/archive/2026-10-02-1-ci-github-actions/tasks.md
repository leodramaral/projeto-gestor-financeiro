# Tasks

## 1. Qualidade de código local

- [x] 1.1 Adicionar `[tool.ruff]` e `[tool.ruff.lint]` ao `pyproject.toml` (regras `E, F, I, B, UP, DJ, C90`, `[tool.ruff.lint.mccabe] max-complexity = 10`, `line-length = 100`, `py312`, migrações excluídas); verificar com `uvx ruff check .` e `uvx ruff format --check .` listando o que há a corrigir
- [x] 1.2 Aplicar `ruff check --fix` e `ruff format` ao código existente, sem mudar comportamento (funções acima de complexidade 10, se houver, são refatoradas aqui); verificar que `docker compose run --rm web pytest` continua passando e que o diff contém só estilo (commit próprio)
- [x] 1.3 Criar `.pre-commit-config.yaml` (Ruff + pre-commit-hooks, com `rev` fixo e `exclude` para `uv.lock`, `package-lock.json`, `openspec/`, `static/dist/`); verificar com `uvx pre-commit run --all-files` terminando com código `0` e sem alterar arquivos na segunda execução
- [x] 1.4 Instalar o hook de commit (`uvx pre-commit install`) e verificar que um commit com import fora de ordem ou espaço no fim da linha é barrado/corrigido

## 2. Cobertura nos testes

- [x] 2.1 Adicionar `pytest-cov` ao grupo `dev` do `pyproject.toml` e atualizar o `uv.lock`; criar `[tool.coverage.run]` (`branch = true`, `source = ["config", "core"]`, `omit` de migrações) e `[tool.coverage.report]` (`show_missing = true`); verificar com `docker compose build web` e `docker compose run --rm web pytest --cov --cov-report=term-missing` mostrando a tabela com branch e código de saída `0`
- [x] 2.2 Fixar `fail_under` em `[tool.coverage.report]` no valor medido na 2.1, sem arredondar para cima; verificar que a suíte passa com ele e que falha (código diferente de `0`) ao remover temporariamente um teste e o `fail_under` não é atingido (reverter em seguida)
- [x] 2.3 Conferir que `.coverage` e `htmlcov/` não aparecem no `git status` após a execução (já estão no `.gitignore`; ajustar se não estiverem)

## 3. Workflow do GitHub Actions

- [x] 3.1 Criar `.github/workflows/ci.yml` com gatilhos `pull_request` e `push` na `main`, `concurrency` por ref e `permissions: contents: read`; verificar a sintaxe com `actionlint` (via contêiner) ou, na falta, com `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
- [x] 3.2 Implementar o job `quality`: `astral-sh/setup-uv` e `uvx pre-commit run --all-files`; verificar rodando o mesmo comando num clone limpo com código `0`
- [x] 3.3 Implementar o job `tests`: gerar `.env` a partir de `.env.example` com `SECRET_KEY` e `POSTGRES_PASSWORD` aleatórios, `docker compose up -d --wait db`, `docker compose run --rm web pytest --cov --cov-report=term-missing`; verificar reproduzindo os mesmos comandos num clone limpo (sem `.env` nem `static/dist/`) e terminando com código `0`
- [x] 3.4 Implementar o job `openspec`: `setup-node`, `npm install -g @fission-ai/openspec@1.13.1` e `openspec validate --all`; verificar rodando os comandos localmente com a mesma versão
- [x] 3.5 Verificar que o CI reprova: introduzir temporariamente código fora do padrão, um teste quebrado e uma spec malformada num branch descartável e confirmar que cada job falha; reverter em seguida
- [x] 3.6 Corrigir a falha do job `tests` no primeiro PR (#17): os contêineres rodam como uid 1000 (`node` no `css`, `app` no `web`) e não conseguem gravar no checkout do runner (uid 1001): `EACCES` em `static/dist` e `sqlite3.OperationalError` ao gravar `.coverage`. Liberar escrita no workspace (`chmod -R a+rwX .`) num passo anterior do workflow; verificar simulando o dono do diretório com uid 1001 num clone limpo (`css` conclui; reproduzido e corrigido) e, no PR, com o job `tests` verde

## 4. Documentação

- [x] 4.1 Atualizar o `README.md` (comando de testes com cobertura, lint/formatação, instalação do pre-commit e uma seção sobre o CI: o que roda, como ler a aba Actions, como reproduzir localmente) e o `AGENTS.md` (comandos de lint, pre-commit e cobertura e regra de que o CI deve estar verde antes do merge); verificar que os comandos documentados funcionam copiados e colados
- [x] 4.2 Ajustar `openspec/config.yaml` (seção "Fora de escopo") e `AGENTS.md` ("Regras") para refletir que lint, pre-commit e CI agora existem; verificar com `openspec validate --all`

## 5. Verificação final

- [x] 5.1 Rodar `openspec validate --all` e abrir o PR com `Closes #1`; verificar na aba Actions do PR que os jobs `quality`, `tests` e `openspec` passam
