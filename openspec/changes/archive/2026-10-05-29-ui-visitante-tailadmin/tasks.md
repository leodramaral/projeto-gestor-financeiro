# Tasks

## 1. Preparação

- [x] 1.1 Copiar o `.env` e gerar o CSS na worktree (`docker compose run --rm css npm run build`) e verificar que `static/dist/css/style.css` existe

## 2. Layout base

- [x] 2.1 Criar `partials/auth_aside.html` (logo, frase, grade decorativa própria, oculto abaixo de `lg`) e verificar que não contém "TailAdmin"
- [x] 2.2 Refatorar `base_auth.html` com variante dividida e variante em cartão, mantendo tema, Alpine e botão de tema; verificar que as telas de confirmação, reenvio e nova senha continuam renderizando (`pytest accounts`)
- [x] 2.3 Adicionar a grade decorativa em `frontend/style.css`, recompilar o CSS e verificar a aparência nos dois temas

## 3. Telas

- [x] 3.1 Aplicar o layout dividido em `login.html` (título, subtítulo, campos, "Lembrar de mim", link de recuperação e de cadastro) e verificar por teste que os elementos existem e o painel aparece
- [x] 3.2 Aplicar o layout dividido em `signup.html`, com link para voltar ao login, e verificar que os requisitos de senha seguem funcionando (teste + conferência manual)
- [x] 3.3 Ajustar `password_reset_form.html` ao layout dividido da demo (link de voltar ao login no topo) e verificar o link de volta ao login

## 4. Testes e verificação

- [x] 4.1 Escrever testes de renderização: painel em entrar/criar conta/recuperação; sem "TailAdmin"; sem botões sociais; e verificar que passam, junto com os testes existentes (`docker compose run --rm --no-deps web pytest`)
- [x] 4.2 Verificar manualmente entrar, criar conta e recuperar senha em tela larga e estreita, nos temas claro e escuro, incluindo erros de formulário, e medir o contraste do painel (≥ 4,5:1)
- [x] 4.3 Rodar `uvx pre-commit run --all-files` e `openspec validate --all` e verificar que passam
