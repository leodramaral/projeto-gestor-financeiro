# Design

## Context

Não há model nem migration no projeto: `admin` e `auth` ainda não foram migrados em produção, mas o
banco de desenvolvimento local já os migrou com o `User` padrão. A infra de e-mail da #18
(`core.emailing.send_templated_email`, `SITE_URL`, Mailpit) está disponível. O layout atual
(`templates/base.html`) traz sidebar e header do painel, inadequados para telas de visitante. A
Issue exige que o cadastro "redirecione ao painel autenticado" e, ao mesmo tempo, que a conta "só
faça login após confirmar o e-mail"; os dois critérios se contradizem (ver decisão 1).

## Goals / Non-Goals

**Goals:**
- Fixar `AUTH_USER_MODEL` na primeira migration, com e-mail como login.
- Fluxo completo cadastro → e-mail → confirmação → login → painel, sem enumeração de contas.

**Non-Goals:**
- Recuperação de senha, limite de tentativas (#19), login social, 2FA, edição de perfil.
- Qualquer modelagem de domínio financeiro.

## Decisions

1. **O cadastro não autentica o usuário.** Resolve a contradição da Issue a favor do requisito
   de segurança ("só faz login após confirmar"): após cadastrar, mostra "verifique seu e-mail"; o
   painel é alcançado no primeiro login, depois da confirmação. Alternativa descartada: autenticar
   no cadastro e bloquear o painel até confirmar, que cria um estado "logado mas sem acesso" e
   contradiz o critério. *Se a intenção era o outro caminho, ajuste a spec antes do `/opsx:apply`.*

2. **App `accounts` com `User(AbstractBaseUser, PermissionsMixin)`**: campos `email`, `name`,
   `is_active`, `is_staff`, `email_confirmed_at` (nulo = não confirmada), `date_joined`;
   `USERNAME_FIELD = "email"`; `UserManager` com `create_user`/`create_superuser`. Alternativa:
   `AbstractUser` com `username` removido — arrasta campos (`first_name`/`last_name`) e um modelo
   de nome que o produto não usa. `is_active` continua significando "conta não desativada";
   confirmação é um campo separado, para o admin poder desativar sem perder o estado.

3. **E-mail case-insensitive em duas camadas**: normalizar para minúsculas em `UserManager`/`clean`
   e `UniqueConstraint(Lower("email"))` no banco. Sem `citext` (evita extensão do PostgreSQL).
   O backend de autenticação (`ModelBackend` com `USERNAME_FIELD`) recebe o e-mail já em minúsculas
   pelo formulário de login.

4. **Token de confirmação com `PasswordResetTokenGenerator` subclassificado**: o hash inclui
   `email_confirmed_at`, então o token morre sozinho após o uso (uso único) e o prazo vem de
   `PASSWORD_RESET_TIMEOUT` (definido em 3 dias; a #19 reaproveita). Link:
   `/accounts/confirm/<uidb64>/<token>/`. Alternativa: tabela de tokens — mais código e limpeza
   sem ganho. Limitação: não distingue "expirado" de "adulterado"; a página usa texto único
   ("inválido ou expirado") com reenvio, e trata à parte o caso de conta já confirmada (decodifica
   o `uid`, vê `email_confirmed_at` preenchido).

5. **Enumeração: aceita só no cadastro.** O cadastro com e-mail existente exibe erro de campo
   ("já cadastrado"), sem enviar e-mail ao endereço existente (decisão do produto: é o
   comportamento esperado pelo usuário e evita e-mail não solicitado a terceiros). Reenvio responde
   sempre igual e o login usa mensagem genérica, então esses dois não revelam contas. Exceção deliberada: e-mail + senha **corretos** de conta não confirmada
   exibem a orientação de confirmar, pois quem acerta a senha já é o titular. Efeito colateral
   aceito: ainda há diferença de tempo de resposta (hash vs. sem hash); mitigação de força bruta
   é a #19.

6. **Login**: `LoginView` com `AuthenticationForm` customizado (rótulo "E-mail", mensagens em
   português, rejeita não confirmadas via `confirm_login_allowed`). "Lembrar de mim":
   `SESSION_EXPIRE_AT_BROWSER_CLOSE = True` e, quando marcado, `request.session.set_expiry(
   SESSION_REMEMBER_SECONDS)` (30 dias, configurável em settings). Logout só por `POST`
   (`LogoutView`), com formulário + CSRF no header.

7. **Proteção das páginas**: `LOGIN_URL`, `LOGIN_REDIRECT_URL = "home"`; `HomeView` com
   `LoginRequiredMixin`. Telas de visitante usam `redirect_authenticated_user=True`. Sem middleware
   global de login obrigatório: a lista de exceções é curta hoje, mas explícito por view evita
   expor página nova por esquecimento só se houver teste; por isso um teste percorre todas as URLs
   registradas fora de `accounts` e exige redirecionamento anônimo.

8. **Layout de visitante**: `templates/base_auth.html` (card centralizado, mesmo CSS/tema do
   TailAdmin, sem sidebar/header); `templates/base.html` ganha o nome do usuário e o botão "Sair"
   no header. E-mails novos estendem `email/base.*` da #18.

9. **Banco existente**: como a primeira migration muda `AUTH_USER_MODEL`, o volume de dev precisa
   ser recriado (`docker compose down -v`), documentado no README. Não há dados a preservar.

## Risks / Trade-offs

- [Trocar `AUTH_USER_MODEL` depois é inviável] → decidido e testado agora, antes de qualquer outro
  model; a migration inicial de `accounts` roda antes de `admin`.
- [O cadastro permite descobrir se um e-mail tem conta] → escolha consciente; o critério "não
  revela se o e-mail existe" da Issue passa a valer só para login e reenvio. A #19 (limite de
  tentativas) deve cobrir também o cadastro, para frear varredura de e-mails.
- [Spam de e-mail de confirmação por reenvio] → fora do escopo; coberto pelo limite da #19.
- [Contradição da Issue resolvida por suposição] → decisão 1 explícita e sinalizada ao usuário.
- [Conta nunca confirmada ocupa o e-mail] → aceito; o reenvio e o aviso de "já existe conta"
  levam o dono ao fluxo; limpeza de contas antigas fica para uma Issue futura se necessário.
- [Cobertura] → `fail_under` só sobe; os testes novos devem elevar o piso, não reduzi-lo.
