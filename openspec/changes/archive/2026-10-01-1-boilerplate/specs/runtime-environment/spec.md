## ADDED Requirements

### Requirement: Execução em contêineres
A aplicação e o PostgreSQL DEVEM subir juntos com `docker compose up`, sem dependência instalada
na máquina além do Docker.

#### Cenário: Subida do ambiente local
- **QUANDO** o desenvolvedor roda `docker compose up --build` com um `.env` válido
- **ENTÃO** os serviços `web` e `db` ficam saudáveis
- **E** a aplicação responde em `127.0.0.1:8000`

### Requirement: Dados do banco persistem entre execuções
O PostgreSQL DEVE gravar seus dados em volume nomeado, e a porta da aplicação NÃO DEVE ser exposta
fora de `127.0.0.1` pelo compose base.

#### Cenário: Reinício dos contêineres
- **QUANDO** os contêineres são recriados sem remover o volume
- **ENTÃO** os dados do banco continuam disponíveis

### Requirement: Migrações aplicadas na subida
O serviço `web` DEVE aplicar as migrações pendentes antes de começar a atender requisições, e NÃO
DEVE subir se a migração falhar.

#### Cenário: Banco novo
- **QUANDO** o desenvolvedor roda `docker compose up --build` com o volume do banco vazio
- **ENTÃO** as migrações são aplicadas antes de o servidor começar a responder
- **E** as tabelas do Django existem no banco

#### Cenário: Sem migração pendente
- **QUANDO** o ambiente é reiniciado sem migrações novas
- **ENTÃO** a aplicação sobe normalmente, sem alterar o banco
