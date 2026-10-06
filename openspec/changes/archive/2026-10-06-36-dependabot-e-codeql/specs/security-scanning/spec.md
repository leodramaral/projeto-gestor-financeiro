## Purpose
Mantém visíveis as vulnerabilidades das dependências e do código do projeto (no GitHub e no lint),
sem ferramenta externa e sem ampliar as permissões dos workflows existentes.

## ADDED Requirements

### Requirement: Atualização de dependências automatizada
O repositório DEVE ter o Dependabot configurado para propor, toda semana, atualizações das
dependências Python, npm, do Dockerfile, das imagens do Compose e das Actions dos workflows. Os PRs
DEVEM seguir o padrão de commit do projeto (`chore(deps)`) e as atualizações de minor e patch de um
mesmo ecossistema DEVEM chegar agrupadas em um único PR.

#### Cenário: Versão nova de uma dependência
- **QUANDO** sai uma versão nova de uma dependência declarada no projeto, dentro das restrições do
  `pyproject.toml`
- **ENTÃO** o Dependabot abre um PR de atualização na semana seguinte
- **E** o CI roda nesse PR como em qualquer outro

#### Cenário: Restrição de versão respeitada
- **QUANDO** existe versão nova fora da faixa declarada (por exemplo, Django 5.3 com `<5.3`)
- **ENTÃO** o Dependabot não propõe a atualização, e subir de faixa continua sendo decisão humana

#### Cenário: Várias atualizações pequenas
- **QUANDO** há mais de uma atualização de minor ou patch no mesmo ecossistema
- **ENTÃO** elas chegam num único PR agrupado, com título no padrão `chore(deps)`

### Requirement: Alertas de segurança de dependências
O repositório DEVE manter ativos os alertas e as atualizações de segurança do Dependabot, para que
uma versão com vulnerabilidade conhecida seja sinalizada e receba PR de correção sem esperar a
rotina semanal.

#### Cenário: Dependência com vulnerabilidade publicada
- **QUANDO** uma versão em uso passa a constar numa base pública de vulnerabilidades
- **ENTÃO** o GitHub registra o alerta na aba Security
- **E** o Dependabot abre o PR de correção quando existe versão corrigida

### Requirement: Análise estática de segurança do código
O repositório DEVE rodar a análise do CodeQL sobre o código Python a cada pull request, a cada push
na `main` e em rotina semanal, e DEVE publicar os achados em Security → Code scanning.

#### Cenário: PR com código vulnerável
- **QUANDO** um PR introduz um padrão vulnerável detectado pelo CodeQL (por exemplo, dado do usuário
  concatenado numa consulta SQL)
- **ENTÃO** o achado aparece como anotação no PR e na aba Code scanning

#### Cenário: Rotina semanal
- **QUANDO** chega o horário semanal agendado
- **ENTÃO** o CodeQL analisa a `main` mesmo sem push novo, para pegar consultas atualizadas

### Requirement: Permissões mínimas nos workflows de segurança
O workflow do CodeQL DEVE declarar a permissão `security-events: write` somente no job que a usa.
Os demais workflows NÃO DEVEM ganhar permissão de escrita por causa desta capacidade, e nenhum
segredo do repositório DEVE ser necessário para a varredura.

#### Cenário: Permissões do CI existente
- **QUANDO** o workflow `CI` roda depois desta change
- **ENTÃO** ele continua apenas com `contents: read`

#### Cenário: PR vindo do Dependabot
- **QUANDO** o CI roda num PR aberto pelo Dependabot, que não recebe segredos do repositório
- **ENTÃO** os jobs de qualidade, testes e OpenSpec executam normalmente

### Requirement: Achados tratados com justificativa
Os achados do CodeQL NÃO DEVEM bloquear o merge, e um achado descartado DEVE registrar o motivo
(falso positivo, usado só em testes ou risco aceito) no próprio alerta do GitHub.

#### Cenário: Falso positivo
- **QUANDO** um achado é avaliado e não representa risco real
- **ENTÃO** ele é descartado na aba Code scanning com o motivo e um comentário

### Requirement: Lint de segurança do código
O lint DEVE incluir as regras de segurança `S` e DEVE bloquear o commit e o CI quando uma delas for
violada em código de produção. Testes NÃO DEVEM ser reprovados por `assert`, senha fixa de fixture ou
leitura de XML controlado. Toda exceção em código de produção DEVE vir com `noqa` e justificativa.

#### Cenário: Padrão inseguro em código de produção
- **QUANDO** um arquivo fora de testes usa um padrão que a regra marca (por exemplo, `mark_safe`)
- **ENTÃO** o lint reprova, com arquivo e linha

#### Cenário: Exceção justificada
- **QUANDO** o uso é seguro e o `noqa` traz o motivo
- **ENTÃO** o lint passa e o motivo fica visível na revisão

#### Cenário: Testes
- **QUANDO** um teste usa `assert` ou uma senha de fixture
- **ENTÃO** o lint não reprova
