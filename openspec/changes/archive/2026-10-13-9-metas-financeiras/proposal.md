# Proposal

## Why

O usuário registra lançamentos e vê o painel, mas não tem como definir um objetivo (ex.: poupar R$ 500) e
acompanhar o quanto já guardou. A Issue #9 (Item 6 — Tarefas e metas) pede metas financeiras com valor-alvo,
prazo opcional, progresso e barra visual. Como a tela de metas ainda não existe, o layout dela deve ser
escolhido antes de implementar: a change começa desenhando **duas opções de tela no FigCraft** para o
usuário decidir.

## What Changes

- **Design primeiro, com escolha.** Duas opções da lista de metas desenhadas em `design/goals.figcraft`
  (página "Opção A" e página "Opção B"), cada uma em desktop claro, desktop escuro e mobile claro, com os
  estados "com metas" e "vazio". O formulário em modal (padrão e com erros) é comum às duas e é desenhado
  uma vez. O usuário escolhe; a implementação só começa depois da escolha registrada no `design.md`. O
  arquivo versionado fica só com a opção escolhida, com frames na convenção `goals · <viewport> · <tema> ·
  <estado>`.
- **Nova app `goals`** com o model `Goal` (nome, valor-alvo, valor já guardado, prazo opcional, conclusão),
  migration, formulários, views e telas, no padrão das telas de lançamentos e categorias (lista, modal de
  criar/editar, confirmação de excluir).
- **Criar meta** com nome, valor-alvo positivo e prazo opcional que não pode estar no passado.
- **Registrar progresso**: informar o total já guardado; a barra mostra guardado ÷ alvo, limitada a 100 %.
- **Concluir e reabrir** uma meta; a lista separa **ativas** e **concluídas**.
- **Editar e excluir** a própria meta (o registro de progresso é uma edição; excluir segue o padrão do app).
- Item "Metas" na barra lateral e rota `/goals/`, protegida por login, com dados isolados por usuário.
- **Seletor de data (datepicker)** no campo `Prazo`, como o da página de formulários do TailAdmin: calendário
  em português, tema claro e escuro, e o campo continua funcionando sem JavaScript.
- Documentação: `README.md` (rotas, estrutura e modelo de dados) e, se o design tiver divergência da
  ferramenta, `AGENTS.md`.

Fora do escopo: ligar a meta aos lançamentos ou ao saldo (guardar em uma meta **não** cria lançamento nem
altera o saldo); histórico de aportes (só o total guardado); metas no painel ou no resumo de status (Item 4,
futuro); lembretes e notificações de prazo; metas recorrentes ou compartilhadas; o restante do Item 6 além de
metas ("tarefas" não consta nas sub-funcionalidades da Issue); o design das outras telas (Issue #55).

## Capabilities

### New Capabilities
- `goals`: metas financeiras do usuário — criação, progresso, conclusão, listagem separada, isolamento e
  proteção por login.

### Modified Capabilities
- `screen-design`: nova tela com mais de uma proposta de layout tem as opções desenhadas em páginas próprias
  do `.figcraft` para escolha, e só a opção escolhida permanece no arquivo versionado.

## Impact

- Código novo: app `goals/` (models, migration, forms, views, urls, testes), templates `templates/goals/`,
  entrada em `INSTALLED_APPS` e em `config/urls.py`, item na `templates/partials/sidebar.html`. Reaproveita
  `ModalMixin`, `StyledFormMixin`, `MoneyField` e `static/js/transaction-modal.js`. Única dependência
  nova: **flatpickr 4.6.13** (MIT, o seletor de datas do TailAdmin), servido localmente pelo build.
- Banco: uma tabela nova (`goals_goal`); nenhuma tabela existente muda.
- Arquivos novos fora do código: `design/goals.figcraft`.
- CSS: o Tailwind recompila só se aparecer classe nova (`docker compose run --rm css npm run build`).
- Depende de ferramenta fora do repositório para o design: FigCraft instalado, MCP registrado e a Outfit
  instalada (`design/fonts/`), como nas Issues #53 e #55.
- Cobertura: o piso `fail_under` do `pyproject.toml` não pode cair.
