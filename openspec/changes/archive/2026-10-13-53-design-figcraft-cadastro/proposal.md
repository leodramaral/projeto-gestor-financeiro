# Proposal

## Why

O projeto não tem um lugar para o design das telas: o que existe está só nos templates, no Tailwind e
nas specs. Não há registro visual das telas nem dos estados (vazio, erro, sucesso), e prototipar uma tela
antes de implementá-la exige escrever código ou usar uma ferramenta fora do repositório. Origem: Issue #53.

Ao documentar a primeira tela, apareceu um defeito do próprio app: o CSS declara a Outfit como fonte de
marca (`--font-outfit`), mas **não a serve** (sem `@font-face` e sem arquivo de fonte no projeto), então o
navegador só a usa em quem a tem instalada e, para quase todo mundo, cai na fonte do sistema. Design e app
nunca bateriam em tipografia sem corrigir isso, e o projeto decidiu corrigi-lo nesta mesma change.

## What Changes

- Nova pasta **`design/`**, versionada: o **`.figcraft` é o artefato de design** (fonte editável). Os
  PNGs exportados dos frames **não são versionados** (`design/png/` no `.gitignore`): cada ajuste criaria
  um binário novo e inalterável no histórico, e qualquer pessoa os regera do `.figcraft`.
- Primeira tela documentada: **cadastro** (`/accounts/signup/`), em desktop claro, desktop escuro e mobile
  claro, mais os estados **com erros** e **com senha válida**, fiéis ao código: tokens de
  `frontend/style.css`, textos e rótulos reais do formulário (`accounts/forms.py`), logo e grade do painel
  de marca.
- **Servir a Outfit a partir do projeto:** nova dependência `@fontsource-variable/outfit` (OFL-1.1); o
  build do frontend copia `outfit-latin-wght-normal.woff2` (32 KB, cobre os acentos do português) de
  `node_modules` para `static/dist/fonts/`, e `frontend/style.css` declara `@font-face` com
  `font-display: swap`. O comentário do CSS que diz que a fonte foi removida é corrigido. Quem visita o
  app passa a ver a Outfit sem tê-la instalada, e as telas são revistas com a tipografia nova.
- Fonte do design: **Outfit**, a mesma do app. Como o FigCraft só desenha com fontes instaladas no
  sistema (`.ttf`), o `Outfit[wght].ttf` e a `OFL.txt` ficam versionados em **`design/fonts/`**, para quem
  clonar o repositório instalar e editar o design.
- Convenção no `AGENTS.md`: onde ficam os arquivos, nome do arquivo por tela, nome dos frames
  (`<tela> · <viewport> · <tema> · <estado>`), como exportar os PNGs (não versionados) e como instalar a fonte do design.
- Instalação e atualização do FigCraft CLI e do servidor MCP, sem versionar binário: o script
  `scripts/figcraft-upgrade` baixa a release do GitHub, confere o checksum e mantém um caminho estável
  (`~/.local/share/figcraft/current/bin/figcraft-cli`), documentado no `AGENTS.md`.
- `.dockerignore` passa a ignorar `design/` e `.gitattributes` marca `design/*.figcraft` como binário.

Fora do escopo: as demais telas (uma change por tela ou por fluxo); servir os arquivos estáticos em
produção (o projeto ainda não configura um servidor de estáticos, e esta change só garante que a fonte
chega a `static/dist/` como o CSS e o Alpine); teste de protótipo com conexões e transições; o modo
`--attach` com o app aberto; versionar o binário do FigCraft.

## Capabilities

### New Capabilities
- `screen-design`: onde o design das telas mora no repositório, o que é versionado, como os frames são
  nomeados e exportados, e a exigência de que o design bata com o código.

### Modified Capabilities
- `visual-identity`: novo requisito de que o app serve a fonte de marca (Outfit) a partir do próprio
  projeto, sem depender de rede nem de a fonte estar instalada no computador de quem acessa.

## Impact

- Arquivos novos: `design/signup.figcraft`, `design/fonts/` e
  `scripts/figcraft-upgrade`.
- Alterados: `AGENTS.md` (convenção e instalação), `.dockerignore`, `.gitattributes` (novo),
  `.pre-commit-config.yaml` (`design/fonts/` entra no `exclude`, para os hooks de espaço em branco não
  alterarem a licença da fonte),
  `package.json` e `package-lock.json` (dependência da fonte), `scripts/copy-alpine.mjs` (cópia do
  `.woff2`) e `frontend/style.css` (`@font-face` e comentário).
- Aparência: toda tela do app muda de tipografia, da fonte do sistema para a Outfit, que é mais estreita;
  quebras de linha e larguras podem mudar e são conferidas nas telas existentes.
- Nenhum model, view ou template muda. O pre-commit já cobre a pasta, e `check-added-large-files`
  (limite padrão de 500 KB) vale para o `.figcraft` e para a fonte.
- Dependência de ferramenta, fora do repositório: FigCraft 0.5.1 (MIT/Apache-2.0, alpha). A dependência
  npm da fonte entra no `npm ci` do serviço `css`; o `static/dist/` continua não versionado.
