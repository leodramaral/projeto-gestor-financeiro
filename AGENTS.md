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
- `environment` vence `env_file` no Compose: ao acrescentar variável, confira que nada a sobrescreve.

## Fluxo de trabalho: Issues + OpenSpec

Spec-Driven Development. **Não implemente sem uma change.**

1. A Issue existe (`gh issue create`) e aponta para o trabalho.
2. `/opsx:explore` quando a intenção tem mais de uma leitura.
3. Branch com o nome da change: `git checkout -b boilerplate`.
4. `/opsx:propose`. O id da change é um nome em kebab-case (`login-por-email`); sem número, porque
   o projeto não usa Issues numeradas.
5. `/opsx:apply`. Marque cada task só depois de **concluída e verificada**.
6. O que surgir no caminho: dentro do escopo vira task **antes** de ser feito; fora do escopo vira
   Issue nova, e o trabalho corrente não desvia.
7. Verificar (`openspec validate --all` e a verificação manual descrita nas tasks).
8. `openspec archive <id> --yes` ainda na branch, antes do PR.
9. PR com `Closes #<n>`.

## Commits

Conventional Commits, em português, com o **nome da change** como escopo:
`chore(boilerplate): base Django + PostgreSQL em Docker`, `feat(login-por-email): ...`.
Trabalho fora de change usa a área como escopo: `docs: ...`, `chore(docker): ...`.
O título do PR segue o mesmo padrão.
