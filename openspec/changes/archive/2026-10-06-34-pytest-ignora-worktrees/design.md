# Design

## Context

O pytest sobe a partir da raiz sem `testpaths`, então percorre todas as pastas. `worktrees/` é
ignorada pelo `.gitignore` e pelo `.dockerignore`, mas o pytest não lê esses arquivos. O `addopts`
atual é `--ds=config.settings.test`.

## Goals / Non-Goals

**Goals:**
- Resultado igual do pytest com ou sem worktrees.

**Non-Goals:**
- Mudar o CI, ou restringir a coleta a uma lista de apps.

## Decisions

- **`--ignore=worktrees` em `addopts`.** Uma linha, e não substitui nenhum padrão do pytest.
  Alternativa descartada: `norecursedirs`, que **substitui** a lista padrão (`node_modules`, `.git`,
  `venv` e outras) e obrigaria a repeti-la. Também descartada: `testpaths` com os apps, que
  precisa de atualização a cada app novo e deixaria de rodar testes de um app esquecido sem avisar.

## Risks / Trade-offs

- [`--ignore` depende do caminho relativo à pasta de execução] → o fluxo do projeto roda o pytest na
  raiz (`/app` no contêiner); rodar de dentro de uma subpasta não é suportado hoje.
