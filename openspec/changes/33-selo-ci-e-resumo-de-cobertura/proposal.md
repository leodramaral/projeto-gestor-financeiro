# Proposal

## Why

O resultado do quality gate só aparece para quem abre o log do job: o README não diz se a `main` está
verde e a tabela de cobertura fica enterrada no meio do log do `pytest`. Tornar os dois visíveis
dá a quem chega ao repositório, e a quem revisa um PR, a resposta em segundos. Origem: Issue #33.

## What Changes

- O `README.md` passa a exibir o selo de status do workflow `CI`, apontando para a página do
  workflow no GitHub.
- O job `tests` passa a publicar, no resumo da execução (aba *Summary* do Actions), a tabela de
  cobertura em Markdown gerada pelo `coverage report --format=markdown`.
- A tabela é gerada no mesmo contêiner e no mesmo comando do `pytest`, porque o contêiner é
  descartado (`--rm`) e o arquivo de cobertura vive em `/tmp`.
- O comando de testes continua decidindo o resultado do job: o código de saída do `pytest`
  (testes quebrados ou cobertura abaixo do piso) é preservado.

Fora do escopo: comentário de cobertura no PR, check runs com JUnit/anotações, Codecov ou
Coveralls, e qualquer mudança em `fail_under`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `continuous-integration`: acrescenta o requisito de que o resultado do CI e a cobertura sejam
  visíveis sem abrir o log (selo no README e resumo da execução).

## Impact

- `.github/workflows/ci.yml` (job `tests`): o passo de pytest e um passo novo de publicação do
  resumo.
- `README.md`: uma linha de selo.
- Nenhuma permissão nova do `GITHUB_TOKEN` (continua `contents: read`), nenhum segredo, nenhuma
  dependência de terceiros.
