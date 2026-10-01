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
