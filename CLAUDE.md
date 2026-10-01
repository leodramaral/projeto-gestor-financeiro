# CLAUDE.md

Este arquivo orienta o Claude Code neste repositório. As instruções do projeto — comandos,
arquitetura, convenções — vivem em `AGENTS.md`, a **fonte única** compartilhada com outras
ferramentas de agente. Ao aprender algo novo sobre o projeto, atualize **`AGENTS.md`**, não este
arquivo.

@AGENTS.md

## Específico do Claude Code

Comandos do OpenSpec instalados por `openspec init --tools claude` em `.claude/`:

| Comando | Uso |
|---|---|
| `/opsx:propose` | Cria uma change nova com todos os artefatos |
| `/opsx:apply` | Implementa as tasks pendentes do `tasks.md` |
| `/opsx:update` | Ajusta artefatos de uma change em andamento |
| `/opsx:sync` | Sincroniza specs |
| `/opsx:archive` | Arquiva a change e mescla os deltas em `openspec/specs/` |
| `/opsx:explore` | Investiga antes de propor |

Se os comandos não aparecerem, rode `openspec update` e reinicie o Claude Code.

### Skills do repositório

Em `.claude/skills/`, espelhadas em `.agents/skills/` (as duas cópias são versionadas e precisam
ficar idênticas — ao editar uma, copie para a outra):

| Skill | Uso |
|---|---|
| `git-commit` | staging + mensagem em Conventional Commits a partir do diff, com confirmação antes de commitar. O escopo é o **número da Issue** (`chore(#1): ...`). |
| `fechar-change` | leva uma change implementada até o PR: verificação, a pergunta "já está pronta para arquivar?", commit via `git-commit`, push e abertura do PR — sem perguntar se deve abrir. |

As demais skills em `.claude/skills/` (`openspec-*`) são geradas por `openspec init`/`openspec update`
e não são editadas à mão.
