# user-authentication Specification

## Purpose
Define como o usuário confirmado entra e sai da aplicação, por quanto tempo a sessão dura e como as
páginas privadas ficam protegidas de acesso anônimo.

## Requirements

### Requirement: Login por e-mail e senha
A aplicação DEVE autenticar o usuário por e-mail (sem diferenciar maiúsculas) e senha, e levá-lo ao
painel. Somente contas confirmadas DEVEM conseguir iniciar sessão. Credenciais inválidas DEVEM
produzir uma única mensagem genérica em português, igual para e-mail inexistente e senha errada.

#### Cenário: Login válido
- **QUANDO** um usuário com conta confirmada envia e-mail e senha corretos
- **ENTÃO** a sessão é iniciada
- **E** ele é redirecionado ao painel

#### Cenário: Credenciais inválidas
- **QUANDO** alguém envia um e-mail inexistente, ou um e-mail existente com senha errada
- **ENTÃO** nenhuma sessão é iniciada
- **E** a mesma mensagem genérica é exibida nos dois casos

#### Cenário: Conta não confirmada
- **QUANDO** alguém envia e-mail e senha corretos de uma conta ainda não confirmada
- **ENTÃO** nenhuma sessão é iniciada
- **E** a página informa que a conta precisa ser confirmada e oferece o reenvio do link

#### Cenário: Caixa do e-mail
- **QUANDO** o usuário digita o e-mail com maiúsculas diferentes das do cadastro
- **ENTÃO** o login funciona

### Requirement: Sessão com "lembrar de mim"
O login DEVE oferecer a opção "lembrar de mim". Sem ela, a sessão DEVE expirar ao fechar o
navegador; com ela, a sessão DEVE persistir por um prazo fixo e configurável.

#### Cenário: Sem lembrar de mim
- **QUANDO** o usuário faz login sem marcar "lembrar de mim"
- **ENTÃO** o cookie de sessão não tem data de expiração (expira ao fechar o navegador)

#### Cenário: Com lembrar de mim
- **QUANDO** o usuário faz login marcando "lembrar de mim"
- **ENTÃO** o cookie de sessão persiste pelo prazo configurado

### Requirement: Logout
A aplicação DEVE permitir encerrar a sessão por uma requisição `POST` protegida contra CSRF, acionada
pela ação "Sair" do menu de usuário no cabeçalho, e DEVE levar o usuário ao login. Uma requisição
`GET` NÃO DEVE encerrar a sessão.

#### Cenário: Logout
- **QUANDO** o usuário autenticado aciona "Sair" no menu de usuário
- **ENTÃO** a sessão é encerrada
- **E** ele é redirecionado ao login
- **E** o painel volta a exigir login

### Requirement: Páginas privadas exigem login
Toda página que não seja de autenticação, cadastro ou confirmação DEVE redirecionar o visitante
anônimo ao login, preservando o destino pretendido. O painel DEVE ser a página inicial do usuário
autenticado. Usuário autenticado que abre login ou cadastro DEVE ser redirecionado ao painel.

#### Cenário: Anônimo no painel
- **QUANDO** um visitante anônimo abre `/`
- **ENTÃO** é redirecionado ao login com o destino original no parâmetro `next`

#### Cenário: Destino após login
- **QUANDO** o login ocorre com um `next` interno válido
- **ENTÃO** o usuário vai a esse destino
- **E** um `next` externo é ignorado em favor do painel

#### Cenário: Autenticado em página de visitante
- **QUANDO** um usuário autenticado abre a página de login ou de cadastro
- **ENTÃO** é redirecionado ao painel

### Requirement: Limite de tentativas de login
O login DEVE contar as tentativas com credenciais erradas por e-mail (sem diferenciar maiúsculas) e,
ao atingir o limite configurável de falhas seguidas, DEVE bloquear novas tentativas daquele e-mail
por um tempo configurável. Durante o bloqueio, nenhuma sessão DEVE ser iniciada, nem com a senha
correta, e a página DEVE informar em português que o login está temporariamente bloqueado. O limite
DEVE valer igualmente para e-mails sem conta, e a mensagem de bloqueio NÃO DEVE revelar se o e-mail
tem conta. O bloqueio DEVE terminar sozinho ao fim do tempo, e um login bem-sucedido DEVE zerar a
contagem.

#### Cenário: Bloqueio após o limite
- **QUANDO** um e-mail acumula o número máximo de tentativas erradas seguidas
- **ENTÃO** a tentativa seguinte, mesmo com a senha correta, não inicia sessão
- **E** a página informa que o login está temporariamente bloqueado e que é preciso aguardar

#### Cenário: Abaixo do limite
- **QUANDO** um e-mail tem menos tentativas erradas do que o limite
- **ENTÃO** o login com a senha correta funciona
- **E** a contagem de falhas desse e-mail volta a zero

#### Cenário: Fim do bloqueio
- **QUANDO** o tempo de bloqueio passa
- **ENTÃO** o login com a senha correta volta a funcionar

#### Cenário: E-mail sem conta
- **QUANDO** alguém erra o login repetidas vezes com um e-mail que não tem conta
- **ENTÃO** atinge o mesmo limite e recebe a mesma mensagem de bloqueio de um e-mail com conta

#### Cenário: Bloqueio isolado por e-mail
- **QUANDO** um e-mail está bloqueado
- **ENTÃO** o login de outro e-mail não é afetado

#### Cenário: Caixa do e-mail
- **QUANDO** as tentativas erradas usam o mesmo e-mail com maiúsculas diferentes
- **ENTÃO** elas somam na mesma contagem

#### Cenário: Redefinição de senha encerra o bloqueio
- **QUANDO** o usuário bloqueado redefine a senha pelo link recebido por e-mail
- **ENTÃO** o bloqueio e a contagem de falhas desse e-mail são zerados
- **E** o login com a nova senha funciona
