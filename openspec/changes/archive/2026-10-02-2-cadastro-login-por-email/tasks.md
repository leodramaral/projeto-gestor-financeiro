# Tasks

## 1. Modelo de usuário e configuração

- [x] 1.1 Criar o app `accounts` com `User` (e-mail como login, `name`, `email_confirmed_at`, `is_staff`, `is_active`), `UserManager` e `UniqueConstraint(Lower("email"))`; verificar com testes de modelo (`create_user` normaliza e-mail e faz hash; `create_superuser`; duplicidade com outra caixa levanta `IntegrityError`)
- [x] 1.2 Em `base.py`: `accounts` em `INSTALLED_APPS` (antes de `admin`), `AUTH_USER_MODEL`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, `SESSION_EXPIRE_AT_BROWSER_CLOSE`, `SESSION_REMEMBER_SECONDS`, `PASSWORD_RESET_TIMEOUT`; gerar a migration inicial e verificar que `docker compose exec web python manage.py makemigrations --check` passa e `migrate` roda num banco recriado
- [x] 1.3 Registrar o `User` no admin (`UserAdmin` adaptado ao e-mail) e verificar com teste que o changelist do admin abre para um superusuário

## 2. Cadastro e confirmação

- [x] 2.1 Criar o formulário de cadastro (nome, e-mail, senha + confirmação, validadores do Django, e-mail normalizado) e testar e-mail inválido e senha fraca com mensagens em português
- [x] 2.2 Criar a view/URL de cadastro, a página "verifique seu e-mail" e o e-mail `confirm_account.{txt,html}`; testar que cadastro novo cria usuário não confirmado e envia o link a `SITE_URL`, e que e-mail duplicado (outra caixa) não cria usuário, exibe o erro no campo de e-mail e não envia e-mail
- [x] 2.3 Implementar o gerador de token e a view de confirmação (`/contas/confirmar/<uidb64>/<token>/`); testar link válido, expirado (tempo simulado), já usado, conta já confirmada e adulterado, conferindo `email_confirmed_at` e as mensagens
- [x] 2.4 Implementar o reenvio do link; testar resposta idêntica para e-mail desconhecido, conta confirmada e conta pendente, e que só a pendente recebe e-mail

## 3. Login, logout e proteção

- [x] 3.1 Implementar `AuthenticationForm` customizado e a view de login (e-mail case-insensitive, mensagem genérica, bloqueio de não confirmada com orientação), "lembrar de mim" e `next` seguro; testar login válido, e-mail inexistente e senha errada com a mesma mensagem, não confirmada, caixa do e-mail, cookie sem `expires` vs. com `max-age`, `next` externo ignorado
- [x] 3.2 Implementar o logout por `POST` e testar que `GET` não encerra a sessão, que o `POST` encerra e redireciona ao login
- [x] 3.3 Aplicar `LoginRequiredMixin` à `HomeView` e redirecionar autenticados longe de login/cadastro; testar o redirecionamento do anônimo com `next` e um teste que percorre as URLs fora de `accounts` e `admin` exigindo login

## 4. Interface

- [x] 4.1 Criar `templates/base_auth.html` e as telas de login, cadastro, "verifique seu e-mail", confirmação (sucesso/erro) e reenvio, em português, com erros de campo visíveis e CSRF; recompilar o CSS (`docker compose run --rm css npm run build`) se surgirem classes novas e verificar que as telas renderizam (testes de status 200 e conteúdo)
- [x] 4.2 Exibir o nome do usuário e o botão "Sair" (formulário `POST`) no header de `base.html`; testar que aparecem no painel autenticado

## 5. Documentação

- [x] 5.1 Atualizar o `README.md` (fluxo de cadastro em dev lendo o link no Mailpit, aviso de recriar o volume com `docker compose down -v`, variáveis novas se houver) e adicionar o modelo de dados do `User`; verificar que os comandos documentados rodam como escritos

## 6. Verificação final

- [x] 6.1 `docker compose exec web pytest --cov --cov-report=term-missing` passa e a cobertura sobe; elevar `fail_under` ao novo patamar
- [x] 6.2 `uvx pre-commit run --all-files` passa
- [x] 6.3 Manual: com o Compose no ar, cadastrar, abrir o link no Mailpit (`127.0.0.1:8025`), fazer login com e sem "lembrar de mim", sair, e tentar `/` anônimo
- [x] 6.4 `openspec validate --all` passa (sem `--strict`)
