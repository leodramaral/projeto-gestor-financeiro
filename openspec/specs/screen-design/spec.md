# screen-design Specification

## Purpose
Define onde o design das telas do Gestor Financeiro mora no repositório, o que é versionado, como os
frames são nomeados e exportados e a exigência de que o design reflita o código, para que qualquer
pessoa abra, inspecione e revise o design sem ferramenta externa ao projeto.

## Requirements

### Requirement: Design versionado na pasta design
O repositório DEVE ter a pasta `design/` na raiz, com um arquivo `.figcraft` por tela ou por fluxo como
**artefato de design** (fonte editável). O design NÃO DEVE ficar só fora do repositório. Os PNGs exportados
dos frames são derivados do `.figcraft` e NÃO DEVEM ser versionados: `design/png/` fica no `.gitignore`, e
qualquer pessoa os regera a partir do `.figcraft`, para o histórico não crescer a cada ajuste de design.

#### Cenário: Tela documentada
- **QUANDO** uma tela tem design documentado
- **ENTÃO** existe `design/<tela>.figcraft` com a página dessa tela
- **E** o arquivo contém um frame para cada estado e tema documentado

#### Cenário: PNG exportado não vai para o git
- **QUANDO** os frames são exportados para `design/png/`
- **ENTÃO** `git status` não lista nenhum PNG dessa pasta
- **E** exportar de novo a partir do `.figcraft` gera os mesmos arquivos

#### Cenário: Binário no contêiner
- **QUANDO** a imagem Docker da aplicação é construída
- **ENTÃO** a pasta `design/` não faz parte do contexto de build

### Requirement: Nomes de arquivos e de frames
Cada frame DEVE se chamar `<tela> · <viewport> · <tema> · <estado>`, com `<tela>` no nome da rota em
inglês (por exemplo `signup`), `<viewport>` em `desktop` ou `mobile`, `<tema>` em `claro` ou `escuro` e
`<estado>` em português (`padrão`, `com erros`, `senha válida`). O PNG exportado de cada frame DEVE ter o mesmo
nome em minúsculas, sem acento e com `-` no lugar do separador (por exemplo `signup-desktop-claro-padrao.png`).

#### Cenário: Frame de erro no desktop claro
- **QUANDO** o frame do cadastro com mensagens de erro, no desktop claro, é nomeado
- **ENTÃO** seu nome é `signup · desktop · claro · com erros`
- **E** o PNG exportado dele é `design/png/signup-desktop-claro-com-erros.png`

### Requirement: Design fiel ao código
O design de uma tela DEVE refletir o que o código exibe: as cores e os tamanhos vêm dos tokens de
`frontend/style.css`, e os textos, rótulos e mensagens vêm dos templates e dos formulários. O design NÃO
DEVE inventar texto de produto, e dado de exemplo (nome, e-mail, senha) DEVE ser claramente fictício. Onde
o design diverge do código por limite da ferramenta, a divergência DEVE estar registrada no `design.md` da
change que a introduziu ou na convenção do `AGENTS.md`. A fonte do design DEVE ser a mesma que o app serve
(Outfit); a tipografia NÃO DEVE ser uma divergência registrada.

#### Cenário: Rótulo do formulário
- **QUANDO** o campo de confirmação de senha do cadastro é desenhado
- **ENTÃO** o rótulo é o do formulário (`Confirmação da senha`)

#### Cenário: Mensagem de erro real
- **QUANDO** o design mostra o e-mail já cadastrado
- **ENTÃO** a mensagem é a do formulário (`Este e-mail já está cadastrado.`)

#### Cenário: Tema escuro
- **QUANDO** o design mostra o tema escuro
- **ENTÃO** as cores do fundo, do campo e da borda são as do tema escuro do CSS

#### Cenário: Mesma fonte do app
- **QUANDO** um texto do design é inspecionado
- **ENTÃO** sua família é `Outfit`, a mesma que o app serve
- **E** nenhuma camada de texto usa outra família

### Requirement: Estados da tela documentados
O design do cadastro DEVE cobrir, no mínimo: desktop claro, desktop escuro, mobile claro, o estado **com
erros** (e-mail já cadastrado, requisitos de senha não atendidos e confirmação divergente) e o estado
**senha válida** (requisitos atendidos e confirmação coincidente). O desktop DEVE mostrar o painel de marca
com logo e frase de apresentação, e o mobile NÃO DEVE mostrá-lo.

#### Cenário: Painel de marca no desktop
- **QUANDO** o frame de desktop do cadastro é aberto
- **ENTÃO** ele mostra o formulário de um lado e o painel de marca com a logo do Gestor Financeiro do outro

#### Cenário: Mobile em coluna única
- **QUANDO** o frame de mobile do cadastro é aberto
- **ENTÃO** o formulário ocupa a largura toda
- **E** o painel de marca não aparece

### Requirement: Convenção e instalação documentadas
O `AGENTS.md` DEVE descrever a convenção de `design/` (onde ficam os arquivos, nomes, como exportar os PNGs
e como instalar a fonte), e como instalar e atualizar o FigCraft CLI e o servidor MCP. O binário do
FigCraft NÃO DEVE ser versionado. A fonte do design DEVE estar em `design/fonts/`, acompanhada da licença,
para quem clonar o repositório instalá-la antes de editar ou exportar. O script de instalação DEVE conferir
o checksum da release antes de instalar e NÃO DEVE instalar nada se a conferência falhar.

#### Cenário: Fonte do design no repositório
- **QUANDO** uma pessoa clona o repositório para editar o design
- **ENTÃO** `design/fonts/` contém a fonte Outfit e a sua licença
- **E** a convenção descreve como instalá-la no sistema

#### Cenário: Atualizar o FigCraft
- **QUANDO** o usuário roda `scripts/figcraft-upgrade`
- **ENTÃO** a última release é baixada e o checksum conferido
- **E** o caminho `~/.local/share/figcraft/current/bin/figcraft-cli` passa a apontar para ela

#### Cenário: Checksum diferente
- **QUANDO** o checksum do arquivo baixado não confere com o da release
- **ENTÃO** o script encerra com erro
- **E** nenhuma versão é instalada nem ativada

### Requirement: Opções de layout para escolha antes de implementar
Quando uma tela nova admite mais de um layout plausível, o design DEVE oferecer **ao menos duas opções**
no `.figcraft` da tela, cada uma numa página própria nomeada `Opção <letra> — <nome curto>`, com os mesmos
estados e temas mínimos, para o usuário escolher antes de a tela ser implementada. As opções DEVEM diferir
no layout, não no conteúdo: textos, rótulos e dados de exemplo são os mesmos. A escolha DEVE ser registrada
no `design.md` da change, com o motivo. O arquivo versionado DEVE conter só a opção escolhida, com frames na
convenção `<tela> · <viewport> · <tema> · <estado>` (sem a letra da opção no nome); a opção descartada fica
descrita no `design.md`, não no arquivo.

#### Cenário: Duas opções para escolha
- **QUANDO** o design de uma tela nova ainda aguarda a escolha
- **ENTÃO** o `.figcraft` tem uma página por opção, com pelo menos duas
- **E** cada página tem os mesmos frames de estado e tema (por exemplo desktop claro, desktop escuro, mobile claro e estado vazio)

#### Cenário: Escolha registrada
- **QUANDO** o usuário escolhe uma opção
- **ENTÃO** o `design.md` da change registra qual foi e por quê
- **E** a implementação da tela segue o layout escolhido

#### Cenário: Arquivo final só com a escolhida
- **QUANDO** a tela foi implementada e a change vai ser arquivada
- **ENTÃO** `design/<tela>.figcraft` não contém a página da opção descartada
- **E** os nomes dos frames seguem a convenção, sem a letra da opção

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
