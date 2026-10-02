# Tasks

## 1. Caixa de entrada local (Mailpit)

- [x] 1.1 Adicionar o serviço `mailpit` ao `docker-compose.yml` (UI em `127.0.0.1:8025`, SMTP 1025 sem publicar) e verificar que `docker compose up` o sobe e `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8025` retorna 200
- [x] 1.2 Verificar que a porta 1025 não está publicada no host (`docker compose ps` não lista `1025->`) e que a 8025 só escuta em `127.0.0.1`

## 2. Configuração por ambiente

- [x] 2.1 Em `base.py`, definir `EMAIL_TIMEOUT = 10`; em `dev.py`, SMTP para `mailpit:1025` sem TLS/autenticação e `SITE_URL = "http://127.0.0.1:8000"`; verificar com `docker compose exec web python manage.py shell -c "from django.conf import settings as s; print(s.EMAIL_HOST, s.EMAIL_PORT, s.SITE_URL)"`
- [x] 2.2 Em `test.py`, fixar o backend `locmem` e `SITE_URL` de teste; verificar com um teste que `settings.EMAIL_BACKEND` termina em `locmem.EmailBackend`
- [x] 2.3 Em `prod.py`, ler `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` e `SITE_URL` sem padrão, e `EMAIL_PORT` (587) e `EMAIL_USE_TLS` (true) com padrão; verificar com teste em `subprocess` que a importação de `config.settings.prod` falha, nomeando a variável e sem imprimir valores, ao remover cada uma das cinco, e passa com todas presentes
- [x] 2.4 Documentar as variáveis de produção em `.env.example` (seção "Somente prod", sem valores reais) e verificar que `git diff .env.example` não contém segredo

## 3. Envio a partir de templates

- [x] 3.1 Criar `templates/email/base.txt`, `base.html` (tabelas + CSS inline, pt-BR) e `test_message.{txt,html}`; verificar que o arquivo existe e que o HTML renderiza sem erro de template
- [x] 3.2 Criar `core/emailing.py` com `send_templated_email` (texto + HTML, `site_url` no contexto, `.txt` sem autoescape); verificar com teste que `mail.outbox[0]` tem corpo em texto e uma alternativa `text/html`
- [x] 3.3 Testar o escape: contexto com `<script>` e `&` aparece escapado no HTML e literal no texto
- [x] 3.4 Testar que o link do e-mail começa por `settings.SITE_URL` e que o assunto não aceita quebra de linha (levanta erro)

## 4. Comando de validação

- [x] 4.1 Criar `core/management/commands/send_test_email.py` (argumento: endereço) e testar com `call_command` que envia uma mensagem para `mail.outbox`
- [x] 4.2 Testar que, com `SMTPException`/`OSError` simulados, o comando termina com `CommandError` identificando a falha, sem exibir configuração

## 5. Documentação

- [x] 5.1 Atualizar o `README.md`: o Mailpit na subida, `docker compose exec web python manage.py send_test_email voce@exemplo.com`, variáveis de e-mail de produção; verificar que cada comando documentado roda como escrito

## 6. Verificação final

- [x] 6.1 `docker compose exec web pytest` passa, incluindo os novos testes
- [x] 6.2 Manual: com o Compose no ar, rodar `send_test_email` e confirmar em `http://127.0.0.1:8025` que a mensagem chegou com texto, HTML e link para `http://127.0.0.1:8000`
- [x] 6.3 `openspec validate --all` passa (sem `--strict`)
