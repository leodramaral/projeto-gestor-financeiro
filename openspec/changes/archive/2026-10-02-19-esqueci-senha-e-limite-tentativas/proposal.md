# Proposal

## Why

Hoje quem esquece a senha não tem como voltar à conta, e o login aceita tentativas ilimitadas, o que
deixa a conta exposta a adivinhação de senha. A Issue #19 fecha a base de autenticação (#2) com a
recuperação de senha por e-mail e um bloqueio temporário após tentativas erradas. A infra de e-mail
(#18) e o login (#2) já existem.

## What Changes

- Fluxo "esqueci minha senha": o usuário informa o e-mail e recebe um link de redefinição; ao abrir o
  link define uma nova senha (validada pelos validadores do Django) e volta ao login.
- O link de redefinição expira e é de uso único; link expirado, adulterado ou já usado mostra uma
  mensagem clara em português e oferece pedir um novo link.
- A resposta ao pedido de redefinição é a mesma exista ou não conta para o e-mail; nenhuma tela ou
  mensagem revela se um e-mail está cadastrado.
- Limite de tentativas de login erradas por e-mail: após **N** falhas seguidas (padrão 5) o login
  daquele e-mail fica bloqueado por um tempo (padrão 15 minutos), com mensagem em português. O limite
  vale também para e-mails sem conta, para não virar um oráculo de existência.
- Redefinir a senha com sucesso encerra o bloqueio daquele e-mail e invalida as sessões abertas.
- A tela de login ganha o atalho "Esqueci minha senha".
- Novas configurações: `LOGIN_MAX_FAILED_ATTEMPTS`, `LOGIN_LOCKOUT_SECONDS` e a validade do link de
  redefinição.

**Fora do escopo:** limite de pedidos de redefinição (anti-flood de e-mail); bloqueio por IP, CAPTCHA
e autenticação em dois fatores; troca de senha por usuário já logado; e-mail de aviso "sua senha foi
alterada"; qualquer model ou tela de domínio financeiro.

## Capabilities

### New Capabilities
- `password-recovery`: pedido de redefinição por e-mail, link de uso único com prazo, definição da
  nova senha e a regra de não revelar a existência de contas.

### Modified Capabilities
- `user-authentication`: o login passa a ter limite de tentativas erradas com bloqueio temporário.

## Impact

- Código: `accounts` (novo model de controle de tentativas + migration, formulários, views, URLs,
  gerador de token, e-mail `password_reset.{txt,html}`, testes); `LoginForm`/`SignInView` passam a
  consultar e registrar tentativas; `config/settings/base.py` (novas configurações);
  `templates/accounts/` (4 telas novas e o link no login).
- Banco: uma tabela nova (`accounts_loginthrottle`), com migration; sem alteração em tabelas existentes.
- Sem dependência nova.
- Documentação: README (fluxo em dev via Mailpit, configurações novas) e modelo de dados.
- Conteúdo do e-mail de confirmação não muda; ele continua usando seu próprio gerador de token.
