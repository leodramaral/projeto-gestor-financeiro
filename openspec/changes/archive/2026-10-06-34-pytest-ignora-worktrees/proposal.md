# Proposal

## Why

Rodar `pytest` na raiz do checkout principal faz o pytest entrar em `worktrees/<nome>/` (pasta local,
não versionada, onde o `AGENTS.md` manda criar as worktrees) e coletar os testes delas. Com uma
worktree antiga presente a coleta quebra com erros e o pytest sai com código 2. No CI isso não
acontece, porque `worktrees/` não é versionado: o problema é só local. Origem: Issue #34.

## What Changes

- `addopts` do pytest em `pyproject.toml` passa a incluir `--ignore=worktrees`.
- A spec `automated-testing` ganha o requisito de que a coleta se restrinja ao código do projeto.

Fora do escopo: `testpaths` com a lista de apps (exigiria atualização a cada app novo) e mudanças
no CI.

## Capabilities

### New Capabilities

### Modified Capabilities
- `automated-testing`: a suíte de testes não coleta o conteúdo de `worktrees/`.

## Impact

- `pyproject.toml` (uma opção do pytest).
- Quem roda `docker compose exec web pytest` na raiz passa a ter o mesmo resultado com ou sem
  worktrees presentes. O CI não muda.
