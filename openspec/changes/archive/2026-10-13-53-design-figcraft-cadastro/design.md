# Design

## Context

- O front é Django com templates e Tailwind v4 (`frontend/style.css`, compilado pelo serviço `css`). As
  telas de visitante usam `base_auth_split.html` (formulário de um lado, `auth_aside.html` do outro) e o
  controle de tema de `theme_toggle.html`. O `AGENTS.md` proíbe tela de domínio sem change, mas o cadastro
  já existe: esta change só o **documenta**.
- O build do frontend é `npm run build` no serviço `css`: `tailwindcss` gera `static/dist/css/style.css`
  e `scripts/copy-alpine.mjs` copia Alpine e Chart.js de `node_modules` para `static/dist/js/`.
  `static/dist/` não é versionado. O Django serve `static/` por `STATICFILES_DIRS`; não há servidor de
  estáticos para produção configurado.
- A fonte declarada é `--font-outfit: Outfit, ui-sans-serif, system-ui, sans-serif`, aplicada ao `body`.
  O CSS removeu o Google Fonts de propósito (`para o build não depender de rede`) e **não pôs nada no
  lugar**: sem `@font-face` nem arquivo de fonte no projeto, a Outfit só aparece em quem a tem instalada.
- O FigCraft 0.5.1 (alpha, MIT/Apache-2.0) tem app desktop, `figcraft-cli` e servidor MCP. O `.figcraft`
  é um **zip** com `document.json`; o git o trata como binário, então o diff de PR não o mostra. Ele
  desenha com fontes **instaladas no sistema** (`.ttf`/`.otf`), não com `.woff2`.
- O pacote npm `@fontsource-variable/outfit` 5.3.0 (OFL-1.1) traz a fonte variável em `woff2`
  (`files/outfit-latin-wght-normal.woff2`, 32 KB; `latin-ext`, 15 KB) e a licença.
- O pre-commit exclui `openspec/`, `static/dist/` e outros do lint; o hook `check-added-large-files` usa o
  limite padrão de 500 KB. O `.dockerignore` não ignora `design/`.
- Já existe um protótipo do cadastro feito fora do repositório: 5 frames, validados contra os templates,
  os tokens do CSS e `accounts/forms.py`. Ele passa para `design/` na implementação.

## Goals / Non-Goals

**Goals:**
- Um lugar versionado e revisável para o design, com o `.figcraft` como fonte.
- Um histórico enxuto: só a fonte do design é versionada; imagens derivadas se regeram quando preciso.
- Que qualquer pessoa instale e atualize o FigCraft sem decisões ad hoc.
- Que design e app usem a mesma fonte, e que o app a entregue a todo visitante.

**Non-Goals:**
- Gerar o design a partir do código, ou o código a partir do design.
- Cobrir mais telas, protótipo com transições ou o modo `--attach`.
- Configurar o servidor de estáticos de produção, ou mudar template, view ou model.

## Decisions

- **`.figcraft` é a fonte; PNG é derivado e não é versionado.** Um arquivo por tela ou fluxo em
  `design/`; os PNGs exportados vão para `design/png/`, que o `.gitignore` ignora. Um PNG não tem diff:
  cada ajuste de design criaria um binário de ~200 KB novo no histórico (os 4 frames de desktop pesam
  ~210 KB cada), para uma informação que o `.figcraft` já contém. Alternativas descartadas: versionar um
  PNG por frame (histórico cresce a cada change), versionar só 1 ou 2 de referência por tela (quebra a
  regra uniforme e ainda cresce), Git LFS (configuração extra no time e no CI sem necessidade) e versionar
  só PNG ou só SVG (perdem camadas, valores e a estrutura de auto layout). O custo aceito: o GitHub não
  mostra a tela no PR; quem quiser ver abre o `.figcraft` no app ou exporta.
- **Exportação sob demanda, com `figcraft-cli export <arquivo> -o design/png/ --format png`**, que escreve um
  arquivo por frame de topo. Se os nomes gerados não seguirem a convenção, os arquivos são renomeados
  logo após a exportação, no mesmo passo. Nada disso entra no git.
- **Convenção de nomes no próprio arquivo:** `<tela> · <viewport> · <tema> · <estado>` no frame,
  `kebab-case` ASCII no PNG. O nome do frame é a chave que liga o design ao PNG e à spec.
- **O app serve a Outfit pelo pacote `@fontsource-variable/outfit`, copiada no build.** O
  `copy-alpine.mjs` já copia ativos de `node_modules` para `static/dist/`; a fonte segue o mesmo caminho,
  para `static/dist/fonts/outfit-latin-wght-normal.woff2`, e o `@font-face` em `frontend/style.css` a
  aponta com `url("../fonts/…")`, relativo ao CSS em `static/dist/css/`. Declara-se o eixo de peso
  inteiro (`font-weight: 100 900`) e `font-display: swap`. Só o subset `latin` é copiado: cobre `ç`, `ã`,
  `é` e demais acentos do português, e `latin-ext` custaria 15 KB sem uso. Alternativas descartadas:
  Google Fonts em runtime (depende de rede, o motivo da remoção original e envia o IP do visitante a
  terceiros), arquivo `.woff2` baixado à mão e versionado (não acompanha atualizações nem traz a licença
  junto) e `@fontsource` estático por peso (mais arquivos para o mesmo resultado). Como `static/dist/`
  não é versionado, a fonte nasce do `npm ci && npm run build`, como o CSS.
- **O design usa a mesma Outfit, mas em `.ttf`.** O FigCraft só desenha com fontes instaladas no
  sistema, então o `.woff2` do app não serve a ele. `design/fonts/Outfit[wght].ttf` e a `OFL.txt` ficam
  versionados (110 KB), e a convenção manda instalá-los antes de editar ou exportar o design. A OFL
  permite redistribuir desde que a licença acompanhe o arquivo. `design/` fica fora do Docker pelo
  `.dockerignore`, então a fonte do design não vai para a imagem. A `OFL.txt` é versionada **idêntica à
  do upstream** (tem espaços no fim de linha): `design/fonts/` entra no `exclude` do pre-commit, porque o
  hook `trailing-whitespace` a reescreveria, e não se altera o texto de uma licença por formatação.
- **Script `scripts/figcraft-upgrade`, versionado**, no mesmo estilo de `scripts/worktree`: baixa a
  release do GitHub com o `gh`, confere o `SHA256SUMS`, instala em
  `~/.local/share/figcraft/<versão>/` e aponta `current` para ela. O caminho do MCP nunca muda e o
  upgrade não toca no registro. Alternativas: `cargo install` (exige Rust e compila; a documentação
  oficial só descreve `cargo build` a partir do clone) e instalação manual (cada upgrade repete tudo).
- **O MCP é registrado por usuário (`claude mcp add --scope local`), não em `.mcp.json`.** O caminho do
  binário é da máquina de cada pessoa, e um `.mcp.json` versionado quebraria para quem o clonasse. O
  registro **não** usa `--no-system-fonts`, para o MCP e a CLI enxergarem a Outfit instalada.
- **O gerador de script que produziu a primeira versão não é versionado.** O design foi refinado depois
  pelo MCP (grade, botão de tema, estados), então o script já não o reproduz; manter os dois levaria a
  divergência. A fonte é o `.figcraft`, editado no app ou pelo MCP.
- **Divergências conhecidas ficam registradas** na convenção do `AGENTS.md` e não são corrigidas aqui:
  só o mobile claro existe; sem estados de foco (o app dá `autofocus` ao campo Nome, então a captura do
  app mostra o anel de foco e o design não) nem `shadow-theme-xs` nos campos; sem a caixa de erro geral
  (`form_errors`). A fonte deixa de ser divergência: design e app usam a Outfit, com as alturas de linha
  da escala do Tailwind e o `tracking-tight` do nome da marca. O `-mt-2` da lista de requisitos e do aviso
  de confirmação também deixa de ser divergência: o auto layout não tem margem negativa, mas o campo e o
  item logo abaixo ficam num grupo com 8 px de espaçamento (`Senha + requisitos`, `Confirmação + aviso`),
  e o formulário fecha com os mesmos 432 px do app. **Medição** (desktop 1440×900, design contra a captura
  do app com a Outfit servida): 0,73% dos pixels diferem no claro e 0,63% no escuro (limite de 40/255 por
  canal), todos de anti-aliasing do texto, do anel de foco e da borda do ícone; nenhum de posição.

## Risks / Trade-offs

- [A Outfit é mais estreita que a fonte do sistema e muda a tipografia do app inteiro] → as telas de
  visitante e do painel são conferidas nos temas claro e escuro, antes e depois, e o que quebrar é
  corrigido nesta change. **Resultado da conferência** (10 telas × 2 temas, 1440×900, "antes" medido com o
  `.woff2` bloqueado e a Outfit fora do sistema): nenhuma tela ganhou estouro de largura nem mudou de
  estrutura; só três textos das telas de visitante passaram de duas linhas para uma (a frase do painel de
  marca, o subtítulo do cadastro e o parágrafo de recuperar senha). As telas autenticadas não mudaram de
  quebra de linha. Nada precisou de correção de CSS ou de template.
- [Como a Outfit já pode estar instalada na máquina de quem testa, ver a tela não prova que o app a
  serve] → a verificação confere a rede (o `.woff2` responde 200) e `document.fonts` (a fonte está
  `loaded`), e não só a aparência.
- [`font-display: swap` mostra a fonte do sistema por instantes antes da troca] → aceito: o texto nunca
  fica invisível, e o arquivo de 32 KB é servido do mesmo host.
- [FigCraft é alpha e pode quebrar um `.figcraft` entre versões] → o script mantém versões lado a lado
  (rollback por `ln -sfn`) e o `document.json` dentro do zip continua legível mesmo que o app deixe de abri-lo.
- [`.figcraft` binário: o PR não mostra o que mudou no design] → aceito: o PR mostra só que o arquivo mudou. Quem revisa abre o
  `.figcraft` ou exporta os PNGs; o SVG é opcional se o diff textual importar.
- [Renderização diverge entre máquinas se faltar a fonte instalada] → a fonte está em `design/fonts/` e a
  convenção exige instalá-la; `--no-system-fonts` é para CI, não para o design.
- [O design e o código divergem com o tempo] → a spec exige fidelidade; quem muda a tela atualiza o
  design na mesma change, como já se faz com as specs.
- [`design/` pesa no histórico] → só o `.figcraft` (dezenas de KB, binário) e a fonte de 110 KB entram no git, sem PNGs; medir de novo se a pasta passar de 5 MB.

## Migration Plan

1. Declarar e servir a Outfit no app (dependência, cópia no build e `@font-face`) e conferir as telas.
2. Copiar o protótipo para `design/`, com a fonte em `design/fonts/`, renomeando os frames pela
   convenção.
3. Adicionar `design/` ao `.dockerignore` e `design/*.figcraft binary` ao `.gitattributes`.
4. Copiar `scripts/figcraft-upgrade` e documentar tudo no `AGENTS.md`.

Rollback: reverter o commit. Sem a dependência e o `@font-face`, o app volta a cair na fonte do sistema
sem erro, e nada mais fora de `design/`, `scripts/`, `.dockerignore`, `.gitattributes`, `AGENTS.md`,
`package.json` e `frontend/style.css` é tocado.
