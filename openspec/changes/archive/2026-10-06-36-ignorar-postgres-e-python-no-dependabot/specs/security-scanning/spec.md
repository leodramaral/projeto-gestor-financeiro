## MODIFIED Requirements

### Requirement: Atualização de dependências automatizada
O repositório DEVE ter o Dependabot configurado para propor, toda semana, atualizações das
dependências Python, npm, do Dockerfile, das imagens do Compose e das Actions dos workflows. Os PRs
DEVEM seguir o padrão de commit do projeto (`chore(deps)`) e as atualizações de minor e patch de um
mesmo ecossistema DEVEM chegar agrupadas em um único PR. O Dependabot NÃO DEVE propor mudança de
versão major ou minor do Django, de major do Node, de major do PostgreSQL nem de major ou minor do
Python da imagem base, para o projeto permanecer nas versões que adotou: trocá-las exige migração
(dados, no caso do banco) e é decisão humana.

#### Cenário: Versão nova de uma dependência
- **QUANDO** sai uma versão nova de uma dependência sem regra de ignorar
- **ENTÃO** o Dependabot abre um PR de atualização na semana seguinte
- **E** o CI roda nesse PR como em qualquer outro

#### Cenário: Restrição de versão respeitada
- **QUANDO** sai uma versão major ou minor do Django (por exemplo, 6.1)
- **ENTÃO** o Dependabot não abre PR dela
- **E** os patches da linha adotada (5.2.x) continuam chegando

#### Cenário: Node em major nova
- **QUANDO** sai uma major do Node (por exemplo, 26) para a imagem do serviço `css`
- **ENTÃO** o Dependabot não abre PR dela, e adotá-la continua sendo decisão humana

#### Cenário: PostgreSQL em major nova
- **QUANDO** sai uma major do PostgreSQL (por exemplo, 18) para a imagem do serviço `db`
- **ENTÃO** o Dependabot não abre PR dela
- **E** subir de major continua sendo uma migração planejada dos dados

#### Cenário: Python em versão nova
- **QUANDO** sai uma major ou minor do Python (por exemplo, 3.13) para a imagem do `Dockerfile`
- **ENTÃO** o Dependabot não abre PR dela, e adotá-la continua sendo decisão humana

#### Cenário: Várias atualizações pequenas
- **QUANDO** há mais de uma atualização de minor ou patch no mesmo ecossistema
- **ENTÃO** elas chegam num único PR agrupado, com título no padrão `chore(deps)`
