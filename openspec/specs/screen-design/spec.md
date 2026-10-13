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
