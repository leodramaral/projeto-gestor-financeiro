# Tasks

## 1. Outfit servida pelo app

- [x] 1.1 Antes de mexer no CSS, capturar com o Playwright a linha de base das telas existentes, nos temas claro e escuro: entrar, criar conta, recuperar senha e, autenticado com um usuário de teste do banco de dev, painel, lançamentos, categorias e perfil; verificar que existem as capturas (guardadas fora do repositório) e que as telas autenticadas abriram sem redirecionar ao login
- [x] 1.2 Adicionar `@fontsource-variable/outfit` (5.3.0, OFL-1.1) às dependências com `docker compose run --rm css npm install --save-exact @fontsource-variable/outfit@5.3.0`; verificar `package.json` e `package-lock.json` alterados e que `docker compose run --rm css npm ci` conclui sem erro
- [x] 1.3 Em `scripts/copy-alpine.mjs`, copiar `node_modules/@fontsource-variable/outfit/files/outfit-latin-wght-normal.woff2` para `static/dist/fonts/` (criando a pasta) e ajustar o comentário do script; verificar com `docker compose run --rm css npm run build` e `ls -l static/dist/fonts` mostrando o arquivo
- [x] 1.4 Declarar o `@font-face` de `Outfit` em `frontend/style.css` (`src: url("../fonts/outfit-latin-wght-normal.woff2") format("woff2")`, `font-weight: 100 900`, `font-display: swap`) e trocar o comentário que diz que a fonte foi removida; verificar que o build conclui e que `static/dist/css/style.css` contém `@font-face` e `outfit-latin-wght-normal`
- [x] 1.5 Provar que o app serve a fonte: com o app no ar, abrir `/accounts/signup/` no Playwright e conferir que a requisição do `.woff2` responde 200 em `/static/dist/fonts/…`, que `document.fonts` lista a `Outfit` como `loaded` e que a fonte aplicada ao `body` é a Outfit; como a fonte pode estar instalada na máquina, o que vale é a requisição e o `loaded`, não a aparência
- [x] 1.6 Repetir a captura da 1.1 com a fonte nova e comparar tela a tela, nos dois temas, procurando texto cortado, quebra de linha nova, desalinhamento e gráfico ou tabela que mudou de largura; corrigir o que quebrar com a menor mudança de CSS ou de template e registrar no `design.md` o que mudou; verificar que nenhuma tela ficou pior e que cada correção tem captura de antes e depois
- [x] 1.7 Rodar `docker compose exec web pytest` e `uvx pre-commit run --all-files`; verificar que ambos passam

## 2. Fonte Outfit no design

- [x] 2.1 Versionar `Outfit[wght].ttf` e a `OFL.txt` em `design/fonts/` e instalar a partir dessa pasta no WSL (`~/.local/share/fonts`) e no Windows; verificar com `fc-list | grep -i outfit` no WSL e vendo "Outfit" na lista de fontes de um texto no app do FigCraft
- [x] 2.2 Recriar o registro do MCP sem `--no-system-fonts` (`claude mcp remove figcraft` e `claude mcp add figcraft --scope local -- ~/.local/share/figcraft/current/bin/figcraft-cli mcp`) e reiniciar a sessão; verificar com `claude mcp list` conectado e criando um texto com `fontFamily: "Outfit"` cujo `screenshot` mostre a Outfit, não um substituto
- [x] 2.3 Trocar `Poppins` por `Outfit` em todas as camadas de texto do protótipo do cadastro; verificar que `inspect_document` não lista `Poppins` em nenhuma camada e conferindo no `screenshot` que o texto não transborda nem muda a altura dos frames

## 3. Pasta `design/` e artefato do cadastro

- [x] 3.1 Renomear os 5 frames pela convenção `<tela> · <viewport> · <tema> · <estado>` (`signup · desktop · claro · padrão`, `... · escuro · padrão`, `signup · mobile · claro · padrão`, `... · com erros`, `... · senha válida`) e conferir os textos contra o código: `Confirmação da senha`, `Este e-mail já está cadastrado.`, `As senhas não coincidem` e `As senhas coincidem`; verificar relendo `get_node` de cada frame
- [x] 3.2 Salvar o arquivo como `design/signup.figcraft`; verificar que `file design/signup.figcraft` mostra um zip e que `figcraft-cli info design/signup.figcraft` lista os 5 frames
- [x] 3.3 Exportar os frames para `design/png/` com `figcraft-cli export design/signup.figcraft -o design/png/ --format png` e renomear pela convenção (`signup-desktop-claro-padrao.png` etc.), só para a conferência; adicionar `design/png/` ao `.gitignore`; verificar que existem 5 PNGs, que cada um abre e que `git status` não os lista
- [x] 3.4 Abrir os 5 PNGs exportados e comparar cada um com a tela renderizada em `127.0.0.1:8000/accounts/signup/` (claro e escuro), agora com a Outfit servida pelo app, anotando as divergências; verificar que cada divergência está na lista do `design.md` e que a tipografia não é uma delas

## 4. Instalação e arquivos de apoio

- [x] 4.1 Copiar `~/.local/bin/figcraft-upgrade` para `scripts/figcraft-upgrade` (executável) com comentário de uso em inglês; verificar com `bash -n`, rodando `scripts/figcraft-upgrade --list` e rodando de novo sem mudar nada (a segunda execução diz que a versão já está instalada)
- [x] 4.2 Verificar a recusa por checksum: rodar o script com uma cópia dele apontando para um `SHA256SUMS.txt` adulterado numa pasta temporária e confirmar que sai com erro e que `current` não muda
- [x] 4.3 Acrescentar `design/` ao `.dockerignore` e criar `.gitattributes` com `design/*.figcraft binary`; verificar com `git check-attr binary design/signup.figcraft` e conferindo que `docker compose build` segue funcionando
- [x] 4.4 Documentar no `AGENTS.md` a convenção de `design/` (arquivos, nomes de frame e de PNG, como exportar; PNG não é versionado), a fonte do design em `design/fonts/` e como instalá-la, a fonte do app servida pelo build, a instalação e o upgrade do FigCraft, o registro do MCP por usuário e as divergências conhecidas; verificar relendo o texto e rodando cada comando documentado

## 5. Verificação

- [x] 5.1 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` (sem `--strict`) e confirmar sucesso, incluindo `check-added-large-files` com o zip e a fonte
- [x] 5.2 Conferir contra `specs/screen-design/spec.md` e `specs/visual-identity/spec.md` cada requisito e cenário, um a um, e arquivar com `openspec archive 53-design-figcraft-cadastro --yes` na branch antes do PR; verificar que `openspec/specs/screen-design/spec.md` foi criado e que `openspec/specs/visual-identity/spec.md` ganhou o requisito da fonte
