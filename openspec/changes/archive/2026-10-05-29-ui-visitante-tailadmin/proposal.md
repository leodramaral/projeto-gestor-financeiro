# Proposta

## Why

As telas de visitante (entrar, criar conta, recuperar senha) hoje são um cartão simples centralizado.
As demos de Sign In, Sign Up e Reset Password do TailAdmin trazem um layout mais maduro (painel de
marca ao lado do formulário, hierarquia e espaçamento melhores). Como é o primeiro contato com o
produto, vale alinhá-las a esse padrão, adaptado à marca jade. Issue #29.

## What Changes

- Entrar, Criar conta e Esqueci minha senha passam a usar layout dividido: formulário de um lado e painel de marca do
  outro (logo, frase de apresentação e grade decorativa) em telas largas; coluna única, sem o painel,
  em telas estreitas.
- Nas três telas: título e subtítulo no padrão da demo, link de navegação no topo (voltar ao login,
  onde fizer sentido), campos e botão principal com o dimensionamento da demo, nos temas claro e escuro.
- As demais telas que usam o layout de visitante (confirmação de conta, reenvio, nova senha) herdam o
  fundo decorativo e o cartão, sem mudar o conteúdo.
- Fora do escopo: botões de login social (Google, X) e qualquer integração com outros apps; campos
  novos (ex.: separar nome e sobrenome); caixa "Mantenha-me conectado" nova (o "Lembrar de mim" já
  existe e permanece); mudanças no painel.
- Nenhum comportamento muda: campos, validações, mensagens e fluxos permanecem.

## Capabilities

### New Capabilities

### Modified Capabilities
- `visual-identity`: acrescenta o requisito de layout das telas de visitante (dividido em entrar e
  criar conta e recuperação de senha), responsivo e nos dois temas.

## Impact

- Templates: `templates/base_auth.html`, `templates/accounts/{login,signup,password_reset_form}.html`
  e um parcial novo para o painel de marca.
- CSS: `frontend/style.css` (grade decorativa), recompilado pelo serviço `css`.
- Testes: `accounts/tests/` (estrutura renderizada, ausência de "TailAdmin", acessibilidade básica).
- Sem mudança em models, views, URLs ou dependências.
