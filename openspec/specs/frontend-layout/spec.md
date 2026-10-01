# frontend-layout Specification

## Purpose
Define a página base da aplicação, com o layout TailAdmin renderizado no servidor, que serve de
estrutura visual para todas as telas seguintes.

## Requirements

### Requirement: Página base com layout TailAdmin
A aplicação DEVE servir em `/` uma página HTML renderizada no servidor que use o layout TailAdmin
(barra lateral, cabeçalho e área de conteúdo) estilizado com Tailwind CSS. O texto exibido ao
usuário DEVE estar em português do Brasil.

#### Cenário: Acesso à página inicial
- **QUANDO** o desenvolvedor acessa `http://127.0.0.1:8000/` com o ambiente no ar
- **ENTÃO** a resposta é `200` com HTML contendo a barra lateral, o cabeçalho e a área de conteúdo
- **E** a página carrega a folha de estilos compilada

#### Cenário: Conteúdo de exemplo
- **QUANDO** a página inicial é exibida
- **ENTÃO** o conteúdo traz o título "Olá, mundo" com um componente breadcrumb do TailAdmin
- **E** um componente de alerta de sucesso do TailAdmin, com texto estático em português e sem dado de domínio

#### Cenário: Reuso do layout por outras telas
- **QUANDO** uma tela futura estende o template base e preenche o bloco de conteúdo
- **ENTÃO** ela herda barra lateral e cabeçalho sem duplicá-los

### Requirement: CSS compilado no fluxo Docker
O CSS DEVE ser compilado pelo próprio `docker compose up --build`, sem exigir Node nem outra
ferramenta instalada na máquina, e o artefato compilado NÃO DEVE ser versionado. O serviço `web`
NÃO DEVE começar a atender antes de o CSS existir.

#### Cenário: Primeira subida
- **QUANDO** o desenvolvedor roda `docker compose up --build` num clone limpo
- **ENTÃO** o CSS é compilado antes de o `web` iniciar
- **E** o arquivo servido em `/static/` contém as classes de utilitário usadas pelos templates

#### Cenário: Falha na compilação
- **QUANDO** a compilação do CSS falha
- **ENTÃO** o serviço `web` não inicia
- **E** o erro do build aparece nos logs do Compose
