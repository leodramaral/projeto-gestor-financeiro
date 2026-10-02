# Proposal

## Why

A confirmação de conta (Issue #2) e a recuperação de senha (Issue #19) dependem de enviar e-mail
com link. Hoje não há nenhuma configuração de e-mail no projeto, e descobrir isso no meio das
features de autenticação misturaria dois problemas. Esta change valida a solução de e-mail
sozinha, antes de existir modelo de usuário, para que as duas features seguintes só a consumam.

Origem: Issue #18 (Item 1.1 — Infra de e-mail transacional).

## What Changes

- Serviço `mailpit` no `docker-compose.yml`: caixa de entrada fake para dev (interface em
  `127.0.0.1:8025`, SMTP só na rede interna do Compose).
- Configuração de e-mail por ambiente em `config/settings/`: SMTP para o Mailpit em dev, backend em
  memória em teste e SMTP configurável por variável de ambiente em prod (que falha ao subir se
  faltar variável obrigatória).
- Setting `SITE_URL`, base dos links absolutos em e-mails enviados fora de uma requisição.
- Função `send_templated_email` e templates-base de e-mail em pt-BR (texto e HTML), que as
  features seguintes reutilizam.
- Comando `send_test_email` para validar o envio ponta a ponta no Compose.
- Testes com pytest do envio e do conteúdo da mensagem.
- `.env.example` e README descrevem as variáveis e o uso do Mailpit.

**Fora do escopo:** modelo de usuário, telas, confirmação de conta, redefinição de senha e limite
de tentativas (Issues #2 e #19); escolha do provedor de e-mail de produção (a prod só recebe
credenciais SMTP por variável); configuração de domínio, SPF/DKIM e deploy (Issue de deploy);
fila assíncrona de envio (envio síncrono basta por ora).

## Capabilities

### New Capabilities
- `transactional-email`: envio de e-mail transacional com configuração por ambiente, caixa de
  entrada local para desenvolvimento, templates-base e validação por comando e testes.

### Modified Capabilities

## Impact

- `docker-compose.yml`: novo serviço `mailpit`.
- `config/settings/{base,dev,test,prod}.py`: configuração de e-mail e `SITE_URL`.
- `core/`: módulo de envio e comando de gerenciamento; `templates/email/`: templates-base.
- `.env.example`, `README.md`: novas variáveis e instruções.
- Sem nova dependência Python; sem migração.
