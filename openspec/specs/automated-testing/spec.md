# automated-testing Specification

## Purpose
Define como os testes automatizados são executados no projeto, para que todos os integrantes
validem o código da mesma forma.

## Requirements

### Requirement: Testes executáveis no contêiner
A suíte de testes DEVE rodar com `docker compose exec web pytest`, usar as configurações do
ambiente de teste independentemente do `DJANGO_SETTINGS_MODULE` do `.env`, e usar o mesmo
PostgreSQL do serviço `db`. Os testes NÃO DEVEM tocar o banco usado em desenvolvimento.

#### Cenário: Execução da suíte
- **QUANDO** o desenvolvedor roda `docker compose exec web pytest` com o ambiente no ar
- **ENTÃO** os testes são coletados e executados e o comando termina com código `0` se todos passam

#### Cenário: Isolamento do banco
- **QUANDO** a suíte roda
- **ENTÃO** ela cria e remove um banco de testes próprio
- **E** os dados do banco de desenvolvimento permanecem intactos

### Requirement: Teste de fumaça da página inicial
A suíte DEVE conter ao menos um teste que confirme que `/` responde `200` e renderiza o layout
base.

#### Cenário: Regressão na página inicial
- **QUANDO** uma alteração quebra a rota `/` ou o template base
- **ENTÃO** o teste de fumaça falha

### Requirement: Cobertura com piso mínimo
A suíte DEVE medir a cobertura de linha e de branch dos pacotes `config` e `core`, listando as linhas
não cobertas, e DEVE falhar quando a cobertura total ficar abaixo do piso mínimo configurado. O
piso DEVE ser o valor medido, sem margem, e só pode ser elevado quando a cobertura real subir. As
migrações NÃO DEVEM entrar na medição.

#### Cenário: Cobertura igual ou acima do piso
- **QUANDO** a suíte roda com a opção de cobertura e a cobertura total é igual ou superior ao piso
- **ENTÃO** o log traz a porcentagem por arquivo e as linhas não cobertas
- **E** o comando termina com código `0` se todos os testes passam

#### Cenário: Cobertura abaixo do piso
- **QUANDO** a suíte roda com a opção de cobertura e a cobertura total fica abaixo do piso
- **ENTÃO** o comando termina com código diferente de `0`, mesmo com todos os testes passando
- **E** a mensagem informa a cobertura medida e o piso exigido

#### Cenário: Artefatos de cobertura
- **QUANDO** a cobertura gera arquivos locais (`.coverage`, `htmlcov/`)
- **ENTÃO** eles não aparecem no `git status`
