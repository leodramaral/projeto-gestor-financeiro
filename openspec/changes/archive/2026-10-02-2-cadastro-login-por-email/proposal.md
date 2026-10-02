# Proposal

## Why

Todos os itens do produto exigem um usuário autenticado e com dados isolados, e a Issue #2 é a base
deles. O modelo de usuário precisa nascer agora: `AUTH_USER_MODEL` não pode ser trocado depois que
a primeira migration do `auth` existe. A infra de e-mail (#18) já está pronta para a confirmação
de conta.

## What Changes

- Novo app `accounts` com modelo de usuário customizado (e-mail como login, nome, senha em hash),
  definido como `AUTH_USER_MODEL` **antes da primeira migration**.
- Cadastro com nome, e-mail e senha, validando e-mail duplicado (sem diferenciar maiúsculas) e
  os validadores de senha do Django, com mensagens em português.
- Confirmação de conta por link enviado por e-mail, com expiração e uso único; reenvio do link.
- Login e logout, com "lembrar de mim" (sessão de navegador vs. sessão persistente).
- Páginas privadas redirecionam anônimos ao login; a home atual (`/`) passa a ser o painel
  autenticado, sem conteúdo de domínio.
- Telas de autenticação com layout próprio (sem sidebar/header do painel).
- Cadastro com e-mail já existente exibe aviso claro na tela; login e reenvio do link NÃO revelam
  se um e-mail existe.

**Fora do escopo:** recuperação de senha e limite de tentativas de login (#19); qualquer model ou
tela de domínio financeiro.

## Capabilities

### New Capabilities
- `user-accounts`: cadastro de usuário, unicidade de e-mail e confirmação de conta por e-mail.
- `user-authentication`: login, logout, sessão persistente opcional e proteção de páginas privadas.

### Modified Capabilities
<!-- Nenhuma: a #18 só é consumida (send_templated_email), seus requisitos não mudam. -->

## Impact

- Código: novo app `accounts` (model, forms, views, urls, templates, testes); `config/settings/base.py`
  (`INSTALLED_APPS`, `AUTH_USER_MODEL`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, sessão); `config/urls.py`;
  `core/views.py` (home exige login); `templates/` (layout de autenticação, cabeçalho com logout,
  e-mail de confirmação).
- Banco: primeira migration do projeto (`accounts`); o banco de desenvolvimento existente precisa
  ser recriado, pois `admin`/`auth` já foram migrados com o `User` padrão.
- Sem dependência nova.
- Documentação: README (fluxo de cadastro em desenvolvimento via Mailpit) e modelo de dados.
- Suposição registrada: o cadastro **não** autentica o usuário (ver `design.md`, decisão 1).
