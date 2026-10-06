# Proposal

## Why

Os primeiros PRs do Dependabot mostraram que o plano da change `36-dependabot-e-codeql` estava
errado num ponto: ele **não respeita** a faixa `django>=5.2,<5.3` do `pyproject.toml`. O PR #40
reescreveu a faixa para `>=6.1.1,<6.2` e o #39 propôs o salto do Node 22 para o 26. O projeto segue
versões de suporte longo (LTS), e a 5.2 do Django e o Node 22 atendem isso; a 6.1 e o Node 26 não.
Sem uma regra explícita, os dois PRs ficam abertos e o Dependabot continua atualizando-os. Origem:
Issue #36 (mesma Issue da change anterior, que deixou esta correção).

## What Changes

- `.github/dependabot.yml` passa a ignorar mudanças de versão **major e minor do Django** e de
  **major do Node** (imagem do serviço `css`), e o comentário do arquivo deixa de afirmar que o
  Dependabot respeita as faixas do `pyproject.toml`.
- A spec `security-scanning` troca o cenário "Restrição de versão respeitada" (que a prática
  desmentiu) por cenários que descrevem o `ignore`.
- O README corrige o parágrafo equivalente e explica como voltar a aceitar uma versão.

Fora do escopo: migrar o Django ou o Node, fechar ou comentar os PRs #39 e #40 à mão, e qualquer
mudança nos demais ecossistemas.

## Capabilities

### New Capabilities

### Modified Capabilities
- `security-scanning`: o requisito de atualização automatizada passa a excluir as majors/minors do
  Django e a major do Node, em vez de depender da faixa do `pyproject.toml`.

## Impact

- `.github/dependabot.yml` e `README.md`.
- Os PRs abertos #39 e #40 deixam de ter versão aceita; o Dependabot os fecha na próxima rodada.
- Patches do Django 5.2 continuam chegando.
