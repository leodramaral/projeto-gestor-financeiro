# Tasks

## 1. Marca

- [x] 1.1 Criar o ícone "G em quadrado" conforme a geometria da decisão 2 do `design.md` (`static/images/logo/logo-icon.svg`) e o `static/images/favicon.svg` (mesmo desenho, em jade e G branco), e remover `logo.svg`, `logo-dark.svg` e `favicon.ico`; verificar que os arquivos novos existem, os antigos não, e que nenhum template referencia os removidos (`grep -rn "logo.svg\|logo-dark.svg\|favicon.ico" templates` vazio)
- [x] 1.2 Criar `templates/partials/brand.html` (ícone + nome "Gestor Financeiro" em texto, parâmetro `compact`) e usá-lo em `sidebar.html`, `header.html` (mobile) e `base_auth.html`; verificar com teste que painel e telas de visitante exibem "Gestor Financeiro" como marca e que a barra recolhida mostra só o ícone
- [x] 1.3 Apontar o favicon SVG em `base.html` e `base_auth.html`; verificar com teste que a resposta contém `<link rel="icon" ... favicon.svg>` e que `/static/images/favicon.svg` responde 200
- [x] 1.4 Teste varrendo as páginas renderizadas (login, cadastro, recuperação, confirmação e painel) e todos os e-mails: nenhum contém "TailAdmin" no conteúdo exibido

## 2. Esquema de cores verde

- [x] 2.1 Substituir `--color-brand-25…950` em `frontend/style.css` pela escala Jade da decisão 4 do `design.md`; verificar que `brand-500` é `#0f766e` e não é mais `#465fff`
- [x] 2.2 Teste de contraste (fórmula WCAG) lendo os tokens: texto branco sobre `brand-500` e `brand-600`, `brand-600` sobre branco e `brand-400` sobre `gray-900` e o G `brand-700` sobre `brand-300` (ícone escuro), todos ≥ 4,5:1; confirmar que a escala fixada no `design.md` passa e, se algum par ficar abaixo, ajustar o tom e o `design.md`
- [x] 2.3 Trocar o azul `#465fff` pelo hex de `brand-500` nos e-mails (`base`, `confirm_account`, `password_reset`, `test_message`); verificar com teste que nenhum template contém `#465fff`
- [x] 2.4 Recompilar o CSS (`docker compose run --rm css npm run build`) e verificar que o CSS servido não contém `#465fff`

## 3. Alternância de tema

- [x] 3.1 Extrair o botão de tema de `header.html` para `partials/theme_toggle.html` com `aria-label="Alternar tema"` e usá-lo no header; verificar que o painel continua exibindo o controle (teste)
- [x] 3.2 Criar `partials/theme_init.html` (script do `<head>` com `try/catch`) e incluí-lo em `base.html` e `base_auth.html`; verificar com teste que ambos os layouts o incluem antes da folha de estilos
- [x] 3.3 Incluir `theme_toggle.html` em `base_auth.html` (canto superior direito) com o `x-data` de `darkMode`; verificar com teste que login, cadastro, confirmação e recuperação de senha exibem o controle com nome acessível

## 4. Documentação

- [x] 4.1 Atualizar o `README.md` (identidade visual, onde ficam os tokens de cor e a marca, e como recompilar o CSS) e verificar que os comandos citados rodam como escritos

## 5. Verificação final

- [x] 5.1 `docker compose exec web pytest --cov --cov-report=term-missing` passa e a cobertura não cai; `uvx pre-commit run --all-files` passa (com os arquivos novos já em stage)
- [x] 5.2 Manual (Playwright ou navegador): login, cadastro e painel nos dois temas — marca, verde, contraste, alternância e persistência após recarregar, e a escolha feita no login valendo no painel
- [x] 5.3 `openspec validate --all` passa (sem `--strict`)
