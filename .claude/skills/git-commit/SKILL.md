---
name: git-commit
description: 'Executa git commit com análise de mensagem de commit convencional, staging inteligente e geração de mensagem. Use quando o usuário pedir para fazer commit de alterações, criar um commit git ou mencionar "/commit". Suporta: (1) Escopo derivado do nome da change OpenSpec, (2) Geração de mensagens de commit convencionais em português a partir do diff, (3) Confirmação interativa com o usuário antes de efetuar o commit.'
license: MIT
---

# Git Commit com Commits Convencionais

## Visão Geral

Crie commits do git padronizados e semânticos usando a especificação de Commits Convencionais
(Conventional Commits), **em português**, no padrão documentado no `AGENTS.md` deste repositório.

## Formato do Commit Convencional

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé(s) opcional(is)]
```

## Tipos de Commit

| Tipo       | Propósito                      |
| ---------- | ------------------------------ |
| `feat`     | Nova funcionalidade            |
| `fix`      | Correção de bug                |
| `docs`     | Apenas documentação            |
| `style`    | Formatação/estilo (sem lógica) |
| `refactor` | Refatoração de código          |
| `perf`     | Melhoria de desempenho         |
| `test`     | Adicionar/atualizar testes     |
| `build`    | Sistema de build/dependências  |
| `ci`       | Alterações de CI/configuração  |
| `chore`    | Manutenção/diversos            |
| `revert`   | Reverter um commit anterior    |

## Escopo: o nome da change, não a camada

Neste repositório o escopo é o **nome da change OpenSpec** — é o que mantém a simetria
"uma change, um branch, uma linha no log" (ver "Fluxo de trabalho" no `AGENTS.md`). Não há Issues
numeradas, então não se usa número:

```
branch        login-por-email
pasta         openspec/changes/login-por-email/
commit        feat(login-por-email): ...
```

Como derivar, nesta ordem:

1. **Nome do branch** — `git rev-parse --abbrev-ref HEAD`; o próprio nome é o escopo
   (`login-por-email`).
2. **Change ativa** — se o branch não disser (ex.: `main`), veja `openspec/changes/` e os arquivos
   tocados pelo diff; se o diff mexe em `openspec/changes/<nome>/`, o escopo é `<nome>`.
3. **Fora de change** — trabalho que não pertence a nenhuma usa a **área** como escopo, ou nenhum:
   `docs: reorganiza a documentação`, `chore(docker): ajusta o compose`.

⚠️ Como o escopo não nomeia mais a camada, **diga a área no assunto** quando ela não for óbvia.
`git log --oneline | grep '(login-por-email)'` devolve a change inteira — é o que se ganha em troca.

## Fluxo de Trabalho

### 1. Analisar o Diff
```bash
# Se os arquivos estiverem em stage, use o diff em stage
git diff --staged

# Se nada estiver em stage, use o diff da árvore de trabalho
git diff

# Verifique também o status
git status --porcelain
```

### 2. Adicionar Arquivos ao Stage (se necessário)
Se nada estiver em stage ou se quiser agrupar alterações de forma lógica:
```bash
# Adicionar arquivos específicos
git add caminho/do/arquivo1 caminho/do/arquivo2
```
**Nunca faça commit de segredos** — `.env` está no `.gitignore` por isso; só `.env.example`, sem
valores reais, é versionado.

### 3. Gerar Mensagem de Commit Técnico
Analise o diff para determinar:
- **Tipo**: Que tipo de alteração é essa?
- **Escopo**: o nome da change, pela regra acima.
- **Descrição**: Resumo técnico em uma linha do que mudou, **em português** (tempo presente, modo
  imperativo, <72 caracteres). Foque estritamente no aspecto técnico (o que mudou, onde e como), sem
  necessidade de justificar valor de negócio.

### 4. Apresentar para Aprovação do Usuário (Obrigatório)
**IMPORTANTE:** Antes de executar qualquer comando de commit, você deve exibir a mensagem de commit gerada claramente para o usuário no chat e perguntar se ele a aprova.
- Se o usuário **aprovar**, prossiga para a execução do commit.
- Se o usuário **rejeitar ou pedir alterações**, ajuste a mensagem conforme solicitado pelo usuário antes de tentar cometer.

### 5. Executar o Commit (Apenas após Aprovação)
```bash
git commit -m "<tipo>[escopo]: <descrição>"
```

## Diretrizes e Boas Práticas
- Um commit por alteração lógica.
- Descrição em português, no imperativo (ex: "adiciona" em vez de "adicionado").
- Mantenha a descrição curta e concisa (menos de 72 caracteres).
- O **título do PR segue o mesmo padrão** — com squash merge ele vira a mensagem na `main`.
- Nunca pule ganchos de validação (`--no-verify`) a menos que solicitado.
