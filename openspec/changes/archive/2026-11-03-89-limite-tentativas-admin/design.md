# Design

## Context

A motivação e o problema de segurança estão detalhados em `proposal.md`.

Atualmente, `accounts/forms.py` define o `LoginForm` herdando de `AuthenticationForm`, implementando a checagem prévia de bloqueio em `clean()` via `throttle.lock_remaining(email)` e o registro de erro `invalid_login` via `throttle.register_failure(email)`. O reset de falhas é realizado em `SignInView.form_valid()` chamando `throttle.reset(email)`.

O Django Admin é incluído em `config/urls.py` via `admin.site.urls`. Seu método `AdminSite.login` instancia `self.login_form or AdminAuthenticationForm` dentro de uma `django.contrib.auth.views.LoginView` interna do Django. Como `self.login_form` não estava customizado, o admin ignorava totalmente o `accounts.throttle`.

## Goals / Non-Goals

**Goals:**
- Proteger a rota `/admin/login/` com o mesmo comportamento e limite de tentativas definido em `accounts.throttle`.
- Compartilhar o contador e a janela de bloqueio entre o login do app e o login administrativo para uma mesma chave de e-mail.
- Garantir que um login bem-sucedido em qualquer ponto (app ou admin) limpe as falhas acumuladas.
- Evitar duplicação de lógica entre `LoginForm` e o formulário do admin.

**Non-Goals:**
- Customizar o visual ou o template padrão de login do Django Admin.
- Criar contadores separados ou limites diferentes para usuários staff.
- Alterar as regras de sessão ou cookies do Django Admin.

## Decisions

### 1. `LoginThrottleFormMixin` compartilhado e `AdminLoginForm`
- **Decisão:** Extrair a lógica de verificação de bloqueio e contagem de falhas para um mixin reutilizável (`LoginThrottleFormMixin`) em `accounts/forms.py`. 
  - O `LoginForm` passa a herdar de `StyledFormMixin`, `LoginThrottleFormMixin`, `AuthenticationForm`.
  - Cria-se `AdminLoginForm(LoginThrottleFormMixin, AdminAuthenticationForm)`.
- **Por que:** `AdminAuthenticationForm` estende `AuthenticationForm` adicionando a checagem de `is_staff` e `is_active` em `confirm_login_allowed()`. O mixin unifica a manipulação do `accounts.throttle` (checagem de `lock_remaining` no início do `clean()` e `register_failure` em caso de `invalid_login`), garantindo que tanto o formulário do app quanto o do admin compartilhem rigorosamente a mesma lógica e as mesmas mensagens de erro formatadas em pt-BR.
- **Alternativa considerada:** Implementar middleware de rate limit por rota. Rejeitada porque o controle do projeto é baseado em e-mail (não em IP), necessitando do e-mail normalizado após a submissão do formulário.

### 2. Injeção de `admin.site.login_form` via `ready()` em `accounts/apps.py`
- **Decisão:** Configurar `admin.site.login_form = AdminLoginForm` dentro do método `ready()` de `accounts/apps.py`.
- **Por que:** O `admin.site` é um singleton instanciado pelo Django. Atribuir o `login_form` no ciclo de inicialização do app `accounts` assegura que a configuração esteja ativa antes de qualquer requisição ser roteada para `admin.site.urls`, sem acoplar `config/urls.py` a formulários de autenticação específicos.
- **Alternativa considerada:** Criar uma subclasse de `AdminSite` e substituir a instância padrão do admin. Rejeitada por excesso de complexidade para um requisito que a própria API do Django suporta via atributo `login_form`.

### 3. Reset do throttle via signal `user_logged_in`
- **Decisão:** Conectar um receiver para o signal `django.contrib.auth.signals.user_logged_in` em `accounts` (ex.: `accounts/signals.py` registrado em `apps.py`), que executa `throttle.reset(user.email)`.
- **Por que:** O Django Admin usa a `LoginView` padrão do Django e não a `SignInView` customizada de `accounts/views.py`. O signal `user_logged_in` é disparado automaticamente pelo Django em qualquer autenticação válida (seja no app, no admin ou em futuras rotas), centralizando a responsabilidade de zerar as tentativas falhas no sucesso. Com isso, podemos manter ou simplificar a chamada em `SignInView`.
- **Alternativa considerada:** Sobrescrever `AdminSite.login` para interceptar `form_valid()`. Rejeitada porque o signal nativo já é o padrão canônico do Django para ações pós-autenticação.

## Risks / Trade-offs

- **[Risco: DoS contra conta de administrador por terceiros]** → **Mitigação:** Como qualquer atacante que conheça o e-mail de um admin pode tentar senhas incorretas até bloquear o e-mail, esse é o trade-off comum de rate-limiting por conta. O admin bloqueado pode utilizar a recuperação de senha ("esqueci minha senha"), que reseta o throttle após a troca, ou aguardar o período configurado de 15 minutos (`LOGIN_LOCKOUT_SECONDS`).
- **[Risco: Falha de credencial do admin revelar existência de conta]** → **Mitigação:** Tanto o `LoginForm` quanto o `AdminLoginForm` usam a mensagem genérica idêntica e bloqueiam e-mails inexistentes com a mesma contagem e resposta, prevenindo enumeração de contas.
