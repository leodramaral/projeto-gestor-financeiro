## MODIFIED Requirements

### Requirement: Página base com layout TailAdmin
A aplicação DEVE servir em `/` uma página HTML renderizada no servidor que use o layout TailAdmin
(barra lateral, cabeçalho e área de conteúdo) estilizado com Tailwind CSS. O texto exibido ao
usuário DEVE estar em português do Brasil.

#### Cenário: Acesso à página inicial
- **QUANDO** o desenvolvedor acessa `http://127.0.0.1:8000/` autenticado com o ambiente no ar
- **ENTÃO** a resposta é `200` com HTML contendo a barra lateral, o cabeçalho e a área de conteúdo
- **E** a página carrega a folha de estilos compilada

#### Cenário: Conteúdo de exemplo
- **QUANDO** a página inicial é exibida
- **ENTÃO** o conteúdo é o painel do usuário, com o título "Painel" num componente breadcrumb do TailAdmin
- **E** não há mais o texto de exemplo "Olá, mundo" nem o alerta estático

#### Cenário: Reuso do layout por outras telas
- **QUANDO** uma tela futura estende o template base e preenche o bloco de conteúdo
- **ENTÃO** ela herda barra lateral e cabeçalho sem duplicá-los
