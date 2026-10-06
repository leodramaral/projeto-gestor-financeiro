# Design

## Context

- O repositório é **público**. A `main` tem um ruleset ativo: PR obrigatório com 1 aprovação, sem
  deleção, sem force push, histórico linear e os checks de status `quality`, `tests` e `openspec`
  obrigatórios. O CodeQL **não** faz parte dos checks exigidos. (Esse ruleset foi ajustado pelo
  dono do repositório durante esta change; antes ele não exigia checks. A API de proteção clássica
  devolve 404 mesmo assim, porque o ruleset aparece só em `repos/<repo>/rulesets`.)
- `dependabot_security_updates` está desabilitado; `secret_scanning` e a proteção de push estão
  habilitados.
- Fontes de dependência: `pyproject.toml` + `uv.lock` (Python), `package.json` + `package-lock.json`
  (Tailwind e Alpine, na raiz), `docker/Dockerfile` (`python:3.12-slim` e `ghcr.io/astral-sh/uv:latest`),
  imagens no `docker-compose.yml` (`node:22-alpine`, `postgres:16-alpine`, `axllent/mailpit`) e as
  Actions do `.github/workflows/ci.yml`.
- O CI não usa segredos (o `.env` é gerado na execução), então roda em PRs do Dependabot, que não
  recebem segredos do repositório.
- O Ruff roda só via pre-commit (`E,F,I,UP,B,DJ,C90`). Medindo `--select S`: 729 achados, sendo 722
  `S101` (assert), 4 `S105`, 1 `S107` e 1 `S314` em testes, e 1 `S308` em produção
  (`category_tags.py:28`, `mark_safe` de `category_icon`).
- Commits seguem Conventional Commits; fora de change, o escopo é a área (`chore(deps)`).

## Goals / Non-Goals

**Goals:**
- Ser avisado de dependência vulnerável e receber PR de correção.
- Receber PR semanal de atualização sem enxurrada de PRs.
- Pegar no commit os padrões inseguros simples (`mark_safe`, senha fixa, hash fraco).
- Ter o CodeQL publicando achados em Security e no PR, com permissão mínima.

**Non-Goals:**
- Tornar o CodeQL ou o Dependabot checks obrigatórios (exigiria incluí-los nos checks obrigatórios do ruleset da `main`).
- Analisar JavaScript (só há scripts de build do Tailwind/Alpine) ou ampliar o conjunto de consultas.

## Decisions

- **Dependabot por `dependabot.yml` + alertas pelas configurações do repositório.** O arquivo
  controla as *atualizações de versão*; os *alertas* e as *atualizações de segurança* são ajuste do
  repositório, feito uma vez por Settings → Advanced Security (ou API) e conferido por
  `gh api repos/<repo> -q .security_and_analysis`. Alternativa descartada: depender só do arquivo,
  que não liga os alertas.
- **Cinco ecossistemas:** `uv` (raiz), `npm` (raiz), `docker` (`/docker`), `docker-compose` (raiz) e
  `github-actions` (`/`). Alternativa: só Python e npm, deixando imagens e Actions envelhecerem,
  que é onde costuma morar a versão esquecida.
- **Semanal, segunda-feira, fuso `America/Sao_Paulo`**, com `open-pull-requests-limit` baixo e
  `groups` de `minor`/`patch` por ecossistema. Major continua em PR próprio, para ser revisado.
- **Prefixo `chore(deps)`** em `commit-message`, e label `dependencies`, para o título do PR já
  seguir o padrão do projeto (com squash merge ele vira a linha da `main`).
- **Restrição do Django mantida.** O Dependabot respeita `django>=5.2,<5.3`: só propõe patches da
  5.2. Subir para 5.3 é decisão humana e uma change própria.
- **CodeQL em workflow próprio (`codeql.yml`), não dentro do `ci.yml`.** Assim a permissão
  `security-events: write` fica isolada no job dele e o `ci.yml` segue com `contents: read`.
  Gatilhos: `pull_request` e `push` na `main`, mais `schedule` semanal. Linguagem `python`, sem
  etapa de build. Alternativa descartada: "default setup" pela interface, que não deixa o
  comportamento versionado nem revisável em PR.
- **Versão das Actions:** usar a major vigente de `github/codeql-action` no momento de implementar
  (confirmar no repositório da action); o próprio Dependabot passa a mantê-la atualizada.
- **CodeQL não bloqueante por ora.** O ruleset exige só os três jobs do CI; o CodeQL fica visível
  mas sem travar o merge, até se conhecer o ruído real. Exigi-lo depois é acrescentar a regra de
  *code scanning* ao ruleset, que pode bloquear só por severidade.
- **Falso positivo:** descartar o alerta em Code scanning com motivo e comentário. Só se o ruído
  se repetir, criar `.github/codeql/codeql-config.yml` com `paths-ignore` para testes.
- **Regras `S` no `select`, com `per-file-ignores` para `**/tests/**`** (`S101`, `S105`, `S106`,
  `S107`, `S314`), em vez de `noqa` em cada teste (728 linhas) ou de ignorar `S` no projeto todo.
- **`S308` com `# noqa: S308` e o motivo**, não `# nosec`, porque o Ruff lê `noqa`. O uso é seguro:
  só chaves de `ICON_BY_KEY` chegam ao arquivo SVG, e o resto retorna antes.
- **Regras `S` e CodeQL se complementam:** `S` casa padrões numa linha, no commit; o CodeQL rastreia o
  dado da entrada ao destino, no CI.
- **Arquivar a change 33 aqui.** A task 3.3 daquela change dependia do PR #35; o arquivamento vem
  nesta branch por decisão do projeto, em commit próprio, antes do arquivamento desta change.

## Risks / Trade-offs

- [Enxurrada de PRs na primeira semana] → limite de PRs abertos e agrupamento de minor/patch.
- [PR do Dependabot quebra o CI] → é o objetivo do gate; revisar antes de mesclar.
- [Falso positivo do CodeQL em código de teste] → descartar com justificativa; `paths-ignore` só
  se virar rotina.
- [Regra `S` nova em versão futura do Ruff gera achado] → a versão do hook é fixa; subir de versão
  passa por PR do Dependabot, que roda o gate.
- [Falso positivo futuro em produção] → `noqa` com justificativa, revisado no PR.
- [`dependabot.yml` inválido não falha o CI] → conferir a aba Insights → Dependency graph →
  Dependabot após o merge, que mostra o erro de configuração.
- [O CodeQL não é check obrigatório] → o risco de mesclar com achado aberto depende do revisor; a
  aprovação obrigatória do PR é a barreira humana, e os três jobs do CI já travam o merge.
- [`dependabot_security_updates` exige admin do repositório] → a task correspondente pede
  confirmação antes de alterar a configuração.

## Open Questions

- Exigir o CodeQL (por severidade) no ruleset da `main`, depois de algumas semanas de uso: fica para
  uma decisão à parte.
