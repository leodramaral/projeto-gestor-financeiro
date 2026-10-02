# Proposal

## Why

A aplicação ainda se apresenta com a marca e as cores do template TailAdmin (logo, ícone, favicon e
azul de marca), o que não identifica o produto. Além disso, quem ainda não entrou não consegue
trocar entre tema claro e escuro: o controle só existe no painel, depois do login. A Issue #24
pede uma identidade visual própria e coerente em todas as telas.

## What Changes

- Substituir o logo, o ícone e o favicon do TailAdmin por uma marca própria do **Gestor
  Financeiro** (um G de moeda, com traços de cifrão, num quadrado arredondado); nenhuma tela, título de página ou e-mail exibe "TailAdmin".
- Trocar a escala de cor de marca do azul do template por um **esquema verde-azulado "Jade"** (claro e escuro),
  aplicado ao painel, às telas de visitante e aos e-mails, com contraste legível.
- Oferecer o **controle de tema** (claro/escuro) nas telas de visitante, compartilhando a escolha
  já usada pelo painel, aplicada antes de pintar a página.
- Extrair a marca e o controle de tema em parciais reutilizáveis, para que painel e telas de
  visitante usem a mesma fonte.
- Mantida a atribuição e a licença do TailAdmin onde há código derivado.

**Fora do escopo:** novas telas; mudanças de layout do painel além de cor e marca; tema que segue
o sistema operacional; internacionalização.

## Capabilities

### New Capabilities
- `visual-identity`: marca do produto, esquema de cores verde e alternância de tema, em todas as
  telas e e-mails.

### Modified Capabilities
<!-- Nenhuma: `frontend-layout` continua válida (o layout derivado do TailAdmin e o fluxo de CSS não mudam). -->

## Impact

- Código: `frontend/style.css` (tokens `--color-brand-*`), `templates/base.html`,
  `templates/base_auth.html`, `templates/partials/{header,sidebar}.html`, novas parciais
  `partials/brand.html` e `partials/theme_toggle.html`, `templates/email/*` (cor inline),
  `static/images/` (logos, ícone e favicon).
- Sem model, migration, dependência nova ou variável de ambiente.
- Documentação: README (menção à identidade visual, se couber).
- Decisões já tomadas com a prévia: símbolo "G em quadrado" e cor Jade. Suposições registradas: o nome exibido é "Gestor Financeiro" (já usado em títulos e e-mails); o
  tema padrão continua sendo o claro quando não há escolha salva (ver `design.md`).
