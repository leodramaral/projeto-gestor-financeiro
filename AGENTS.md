# AGENTS.md

> Como trabalhar neste repositório: convenções, fronteiras e armadilhas. `CLAUDE.md` importa este
> arquivo. O `README.md` diz como rodar o projeto.

## Idioma

- **Código-fonte em inglês:** nome de módulo, classe, função, variável, docstring, comentário,
  mensagem de log e rota.
- **Texto de produto** (o que o usuário lê na tela) em português do Brasil.
- **Tudo o mais em pt-BR:** proposals, specs, design, tasks, commits, Issues e documentação em
  prosa. Requisitos usam **DEVE / NÃO DEVE**; cenários usam `#### Cenário:` com
  `- **QUANDO**` / `- **ENTÃO**` / `- **E**`.
- Única exceção, por ser estrutura de ferramenta: o marcador `### Requirement:` fica em inglês
  (o parser do OpenSpec o reconhece por regex fixa). Por isso a validação roda sem `--strict`.
- Nome de variável de ambiente não muda: é contrato operacional (`.env`, `docker-compose.yml`).

## Entry points

Tudo roda em Docker; o Python do sistema não é usado.

```bash
cp .env.example .env                                  # primeira vez
docker compose up --build                             # web + db em 127.0.0.1:8000 (migra ao subir)
docker compose exec web python manage.py <comando>    # qualquer comando do Django
docker compose exec web pytest                        # testes (settings de teste, banco próprio)
docker compose exec web pytest --cov --cov-report=term-missing   # com cobertura (como o CI; piso em `fail_under`)
uvx pre-commit run --all-files                        # lint (Ruff, inclui complexidade), formatação e higiene
docker compose run --rm css npm run build             # recompila o CSS (`watch` para acompanhar)
openspec validate --all                               # SEM --strict
```

`DJANGO_SETTINGS_MODULE` escolhe o ambiente: `config.settings.dev` (local), `.test` ou `.prod`.
`config.settings.base` é só o módulo comum, não um ambiente.

## Regras

- **Não versione segredos.** `.env` está no `.gitignore`; só `.env.example` é versionado, sem valores
  reais. `SECRET_KEY` e `DATABASE_URL` não têm valor padrão: a aplicação deve falhar sem elas.
- **Dependências com `uv`** (`pyproject.toml` + `uv.lock`); nunca `requirements.txt`.
- **O domínio ainda não foi modelado.** Não crie model, regra de negócio nem tela de domínio sem uma
  change que a autorize.
- **`static/dist/` e `node_modules/` não são versionados:** o CSS compilado nasce do serviço `css` do
  Compose. Node só existe dentro do contêiner.
- **Qualidade e CI.** Ruff (`E,F,I,UP,B,DJ,C90`, complexidade máxima 10, linha de 100) roda só via
  pre-commit (`.pre-commit-config.yaml`; instale com `uvx pre-commit install`). O CI
  (`.github/workflows/ci.yml`: `quality`, `tests`, `openspec`) repete tudo; **não mescle com o CI
  vermelho**. O piso de cobertura (`fail_under` no `pyproject.toml`) só sobe, nunca é rebaixado para
  fazer um PR passar.
- `environment` vence `env_file` no Compose: ao acrescentar variável, confira que nada a sobrescreve.
- **Worktrees ficam em `worktrees/<nome>`, dentro do repositório** (pasta já ignorada pelo
  `.gitignore` e pelo `.dockerignore`), nunca como pasta irmã fora dele. Use `scripts/worktree`
  (o `db` precisa estar de pé); o nome pode seguir o id da change (`3-registrar-lancamentos`):
  - `scripts/worktree new <nome> [branch]`: cria a worktree, copia o `.env` (lista `COPY_FILES` no
    topo do script), define `APP_DB_NAME=gestor_<nome>` nele e cria esse banco como cópia do
    principal. Sem `[branch]`, a branch tem o nome da worktree.
  - `scripts/worktree resync <nome>`: refaz o banco da worktree a partir do principal (a cópia não
    o acompanha depois de criada; apaga o que houver no banco da worktree).
  - `scripts/worktree remove <nome>`: remove a worktree e apaga o banco dela; recusa o principal.
  - O Compose fixa `name: projeto-gestor-financeiro`: todas as worktrees compartilham o contêiner
    `web`, a rede e o servidor Postgres, mas cada uma usa **o seu banco** (`APP_DB_NAME`); o do
    pytest vira `test_gestor_<nome>`, então rodadas em worktrees diferentes não colidem.
  - Para validar a worktree no navegador (porta 8000), rode `docker compose up -d` **nela**: recria o
    `web` apontando para ela, o `css` recompila `static/dist/` e o `migrate` roda no banco **da
    worktree**. Só uma worktree por vez na 8000. `--build` só se `pyproject.toml` ou `uv.lock`
    mudaram. Para voltar ao checkout principal, rode `docker compose up -d` nele.
  - Testes sem trocar o `web`: `docker compose run --rm --no-deps web pytest` (o `db` de pé).

## Fluxo de trabalho: Issues + OpenSpec

Spec-Driven Development. **Não implemente sem uma change.**

1. A Issue existe (`gh issue create`) e aponta para o trabalho.
2. `/opsx:explore` quando a intenção tem mais de uma leitura.
3. Branch com o id da change: `git checkout -b 2-login-por-email`.
4. `/opsx:propose`. O id da change é `<n>-<nome>`: o número da Issue seguido de um nome em
   kebab-case (`2-login-por-email`). Ao arquivar, a pasta ganha a data na frente
   (`2026-10-01-2-login-por-email`). Exceção histórica: `1-boilerplate` e `1-frontend-testes`
   repetem o `1`, porque ambas atendem à Issue #1.
5. `/opsx:apply`. Marque cada task só depois de **concluída e verificada**.
6. O que surgir no caminho: dentro do escopo vira task **antes** de ser feito; fora do escopo vira
   Issue nova, e o trabalho corrente não desvia.
7. Verificar (`openspec validate --all` e a verificação manual descrita nas tasks).
8. `openspec archive <id> --yes` ainda na branch, antes do PR.
9. PR com `Closes #<n>`.

## Commits

Conventional Commits, em português, com o **número da Issue** da change como escopo:
`feat(#2): login por e-mail`, `chore(#1): base Django + PostgreSQL em Docker`.
Trabalho fora de change usa a área como escopo: `docs: ...`, `chore(docker): ...`.
O título do PR segue o mesmo padrão.
