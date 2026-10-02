# Spec Delta

## Purpose

Define a identidade visual do Gestor Financeiro: a marca exibida ao usuário, o esquema de cores
verde e a alternância entre tema claro e escuro, de modo consistente em todas as telas e e-mails.

## ADDED Requirements

### Requirement: Marca própria do produto
A aplicação DEVE exibir a marca do Gestor Financeiro (logo, ícone e favicon) em todas as telas, e
NÃO DEVE exibir o nome ou o logo "TailAdmin" em nenhuma tela, título de página ou e-mail. A marca
DEVE ter versão legível sobre fundo claro e sobre fundo escuro, e o texto alternativo da imagem
DEVE ser o nome do produto.

#### Cenário: Marca no painel
- **QUANDO** um usuário autenticado abre o painel
- **ENTÃO** a barra lateral exibe a marca do Gestor Financeiro
- **E** o recolhimento da barra mostra apenas o ícone da marca

#### Cenário: Marca nas telas de visitante
- **QUANDO** um visitante abre login, cadastro ou recuperação de senha
- **ENTÃO** a tela exibe a marca do Gestor Financeiro
- **E** o favicon da aba é o da marca

#### Cenário: Sem rastro do template
- **QUANDO** qualquer página ou e-mail da aplicação é renderizado
- **ENTÃO** o conteúdo exibido ao usuário não contém "TailAdmin"
- **E** a licença do TailAdmin continua preservada no repositório

### Requirement: Esquema de cores verde
A cor de marca da aplicação DEVE ser o verde-azulado "jade", em escala completa para os temas claro e escuro,
aplicada a botões, links, foco, itens ativos e destaques, nas telas e nos e-mails. O texto sobre a
cor de marca e a cor de marca usada como texto DEVEM ter contraste mínimo de 4,5:1 com o fundo.

#### Cenário: Botão e link na cor de marca
- **QUANDO** uma tela exibe um botão principal ou um link de destaque
- **ENTÃO** a cor aplicada pertence à escala jade da marca
- **E** o texto do botão tem contraste mínimo de 4,5:1 com o fundo

#### Cenário: Tema escuro
- **QUANDO** o tema escuro está ativo
- **ENTÃO** textos e destaques na cor de marca usam um tom jade claro com contraste mínimo de 4,5:1
  sobre o fundo escuro

#### Cenário: E-mail transacional
- **QUANDO** a aplicação envia um e-mail transacional
- **ENTÃO** o cabeçalho e o botão principal do e-mail usam o jade da marca

### Requirement: Alternância de tema antes do login
As telas de visitante (login, cadastro, confirmação e recuperação de senha) DEVEM oferecer um
controle para alternar entre tema claro e escuro. A escolha DEVE persistir no navegador, valer
também no painel e ser aplicada antes de a página ser pintada, sem piscar. Sem escolha salva, o tema
DEVE ser o claro. O controle DEVE ser acessível por teclado e ter nome acessível.

#### Cenário: Trocar o tema no login
- **QUANDO** o visitante aciona o controle de tema na tela de login
- **ENTÃO** a página passa a usar o outro tema imediatamente
- **E** a escolha é guardada no navegador

#### Cenário: Escolha vale no painel
- **QUANDO** o visitante escolheu o tema escuro no login e entra na conta
- **ENTÃO** o painel abre no tema escuro

#### Cenário: Sem piscar
- **QUANDO** uma página é carregada com o tema escuro salvo
- **ENTÃO** a classe do tema é aplicada antes de a página ser pintada

#### Cenário: Armazenamento indisponível
- **QUANDO** o navegador bloqueia o armazenamento local
- **ENTÃO** a página continua funcionando no tema claro
- **E** o controle ainda alterna o tema durante a visita
