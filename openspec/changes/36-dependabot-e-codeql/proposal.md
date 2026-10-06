# Proposal

## Why

O quality gate valida estilo, testes, cobertura e specs, mas não olha duas coisas que pesam num app
financeiro: as **dependências** (Django, psycopg, imagens Docker, Actions) e as **vulnerabilidades
no código escrito aqui**. Hoje ninguém é avisado de uma versão com falha conhecida, e uma injeção de
SQL ou um XSS só seria pego na revisão humana. Origem: Issue #36.

## What Changes

- Novo `.github/dependabot.yml`: atualizações semanais de versão para Python (`uv`), npm, Dockerfile,
  imagens do `docker-compose.yml` e GitHub Actions, agrupando atualizações de minor/patch por
  ecossistema e usando o prefixo de commit `chore(deps)`.
- Habilitar no repositório os alertas e as atualizações de segurança do Dependabot (hoje
  `dependabot_security_updates` está desabilitado).
- Ativar as regras `S` (flake8-bandit) do Ruff, com `**/tests/**` isento de `S101`, `S105`, `S106`,
  `S107` e `S314`, e um `# noqa: S308` justificado em `transactions/templatetags/category_tags.py`.
  Medido na base atual: 729 achados, 728 em testes e 1 em código de produção (`mark_safe` de
  `category_icon`).
- Novo workflow `.github/workflows/codeql.yml`: análise de segurança do código Python a cada PR, a
  cada push na `main` e uma vez por semana, com os achados em Security → Code scanning.
- A permissão `security-events: write` fica só no job do CodeQL; os demais workflows seguem com
  `contents: read`.
- Documentar no README (seção de qualidade e CI) o que cada ferramenta faz e como tratar um alerta.
- Os achados do CodeQL **não bloqueiam** o merge por ora, e falso positivo é descartado no próprio
  GitHub com justificativa (ver `design.md`).
- Inclui o arquivamento da change `33-selo-ci-e-resumo-de-cobertura` nesta mesma branch e PR, por
  decisão do projeto: a task 3.3 daquela change só podia ser provada depois do PR #35.

Fora do escopo: análise de JavaScript,
tornar o CodeQL um check obrigatório no ruleset da `main`.

## Capabilities

### New Capabilities
- `security-scanning`: varredura contínua de dependências (Dependabot) e do código (CodeQL e regras `S`
  do Ruff), com os achados visíveis no GitHub e permissões mínimas.

### Modified Capabilities

## Impact

- Arquivos novos: `.github/dependabot.yml` e `.github/workflows/codeql.yml`.
- `pyproject.toml` (`select` e `per-file-ignores` do Ruff) e `transactions/templatetags/category_tags.py`
  (um `noqa` justificado).
- `README.md`: parágrafo na seção de qualidade e CI.
- Configuração do repositório no GitHub (Settings → Advanced Security), fora do código.
- Passa a chegar PR de atualização toda semana, e cada um roda o CI existente (que não usa segredos).
- Nenhuma dependência de runtime nova.
