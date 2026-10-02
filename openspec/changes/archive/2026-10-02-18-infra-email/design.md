# Design

## Context

O projeto não tem nenhuma configuração de e-mail e ainda não tem modelo de usuário (ver
`proposal.md`). A configuração vive em `config/settings/{base,dev,test,prod}.py`, lida com
`django-environ`; `SECRET_KEY` e `DATABASE_URL` já não têm padrão e derrubam a subida se faltarem.
No Compose, `environment` vence `env_file` (ver `AGENTS.md`). Existe um único app, `core`, e a
pasta `templates/` na raiz com `base.html` (TailAdmin) e `partials/`.

## Goals / Non-Goals

**Goals:**
- Validar de ponta a ponta, no Compose, que um e-mail com link sai da aplicação e é visível.
- Deixar um ponto único de envio (`send_templated_email`) para as Issues #2 e #19 reutilizarem.
- Manter a produção agnóstica de provedor: só SMTP por variável de ambiente.

**Non-Goals:**
- Escolher provedor de produção, configurar domínio/SPF/DKIM ou enviar e-mail real.
- Envio assíncrono, fila, reenvio automático ou rastreio de entrega.
- Reaproveitar o layout TailAdmin nos e-mails (e-mail exige HTML próprio, com CSS inline).

## Decisions

**1. Mailpit como caixa de entrada de dev.** Imagem `axllent/mailpit`, um contêiner único, com
interface web em `127.0.0.1:8025` e SMTP em `mailpit:1025` apenas na rede do Compose (porta 1025
não é publicada). Sem volume: as mensagens somem ao recriar o contêiner, o que é desejável.
O `web` não depende dele para subir (`depends_on` simples, sem health) — se o Mailpit estiver
fora, só o envio falha. *Alternativas:* backend de console (sugerido na Issue #2) não mostra HTML
nem valida o link clicável; MailHog está sem manutenção; um SMTP real em dev arrisca enviar para
terceiros.

**2. Backend por ambiente, configuração em Python e não em `.env`, no dev.** `dev.py` fixa
`EMAIL_BACKEND` SMTP com `EMAIL_HOST="mailpit"`, `EMAIL_PORT=1025`, sem TLS e sem autenticação, e
`EMAIL_TIMEOUT=10` em `base.py` para todos os ambientes: não há segredo em dev, e assim o `.env` do desenvolvedor não ganha variáveis obrigatórias nem há
risco de `environment` sobrescrever `env_file`. `test.py` usa `locmem` (Django já troca para isso
sob o pytest-django, mas fixar explicitamente documenta a intenção). `prod.py` lê tudo por
variável (decisão 3). *Alternativa:* um único `EMAIL_URL` com `env.email_url()`; descartada por
embutir senha em URL (exige escapar caracteres) e mascarar qual variável falta.

**3. Variáveis de produção, todas validadas na subida.** Obrigatórias, sem padrão: `EMAIL_HOST`,
`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SITE_URL`. Com padrão seguro:
`EMAIL_PORT=587` e `EMAIL_USE_TLS=true`. `django-environ` já falha com
`ImproperlyConfigured: Set the X environment variable` sem imprimir valores, o que satisfaz o
requisito de não vazar credencial. `SERVER_EMAIL` fica no padrão do Django. Exigir usuário e
senha exclui relays SMTP sem autenticação; aceitável porque provedores transacionais exigem.

**4. `SITE_URL` em settings, não `django.contrib.sites`.** Links em e-mail precisam de esquema e
host mesmo fora de uma requisição (comando, tarefa futura). Basta uma string: dev
`http://127.0.0.1:8000` em `dev.py`, test fixo, prod obrigatória. `request.build_absolute_uri`
não serve fora de request e, atrás de proxy, depende de cabeçalhos; `contrib.sites` traz tabela e
migração por ganho nenhum com um único domínio.

**5. Módulo `core/emailing.py` com `send_templated_email(to, subject, template, context)`.**
Renderiza `<template>.txt` e `<template>.html` de `templates/email/`, monta
`EmailMultiAlternatives` (texto como corpo, HTML como alternativa), injeta `site_url` no contexto
e envia com `fail_silently=False`. Texto sempre presente. O escape do HTML vem do autoescape do
Django; o `.txt` é renderizado com `autoescape off` para não gravar `&amp;` no texto puro.
Assunto sem quebra de linha (o Django já rejeita header injection). *Alternativa:* um helper por
tipo de e-mail; adiado, pois os tipos reais nascem nas Issues #2/#19 e usarão este núcleo.
O nome é `emailing` para não sombrear o pacote `email` da biblioteca padrão.

**6. Templates em `templates/email/`.** `base.txt` e `base.html` com `{% block content %}`;
o HTML usa tabelas e CSS inline (compatibilidade com clientes de e-mail), marca "Gestor
Financeiro" e rodapé. Um par `test_message.{txt,html}` serve ao comando e aos testes; as features
seguintes adicionam os seus. Idioma pt-BR; não importam o `base.html` do site.

**7. Comando `send_test_email <endereço>` em `core/management/commands/`.** Chama o núcleo da
decisão 5 com um link `SITE_URL` de exemplo. Em falha de conexão (`OSError`/`SMTPException`)
termina com `CommandError` identificando a falha, sem repetir configuração. É o roteiro de
verificação manual: sobe o Compose, roda o comando, abre `127.0.0.1:8025`.

**8. Testes.** Com `locmem` e `mail.outbox`: assunto, partes texto/HTML, escape, link com
`SITE_URL`, comando (sucesso e falha de conexão simulada). A validação de produção é testada
importando `config.settings.prod` num `subprocess` com o ambiente controlado e uma variável por vez
removida (não há teste análogo hoje; `base.py` avalia `env(...)` na importação, então basta o
import falhar).

## Risks / Trade-offs

- [Dev difere da prod: Mailpit aceita tudo, SMTP real exige TLS/autenticação] → o backend é o
  mesmo SMTP do Django nos dois; a diferença fica só em parâmetros. A verificação com provedor
  real fica para a change de deploy.
- [E-mail HTML renderiza diferente em cada cliente] → HTML simples e a parte em texto sempre
  presente; teste visual manual só no Mailpit.
- [Envio síncrono bloqueia a requisição se o SMTP estiver lento] → aceitável no volume atual;
  definir `EMAIL_TIMEOUT` (10 s) em todos os ambientes para não pendurar a requisição.
- [Exigir credencial SMTP em prod trava quem usa relay aberto] → decisão consciente; revisitar se
  o provedor escolhido não usar autenticação.
- [`SITE_URL` errada em prod gera links quebrados em e-mail] → obrigatória e documentada no
  `.env.example` e no README.

## Migration Plan

Sem migração de dados nem mudança de contrato. Quem já tem `.env` local não precisa alterar nada
(dev usa Mailpit sem variáveis); `docker compose up` baixa a imagem do Mailpit na primeira vez.
Rollback: reverter o commit. Para produção, as cinco variáveis novas devem existir antes do
primeiro deploy que contiver esta change (nenhum deploy existe ainda).
