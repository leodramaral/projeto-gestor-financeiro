## ADDED Requirements

### Requirement: Resultado do CI visível sem abrir o log
O repositório DEVE exibir o estado do workflow `CI` na `main` no `README.md`, e o job de testes
DEVE publicar a tabela de cobertura no resumo da execução. A publicação do resumo NÃO DEVE alterar
o resultado do job: ele continua falhando por teste quebrado ou cobertura abaixo do piso, e NÃO
DEVE passar nem falhar por causa do resumo.

#### Cenário: Selo no README
- **QUANDO** alguém abre o `README.md` no GitHub
- **ENTÃO** vê o selo de status do workflow `CI`
- **E** o selo leva à página do workflow

#### Cenário: Resumo com a cobertura
- **QUANDO** o job de testes termina, com sucesso ou não
- **ENTÃO** o resumo da execução traz a tabela de cobertura por arquivo, com as linhas sem teste

#### Cenário: Teste quebrado continua reprovando
- **QUANDO** algum teste falha e o resumo é publicado
- **ENTÃO** o job de testes falha
- **E** o resumo mostra a cobertura medida até ali

#### Cenário: Sem permissões nem segredos extras
- **QUANDO** o resumo é publicado
- **ENTÃO** o workflow continua com permissão `contents: read`
- **E** nenhum segredo do repositório é necessário
