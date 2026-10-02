# user-accounts Specification

## Purpose
Define como uma pessoa cria sua conta e a confirma por e-mail, de modo que cada usuário tenha uma
identidade individual, única e verificada.

## Requirements

### Requirement: Cadastro de usuário
A aplicação DEVE permitir que um visitante crie uma conta informando nome, e-mail e senha. O e-mail
DEVE ser o identificador de login. A senha DEVE ser armazenada somente em hash e DEVE passar pelos
validadores de senha do Django. Erros de validação DEVEM ser exibidos em português do Brasil.

#### Cenário: Cadastro válido
- **QUANDO** o visitante envia nome, e-mail válido ainda não cadastrado e senha aceita
- **ENTÃO** a conta é criada como não confirmada, com a senha em hash
- **E** um e-mail de confirmação é enviado ao endereço informado
- **E** a página informa que o e-mail de confirmação foi enviado

#### Cenário: Senha fraca
- **QUANDO** o visitante envia uma senha rejeitada pelos validadores (curta, comum ou só numérica)
- **ENTÃO** nenhuma conta é criada
- **E** o formulário exibe, em português, o motivo da rejeição

#### Cenário: E-mail inválido
- **QUANDO** o visitante envia um e-mail malformado
- **ENTÃO** nenhuma conta é criada
- **E** o formulário exibe um erro em português no campo de e-mail

### Requirement: Unicidade de e-mail sem distinção de maiúsculas
O e-mail DEVE ser único sem diferenciar maiúsculas de minúsculas, e DEVE ser normalizado antes de
ser gravado. A unicidade DEVE ser garantida também pelo banco de dados. Ao tentar cadastrar um
e-mail que já possui conta, a aplicação DEVE exibir erro em português no campo de e-mail e NÃO DEVE
criar outra conta nem enviar e-mail ao endereço existente.

#### Cenário: E-mail já cadastrado com outra caixa
- **QUANDO** o visitante se cadastra com `Ana@Exemplo.com` e já existe conta `ana@exemplo.com`
- **ENTÃO** nenhuma segunda conta é criada
- **E** o formulário exibe, no campo de e-mail, o aviso de que o e-mail já está cadastrado
- **E** nenhum e-mail é enviado

#### Cenário: Duplicidade no banco
- **QUANDO** duas contas com o mesmo e-mail, diferindo só na caixa, são gravadas diretamente
- **ENTÃO** o banco rejeita a segunda

### Requirement: Confirmação de conta por link
A aplicação DEVE enviar, no cadastro, um link de confirmação de uso único e com prazo de validade,
montado a partir da URL base configurada. Abrir um link válido DEVE marcar a conta como confirmada.
Um link expirado, adulterado ou já usado DEVE exibir mensagem clara em português e oferecer o
reenvio, sem confirmar nada.

#### Cenário: Link válido
- **QUANDO** o usuário abre o link de confirmação dentro do prazo
- **ENTÃO** a conta passa a confirmada
- **E** a página informa o sucesso e leva ao login

#### Cenário: Link expirado
- **QUANDO** o usuário abre o link depois do prazo de validade
- **ENTÃO** a conta continua não confirmada
- **E** a página informa que o link expirou e oferece o reenvio

#### Cenário: Link já usado
- **QUANDO** o usuário abre um link de uma conta já confirmada
- **ENTÃO** nada muda
- **E** a página mostra a mesma mensagem genérica de link inválido, expirado ou já utilizado, sem revelar o estado da conta, e oferece o login e o reenvio

#### Cenário: Link adulterado
- **QUANDO** o usuário abre um link com token ou identificador inválido
- **ENTÃO** nenhuma conta é confirmada
- **E** a página informa que o link é inválido e oferece o reenvio

### Requirement: Reenvio do link de confirmação
A aplicação DEVE permitir solicitar novo link de confirmação a partir de um e-mail. A resposta DEVE
ser a mesma exista ou não conta para o e-mail, e o e-mail só DEVE ser enviado a contas existentes
e ainda não confirmadas.

#### Cenário: Reenvio para conta não confirmada
- **QUANDO** alguém solicita o reenvio para o e-mail de uma conta não confirmada
- **ENTÃO** um novo e-mail de confirmação é enviado
- **E** a página informa que, se houver conta pendente, o e-mail foi enviado

#### Cenário: Reenvio para e-mail desconhecido ou conta já confirmada
- **QUANDO** alguém solicita o reenvio para um e-mail sem conta ou de conta já confirmada
- **ENTÃO** nenhum e-mail de confirmação é enviado
- **E** a página exibe a mesma mensagem do cenário anterior
