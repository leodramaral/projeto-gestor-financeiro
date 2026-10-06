## MODIFIED Requirements

### Requirement: Atualização de dependências automatizada
O repositório DEVE ter o Dependabot configurado para propor, toda semana, atualizações das
dependências Python, npm, do Dockerfile, das imagens do Compose e das Actions dos workflows. Os PRs
DEVEM seguir o padrão de commit do projeto (`chore(deps)`) e as atualizações de minor e patch de um
mesmo ecossistema DEVEM chegar agrupadas em um único PR. O Dependabot NÃO DEVE propor mudança de
versão major ou minor do Django nem de major do Node, para o projeto permanecer nas versões de
suporte longo (LTS) que adotou.

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

#### Cenário: Várias atualizações pequenas
- **QUANDO** há mais de uma atualização de minor ou patch no mesmo ecossistema
- **ENTÃO** elas chegam num único PR agrupado, com título no padrão `chore(deps)`
