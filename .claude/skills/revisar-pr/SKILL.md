---
name: revisar-pr
description: 'Revisa um Pull Request do GitHub: lê o diff, a change do OpenSpec e os comentários já existentes, verifica cada hipótese no código e publica apontamentos inline classificados por criticidade (🔴 Alta, 🟡 Média, 🟢 Baixa), com resumo no corpo e assinatura. Mostra o rascunho e espera aprovação antes de publicar. Use quando o usuário pedir "revisa o PR X", "faça o code review do PR #Y" ou "analisa as alterações do PR Z". Para tratar os comentários que chegaram ao nosso PR, use `responder-review`.'
license: MIT
---

# Revisar Pull Request

## Objetivo

Revisão técnica construtiva de um PR, com apontamentos **verificados** e publicados **inline**, em
conformidade com o `AGENTS.md` e com as specs do OpenSpec. Esta skill só **lê código e escreve no
GitHub**; não altera o repositório. Corrigir o que foi apontado é papel de `responder-review`.

## Quando dispara

- "revisa o PR 21", "faça o code review do PR #18", "analisa o PR aberto".
- Auditoria antes de aprovar ou mesclar uma alteração relevante.

## Regras

1. **Só publique o que foi verificado.** Todo apontamento precisa ter sido confirmado lendo o código
   ou reproduzindo o cenário. Suspeita não confirmada não vira comentário.
2. **Corpo = resumo; problemas = inline.** O corpo traz só o que o PR implementa (arquitetura,
   decisões, pontos fortes, testes) e a assinatura. Não repita os problemas no corpo nem escreva
   frases sobre onde eles foram comentados.
3. **Sem ruído.** Priorize por custo × valor. Nit sem impacto real é 🟢 e, se houver muitos, publique
   só os mais úteis. Não repita o que um review existente (Copilot, humano) já apontou.
4. **Confirmação antes de publicar.** Publicar é visível a terceiros: mostre o rascunho ao usuário e
   só publique após aprovação (passo 5). Se o usuário pediu para não comentar ainda, pare no rascunho.
5. **Assinatura em todo comentário** e no corpo: `_— Revisado por <Assistente>_`, com o nome do
   assistente que está executando.
6. **Idioma:** pt-BR; termos técnicos e nomes de código em inglês (`AGENTS.md`).
7. **`event: "COMMENT"` por padrão.** `APPROVE` e `REQUEST_CHANGES` só se o usuário pedir. Em PR do
   próprio usuário o GitHub só aceita `COMMENT`.

## Criticidade

Cada comentário inline começa com a tag no título. A tag é contrato: `responder-review` a lê.

- `**🔴 [Alta] <Título>**`: vulnerabilidade de segurança, perda ou corrupção de dados, vazamento de
  credencial, quebra de fluxo crítico.
- `**🟡 [Média] <Título>**`: comportamento que contradiz a spec ou o PR, falha em caso esperado sem
  tratamento, concorrência, violação de convenção do projeto.
- `**🟢 [Baixa] <Título>**`: fragilidade de configuração, acessibilidade, legibilidade, reprodutibilidade.

## Passos

### 1. Coletar o contexto

```bash
gh pr view <n> --json title,body,headRefName,baseRefName,commits,files,statusCheckRollup
gh pr diff <n>
gh pr checks <n>
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id, user: .user.login, path, line, body}'
gh pr view <n> --comments
```

- Guarde o SHA do último commit (`commit_id` do review).
- Leia os comentários existentes para não duplicar.
- Se o PR pertence a uma change, leia `proposal.md`, `design.md`, `tasks.md` e a spec.
- CI vermelho é achado: o `AGENTS.md` proíbe mesclar assim.

### 2. Analisar

Considere:

- **Corretude e spec:** atende à Issue e aos cenários da spec? As tasks marcadas estão de fato feitas?
- **Segurança e privacidade:** injeção, CSRF, enumeração, segredos, dados sensíveis em log ou erro.
- **Robustez:** tratamento de erro, transações, idempotência, estados vazios e valores em branco.
- **Convenções do `AGENTS.md`:** código em inglês, texto de tela em pt-BR, Docker-first, sem domínio
  fora de change, segredos fora do repo, cobertura (`fail_under`) sem rebaixar, escopo do commit e
  título do PR no padrão.
- **OpenSpec:** `openspec validate --all` passa; spec e código coerentes; change arquivada se for o caso.

Teste hipóteses no ambiente em vez de supor:

```bash
docker compose exec web pytest
docker compose exec web python manage.py shell -c "..."
```

> **Git:** se precisar trocar de branch para testar, volte à branch original e deixe o working tree
> limpo antes de seguir.

### 3. Mapear as linhas

`line` precisa estar dentro do diff, no lado `RIGHT`; fora dele a API responde 422. Para obter as
linhas válidas:

```bash
gh api repos/{owner}/{repo}/pulls/<n>/files --jq '.[] | {filename, patch}'
```

Se o ponto não estiver em nenhuma linha do diff (ex.: arquivo que deveria existir e não existe),
comente na linha mais próxima da causa ou, só nesse caso, cite no corpo.

### 4. Redigir

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

### 5. Mostrar o rascunho e esperar aprovação

Liste ao usuário, por severidade: `arquivo:linha`, título e a sugestão em uma linha, mais o resumo
que irá no corpo. Aguarde aprovação, e ajuste o que o usuário pedir. Só então publique.

### 6. Publicar

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

Coloque o payload no diretório temporário da sessão, não no repositório.

### 7. Confirmar e responder

```bash
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id, line, path, title: (.body | split("\n")[0])}'
```

Responda ao usuário com o link do review e um resumo curto: quantos apontamentos por severidade e o
principal ponto de atenção.
