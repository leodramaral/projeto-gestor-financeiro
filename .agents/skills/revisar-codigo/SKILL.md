---
name: revisar-codigo
description: 'Revisa código de um Pull Request aberto do GitHub. Um juiz em subagente de contexto limpo avalia o diff pela rubrica da skill (cada cenário da spec tem um teste que o prova, testes que passam mesmo com o código quebrado, aderência ao `AGENTS.md`, severidade ancorada), um script confere cada citação `arquivo:linha`, cada hipótese é verificada no código e os apontamentos saem inline por criticidade (🔴 Alta, 🟡 Média, 🟢 Baixa), com resumo no corpo e assinatura. Problema fora do escopo do PR vira proposta de Issue. Mostra o rascunho e espera aprovação antes de publicar. Use quando o usuário pedir "revisa o PR X", "faça o code review do PR #Y" ou "analisa as alterações do PR Z". Para tratar os comentários que chegaram ao nosso PR, use `tratar-review`.'
license: MIT
---

# Revisar código

## Objetivo

Revisão técnica construtiva, com apontamentos **verificados** e publicados **inline**, em
conformidade com o `AGENTS.md` e com as specs do OpenSpec. Um juiz independente (subagente) aplica a
rubrica; esta skill confere o que ele disse, mostra o rascunho e, aprovado, publica. Ela só **lê
código e escreve no GitHub** (comentários do review e Issues aprovadas); não altera o repositório.
Corrigir o que foi apontado é papel de `tratar-review`.

Os arquivos da skill:

- `rubric.md`: a rubrica do juiz (escopo, severidade, critérios T1-T5 e C1, formato da resposta).
  É a fonte única desses critérios e da escala de severidade: ajuste-a lá, não aqui.
- `scripts/verify_citations.py`: confere as citações do veredito. Só usa a biblioteca padrão do
  Python; a skill é autocontida e pode ser copiada para outro projeto (os testes dele ficam em
  `scripts/tests/` deste repositório).

## Papéis

- **Juiz (quality gate):** subagente de contexto limpo, rubrica fixa, resposta em JSON. Responde só se
  os testes provam a spec (T1-T5) e se o código a implementa (C1). É repetível e comparável entre
  rodadas; por isso roda duas vezes.
- **Revisor (esta skill):** confere o veredito (citações, reprodução), faz a revisão geral que o juiz
  não faz (passo 5: convenções, simplicidade, robustez e segurança, legibilidade, OpenSpec, CI) e
  publica. É julgamento aberto, com o contexto completo.

Se o juiz apontar algo fora do recorte, vai para `limites`; quem decide se vira apontamento é o
revisor.

## Quando dispara

- "revisa o PR 21", "faça o code review do PR #18", "analisa o PR aberto".
- Auditoria antes de aprovar ou mesclar uma alteração relevante.

A revisão parte sempre de um **PR aberto** (ou já mesclado, para auditoria). Nenhuma outra skill a chama,
em especial o `fechar-change`: quem escreveu o código não deve revisar a própria entrega no fluxo que
a abre.

## Regras

1. **Só publique o que foi verificado.** Todo apontamento precisa ter sido confirmado lendo o código
   ou reproduzindo o cenário. Suspeita não confirmada não vira comentário. Citação que o verificador
   reprova não é publicada, a menos que você confirme o achado lendo o código e corrija a citação.
2. **Corpo = resumo; problemas = inline.** O corpo traz só o que o PR implementa (arquitetura,
   decisões, pontos fortes, testes) e a assinatura. Não repita os problemas no corpo nem escreva
   frases sobre onde eles foram comentados.
3. **Só o que o PR altera.** Problema que já existia, ou em código que o PR não tocou, não é
   comentário do review: se for real e verificado, vira **proposta de Issue** (passo 6).
4. **Sem ruído.** Priorize por custo × valor. Nit sem impacto real é 🟢 e, se houver muitos, publique
   só os mais úteis. Não repita o que um review existente (Copilot, humano) já apontou.
5. **Confirmação antes de publicar.** Publicar é visível a terceiros: mostre o rascunho ao usuário e
   só publique após aprovação (passo 7). Vale para o review e para cada Issue. Se o usuário pediu
   para não comentar ainda, pare no rascunho.
6. **O juiz só lê.** Ele nunca escreve no repositório nem no GitHub; quem publica é você, depois da
   aprovação.
7. **Assinatura em todo comentário** e no corpo: `_— Revisado por <Assistente>_`, com o nome do
   assistente que está executando.
8. **Idioma:** pt-BR; termos técnicos e nomes de código em inglês (`AGENTS.md`).
9. **`event: "COMMENT"` por padrão.** `APPROVE` e `REQUEST_CHANGES` só se o usuário pedir. Em PR do
   próprio usuário o GitHub só aceita `COMMENT`.

## Criticidade

Cada comentário inline começa com a tag no título. A tag é contrato: `tratar-review` a lê. As
definições (ancoradas no que acontece se o problema chegar à produção) estão em `rubric.md`, na seção
Severidade:

- `**🔴 [Alta] <Título>**`: severidade `alta` da rubrica.
- `**🟡 [Média] <Título>**`: severidade `media`.
- `**🟢 [Baixa] <Título>**`: severidade `baixa`.

## Passos

### 1. Coletar o contexto

```bash
gh pr view <n> --json title,body,headRefName,baseRefName,commits,files,statusCheckRollup
gh pr checks <n>
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id, user: .user.login, path, line, body}'
gh pr view <n> --comments
```

- Leia os comentários existentes para não duplicar.
- Se o PR pertence a uma change, leia `proposal.md`, `design.md`, `tasks.md` e a spec.
- CI vermelho é achado: o `AGENTS.md` proíbe mesclar assim.

### 2. Preparar o snapshot e o diff

O juiz lê o código **na versão sob revisão**, não no working tree: a ponta do PR. O snapshot fica em `worktrees/` (já
ignorada pelo git e pelo Docker, e visível ao contêiner para o verificador). `<id>` é `pr<n>`.

```bash
id=pr<n>
# PR aberto: a ponta do PR e o ponto onde ele saiu da base
git fetch origin pull/<n>/head && head=$(git rev-parse FETCH_HEAD)
base=$(git merge-base origin/<baseRefName> "$head")
# PR já mesclado: head=<mergeCommit>, base=<mergeCommit>^1.

mkdir -p worktrees/review-$id
git archive "$head" -- . ':!design' ':!static/dist' ':!node_modules' ':!worktrees' | tar -x -C worktrees/review-$id
git diff "$base" "$head" -- . ':(exclude)*.svg' ':(exclude)*.figcraft' ':(exclude)static/dist' > worktrees/review-$id.diff
git diff --stat "$base" "$head" > worktrees/review-$id.stat
```

O diff é o do PR **inteiro** (código, testes, templates, specs); só SVG, `.figcraft` e `static/dist`
ficam de fora do patch e aparecem no `.stat`. Não troque de branch para isso.

### 3. Julgar (dois subagentes de contexto limpo)

Lance **dois** subagentes `general-purpose` **em paralelo** (numa só mensagem), sem o histórico da
conversa, com o prompt abaixo (troque os `<...>`; `<k>` é `1` e `2`, cada um grava o seu arquivo). Um
juiz sozinho deixa passar achados reais de uma execução para outra; a união das duas rodadas, com as
citações conferidas, recupera o que uma delas perdeu. Se puder, peça um modelo diferente do que
escreveu o código (parâmetro `model`): o juiz tende a gostar do código que se parece com o dele.

```text
Você é um juiz de qualidade de código e testes. Leia a rubrica e siga-a à risca:
<caminho desta skill>/rubric.md

Objeto: PR <n> deste repositório.
- Snapshot do código na versão sob revisão (só leitura; leia os arquivos DAQUI): worktrees/review-<id>
- Diff do PR inteiro: worktrees/review-<id>.diff  (e o resumo: worktrees/review-<id>.stat)
- Change (specs delta, tasks, design): <pasta da change dentro do snapshot, ou "sem change">
- Regras do projeto: worktrees/review-<id>/AGENTS.md

Restrições: só leitura; não rode testes nem comandos que alterem algo; não edite o snapshot nem o
projeto. ÚNICA exceção: grave o JSON final com Write em worktrees/review-<id>.<k>.json e devolva o
mesmo JSON. Cite caminhos completos a partir da raiz do repositório (as citações serão conferidas por
script). Entregue o JSON do formato da rubrica, com a T1_matriz completa (uma linha por cenário).
```

### 4. Conferir as citações

Rode o verificador **em cada** veredito:

```bash
for k in 1 2; do
  docker compose run --rm --no-deps web python .claude/skills/revisar-codigo/scripts/verify_citations.py \
    worktrees/review-$id.$k.json worktrees/review-$id
done
```

- **Falha** (arquivo inexistente, linha fora do arquivo, trecho que não aparece): o achado não é
  publicado. Leia o código: se o achado for real, corrija a citação e siga; senão, descarte.
- **Aviso** (nome de arquivo sem caminho completo, ambíguo): não é erro; confira à mão se for um
  achado.

### 5. Unir as duas rodadas e verificar o resto

Una os dois vereditos antes de verificar:

- **Achados:** a união. Dois achados são o mesmo quando apontam o mesmo arquivo, a até 3 linhas de
  distância, para o mesmo problema; fique com um só, com a maior severidade que você conseguir
  confirmar. Achado que só uma rodada trouxe **não** é rebaixado por isso: o que vale é a verificação
  abaixo.
- **Matriz do T1:** cenário a cenário. Se as rodadas discordam, adote o pior caso
  (`ausente` > `manual` > `automatizada`) e confirme lendo o teste citado; quem tiver razão decide.
- **`fora_do_escopo`:** a união, sem duplicar o mesmo defeito.

O veredito é a base, não a palavra final. Para cada achado 🟡 e 🔴, confirme lendo o código e, quando
for barato, reproduzindo o que o juiz descreveu (qual linha mudar e qual teste continua passando).
Agora faça a revisão geral, que o juiz não cobre. Leia o diff com estes critérios (cada achado tem
severidade pela rubrica e precisa ser confirmado no código):

- **Convenções do `AGENTS.md` (C2):** código, comentários e logs em inglês; texto de produto em
  pt-BR; ícone da Lucide; aviso como toast; sem segredo; domínio só dentro de change.
- **Simplicidade (C3):** sem abstração sem uso, duplicação evitável, função longa ou ramificada
  demais (complexidade máxima 10).
- **Robustez e segurança (C4):** consultas escopadas por usuário, entrada validada, erros sem vazar
  detalhe, sem XSS (texto entra como texto).
- **Legibilidade (C5):** nomes claros; comentário só onde o porquê não é óbvio; segue o estilo do
  entorno.

E também:

- **Privacidade:** injeção, CSRF, enumeração, segredos, dados sensíveis em log ou erro.
- **OpenSpec:** `openspec validate --all` passa; spec e código coerentes; change arquivada se for o caso.
- **Processo do `AGENTS.md`:** Docker-first, cobertura (`fail_under`) sem rebaixar, escopo do commit
  e título do PR no padrão.

Teste hipóteses no ambiente em vez de supor:

```bash
docker compose exec web pytest
docker compose exec web python manage.py shell -c "..."
```

> **Git:** se precisar trocar de branch para testar, volte à branch original e deixe o working tree
> limpo antes de seguir.

### 6. Montar o rascunho a partir do veredito unido

- **Matriz do T1** (todos os cenários da change): vai só no rascunho, para o usuário; **não** é
  publicada.
- **Achados** (`achados_principais`, incluindo cada cenário `ausente`): viram comentários inline, com
  a severidade pela rubrica.
- **Avisos `manual`** (cenário só verificado à mão): na apresentação, **agrupados por task**, um item
  por task com os cenários dela ("task 5.1: abertura no celular, alternar a visão, tema alternado").
  São 🟢 e ficam no rascunho; só viram comentário se o usuário pedir, num único comentário 🟢 por
  task, na linha da task em `tasks.md` (se estiver no diff).
- **Issues sugeridas** (`fora_do_escopo`): agrupe, **uma Issue por defeito real distinto**; lacunas
  de cenário sem teste que já existiam, **uma por spec**. Antes de propor, procure duplicata:

  ```bash
  gh issue list --state all --search "<termos>" --json number,title,state
  ```

  Cada Issue segue o molde do repositório (pt-BR): origem (o PR e este review), problema
  com a evidência `arquivo:linha`, severidade indicativa pela rubrica, sugestão de correção e o que
  fica fora do escopo. Use só rótulos que existem (`gh label list`).

### 7. Mapear as linhas, redigir e mostrar o rascunho

`line` precisa estar dentro do diff, no lado `RIGHT`; fora dele a API responde 422. Para obter as
linhas válidas:

```bash
gh api repos/{owner}/{repo}/pulls/<n>/files --jq '.[] | {filename, patch}'
```

Se o ponto não estiver em nenhuma linha do diff (ex.: arquivo que deveria existir e não existe),
comente na linha mais próxima da causa ou, só nesse caso, cite no corpo.

Cada comentário tem: título com ícone e severidade; o problema e o impacto real, em poucas linhas;
**Sugestão** com código ou orientação objetiva; assinatura. Modelo (cerca de 4 crases porque o
exemplo contém um bloco de código):

````markdown
**🟡 [Média] Valor vazio é aceito na validação de startup**

`env("NOME")` só distingue variável ausente de definida; `NOME=` passa como string vazia e o erro só
aparece no primeiro uso.

**Sugestão:** rejeitar vazio na leitura.

```python
value = env(name)
if not value.strip():
    raise ImproperlyConfigured(f"Defina {name}.")
```

_— Revisado por <Assistente>_
````

Mostre ao usuário, nesta ordem: (1) a matriz do T1; (2) os achados por severidade, com
`arquivo:linha`, título e a sugestão em uma linha; (3) os avisos `manual` agrupados por task; (4) as
Issues sugeridas (título, o que agrupam, duplicatas encontradas); (5) o resumo que irá no corpo.
Aguarde aprovação e ajuste o que o usuário pedir.

### 8. Publicar

Monte o payload em arquivo JSON, com um script Python, para evitar problemas de escape no shell, e
envie:

```bash
gh api --method POST repos/{owner}/{repo}/pulls/<n>/reviews --input payload.json
```

```json
{
  "commit_id": "<HEAD_SHA>",
  "body": "## Code Review: PR #<n> - <Título>\n\n### Resumo do que foi implementado\n\n<resumo>\n\n---\n_— Revisado por <Assistente>_",
  "event": "COMMENT",
  "comments": [
    {"path": "caminho/arquivo.py", "line": 77, "side": "RIGHT", "body": "**🔴 [Alta] ...\n\n_— Revisado por <Assistente>_"}
  ]
}
```

Coloque o payload em `worktrees/`, não em outra pasta do repositório. Depois, crie **só as Issues
que o usuário aprovou**, uma a uma:

```bash
gh issue create --title "<título>" --label <rótulo> --body-file worktrees/issue-<k>.md
```

### 9. Confirmar, responder e limpar

```bash
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id, line, path, title: (.body | split("\n")[0])}'
chmod -R u+w worktrees/review-$id && rm -rf worktrees/review-$id worktrees/review-$id.* worktrees/issue-*.md
```

Responda ao usuário com o link do review, as Issues criadas e um resumo curto: quantos apontamentos
por severidade e o principal ponto de atenção.
