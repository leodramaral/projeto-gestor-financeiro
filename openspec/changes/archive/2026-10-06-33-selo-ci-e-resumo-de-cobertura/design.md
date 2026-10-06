# Design

## Context

O job `tests` roda `docker compose run --rm -e COVERAGE_FILE=/tmp/.coverage web pytest --cov
--cov-report=term-missing`. O contêiner é descartado ao final, então o `.coverage` (em `/tmp`
dentro dele) some antes de qualquer passo seguinte do workflow. Só o checkout montado em `/app`
sobrevive, e o workflow já libera escrita em `static/dist` e `.pytest_cache`. O piso é o
`fail_under` do `pyproject.toml`, e o `coverage report` também o aplica.

## Goals / Non-Goals

**Goals:**
- Tabela de cobertura no resumo da execução, mesmo quando o job falha.
- O resultado do job continua sendo o do `pytest`.

**Non-Goals:**
- Comentar no PR, publicar check runs, histórico de cobertura ou serviço externo.

## Decisions

- **Gerar a tabela no mesmo `docker compose run`**, num `sh -c` que roda o `pytest`, guarda o
  código de saída, gera o Markdown e sai com o código guardado. Alternativa descartada: montar um
  volume para o `.coverage` e rodar um segundo contêiner, que adiciona uma subida de contêiner e
  um ponto de falha.
- **Arquivo em `.pytest_cache/cobertura.md`**: caminho já liberado para escrita e ignorado pelo
  git, sem mexer no passo de permissões.
- **Publicar com `if: always()`** num passo próprio que anexa o arquivo a `$GITHUB_STEP_SUMMARY`,
  tolerando a ausência do arquivo (falha antes do pytest). Mecanismo nativo do GitHub, sem action
  de terceiros.
- **`coverage report --format=markdown` com `|| true`** para o `fail_under` (que o comando
  também aplica) não mascarar o código de saída do `pytest`, que é quem decide o job.
- **Selo nativo do workflow** (`badge.svg` em `actions/workflows/ci.yml`), sem serviço externo.
  O repositório é público, então o selo funciona sem token.

## Risks / Trade-offs

- [O `sh -c` esconde o código de saída se for escrito errado] → verificar nos dois sentidos: job
  verde com testes verdes e job vermelho com um teste quebrado de propósito (na branch, sem
  commitar).
- [`coverage report` sem dados quando o pytest nem chega a rodar] → o passo do resumo ignora
  arquivo ausente ou vazio.
- [Tabela longa no resumo] → aceitável: o projeto tem poucos módulos; reavaliar se crescer.
