# Delta: frontend-layout

## ADDED Requirements

### Requirement: Título da página sem breadcrumb
Toda página autenticada DEVE ter um único `h1` com o título dela (por exemplo "Painel", "Lançamentos",
"Novo lançamento"), logo acima do conteúdo, e NÃO DEVE ter breadcrumb nem outra trilha de
navegação. O título de um modal NÃO é o título da página e NÃO DEVE ser um `h1`.

#### Cenário: Título e nenhuma trilha
- **QUANDO** um usuário autenticado abre o painel, a listagem de lançamentos ou a tela de metas
- **ENTÃO** a página tem exatamente um `h1` com o nome da tela
- **E** não há elemento com o nome acessível "Trilha de navegação" nem o texto "Início" como link de trilha

#### Cenário: Telas de formulário e de exclusão
- **QUANDO** o usuário abre "Novo lançamento", "Editar meta" ou "Excluir categoria" como página
- **ENTÃO** a página tem um `h1` com esse título e nenhum breadcrumb

#### Cenário: Título de modal
- **QUANDO** o formulário de lançamento abre num modal sobre a listagem
- **ENTÃO** o título do modal não é um `h1`
- **E** o `h1` da página continua sendo "Lançamentos"

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
- **ENTÃO** o conteúdo é o painel do usuário, com o título "Painel" como título da página, sem breadcrumb
- **E** não há mais o texto de exemplo "Olá, mundo" nem o alerta estático

#### Cenário: Reuso do layout por outras telas
- **QUANDO** uma tela futura estende o template base e preenche o bloco de conteúdo
- **ENTÃO** ela herda barra lateral e cabeçalho sem duplicá-los
