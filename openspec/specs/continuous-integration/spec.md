# continuous-integration Specification

## Purpose
Garante que toda alteração proposta por PR ou enviada à `main` seja validada automaticamente da
mesma forma que localmente: testes e artefatos do OpenSpec.

## Requirements

### Requirement: Execução em PR e na main
O CI DEVE rodar em todo pull request e em todo push na `main`, e DEVE cancelar a execução anterior
da mesma branch quando um novo push chegar.

#### Cenário: Pull request aberto ou atualizado
- **QUANDO** um PR é aberto ou recebe novos commits
- **ENTÃO** o CI executa os jobs de qualidade de código, de testes e de validação do OpenSpec

#### Cenário: Push consecutivo na mesma branch
- **QUANDO** um novo push chega enquanto a execução anterior da branch ainda roda
- **ENTÃO** a execução anterior é cancelada

### Requirement: Qualidade de código verificada
O CI DEVE executar os mesmos hooks do pre-commit sobre todos os arquivos e DEVE falhar se algum
hook reportar problema ou alterar arquivo.

#### Cenário: Código fora do padrão
- **QUANDO** um PR contém código que o lint reprova ou que a formatação alteraria
- **ENTÃO** o job de qualidade falha

#### Cenário: Código conforme
- **QUANDO** todos os hooks passam sem alterar arquivos
- **ENTÃO** o job de qualidade termina com sucesso

### Requirement: Testes no mesmo ambiente do desenvolvimento
O CI DEVE executar a suíte de testes pelo Docker Compose do projeto, contra o PostgreSQL do serviço
`db`, e DEVE falhar se a compilação do CSS, a subida do banco, qualquer teste ou o piso de cobertura falhar. O CI NÃO
DEVE depender de segredos do repositório: os valores do `.env` são gerados na execução.

#### Cenário: Suíte verde
- **QUANDO** todos os testes passam
- **ENTÃO** o job de testes termina com sucesso
- **E** o relatório de cobertura aparece no log

#### Cenário: Cobertura abaixo do piso
- **QUANDO** os testes passam mas a cobertura fica abaixo do piso configurado
- **ENTÃO** o job de testes falha

#### Cenário: Teste quebrado
- **QUANDO** algum teste falha
- **ENTÃO** o job de testes falha e o PR fica marcado como reprovado

#### Cenário: Execução sem segredos
- **QUANDO** o CI roda em um PR vindo de fork
- **ENTÃO** o job de testes executa normalmente, sem acesso a segredos do repositório

### Requirement: Validação dos artefatos do OpenSpec
O CI DEVE rodar `openspec validate --all` sem `--strict` e DEVE falhar se qualquer change ou spec
for inválida.

#### Cenário: Artefatos válidos
- **QUANDO** `openspec validate --all` termina com código `0`
- **ENTÃO** o job de validação termina com sucesso

#### Cenário: Spec inválida
- **QUANDO** um PR introduz uma spec ou change malformada
- **ENTÃO** o job de validação falha

### Requirement: Versão do OpenSpec fixada
O CI DEVE usar uma versão fixa e explícita do OpenSpec CLI, para que uma versão nova da ferramenta
não quebre PRs sem mudança no repositório.

#### Cenário: Versão do CLI
- **QUANDO** o job de validação instala o OpenSpec
- **ENTÃO** ele instala a versão declarada no workflow, não a mais recente
