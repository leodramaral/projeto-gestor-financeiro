# Design

## Context

O `design.md` da change `36-dependabot-e-codeql` dizia que o Dependabot respeita
`django>=5.2,<5.3`. O PR #40 (Django 6.1.1) mostrou o contrário: o ecossistema `uv` reescreveu o
limite superior no `pyproject.toml` e no `uv.lock`. O PR #39 trouxe o Node 26 (Current, com LTS
prevista para outubro de 2026) para o `docker-compose.yml`. Os dois passaram no CI, que não mede
política de suporte. O `config.yaml` do OpenSpec define o Django como "versão LTS".

## Goals / Non-Goals

**Goals:**
- Versionar no `dependabot.yml` a decisão de ficar nas linhas LTS atuais.
- Corrigir os textos que afirmavam que a faixa do `pyproject.toml` bastava.

**Non-Goals:**
- Migrar para Django 6.x ou Node 24/26.
- Alterar os alertas e as atualizações de segurança do repositório.

## Decisions

- **`ignore` no `dependabot.yml`**, não `@dependabot ignore` em cada PR: o comando vale só para
  aquele PR e não fica no repositório. Django: `version-update:semver-major` e `semver-minor`
  (5.2 → 6.x é major; 5.2 → 5.3 seria minor). Node (ecossistema `docker-compose`):
  `version-update:semver-major`, porque a tag `22-alpine` já acompanha os patches da 22.
- **Não fechar nem comentar os PRs #39 e #40 à mão.** Com a regra publicada, o Dependabot os
  reavalia na próxima rodada e os fecha.
- **Voltar a aceitar uma versão** é remover a entrada de `ignore`, e o README diz isso.
- **Corrigir o comentário do `dependabot.yml` e o README** no mesmo PR, para o repositório não
  carregar duas versões do que o Dependabot faz.

## Risks / Trade-offs

- [Ignorar majors do Django pode esconder correção de segurança] → os patches 5.2.x seguem
  chegando; a rotina de alertas e as atualizações de segurança do repositório continuam ligadas.
  Se um alerta exigir major, ele aparece na aba Security e a decisão é humana.
- [O `ignore` fica esquecido quando a 6.2 LTS ou o Node 26 LTS chegarem] → o comentário no arquivo
  e o README dizem como e quando reavaliar.
- [A efetividade só aparece depois do merge] → o Dependabot lê o arquivo da `main`; o resultado
  (PRs #39 e #40 fechados) é conferido com `gh` depois do merge, sem task pendente.
