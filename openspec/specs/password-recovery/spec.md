# password-recovery Specification

## Purpose
Define como o usuário que esqueceu a senha a redefine com segurança por um link enviado ao seu
e-mail, sem que a aplicação revele quais e-mails possuem conta.

## Requirements

### Requirement: Pedido de redefinição de senha
A aplicação DEVE oferecer, a partir da tela de login, o pedido de redefinição de senha por e-mail.
O e-mail com o link DEVE ser enviado somente a contas ativas e com e-mail confirmado, e o link DEVE
ser montado a partir da URL base configurada. A resposta ao pedido DEVE ser idêntica exista ou não
conta para o e-mail, e falha no envio NÃO DEVE alterar essa resposta.

#### Cenário: Atalho no login
- **QUANDO** o visitante abre a tela de login
- **ENTÃO** ela exibe o atalho "Esqueci minha senha" que leva ao pedido de redefinição

#### Cenário: Pedido para conta existente
- **QUANDO** alguém solicita a redefinição para o e-mail de uma conta ativa e confirmada
- **ENTÃO** um e-mail com o link de redefinição é enviado a esse endereço
- **E** a página informa que, se houver conta para o e-mail, as instruções foram enviadas

#### Cenário: E-mail inexistente ou conta sem direito ao envio
- **QUANDO** alguém solicita a redefinição para um e-mail sem conta, de conta inativa ou de conta não confirmada
- **ENTÃO** nenhum e-mail é enviado
- **E** a página exibe exatamente a mesma mensagem do cenário anterior

#### Cenário: Caixa do e-mail
- **QUANDO** o pedido usa maiúsculas diferentes das do cadastro
- **ENTÃO** o e-mail com o link é enviado normalmente

### Requirement: Link de redefinição de uso único e com prazo
O link de redefinição DEVE expirar após um prazo configurável e DEVE poder ser usado uma única vez:
definir a nova senha, ou qualquer outra alteração da senha da conta, DEVE invalidar os links
emitidos antes. O link NÃO DEVE servir à confirmação de conta, e o de confirmação NÃO DEVE servir à
redefinição.

#### Cenário: Link válido
- **QUANDO** o usuário abre o link de redefinição dentro do prazo
- **ENTÃO** a página exibe o formulário de nova senha

#### Cenário: Link expirado
- **QUANDO** o usuário abre o link depois do prazo de validade
- **ENTÃO** nenhuma senha é alterada
- **E** a página informa em português que o link é inválido, expirado ou já utilizado e oferece pedir um novo

#### Cenário: Link já usado
- **QUANDO** o usuário abre, depois de redefinir a senha, o mesmo link
- **ENTÃO** nenhuma senha é alterada
- **E** a página mostra a mesma mensagem do link expirado

#### Cenário: Link adulterado
- **QUANDO** o usuário abre um link com token ou identificador inválido
- **ENTÃO** nenhuma senha é alterada
- **E** a página mostra a mesma mensagem do link expirado, sem revelar se o identificador existe

### Requirement: Definição da nova senha
Ao abrir um link válido, a aplicação DEVE pedir a nova senha com confirmação e DEVE aplicar os
validadores de senha do Django, com erros em português. Definida a senha, ela DEVE ser armazenada
somente em hash, as sessões abertas da conta DEVEM ser encerradas, o usuário NÃO DEVE ser autenticado
automaticamente e DEVE ser levado ao login com aviso de sucesso.

#### Cenário: Senha redefinida
- **QUANDO** o usuário envia uma nova senha aceita pelos validadores, com a confirmação igual
- **ENTÃO** a senha da conta é trocada
- **E** ele é levado ao login com a informação de que a senha foi redefinida
- **E** entrar com a senha antiga falha e com a nova funciona

#### Cenário: Senha fraca ou confirmação diferente
- **QUANDO** o usuário envia uma senha rejeitada pelos validadores, ou duas senhas diferentes
- **ENTÃO** a senha da conta não muda
- **E** o formulário exibe, em português, o motivo da rejeição
- **E** o link continua válido

#### Cenário: Sessão aberta em outro navegador
- **QUANDO** a senha é redefinida enquanto a conta tem uma sessão aberta
- **ENTÃO** essa sessão deixa de ser aceita e exige novo login

### Requirement: Mensagens que não revelam contas
Nenhuma página, mensagem ou e-mail do fluxo de recuperação DEVE permitir distinguir um e-mail
cadastrado de um não cadastrado.

#### Cenário: Respostas indistinguíveis
- **QUANDO** o pedido de redefinição é feito para um e-mail cadastrado e depois para um não cadastrado
- **ENTÃO** o código de status, o destino e o texto exibidos são os mesmos nos dois casos
