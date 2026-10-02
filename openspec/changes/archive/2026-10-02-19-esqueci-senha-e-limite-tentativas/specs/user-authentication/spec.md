# Spec Delta

## ADDED Requirements

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
