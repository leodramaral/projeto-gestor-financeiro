# Tasks

## 1. Preparação

- [x] 1.1 Definir o conjunto de dados de exemplo (usuário `Maria Silva`, mês, ~8 lançamentos categorias reais) num arquivo temporário fora do repositório; verificar que a contagem por categoria bate com a lista
- [x] 1.2 Confirmar o ambiente de design: `fc-list | grep -i outfit`, `claude mcp list` com `figcraft` conectado e `figcraft-cli --version`; verificar criando um texto `Outfit` e olhando o `screenshot`
- [x] 1.3 Com o app no ar e um usuário de teste com o conjunto da 1.1 no banco de dev, capturar com o Playwright cada tela (claro, escuro, mobile) para servir de referência (usado o usuário `demo@exemplo.com`, que já existia, com dados diferentes: compara-se estrutura, não valores); verificar que as telas autenticadas abriram sem redirecionar ao login

## 2. Telas de visitante

- [x] 2.1 `design/login.figcraft`: `login` em desktop claro, desktop escuro e mobile claro, mais o estado com erro de credenciais (mensagem real do formulário) e o aviso de conta não confirmada, se o template o exibir; reaproveitar painel de marca, campos e botão de tema de `design/signup.figcraft`; verificar com `get_node` os textos contra `templates/accounts/login.html` e `accounts/forms.py`
- [x] 2.2 `design/account-confirmation.figcraft`: `signup_done`, `confirm` (sucesso e link inválido ou expirado), `resend` (com erro) e `resend_done`, nos três viewport/tema onde o layout muda e em claro/mobile nos demais; verificar os textos contra os templates e `figcraft-cli info` listando os frames com a convenção de nomes
- [x] 2.3 `design/password-reset.figcraft`: `password_reset`, `password_reset_done` e `password_reset_confirm` (formulário e link inválido), com o estado de erro de senha; verificar contra `templates/accounts/password_reset_*.html`
- [x] 2.4 Salvar e comparar cada frame de visitante com a captura da 1.3; verificar que o que diverge é limite da ferramenta e anotá-lo para a 6.2

## 3. Lançamentos e categorias

- [x] 3.1 `design/transactions.figcraft`: lista (com o filtro de categoria e o vazio filtrado), formulário de lançamento aberto no modal (padrão e com erros), e confirmação de exclusão, em desktop claro e escuro, e a lista em mobile claro; verificar contra `templates/transactions/transaction_*.html` e `transactions/forms.py`
- [x] 3.2 `design/categories.figcraft`: lista (categorias padrão e próprias, contagem de lançamentos), formulário no modal (padrão e com erros) e confirmação de exclusão (com e sem lançamentos), em desktop claro e escuro, e a lista em mobile claro; verificar contra `templates/transactions/category_*.html`
- [x] 3.3 Comparar com as capturas da 1.3 e anotar divergências

## 4. Perfil

- [x] 4.1 `design/profile.figcraft`: `profile` em desktop claro, desktop escuro e mobile claro, com o estado de erro de formulário se existir; verificar contra `templates/accounts/profile.html` e o formulário do perfil
- [x] 4.2 Comparar com a captura da 1.3 e anotar divergências

## 5. Correção do cartão de visitante

- [x] 5.1 Em `templates/base_auth.html`, trocar `relativeflex` por `relative flex`; verificar no Playwright (claro, escuro e 390 px) que o cartão de `/accounts/signup/done/` e `/accounts/confirm/resend/` fica centralizado e que a grade cobre a janela
- [x] 5.2 Teste em `accounts/tests/test_guest_layout.py` que falha com `relativeflex` e passa com `relative flex`; verificar vendo-o falhar com a classe antiga e passar com a nova, e `docker compose exec web pytest` verde

## 6. Convenção e verificação

- [x] 6.1 Em cada `.figcraft`: nenhuma camada de texto com família diferente de `Outfit` (`inspect_document`), nomes de frame na convenção, nenhum frame de estado que o código não tem; verificar por arquivo e que `file design/*.figcraft` mostra zip
- [x] 6.2 Atualizar no `AGENTS.md` a lista de divergências conhecidas com o que as tasks 2.4, 3.3 e 4.2 anotaram; verificar relendo o texto
- [x] 6.3 Exportar os PNGs de cada arquivo para `design/png/` (não versionados), renomear pela convenção e abrir uma amostra; verificar que `git status` não lista nenhum PNG e que nenhum `.figcraft` passa de 500 KB
- [x] 6.4 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` (sem `--strict`); verificar sucesso
- [x] 6.5 Documentar o uso do FigCraft no `README.md` (Parte 2, subseção "Design das telas (FigCraft)", e a pasta `design/` na estrutura do repositório); verificar relendo o texto e conferindo cada caminho e comando citado contra o `AGENTS.md` e o repositório
- [x] 6.6 Conferir cada requisito e cenário de `specs/screen-design/spec.md` contra os arquivos, um a um; arquivar com `openspec archive 55-design-figcraft-telas --yes` na branch antes do PR
