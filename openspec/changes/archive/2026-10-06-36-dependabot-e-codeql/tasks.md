# Tasks

## 1. Pendência da change 33

- [x] 1.1 Conferir na aba Summary da execução do CI na `main` (run 37475773106) que a seção "Cobertura de testes" traz a tabela, e no README da `main` que o selo do CI aparece verde; resultado: tabela presente no Summary (confirmado pelo usuário) e selo verde
- [x] 1.2 Marcar a task 3.3 de `33-selo-ci-e-resumo-de-cobertura` e rodar `openspec archive 33-selo-ci-e-resumo-de-cobertura --yes`; verificar que a pasta foi para `changes/archive/` e que `openspec/specs/continuous-integration/spec.md` ganhou o requisito "Resultado do CI visível sem abrir o log"

## 2. Dependabot

- [x] 2.1 Criar `.github/dependabot.yml` com `uv`, `npm`, `docker` (`/docker`), `docker-compose` e `github-actions`, semanal, agrupando minor/patch, com prefixo `chore(deps)` e label `dependencies`; verificar com `uvx pre-commit run --all-files` (check-yaml) e conferindo que cada `directory` aponta para arquivos existentes
- [x] 2.2 Habilitar os alertas e as atualizações de segurança do Dependabot no repositório, **após confirmar com o usuário**; verificar com `gh api repos/leodramaral/projeto-gestor-financeiro -q .security_and_analysis` mostrando `dependabot_security_updates` como `enabled`

## 3. CodeQL

- [x] 3.1 Criar `.github/workflows/codeql.yml` (PR, push na `main` e cron semanal, linguagem `python`, `security-events: write` e `contents: read` só no job); verificar o YAML com o pre-commit e confirmar que o `ci.yml` não ganhou permissões
- [x] 3.2 Confirmar no repositório da action a major vigente de `github/codeql-action` e usá-la; verificar que o workflow roda sem erro de versão no PR

## 4. Regras S do Ruff

- [x] 4.1 Acrescentar `"S"` ao `select` e o `per-file-ignores` de `**/tests/**` (`S101`, `S105`, `S106`, `S107`, `S314`) em `pyproject.toml`; verificar com `uvx ruff check --select S --exclude worktrees,node_modules .` que só resta o `S308` de `category_tags.py`
- [x] 4.2 Justificar o `mark_safe` de `category_icon` com `# noqa: S308` e o motivo; verificar que `uvx pre-commit run --all-files` passa e que os testes de categorias seguem verdes

## 5. Documentação

- [x] 5.1 Acrescentar ao README, na seção de qualidade e CI, o que o Dependabot, o CodeQL e as regras `S` do Ruff fazem, onde ver os achados e como descartar um falso positivo; verificar relendo o texto e os links

## 6. Verificação

- [x] 6.1 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e confirmar sucesso
- [x] 6.2 Abrir o PR e verificar que o job do CodeQL roda e conclui, e que a aba Security → Code scanning aparece com a análise
- [x] 6.3 Depois do merge, verificar em Insights → Dependency graph → Dependabot que não há erro de configuração e que a primeira rodada abre PRs `chore(deps)`; só então arquivar esta change
