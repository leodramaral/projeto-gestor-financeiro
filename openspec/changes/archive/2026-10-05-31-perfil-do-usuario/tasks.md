# Tasks

## 1. Preparação

- [x] 1.1 Gerar o CSS na worktree (`docker compose run --rm css npm run build`) e verificar que `static/dist/css/style.css` existe

## 2. Perfil

- [x] 2.1 Criar `partials/user_avatar.html` com as iniciais (tamanho por parâmetro) e verificar por teste os casos de nome com duas palavras, uma palavra e vários espaços
- [x] 2.2 Criar a view `profile` (`accounts/profile/`, só para autenticados) e `templates/accounts/profile.html` somente leitura, e verificar por teste que exibe os dados do próprio usuário, redireciona o anônimo ao login e não tem edição nem "TailAdmin"

## 3. Cabeçalho

- [x] 3.1 Substituir nome e botão "Sair" soltos em `header.html` pelo card e menu do usuário (nome, e-mail, "Ver perfil", "Sair" em `POST` com CSRF) e verificar por teste que o menu tem os itens e que o logout continua encerrando a sessão
- [x] 3.2 Fechar o menu ao clicar fora e com Esc, com `aria-expanded` e operação por teclado, e verificar manualmente no navegador

## 4. Testes e verificação

- [x] 4.1 Ajustar `accounts/tests/test_access.py` ao novo cabeçalho e verificar que a suíte inteira passa (`docker compose run --rm --no-deps web pytest`)
- [x] 4.2 Verificar manualmente perfil e menu em tela larga e estreita (375 px, sem rolagem horizontal), nos temas claro e escuro, comparando com a demo, e medir o contraste (≥ 4,5:1)
- [x] 4.3 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e verificar que passam
