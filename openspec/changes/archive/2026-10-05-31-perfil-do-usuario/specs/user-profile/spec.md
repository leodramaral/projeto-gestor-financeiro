## Purpose

Define a página de perfil do usuário autenticado e o menu de usuário no cabeçalho, pelos quais ele
consulta os dados da própria conta e acessa as ações de conta.

## ADDED Requirements

### Requirement: Página de perfil somente leitura
A aplicação DEVE oferecer ao usuário autenticado uma página de perfil, no padrão da demo User Profile
do TailAdmin, que exiba apenas os dados do próprio usuário: nome, e-mail, situação da confirmação do
e-mail e data de cadastro, com um avatar de iniciais. A página NÃO DEVE oferecer edição de nenhum
dado, DEVE funcionar nos temas claro e escuro e em telas estreitas, e NÃO DEVE conter o nome ou o
logo "TailAdmin". Visitante anônimo DEVE ser redirecionado ao login, preservando o destino.

#### Cenário: Ver o próprio perfil
- **QUANDO** um usuário autenticado abre a página de perfil
- **ENTÃO** ela exibe o nome, o e-mail, a situação do e-mail e a data de cadastro dele
- **E** não exibe dados de outro usuário

#### Cenário: Perfil exige login
- **QUANDO** um visitante anônimo abre a página de perfil
- **ENTÃO** é redirecionado ao login, preservando o destino pretendido

#### Cenário: Sem edição
- **QUANDO** a página de perfil é exibida
- **ENTÃO** não há botão, link nem formulário de edição de perfil

#### Cenário: Tela estreita e tema escuro
- **QUANDO** a página de perfil é aberta em uma tela estreita ou no tema escuro
- **ENTÃO** o conteúdo permanece legível, sem rolagem horizontal, com contraste mínimo de 4,5:1

### Requirement: Menu de usuário no cabeçalho
O cabeçalho das telas autenticadas DEVE exibir, no canto superior direito, um card do usuário com
avatar de iniciais, nome e indicador de abertura. Ao ser acionado, o card DEVE abrir um menu com o
nome e o e-mail do usuário, o atalho "Ver perfil" e a ação "Sair". O menu DEVE fechar ao clicar fora
dele e ao pressionar Esc, DEVE ser operável por teclado e DEVE funcionar em telas estreitas. O
cabeçalho NÃO DEVE manter o botão "Sair" nem o nome do usuário soltos fora do menu.

#### Cenário: Abrir o menu
- **QUANDO** o usuário autenticado aciona o card do usuário no cabeçalho
- **ENTÃO** o menu exibe o nome e o e-mail dele
- **E** oferece "Ver perfil" e "Sair"

#### Cenário: Ver perfil pelo menu
- **QUANDO** o usuário aciona "Ver perfil" no menu
- **ENTÃO** é levado à página de perfil

#### Cenário: Fechar o menu
- **QUANDO** o menu está aberto e o usuário clica fora dele ou pressiona Esc
- **ENTÃO** o menu fecha

#### Cenário: Sem botão solto
- **QUANDO** qualquer tela autenticada é exibida com o menu fechado
- **ENTÃO** o cabeçalho não mostra um botão "Sair" nem o nome do usuário fora do card
