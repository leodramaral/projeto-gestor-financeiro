# Spec Delta

## Purpose

Mantém o código Python do projeto num padrão único de estilo e livre de erros estáticos comuns,
verificado da mesma forma na máquina de cada integrante e no CI.

## ADDED Requirements

### Requirement: Lint e formatação padronizados
O projeto DEVE definir uma única configuração de lint e formatação para o código Python, e o código
versionado DEVE estar em conformidade com ela. Migrações geradas pelo Django NÃO DEVEM ser
reformatadas.

#### Cenário: Código em conformidade
- **QUANDO** o lint e a verificação de formatação rodam sobre o repositório
- **ENTÃO** ambos terminam com código `0` e sem apontar problemas

#### Cenário: Código fora do padrão
- **QUANDO** um arquivo tem import desordenado, variável não usada ou linha fora do formato
- **ENTÃO** a ferramenta aponta o problema com arquivo e linha

### Requirement: Limite de complexidade ciclomática
O lint DEVE reprovar qualquer função com complexidade ciclomática (McCabe) acima de 10, e esse
limite DEVE bloquear o commit e o CI, sem isenção.

#### Cenário: Função dentro do limite
- **QUANDO** todas as funções têm complexidade igual ou inferior a 10
- **ENTÃO** o lint não aponta problema de complexidade

#### Cenário: Função acima do limite
- **QUANDO** uma função tem complexidade 11 ou mais
- **ENTÃO** o lint reprova, informando a função e a complexidade medida

### Requirement: Verificação automática antes do commit
O repositório DEVE trazer a configuração do pre-commit com os hooks de lint, formatação e higiene de
arquivos (espaço no fim da linha, nova linha final, YAML válido, marcador de merge, chave privada
e arquivo grande). Os hooks DEVEM usar versões fixas e NÃO DEVEM alterar arquivos gerados nem
lockfiles.

#### Cenário: Commit com problema corrigível
- **QUANDO** o desenvolvedor, com o hook instalado, commita um arquivo com problema que o hook corrige
- **ENTÃO** o commit é interrompido, o arquivo é corrigido e o desenvolvedor revisa e commita de novo

#### Cenário: Commit com chave privada
- **QUANDO** o commit inclui uma chave privada
- **ENTÃO** o hook reprova o commit

#### Cenário: Execução idempotente
- **QUANDO** os hooks rodam duas vezes seguidas sobre todos os arquivos
- **ENTÃO** a segunda execução não altera nenhum arquivo
