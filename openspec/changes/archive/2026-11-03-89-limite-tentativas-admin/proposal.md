# Proposal

Origem: Issue #89 (`Login: /admin/login/ não passa pelo limite de tentativas`), identificada na auditoria da suíte de testes (#82).

## Why

O requisito "Limite de tentativas de login" da especificação `user-authentication` bloqueia novas tentativas de login para um e-mail após 5 senhas incorretas consecutivas por 15 minutos. No entanto, essa proteção foi implementada exclusivamente no `LoginForm` da tela do app (`/accounts/login/`).

A rota de administração do Django (`/admin/login/`) utiliza o `AdminAuthenticationForm` padrão do framework, que não passa pelo `accounts.throttle`. Com isso, contas com privilégios de staff ou superusuário ficam vulneráveis a ataques de força bruta e dicionário sem bloqueio, criando uma brecha crítica no perímetro de segurança da aplicação.

## What Changes

- **Proteção do login administrativo:** O formulário de autenticação do Django Admin (`admin.site.login_form`) passa a incorporar o controle de throttle (`AdminLoginForm`), bloqueando tentativas quando o e-mail estiver temporariamente suspenso e registrando falhas de credenciais inválidas.
- **Contador unificado por e-mail:** O controle de tentativas utiliza a mesma tabela e chave de e-mail normalizado (`LoginThrottle`). Falhas consecutivas no app e no admin somam-se contra o mesmo limite.
- **Reset unificado no sucesso:** Um login bem-sucedido — seja pela tela do app ou pelo Django Admin — zera a contagem de falhas do e-mail através do signal `user_logged_in` do Django.
- **Mensagem de bloqueio em português:** Tentativas em `/admin/login/` durante o bloqueio ativo exibem mensagem amigável em pt-BR com o tempo restante, sem revelar se a conta existe ou tem privilégios de staff.

## Capabilities

### Modified Capabilities

- `user-authentication`: O requisito "Limite de tentativas de login" passa a cobrir explicitamente tanto o login da aplicação (`/accounts/login/`) quanto o login da interface administrativa (`/admin/login/`), compartilhando a contagem de tentativas e o período de bloqueio por e-mail.

## Out of Scope

- Desativação ou alteração da URL `/admin/` por ambiente.
- Autenticação em dois fatores (2FA) ou restrição por IP (demandas para changes futuras).
- Alterações no comportamento de expiração de sessão ou "lembrar de mim" para a área administrativa.
- Modificações em telas internas ou models do admin do Django além do formulário de autenticação.

## Impact

- **Código:**
  - `accounts/forms.py`: criação de `AdminLoginForm` herdando de `AdminAuthenticationForm` com a mesma lógica de verificação e registro de throttle do `LoginForm`.
  - `accounts/apps.py` / `accounts/signals.py`: conexão ao signal `user_logged_in` para resetar o throttle após autenticação com sucesso.
  - `config/urls.py` ou `accounts/apps.py`: atribuição de `admin.site.login_form = AdminLoginForm`.
- **Testes:**
  - `accounts/tests/test_throttle.py` (ou `test_admin_login.py`): novos testes simulando requisições POST com credenciais incorretas em `/admin/login/`, verificação do bloqueio subsequente com credencial correta de superusuário e reset após login com sucesso.
