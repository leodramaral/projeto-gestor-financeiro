# Proposal

## Why

A Issue #1 ("Configuração do ambiente") ainda tem um critério de aceitação em aberto: o CI deve
rodar testes e `openspec validate --all` em cada PR. Hoje a verificação depende de cada integrante
lembrar de rodá-la localmente; sem o CI, uma regressão chega à `main` sem ninguém ver. Também não
há lint, formatação nem pre-commit, então o estilo depende de revisão manual. A stack de
testes (pytest + pytest-django, isolamento de banco, teste de fumaça) já existe, mas não mede
cobertura, o que deixa o CI sem um indicador do que a suíte exercita e sem proteção contra queda
de cobertura.

## What Changes

- Novo workflow do GitHub Actions, disparado em `pull_request` e em `push` na `main`, com três jobs
  independentes: qualidade de código (lint + formatação), testes (no mesmo Docker Compose usado
  localmente) e validação do OpenSpec (`openspec validate --all`, sem `--strict`).
- Lint, formatação e complexidade ciclomática (McCabe, limite 10, bloqueante) com Ruff (configuração em `pyproject.toml`) e pre-commit (`.pre-commit-config.yaml`)
  com Ruff e verificações básicas de arquivo; o CI executa os mesmos hooks, uma única fonte de regras.
- Aplicar a formatação uma vez ao código existente, num commit próprio.
- Atualizar `openspec/config.yaml`: lint, pre-commit e CI deixam de constar como fora de escopo.
- Adicionar `pytest-cov` ao grupo `dev` e medir a cobertura de linha e de branch de `config` e `core`, com piso mínimo (`fail_under`) fixado
  no valor medido, como no projeto analytics; abaixo dele a execução dos
  testes falha. Os parâmetros ficam em `[tool.coverage.*]` no `pyproject.toml`.
- Atualizar o README (testes, qualidade de código, pre-commit e CI) e o `AGENTS.md` (comandos e regra
  de que o CI precisa passar antes do merge).
- Fora de escopo: teste de mutação (descartado pela equipe), lint de templates/CSS/JS, checagem de
  tipos, `import-linter`, deploy/CD, matriz de versões e proteção de branch (configuração do GitHub,
  não do repositório).

## Capabilities

### New Capabilities
- `code-quality`: lint, formatação e pre-commit que mantêm o código dentro do padrão.
- `continuous-integration`: o que o CI executa em cada PR/push e quando ele deve falhar.

### Modified Capabilities
- `automated-testing`: a suíte passa a medir cobertura (linha e branch) e a exigir um piso mínimo.

## Impact

- Novo `.github/workflows/ci.yml`, `.pre-commit-config.yaml` e seção `[tool.ruff]` no `pyproject.toml`.
- Código Python existente reformatado pelo Ruff; `openspec/config.yaml` ajustado.
- `pyproject.toml` e `uv.lock` (`pytest-cov`); a imagem do `web` já instala o grupo `dev`.
- `README.md` e `AGENTS.md`.
- Issue: #1 (fecha o último critério de aceitação de CI).
