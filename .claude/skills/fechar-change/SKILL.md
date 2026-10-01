---
name: fechar-change
description: 'Leva uma change do OpenSpec já implementada até o PR aberto: roda a verificação completa, decide se já dá para arquivar ou se a conclusão depende de algo que só existe depois do PR (ex.: CI passando na aba Actions), commita via skill `git-commit` (sempre com confirmação), empurra e abre o PR — sem perguntar se deve abrir, isso é parte da entrega. Use quando o usuário disser "fecha a change X", "abre o PR da change Y", "isso já tá pronto pra virar PR?", ou ao final de um `/opsx:apply` quando o último checkbox de `tasks.md` for marcado. Não use para o commit isolado de artefatos de `/opsx:propose` (esses não commitam ainda) nem para decidir se uma Issue entra na sprint (skill `sprint-gate`).'
license: MIT
---

# Fechar change → PR

## Objetivo

Reunir os passos 7-9 de "Fluxo de trabalho: Issues + OpenSpec" (`AGENTS.md`) — verificar, arquivar,
abrir o PR — numa sequência só, sem pular a pergunta **"esta change já está pronta para arquivar?"**. Nem toda change arquiva de forma
mecânica antes do PR; algumas só provam conclusão depois de ver o resultado num PR de verdade.

## Quando dispara

- Usuário pede para fechar/concluir uma change, ou para abrir o PR dela.
- Ao final de um `/opsx:apply`, quando a última task de `tasks.md` é marcada — é o momento de se
  perguntar se já está pronta, não de assumir que sim.

**Não dispara** logo depois de `/opsx:propose` ou `/opsx:update` — artefatos de planejamento não
commitam sozinhos, só depois que `/opsx:apply` implementar as tasks.

## Passos

### 1. Verificar

Ainda não há quality gate automatizado (lint, testes, CI): a verificação é o que as tasks da
change descrevem. No mínimo:

```bash
openspec validate --all               # sem --strict
docker compose up --build -d          # o ambiente sobe e responde (ver tasks da change)
docker compose down
```

Rode também cada verificação manual listada em `tasks.md` e registre o resultado lá. Quando o
projeto ganhar testes e lint, acrescente os comandos aqui.

Se algo falhar, corrija antes de seguir. Não é o commit nem o PR que existem para empurrar uma
quebra para o CI.

### 2. Pergunte-se: esta change já está pronta para arquivar?

Não é sequência mecânica. Duas respostas possíveis:

- **Caso A — pronta agora.** Todas as tasks marcadas **e verificadas** (passo 1 passou), e nenhum
  critério de conclusão da própria change depende de algo que só existe depois do PR. Arquive já,
  nesta branch, antes de commitar:
  ```bash
  openspec archive <id> --yes   # --yes é obrigatório: sem TTY o comando aborta
  ```
- **Caso B — depende do PR.** A própria `tasks.md` (ou o bom senso) diz que a prova de conclusão só
  existe depois de abrir o PR — por exemplo, confirmar que um workflow de CI passa só é possível
  vendo a aba Actions de um PR de verdade. Não arquive ainda. Registre explicitamente, como task
  pendente, o que falta ("arquivar depois de ver o workflow passar no PR #X") — nunca deixe a change
  parada sem dizer por quê.

Se a resposta for "não sei", trate como Caso B: é melhor adiar o arquivamento e registrar a dúvida
do que arquivar cedo demais.

### 3. Commit

**Nunca `git commit` direto via Bash.** Invoque a skill `git-commit` — ela faz o staging, deriva o
escopo (nome da change) e **pede confirmação da mensagem antes de commitar**, mesmo quando o
usuário já pediu a mudança em si. Isso vale mesmo sob pressão de tempo (PR bloqueado, deploy
esperando).

- Caso A: o commit inclui a implementação e o resultado do `archive` (pasta movida para
  `changes/archive/`, specs mescladas em `openspec/specs/`) — junto ou em commits separados, mas
  ambos **antes** do push.
- Caso B: só a implementação; o `archive` fica para depois, quando o critério pendente aparecer.

### 4. Push

```bash
git push -u origin <branch>   # ou push simples, se o branch já tem upstream
```

Nunca `--force` sem pedido explícito.

### 5. Abrir o PR — sem perguntar se deve

Abrir o PR **faz parte da entrega**, no mesmo pé que o commit e o `archive` — não é um passo
opcional para confirmar depois. Título no mesmo padrão do commit (`feat(<nome-da-change>): ...`, mesmo com
escopo do nome da change): com squash merge ele vira a linha na `main`.

```bash
gh pr create --title "feat(<nome-da-change>): ..." --body "$(cat <<'EOF'
## Resumo
...

## Verificação
- [x] openspec validate --all
- [x] verificações manuais das tasks (ambiente sobe, endpoints respondem)

Closes #<issue>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

O corpo leva: o que entrou, as decisões congeladas no `design.md` com o porquê e a lista de
verificação acima.

**Se for Caso B**, o corpo diz isso explicitamente — "arquivamento pendente, aguardando X" — para
não passar a impressão de que a change já fechou.

### 6. Depois do merge, se ficou em Caso B

Volte e rode `openspec status` quando o critério pendente aparecer (CI verde no PR, por exemplo) —
é o passo que costuma ser esquecido: o PR é mesclado e ninguém checa de novo. Se o
critério já apareceu, arquive ali mesmo, mesmo que isso signifique um commit/PR só para o
`archive`.

## Regras

- **Não pule a pergunta do passo 2.** "Todas as tasks marcadas" não é sinônimo de "pronta para
  arquivar" — só é, se nenhuma delas depender de um resultado que só existe depois do PR.
- **Commit sempre via skill `git-commit`, nunca `git commit` direto.** A confirmação da mensagem não
  é negociável, nem sob pressão de prazo.
- **Abrir o PR não é opcional.** Não pergunte "quer que eu abra o PR?" — abra, como parte da mesma
  entrega do commit e do `archive`. Só pare para perguntar se o usuário pedir explicitamente para
  não abrir ainda (ex.: quer revisar o diff local antes).
- **Se algo no diff parecer segredo** (`.env`, token, credencial) — mesmo com nome de arquivo
  inocente — pare antes do commit e avise, não empurre para descobrir depois.
