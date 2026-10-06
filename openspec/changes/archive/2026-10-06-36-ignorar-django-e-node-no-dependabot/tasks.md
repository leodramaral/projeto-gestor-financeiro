# Tasks

## 1. Dependabot

- [x] 1.1 Acrescentar `ignore` do Django (major e minor) no ecossistema `uv` e do Node (major) no `docker-compose` em `.github/dependabot.yml`; verificar o YAML com o pre-commit e conferindo as entradas com um `python3 -c` que carregue o arquivo
- [x] 1.2 Corrigir o comentário do topo do `dependabot.yml`, que dizia que o Dependabot respeita as faixas do `pyproject.toml`; verificar relendo o arquivo

## 2. Documentação

- [x] 2.1 Corrigir no README o parágrafo sobre as faixas do `pyproject.toml` e explicar como voltar a aceitar uma versão (remover o `ignore`); verificar relendo o texto

## 3. Verificação

- [x] 3.1 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e confirmar sucesso
