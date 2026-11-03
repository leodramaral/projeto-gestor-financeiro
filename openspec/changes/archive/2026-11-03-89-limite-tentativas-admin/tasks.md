# Tasks

## 1. Throttle e formulário de autenticação do admin

- [x] 1.1 Extrair `LoginThrottleFormMixin` em `accounts/forms.py` unificando a checagem de `lock_remaining` e a captura de `invalid_login` com `register_failure`; refatorar `LoginForm` e criar `AdminLoginForm(LoginThrottleFormMixin, AdminAuthenticationForm)`; verificar com testes de unidade dos formulários
- [x] 1.2 Conectar o signal `django.contrib.auth.signals.user_logged_in` ao `throttle.reset` em `accounts/signals.py` e registrá-lo em `accounts/apps.py`; verificar que um login bem-sucedido limpa o registro de falhas
- [x] 1.3 Injetar `admin.site.login_form = AdminLoginForm` no método `ready()` de `accounts/apps.py`; verificar que `admin.site.login_form` é instanciado nas requisições para `/admin/login/`

## 2. Testes de integração e comportamento da rota admin

- [x] 2.1 Adicionar testes para `/admin/login/` em `accounts/tests/test_throttle.py` cobrindo falhas seguidas até o bloqueio, bloqueio subsequente com a senha correta de staff/superusuário e verificação da mensagem em português com tempo restante; verificar com pytest
- [x] 2.2 Adicionar testes de contagem unificada intercalando tentativas erradas no app e no admin, e teste de reset da contagem após login válido no admin; verificar com pytest

## 3. Verificação de conformidade e qualidade

- [x] 3.1 Executar os testes automatizados da aplicação (`docker compose exec web pytest --cov --cov-report=term-missing`) e assegurar 100% de sucesso sem queda de cobertura
- [x] 3.2 Executar `uvx pre-commit run --all-files` e assegurar que lint, formatação, complexidade ciclomática e regras de segurança (Bandit) passem sem avisos
- [x] 3.3 Executar `openspec validate --all` e validar a conformidade da change e das specs
