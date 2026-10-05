# Design

## Context

`templates/partials/header.html` mostra, no lado direito, o alternador de tema, o nome do usuário e
um formulário `POST` com o botão "Sair". O modelo `User` já tem `name`, `email`,
`email_confirmed_at` e `date_joined`; o `accounts/urls.py` concentra as rotas de conta e o logout
usa o `LogoutView` do Django. O Alpine.js já está carregado em todas as telas autenticadas
(`base.html`). Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**
- Reproduzir a estrutura da demo (página de perfil e menu do usuário) com Tailwind e Alpine, usando
  só dados que já existem.
- Manter o logout exatamente como é (`POST` com CSRF), só mudando onde o botão mora.

**Non-Goals:**
- Edição de perfil, upload de foto, campos novos no modelo, itens extras do menu da demo.

## Decisions

- **Rota e view em `accounts`:** `accounts/profile/` (`name="profile"`), uma `TemplateView` com
  `LoginRequiredMixin` que lê `request.user`; não há como abrir o perfil de outro usuário, o que
  dispensa checagem de permissão. Alternativa: um app `profiles` — descartada, pois não há modelo
  nem regra própria. Como `accounts/` é prefixo público no teste de rotas privadas, o acesso
  anônimo ganha teste explícito.
- **Menu com Alpine:** `x-data="{ open: false }"`, botão com `aria-haspopup`/`aria-expanded`,
  `@click.outside` e `@keydown.escape` para fechar, `x-cloak` para não piscar aberto. Segue o padrão
  do restante do projeto (Alpine, sem JS próprio).
- **Avatar de iniciais em parcial** (`partials/user_avatar.html`), com tamanho por parâmetro, usado
  no card, no menu e na página. Iniciais: primeira letra das duas primeiras palavras do nome,
  calculadas por um filtro/propriedade simples; sem imagem enviada. Alternativa: Gravatar —
  descartada por vazar o e-mail a terceiro.
- **Formulário de logout dentro do menu:** o `<form method="post">` com `{% csrf_token %}` permanece,
  só muda de lugar; o item "Sair" é o `submit`. Nada muda na view de logout.
- **Página de perfil:** cartão com avatar, nome e e-mail, seguido de grade "rótulo / valor" no
  padrão da demo (Nome, E-mail, E-mail confirmado, Membro desde), sem botões "Edit". Título e
  breadcrumb pelo parcial `breadcrumb.html` existente.
- **Sem item na barra lateral:** a demo tem, mas o acesso já vem do menu; evita mexer em
  `sidebar.html` e no estado recolhido.

## Risks / Trade-offs

- [Teste existente procura o botão "Sair" no cabeçalho] → o formulário continua no HTML (dentro do
  menu), então o teste segue válido; ajustar só se o texto mudar.
- [Menu cortado em telas estreitas] → posicionar à direita com largura máxima `calc(100vw - 2rem)`
  e verificar em 375 px.
- [Nome vazio ou com uma palavra só nas iniciais] → o filtro trata ambos (uma letra) e é testado.
