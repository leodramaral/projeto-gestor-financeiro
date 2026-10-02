# Tasks

## 1. Limite de tentativas de login

- [x] 1.1 Acrescentar `LOGIN_MAX_FAILED_ATTEMPTS` (5) e `LOGIN_LOCKOUT_SECONDS` (900) em `config/settings/base.py`, criar o model `LoginThrottle` e a migration; verificar que `docker compose exec web python manage.py makemigrations --check` passa e que `migrate` roda
- [x] 1.2 Criar `accounts/throttle.py` (`is_locked`, `register_failure`, `reset`, com `select_for_update` e e-mail normalizado); verificar com testes de unidade: contagem até o limite, bloqueio, expiração com tempo simulado, reaproveitamento de registro vencido, `reset` e isolamento entre e-mails
- [x] 1.3 Integrar ao `LoginForm`/`SignInView`: consultar o bloqueio antes de autenticar, registrar falha de credencial (não a de conta não confirmada) e zerar no sucesso; verificar com testes de login: bloqueio após N falhas mesmo com a senha certa, mensagem em português com o tempo restante, e-mail inexistente com a mesma mensagem e o mesmo limite, caixa do e-mail, sucesso zera a contagem, fim do bloqueio
- [x] 1.4 Exibir a mensagem de bloqueio na tela de login em português; verificar com teste de conteúdo da página (status 200, texto de bloqueio, nenhuma sessão criada)

## 2. Recuperação de senha

- [x] 2.1 Criar o gerador de token de redefinição (`accounts/tokens.py`: sal próprio, prazo `PASSWORD_RESET_LINK_TIMEOUT` de 1 hora em `base.py`); verificar com testes: token válido, expirado (tempo simulado), invalidado pela troca de senha e rejeitado quando vem do gerador de confirmação (e vice-versa)
- [x] 2.2 Criar o e-mail `templates/email/password_reset.{txt,html}` e a função de envio em `accounts/emails.py`; verificar com teste que o corpo contém o link absoluto a partir de `SITE_URL` e o prazo de validade
- [x] 2.3 Implementar o pedido de redefinição (formulário, view, URL, páginas de pedido e de "verifique seu e-mail"); verificar com testes: conta confirmada recebe e-mail; e-mail inexistente, conta inativa e conta não confirmada não recebem; resposta (status, destino, texto) idêntica nos casos; caixa do e-mail; falha de SMTP não muda a resposta
- [x] 2.4 Implementar a definição da nova senha com `PasswordResetConfirmView` (gerador próprio, formulário estilizado, validadores, sem login automático, sucesso leva ao login com mensagem) e o template único de link inválido; verificar com testes: link válido mostra o formulário, senha trocada em hash, senha fraca e confirmação diferente mantêm o link válido, link expirado/usado/adulterado mostram a mesma mensagem sem alterar a senha, sessão aberta em outro cliente cai
- [x] 2.5 Chamar `throttle.reset(email)` ao concluir a redefinição; verificar com teste que um e-mail bloqueado volta a logar com a nova senha após redefinir
- [x] 2.6 Acrescentar "Esqueci minha senha" em `templates/accounts/login.html` e exibir a mensagem de sucesso (`partials/alert.html`); verificar com teste que o login contém o link e que, após a redefinição, a mensagem aparece

## 3. Segurança e interface

- [x] 3.1 Telas de recuperação em português, com `base_auth.html`, CSRF e erros de campo visíveis; recompilar o CSS (`docker compose run --rm css npm run build`) se surgirem classes novas; verificar que cada tela renderiza (status 200 e conteúdo) e que `AnonymousOnlyMixin` redireciona o autenticado nas telas de pedido
- [x] 3.2 Teste que percorre as rotas novas e confirma que nenhuma resposta do fluxo difere entre e-mail cadastrado e não cadastrado (status, `Location` e corpo normalizado)

## 4. Documentação

- [x] 4.1 Atualizar o `README.md` (fluxo de redefinição em dev lendo o link no Mailpit, as três configurações novas, as rotas) e o modelo de dados com `LoginThrottle`; verificar que os comandos documentados rodam como escritos

## 5. Verificação final

- [x] 5.1 `docker compose exec web pytest --cov --cov-report=term-missing` passa e a cobertura não cai; elevar `fail_under` se subir
- [x] 5.2 `uvx pre-commit run --all-files` passa
- [x] 5.3 Manual: com o Compose no ar, errar a senha N vezes e ver o bloqueio; pedir a redefinição, abrir o link no Mailpit (`127.0.0.1:8025`), trocar a senha, reabrir o link (mensagem de link usado) e entrar com a nova senha; pedir para um e-mail inexistente e comparar as telas
- [x] 5.4 `openspec validate --all` passa (sem `--strict`)
