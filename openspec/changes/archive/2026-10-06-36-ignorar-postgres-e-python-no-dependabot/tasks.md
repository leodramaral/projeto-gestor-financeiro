# Tasks

## 1. Dependabot

- [x] 1.1 Acrescentar o `ignore` da major do `postgres` no `docker-compose` e o de major e minor do `python` no `docker` (`/docker`) em `.github/dependabot.yml`; verificar o YAML com o pre-commit e carregando o arquivo com um `python3 -c` que liste as entradas de `ignore` dos quatro ecossistemas
- [x] 1.2 Atualizar o comentário do topo do `dependabot.yml` com as quatro linhas fixadas (Django 5.2, Node 22, Postgres 16, Python 3.12); verificar relendo o arquivo

## 2. Documentação

- [x] 2.1 Atualizar no README o parágrafo "Versões fixadas por `ignore`" com Postgres e Python; verificar relendo o texto

## 3. Verificação

- [x] 3.1 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e confirmar sucesso
