## ADDED Requirements

### Requirement: Telas implementadas documentadas
Toda tela de usuário já implementada no app DEVE ter design em `design/`, num `.figcraft` por tela ou
fluxo: entrar (`login`), confirmação de conta (`signup_done`, `confirm`, `resend`), recuperação de senha
(`password_reset` e seus passos), lançamentos, categorias e perfil. Cada tela DEVE cobrir desktop claro, desktop escuro e mobile claro, e os
estados que o código exibe: erro de formulário, vazio, sucesso, modal aberto e confirmação de exclusão,
conforme existirem na tela. O painel (visão geral, categorias, fluxo, lançamentos e estado vazio) NÃO ENTRA por ora, porque o
FigCraft não executa o Chart.js e as telas ficariam sem os gráficos que as definem; elas NÃO DEVEM ser
desenhadas com gráfico aproximado. Telas ainda não implementadas NÃO DEVEM ter design nesta capacidade. E-mails
transacionais NÃO SÃO telas do app e ficam fora.

#### Cenário: Entrar documentado
- **QUANDO** a pasta `design/` é aberta
- **ENTÃO** existe `design/login.figcraft` com frames de `login` em desktop claro, desktop escuro e mobile claro
- **E** há o estado com erro de credenciais, com a mensagem real do formulário

#### Cenário: Painel fora do design
- **QUANDO** a pasta `design/` é aberta
- **ENTÃO** não há `.figcraft` do painel
- **E** nenhum frame mostra gráfico

#### Cenário: Lançamento em modal
- **QUANDO** o design de lançamentos é aberto
- **ENTÃO** há o frame da lista, o do formulário de lançamento aberto no modal e o da confirmação de exclusão

#### Cenário: Estado inexistente não é inventado
- **QUANDO** uma tela não tem determinado estado no código (por exemplo, o perfil não tem estado vazio)
- **ENTÃO** o design não cria esse frame

### Requirement: Telas autenticadas com dado de exemplo coerente
Os frames das telas autenticadas DEVEM usar dados de exemplo fictícios e coerentes entre si: o mesmo
usuário (`Maria Silva`, `maria@exemplo.com`), lançamentos iguais nas telas que os listam, e categorias com os nomes e cores reais do app. O design NÃO DEVE usar dado real de pessoa ou de
conta.

#### Cenário: Totais batem
- **QUANDO** os frames de lançamentos mostram a lista
- **ENTÃO** a contagem por categoria na tela de categorias bate com essa lista
