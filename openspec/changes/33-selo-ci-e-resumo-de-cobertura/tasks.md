# Tasks

## 1. Resumo de cobertura no CI

- [x] 1.1 No job `tests` de `.github/workflows/ci.yml`, trocar o passo do pytest por um `sh -c` que roda `pytest --cov --cov-report=term-missing`, guarda o código de saída, grava `coverage report --format=markdown` em `.pytest_cache/cobertura.md` e sai com o código do pytest; verificar com `docker compose run` local que o arquivo é criado e que o código de saída é o do pytest
- [x] 1.2 Acrescentar o passo `if: always()` que anexa o arquivo a `$GITHUB_STEP_SUMMARY` e tolera a ausência dele; verificar rodando o trecho do shell localmente sem o arquivo (não pode falhar)
- [x] 1.3 Confirmar que as permissões do workflow continuam só `contents: read` e que nenhum segredo foi acrescentado, lendo o diff do `ci.yml`

## 2. Selo no README

- [x] 2.1 Acrescentar o selo do workflow `CI` no topo do `README.md` e verificar que a URL do `badge.svg` e o link da página do workflow apontam para `leodramaral/projeto-gestor-financeiro`

## 3. Verificação

- [x] 3.1 Simular teste quebrado localmente (sem commitar) e confirmar que o comando do passo 1.1 sai com código diferente de zero e ainda grava a tabela
- [x] 3.2 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e confirmar sucesso
- [ ] 3.3 Abrir o PR e verificar na aba Summary da execução que a tabela aparece e que o selo do README mostra o estado do CI
