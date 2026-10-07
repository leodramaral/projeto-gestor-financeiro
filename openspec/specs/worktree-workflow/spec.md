# worktree-workflow Specification

## Purpose
TBD - created by archiving change 49-banco-por-worktree. Update Purpose after archive.

## Requirements

### Requirement: Criação de worktree com banco próprio
`scripts/worktree new <nome> [branch]` DEVE criar a worktree em `worktrees/<nome>`, copiar para ela os
arquivos locais não versionados da lista do script (ao menos `.env`), definir `APP_DB_NAME=gestor_<nome>`
no `.env` da worktree e criar o banco `gestor_<nome>` como cópia do banco principal. O comando NÃO DEVE
alterar o banco principal e DEVE falhar, sem deixar worktree ou banco pela metade, se algum passo falhar.

#### Cenário: Worktree nova
- **QUANDO** o usuário roda `scripts/worktree new x` com o `db` no ar
- **ENTÃO** existe `worktrees/x` com `.env` contendo `APP_DB_NAME=gestor_x`
- **E** o banco `gestor_x` contém os dados do banco principal

#### Cenário: Nome inválido para Postgres
- **QUANDO** o `<nome>` tem caracteres fora de letras, dígitos e `_` (como `-`)
- **ENTÃO** o nome do banco usa `_` no lugar deles, em minúsculas
- **E** nome que resulte vazio ou acima do limite de 63 caracteres do Postgres é recusado antes de criar qualquer coisa

#### Cenário: Banco ou worktree já existe
- **QUANDO** `worktrees/<nome>` ou o banco `gestor_<nome>` já existe
- **ENTÃO** o comando recusa, sem sobrescrever nada

### Requirement: Remoção de worktree e do banco
`scripts/worktree remove <nome>` DEVE remover a worktree e apagar o banco dela. O comando DEVE recusar
apagar o banco principal e DEVE conferir que o nome do banco a apagar é o derivado de `<nome>` (prefixo
`gestor_`) e diferente de `POSTGRES_DB`.

#### Cenário: Remoção normal
- **QUANDO** o usuário roda `scripts/worktree remove x`
- **ENTÃO** `worktrees/x` e o banco `gestor_x` deixam de existir

#### Cenário: Tentativa de apagar o principal
- **QUANDO** o nome de banco derivado coincide com o banco principal
- **ENTÃO** o comando encerra com erro sem apagar banco algum

### Requirement: Ressincronização do banco
`scripts/worktree resync <nome>` DEVE recriar o banco `gestor_<nome>` a partir do principal, descartando
os dados atuais dele, mesmo com conexões abertas, e NÃO DEVE alterar o banco principal.

#### Cenário: Banco da worktree desatualizado
- **QUANDO** o principal recebeu dados novos depois da criação e o usuário roda `scripts/worktree resync x`
- **ENTÃO** `gestor_x` passa a ter os dados atuais do principal
- **E** o `web` conectado a `gestor_x` não impede a operação

### Requirement: Isolamento entre worktrees
Migração aplicada, dado gravado ou banco de teste criado numa worktree NÃO DEVEM afetar o banco principal
nem o de outra worktree.

#### Cenário: Testes simultâneos
- **QUANDO** o pytest roda ao mesmo tempo em duas worktrees com `APP_DB_NAME` distintos
- **ENTÃO** cada uma usa seu próprio `test_gestor_<nome>` e as rodadas não colidem
