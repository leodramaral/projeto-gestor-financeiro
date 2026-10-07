## ADDED Requirements

### Requirement: Banco selecionável por variável
O `web` DEVE usar o banco indicado por `APP_DB_NAME` quando a variável estiver definida, e `POSTGRES_DB`
quando não estiver. O servidor Postgres, o usuário e o volume continuam os mesmos.

#### Cenário: Sem APP_DB_NAME
- **QUANDO** o `.env` não define `APP_DB_NAME`
- **ENTÃO** a `DATABASE_URL` do `web` aponta para `POSTGRES_DB`, como antes desta change

#### Cenário: Com APP_DB_NAME
- **QUANDO** o `.env` define `APP_DB_NAME=gestor_x`
- **ENTÃO** o `web` conecta ao banco `gestor_x`
- **E** as migrações da subida são aplicadas nesse banco, sem tocar nos demais
- **E** o pytest cria o banco de teste `test_gestor_x`
