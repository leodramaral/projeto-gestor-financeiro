---
name: responder-review
description: 'Trata os comentários de review recebidos no nosso Pull Request (de bots como o Copilot, de pessoas ou da skill `revisar-pr`): coleta, verifica cada achado no código, recomenda resolver ou não, espera a decisão do usuário, aplica as correções com verificação e commit, empurra e responde em cada comentário citando o commit. Use quando o usuário disser "analise os comentários do PR X", "resolva os comentários do review", "faz sentido resolver?" ou "responda os comentários". Para revisar um PR, use `revisar-pr`.'
license: MIT
---

# Responder review

## Objetivo

Transformar os comentários de um review em decisões fundamentadas, correções verificadas e respostas
rastreáveis. Cobre o ciclo: **coletar → triar → o usuário decide → corrigir → verificar → commitar →
empurrar → responder**.

## Quando dispara

- "analise os comentários do PR 20 e diga se faz sentido resolver".
- "resolva os comentários", "aplique as correções do review", "responda os comentários".

## Regras

1. **Verifique antes de concordar.** Um comentário (de bot ou de pessoa) pode estar certo, errado ou já
   resolvido. Leia o código atual e, se for barato, reproduza o cenário.
2. **O usuário decide.** Apresente a triagem com uma recomendação e **espere**. Não implemente antes.
3. **Responda só depois do push.** Cada resposta cita o hash curto do commit que contém a correção.
4. **Commit novo; nunca `--amend` em commit já publicado** e nunca `--force`. `--force-with-lease`
   só se o usuário pedir e o commit ainda não estiver no remoto.
5. **Commit sempre via skill `git-commit`**, com a confirmação da mensagem.
6. **Siga o fluxo do repo** (`AGENTS.md`): o que for do escopo da change vira task/ajuste de spec
   **antes** de ser feito; o que for de outro escopo vira Issue e não desvia o trabalho.
7. **Não rebaixe `fail_under`**, não use `--no-verify` e não marque como resolvido o que não foi
   verificado.
8. **Recusar comentário de pessoa é decisão do usuário.** Para bots, recomende e justifique; para
   pessoas, não responda "não vou fazer" sem o usuário aprovar o texto.

## Passos

### 1. Coletar

```bash
gh pr view <n> --json title,state,headRefName,body
gh pr view <n> --comments
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id, user: .user.login, path, line, body, diff_hunk}'
gh api repos/{owner}/{repo}/pulls/<n>/reviews --jq '.[] | {user: .user.login, state, body}'
```

- Inclua os achados que só aparecem no **resumo** de bots (ex.: o Copilot lista achados de poucos
  votos que não viram comentário inline).
- Ignore threads já resolvidos ou desatualizados (`outdated`), a menos que o problema persista.
- Garanta que está na branch do PR (`headRefName`) e que o working tree está limpo.

### 2. Triar

Para cada achado, abra o arquivo e o `diff_hunk` e responda:

- **Procede?** O problema existe no código atual? Contradiz a spec, o PR ou o `.env.example`?
- **Impacto real:** quem sofre, quando e com que frequência?
- **Custo:** quantas linhas, quais arquivos, mexe em spec? Há risco de regressão?
- **Escopo:** é desta change ou de outra Issue?

Veredito por achado: **Resolver**, **Não resolver** (com motivo) ou **Já resolvido**. Evite resolver o
que só adiciona complexidade sem ganho (ex.: healthcheck para algo que só roda sob demanda).

### 3. Apresentar e esperar

Mostre uma tabela curta: achado, severidade, veredito, motivo em uma linha, custo. Termine com a
recomendação e pergunte o que o usuário quer fazer. **Pare aqui** até a resposta.

### 4. Corrigir

- Aplique só o que o usuário aprovou, na menor mudança que resolve.
- Se o comportamento especificado muda, atualize a spec (`openspec/specs/...` quando a change já foi
  arquivada) e inclua um cenário que cubra o caso.
- Acrescente teste que **falha sem a correção** quando houver lógica envolvida.

### 5. Verificar

```bash
docker compose exec web pytest
openspec validate --all
uvx pre-commit run --all-files
```

Rode também a verificação manual relevante (ex.: `send_test_email` quando mexer em e-mail). Se algo
falhar, corrija antes de seguir; não commite com a verificação vermelha.

### 6. Commitar e empurrar

Use a skill `git-commit` (tipo `fix`, ou o que couber, com o escopo da Issue). Liste no corpo o que
mudou e por quê. Depois:

```bash
git push
```

### 7. Responder em cada comentário

Só depois do push. Para comentário inline:

```bash
gh api repos/{owner}/{repo}/pulls/<n>/comments/<id>/replies -f body='<texto>' --jq .html_url
```

- **Resolvido:** diga o que mudou, citando o hash (`Ajustado em <sha>: ...`), em uma ou duas frases.
- **Não resolvido:** diga o motivo objetivamente, sem tom defensivo.
- Termine com `_— Respondido por <Assistente>_`.
- Achados que só existem no resumo do bot não têm thread: cite-os no relato ao usuário e, se ele
  quiser, em um comentário geral do PR (`gh pr comment`).
- Resolver o thread (`resolveReviewThread`, GraphQL) só se o usuário pedir.

### 8. Relatar

Diga ao usuário o que foi corrigido (com o hash), o que ficou de fora e por quê, o resultado da
verificação e os links das respostas.
