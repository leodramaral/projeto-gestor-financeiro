# Spec Delta

## ADDED Requirements

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
