# Design

## Context

`templates/base_auth.html` embrulha todo o conteúdo de visitante num cartão `max-w-md` centralizado,
com a marca no topo e o botão de tema fixo no canto. Login, cadastro, recuperação, confirmação,
reenvio e nova senha herdam dele; os formulários usam os parciais `form_field.html` e
`form_errors.html`. O CSS é Tailwind compilado a partir de `frontend/style.css` (tokens jade já
definidos). Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**
- Reproduzir a estrutura visual das demos (dividido / cartão com grade) usando só Tailwind e os
  tokens da marca.
- Concentrar o layout em poucos pontos, sem duplicar HTML entre as telas.

**Non-Goals:**
- Copiar assets, textos ou logo do TailAdmin; botões sociais; novos campos; mudanças em views.

## Decisions

- **Dois blocos de layout em `base_auth.html`:** `{% block layout %}` com o padrão "cartão
  centralizado + grade" (usado por confirmação, reenvio e nova senha) e uma variante dividida
  (`base_auth_split.html`), usada por entrar, criar conta e recuperar senha. Alternativa: dois arquivos base — descartada
  por duplicar `<head>`, tema e Alpine; as demais telas continuam no cartão sem alteração.
- **Painel de marca em parcial (`partials/auth_aside.html`):** logo, frase "Controle suas finanças
  com clareza" (texto de produto em pt-BR, redigido por nós) e grade decorativa. Visível a partir de
  `lg:`; abaixo disso fica oculto (`hidden lg:flex`).
- **Grade decorativa em CSS/SVG inline próprios**, não o `grid-01.svg` do TailAdmin, para não
  carregar asset do template; cores via tokens para funcionar nos dois temas. O painel usa fundo
  `brand-950`/`brand-700` (contraste do texto branco ≥ 4,5:1, a verificar).
- **Sem alterar `form_field.html`:** o ajuste de tamanho/foco dos inputs vem das classes dos widgets
  já existentes; só se algo destoar da demo isso vira task própria.
- **Link no topo:** "Voltar ao login" em cadastro e recuperação. Em entrar não há link (a raiz do
  site exige login, então "voltar ao painel" levaria de volta ao próprio login).
- **"Lembrar de mim"** permanece como está; a demo tem "Keep me logged in" e já temos equivalente.
- **Teste:** assertivas sobre o HTML renderizado (painel presente em entrar/criar conta, ausente em
  recuperar; sem "TailAdmin"; sem botões sociais); a parte visual é verificada manualmente.

## Risks / Trade-offs

- [Contraste do texto sobre o painel de marca] → medir os pares de cor e ajustar a escala usada.
- [Quebra de teste que checa `base_auth.html`] → manter o nome do template base; só mudam blocos.
- [Telas de confirmação com cartão levemente diferente] → verificação visual de todas as telas de
  visitante nos dois temas e em largura de celular.
