---
name: code-review
description: 'Executa code review completo de um Pull Request no GitHub: analisa o diff e o contexto da change, sumariza o que foi implementado no corpo do review, publica comentários inline diretamente nas linhas do diff classificados por criticidade com ícones (🔴 Alta, 🟡 Média, 🟢 Baixa), sem redundância entre o cabeçalho e os comentários, e inclui assinatura em todos os apontamentos. Use quando o usuário pedir "faça o code review do PR X", "revisa o PR #Y", "analisa as alterações do PR Z" ou mencionar code review de um PR.'
license: MIT
---

# Code Review de Pull Request

## Objetivo

Conduzir uma revisão técnica aprofundada, padronizada e construtiva de Pull Requests no GitHub,
garantindo alta qualidade de código, segurança, conformidade com a arquitetura do projeto e
especificações do OpenSpec, publicando os apontamentos diretamente **inline** no PR.

## Quando dispara

- O usuário pede para revisar ou fazer code review de um PR (ex.: "faça o code review do PR 21",
  "revisa o PR #18", "analisa o PR aberto").
- Como etapa de auditoria antes da aprovação ou mesclagem de alterações significativas.

## Diretrizes e Não-Negociáveis

1. **Sem redundância entre cabeçalho e inline:**
   - O corpo do review (cabeçalho geral) deve conter **apenas o resumo do que o PR implementa**
     (arquitetura, decisões técnicas, pontos fortes observados, cobertura de testes) e a assinatura.
   - **NÃO liste ou detalhe os problemas no corpo do review** se eles forem comentados inline.
   - Não adicione meta-comentários no cabeçalho sobre onde os apontamentos foram colocados
     (ex.: evitar frases como *"os apontamentos foram comentados inline nas linhas correspondentes"*).
2. **Apontamentos estritamente inline:**
   - Todos os problemas, riscos de segurança, bugs, inconsistências e sugestões de melhoria
     devem ser comentados diretamente na linha correspondente do diff do PR.
3. **Classificação por criticidade com ícones obrigatórios:**
   Cada comentário inline DEVE iniciar com a tag de criticidade no título:
   - `**🔴 [Alta] <Título>**`: Vulnerabilidades de segurança (ex.: oráculos de enumeração, falhas de
     autorização), risco de perda de dados, vazamento de credenciais ou quebra de fluxo crítico.
   - `**🟡 [Média] <Título>**`: Inconsistências de comportamento/especificação (ex.: login case-insensitive
     quebrando no Django Admin), problemas de concorrência, ausência de tratamento de exceções
     esperadas ou violação de convenções de arquitetura.
   - `**🟢 [Baixa] <Título>**`: Fragilidades de configuração/ambiente (ex.: caminhos sem normalização de
     barra), pequenas melhorias de UX/acessibilidade (`autocomplete`, `aria-label`), legibilidade
     ou micro-otimizações.
4. **Estrutura de cada comentário inline:**
   - Título com ícone e severidade.
   - Explicação concisa e objetiva do problema e seu impacto real.
   - **Sugestão:** Bloco de código demonstrando a correção recomendada ou orientação objetiva.
   - Assinatura no rodapé.
5. **Assinatura obrigatória:**
   - Tanto o corpo geral do review quanto **cada um dos comentários inline** devem terminar com a
     assinatura do assistente executor (ex.: `_— Revisado por Antigravity_` quando executado via
     Antigravity, ou `_— Revisado por Claude_` quando executado via Claude):
     ```markdown
     _— Revisado por <NomeDoAssistente>_
     ```
6. **Idioma:**
   - Todo o texto de comunicação, resumo e comentários deve ser em **português do Brasil (pt-BR)**,
     mantendo termos técnicos universais e nomes de classes/funções em inglês, conforme `AGENTS.md`.

## Fluxo de Trabalho (Passo a Passo)

### 1. Inspecionar o Pull Request e Obter o Diff

Colete os metadados do PR e o diff completo:

```bash
gh pr view <n> --json title,body,headRefName,baseRefName,commits,files
gh pr diff <n>
```

Identifique o commit SHA mais recente da branch do PR (`commit_id`), que será utilizado na API de review.

### 2. Análise Técnica e Validação de Hipóteses

Analise as mudanças considerando:
- **Corretude e Regras de Negócio:** Atende aos requisitos da Issue e das specs OpenSpec?
- **Segurança e Privacidade:** Há vetores de injeção, CSRF, enumeração de usuários, oráculos em
  tokens ou exposição de dados sensíveis?
- **Robustez Operacional:** Tratamento de erros, transações de banco (`transaction.atomic`), idempotência.
- **Padrões do Repositório (`AGENTS.md`):** Código em inglês, textos de tela em pt-BR, Docker-first.

Se necessário, teste hipóteses e reproduza cenários no ambiente de desenvolvimento:
```bash
docker compose exec web pytest
docker compose exec web python manage.py shell -c "..."
```

> **Atenção com Git:** Se precisar alternar de branch para testes locais, **sempre retorne à branch
> original** e garanta que o working tree continue limpo antes de prosseguir.

### 3. Mapear Linhas e Construir Comentários Inline

Para cada apontamento:
1. Localize o arquivo (`path`) e a linha exata no diff (`line` no lado `RIGHT`).
2. Redija o comentário seguindo o padrão com ícone e assinatura.

Exemplo de comentário inline:
```markdown
**🔴 [Alta] Oráculo de enumeração de contas e estado de confirmação**

A checagem `if user.is_email_confirmed:` ocorre antes de validar o token (`check_token`). Isso permite que visitantes não autenticados sonde IDs de usuário com tokens arbitrários para identificar se existem e se estão confirmados.

**Sugestão:**
Validar o token criptográfico antes de checar o status de confirmação do usuário:
```python
if not email_confirmation_token.check_token(user, token):
    return self._render(request, "invalid")
```

_— Revisado por Antigravity_
```

### 4. Publicar o Review via GitHub API

Para evitar problemas de interpolação e escaping de aspas ou crases no shell bash, prepare o payload
em um arquivo temporário JSON usando um script Python e submeta via `gh api`.

Endpoint:
```bash
gh api --method POST /repos/{owner}/{repo}/pulls/<n>/reviews --input payload.json
```

Estrutura do payload:
```json
{
  "commit_id": "<HEAD_COMMIT_SHA>",
  "body": "## Code Review: PR #<n> - <Título>\n\n### Resumo do que foi implementado\n\n<Resumo objetivo dos pontos entregues e qualidades arquiteturais>\n\n---\n_— Revisado por Antigravity_",
  "event": "COMMENT",
  "comments": [
    {
      "path": "caminho/do/arquivo.py",
      "line": 77,
      "side": "RIGHT",
      "body": "**🔴 [Alta] Título...\n\nDescrição...\n\n**Sugestão:**\n...\n\n_— Revisado por Antigravity_"
    }
  ]
}
```

> **Nota:** Use `event: "COMMENT"` por padrão para registrar a revisão sem bloquear ou aprovar
> indevidamente, a menos que o usuário solicite explicitamente aprovação (`APPROVE`) ou bloqueio (`REQUEST_CHANGES`).

### 5. Verificar e Responder ao Usuário

1. Confirme que os comentários foram publicados:
   ```bash
   gh api /repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {id: .id, line: .line, path: .path, title: .body | split("\n")[0]}'
   ```
2. Responda ao usuário com:
   - Link direto para o PR e os comentários de revisão.
   - Resumo breve e conciso do resultado da revisão e principais pontos de atenção.
