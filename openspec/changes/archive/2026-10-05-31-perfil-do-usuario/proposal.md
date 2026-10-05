# Proposta

## Why

Hoje o usuário autenticado só vê o nome e um botão "Sair" solto na barra superior: não há onde
consultar os dados da própria conta. A demo do TailAdmin traz uma página de perfil e um menu de
usuário no canto superior direito, que organizam essas ações de conta. Issue #31.

## What Changes

- Nova página de perfil, **somente leitura**, no padrão da demo User Profile: avatar com iniciais,
  nome e os dados que já existem na conta (nome, e-mail, situação da confirmação do e-mail e data de
  cadastro), nos temas claro e escuro.
- Novo card de usuário no canto superior direito do cabeçalho (avatar, nome e seta) que abre um menu
  com nome, e-mail, **Ver perfil** e **Sair**. O menu fecha ao clicar fora e com Esc, e funciona em
  telas estreitas.
- O botão "Sair" avulso e o nome solto saem do cabeçalho: a ação de sair passa a viver só no menu.
  O logout continua sendo `POST` com CSRF.
- Fora do escopo: qualquer edição de perfil (os botões "Edit" da demo não entram), foto enviada,
  endereço, redes sociais, telefone e demais campos novos no modelo; itens da demo como "Account
  settings", "Support" e "Language"; item de perfil na barra lateral.
- Nenhum model, migração ou dependência muda.

## Capabilities

### New Capabilities
- `user-profile`: página de perfil somente leitura e menu de usuário no cabeçalho.

### Modified Capabilities
- `user-authentication`: o "Sair" passa a ser acionado pelo menu do usuário, sem mudar a regra
  (`POST` com CSRF, redirecionamento ao login).

## Impact

- Templates: `templates/partials/header.html` (card e menu), página nova em `templates/accounts/`
  e parcial do avatar.
- Código: uma view e uma rota em `accounts` (`accounts/profile/`), sem model novo.
- Testes: `accounts/tests/` (acesso, conteúdo, menu) e ajuste do teste que procura o botão "Sair".
- Sem mudança em dependências.
