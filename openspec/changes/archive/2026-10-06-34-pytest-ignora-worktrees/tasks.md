# Tasks

## 1. Pytest

- [x] 1.1 Acrescentar `--ignore=worktrees` ao `addopts` de `pyproject.toml`; verificar com `docker compose exec web pytest -q` na raiz (com a worktree antiga presente) que a coleta passa sem erro e que a contagem de testes é a da suíte do projeto
- [x] 1.2 Criar temporariamente `worktrees/_probe/test_probe.py` com um teste que falha, rodar o pytest na raiz e confirmar que ele não é coletado; remover o arquivo em seguida

## 2. Verificação

- [x] 2.1 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e confirmar sucesso
