# Design

## Context

O login (`SignInView` + `LoginForm`, sobre `AuthenticationForm`) e a confirmação de conta (token
`EmailConfirmationTokenGenerator`, e-mail via `core.emailing.send_templated_email`) existem desde a #2.
`PASSWORD_RESET_TIMEOUT` (3 dias) já é usado pela confirmação e foi deixado com o comentário "e, depois,
links de redefinição". Não há cache configurado (o padrão do Django é `LocMemCache`, por processo) nem
rate limiting. Ver `proposal.md` para a motivação.

## Goals / Non-Goals

**Goals:**
- Reaproveitar as peças do Django (token de redefinição, `PasswordResetConfirmView`, validadores) em vez de reinventá-las.
- Limite de tentativas que funcione com vários processos e sobreviva a reinício, sem depender de infra nova.
- Nenhum ponto do fluxo distingue e-mail cadastrado de não cadastrado.

**Non-Goals:**
- Limitar o volume de pedidos de redefinição, bloquear por IP, CAPTCHA, 2FA e troca de senha logado.

## Decisions

**1. Tokens: `PasswordResetTokenGenerator` próprio, com sal e prazo próprios.**
`PasswordResetTokenGenerator` embute o hash da senha e o `last_login` no token, então trocar a senha
invalida o link (uso único) sem guardar estado. Um gerador novo (`password_reset_token`, `key_salt`
distinto) impede que o link de confirmação sirva para redefinir, e vice-versa. O prazo é próprio
(`PASSWORD_RESET_LINK_TIMEOUT`, padrão 1 hora): redefinição dá acesso à conta, então vive menos que o
link de confirmação (3 dias). O `check_token` do Django lê `settings.PASSWORD_RESET_TIMEOUT` direto,
então o gerador sobrescreve a checagem de prazo para usar a configuração própria.
*Alternativa descartada:* reusar `default_token_generator` com `PASSWORD_RESET_TIMEOUT` — forçaria o
mesmo prazo para confirmação e redefinição, ou um prazo curto demais para a confirmação.

**2. Views: pedido próprio, confirmação com `PasswordResetConfirmView`.**
O pedido (`PasswordResetRequestView`, um `FormView` como o reenvio de confirmação) busca
`is_active=True, email_confirmed_at__isnull=False`, `email__iexact`, envia o e-mail e **sempre**
redireciona à mesma página "verifique seu e-mail"; erro de SMTP só é logado (mesmo padrão do
reenvio). A confirmação usa `PasswordResetConfirmView` com o gerador novo: ela já troca o link do
token por uma URL de sessão (o token sai da URL), aplica os validadores e, ao salvar, não autentica
(`post_reset_login=False`). Token inválido cai num template único, que não diferencia expirado,
adulterado e já usado — mesma mensagem da confirmação de conta. O `success_url` é o login, com
mensagem de sucesso (`django.contrib.messages`; o alerta já existe em `partials/alert.html`).
Rotas sob `/accounts/password-reset/...`, no mesmo `accounts:`.
*Alternativa descartada:* escrever as views de confirmação à mão — duplica lógica sensível já testada.

**3. Sessões antigas caem sozinhas.**
Com `SessionMiddleware` + `AuthenticationMiddleware`, o hash da sessão deriva do hash da senha;
trocar a senha invalida as demais sessões. O teste cobre isso, sem código extra.

**4. Limite de tentativas: tabela própria, chave = e-mail normalizado.**
Model `LoginThrottle` (`email` único e normalizado, `failed_count`, `locked_until`, `updated_at`), sem
FK para `User`. Sem FK, e-mails sem conta também são contados, e a mensagem de bloqueio é igual para
todos: nada de oráculo. Funciona com vários processos e sobrevive a reinício, o que `LocMemCache`
não garante, e não pede Redis. Um módulo `accounts/throttle.py` expõe `is_locked(email)`,
`register_failure(email)` e `reset(email)`; as atualizações usam `select_for_update` em transação para
que requisições concorrentes não percam contagem.
- O `LoginForm.clean()` consulta `is_locked` **antes** de `authenticate()` (não gasta hash de senha
  e não deixa a senha correta passar durante o bloqueio) e levanta erro `locked` com a mensagem
  de bloqueio e o tempo restante em minutos.
- Credencial errada chama `register_failure`: incrementa; ao chegar a `LOGIN_MAX_FAILED_ATTEMPTS`
  define `locked_until = agora + LOGIN_LOCKOUT_SECONDS` e zera a contagem. Falhas de "conta não
  confirmada" **não** contam (a senha estava certa).
- Login ok e redefinição de senha chamam `reset`. Registro cujo bloqueio já passou é reaproveitado
  (recomeça do zero), sem job de limpeza.
Padrões: 5 falhas, 15 minutos; `LOGIN_MAX_FAILED_ATTEMPTS` e `LOGIN_LOCKOUT_SECONDS` em `base.py`.
*Alternativas descartadas:* cache do Django (`LocMemCache` é por processo e perde-se no reinício;
Redis é infra nova); `django-axes`/`django-ratelimit` (dependência nova para uma regra pequena, e
o `axes` traz tabelas e middlewares além do necessário); contar também por IP (atrás de proxy o IP
exige configuração confiável de cabeçalhos; fica como evolução).

**5. Senha e "lembrar de mim" não mudam.** O limite só envolve a etapa de credenciais.

## Risks / Trade-offs

- **[Bloqueio de conta por terceiros]** Quem sabe o e-mail da vítima pode mantê-la bloqueada
  errando de propósito. → O bloqueio é temporário, curto e não atinge outros e-mails; a vítima
  desbloqueia redefinindo a senha por e-mail. Limite por IP/CAPTCHA fica para uma change própria.
- **[Janela de concorrência]** Muitas tentativas simultâneas podem passar do limite antes do
  bloqueio. → `select_for_update` na atualização da contagem; o excesso, se houver, é de poucas
  tentativas.
- **[Flood de e-mails de redefinição]** O pedido não é limitado. → Declarado fora do escopo;
  só contas confirmadas recebem e-mail.
- **[Dado de e-mails inexistentes]** A tabela guarda e-mails sem conta que alguém tentou. → Guardam
  só o e-mail digitado e contadores; sem job de limpeza agora (ver Open Questions).

## Migration Plan

Uma migration nova e aditiva (`accounts_loginthrottle`); basta `migrate` ao subir. Reverter é
remover o código e a tabela; nenhuma tabela existente muda.

## Open Questions

- Rotina de limpeza de registros antigos de `LoginThrottle` (comando de manutenção) pode vir depois;
  não altera specs nem tarefas.
