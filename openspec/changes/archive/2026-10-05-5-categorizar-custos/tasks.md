# Tasks

## 1. Modelo, constantes e migrations

- [x] 1.1 Módulo `transactions/appearance.py` com os 20 ícones da Lucide (chave e nome em português) e as 8 cores (chave, nome, hex de preenchimento e de texto nos modos claro e escuro), sem vermelho; verificar com testes: exatamente 20 ícones e 8 cores, sem duplicata, o texto do selo com contraste ≥ 4,5:1 e o preenchimento ≥ 3:1 nos dois modos
- [x] 1.2 Model `Category` (`name`, `user` anulável, restrições de unicidade sem diferenciar maiúsculas para padrão e personalizadas, `for_user`) e `Transaction.category` (FK anulável, `PROTECT`, `CheckConstraint` "entrada ou categoria preenchida", `select_related` na listagem), com a migration de esquema; verificar `docker compose exec web python manage.py makemigrations --check` e `migrate`
- [x] 1.3 Data migration que cria as seis padrão e move as despesas existentes para "Outros" (reversa: zera a FK e apaga as padrão); verificar com teste de migração: base com despesas e entradas termina com despesas em "Outros", entradas sem categoria, nada perdido, e a reversa volta ao estado anterior
- [x] 1.4 Testes de modelo: nome duplicado (maiúsculas incluídas) recusado no mesmo usuário e entre padrão, permitido entre usuários, `for_user` devolve padrão + próprias, `PROTECT` impede apagar categoria em uso, despesa sem categoria recusada pelo banco; verificar com `pytest transactions/tests/test_models.py`
- [x] 1.5 Migration `0005` que renomeia `emoji` para `icon` (chave da Lucide, padrão `package`) e converte os valores existentes (🍔 → `utensils` etc.), com reversa; verificar com teste de migração: categorias padrão e uma personalizada com emoji viram a chave certa, a reversa devolve o emoji, nenhum lançamento muda, e `makemigrations --check` passa

## 2. Ícones da Lucide e cores

- [x] 2.1 Copiar os 20 SVGs da `lucide-static` (versão fixada) já limpos para `transactions/icons/<chave>.svg`, com o texto da licença ISC; verificar com teste que existe um arquivo válido para cada ícone da lista e nenhum arquivo SVG extra
- [x] 2.2 Template tags `category_icon`, `category_badge` e `category_chip` (SVG inline com `aria-hidden`, chave fora da lista não gera nada) e as 8 classes `.cat-<chave>`, `.cat-badge` e `.cat-icon` em `frontend/style.css` (claro e `.dark`); verificar com testes das tags (cada ícone da lista, chave inválida e HTML do nome escapado) e que todas as chaves da paleta têm classe no CSS; recompilar o CSS (`docker compose run --rm css npm run build`) e conferir no navegador em modo claro e escuro

## 3. Categoria no lançamento e seletor flutuante

- [x] 3.1 `TransactionForm` com o campo `category` (queryset `for_user`, `user` vindo de `get_form_kwargs` nas views de criar e editar), obrigatório para despesa e zerado para entrada, com erros em português e opções do `<select>` nativo só com o nome; verificar com testes: despesa com e sem categoria, entrada com categoria preenchida, trocar o tipo na edição, categoria alheia e inexistente recusadas
- [x] 3.2 Template tag `category_select` e componente Alpine `categorySelect` (`static/js/category-select.js`, carregado antes do Alpine): `<select>` nativo como base, botão com selo e nome, painel flutuante com `role="listbox"`, teclado completo e clique fora; verificar com testes de renderização (select nativo presente, uma opção com selo por categoria, a escolhida marcada, categoria alheia ausente, nome escapado, papéis ARIA) e conferir no navegador: abrir, escolher com mouse e com teclado, Esc, clique fora, modo claro e escuro, dentro do modal sem corte
- [x] 3.3 Templates: o campo de categoria usa o seletor flutuante (modal e página completa), e a listagem exibe a pílula com ícone, cor e nome nas despesas; verificar com testes de renderização (pílula na linha, entrada sem categoria, seletor no formulário) e conferir no navegador

## 4. Gestão de categorias

- [x] 4.1 `CategoryForm` (strip, vazio, tamanho máximo, unicidade contra as próprias e as padrão, ícone e cor restritos às listas com caixa e Grafite iniciais, erros em português) e as views de lista, criar, renomear e excluir com `LoginRequiredMixin`, `ModalMixin` e `OwnedCategoryMixin` (404 para padrão, alheia ou inexistente), mais as rotas; verificar com testes de view e formulário: ícone fora da lista (`rocket`, um emoji), cor fora da lista (`red`, `#ff0000`), valores iniciais, GET na exclusão que não apaga e visitante anônimo redirecionado ao login
- [x] 4.2 Exclusão de categoria em uso: confirmação com a quantidade de lançamentos, e no POST mover os lançamentos para "Outros" e apagar em `atomic`; verificar com teste: categoria com 3 despesas some, as 3 continuam em "Outros", e o saldo não muda
- [x] 4.3 Templates de categorias (lista com padrão marcadas e sem ações, seletor de ícone e de cor com prévia, confirmação) no padrão visual existente, e item "Categorias" no menu lateral com estado ativo; verificar que cada tela renderiza (200 e conteúdo), `aria-current` no item certo, e conferir no navegador (modal e página completa)

## 5. Filtro da listagem

- [x] 5.1 Filtro `?category=<id>` na `TransactionListView` (valor inválido, alheio ou inexistente é ignorado), seletor flutuante com "Todas as categorias" e botão "Filtrar", links de paginação que mantêm o filtro, estado vazio do filtro e saldo sem filtro; verificar com testes: filtra e mantém a ordem, paginação preserva o filtro, valor `abc`/alheio/inexistente devolve 200 sem filtro, filtro vazio, saldo igual com e sem filtro, isolamento entre usuários

## 6. Entrega

- [x] 6.1 Conferir no navegador, em modo claro e escuro e em tela estreita: criar categoria com ícone e cor, criar despesa escolhendo a categoria no seletor, excluir categoria em uso, filtrar e paginar
- [x] 6.2 Atualizar o README (rotas de categorias e o filtro, tabela `transactions_category` com `icon` e `color`, estrutura, crédito e licença da Lucide no lugar do Twemoji); verificar que o modelo de dados descreve a categoria e que não sobrou menção ao Twemoji
- [x] 6.3 Rodar `uvx pre-commit run --all-files`, `docker compose exec web pytest --cov --cov-report=term-missing` (sem rebaixar `fail_under`) e `openspec validate --all`; verificar que os três passam
