# Design

## Context

Existe o app `transactions` com `Transaction` (`user`, `kind`, `amount`, `date`, `description`),
`TransactionForm` (com `StyledFormMixin`, `MoneyField` e o tipo como botões), views genéricas com
`OwnedQuerysetMixin` e `ModalMixin` (modal por melhoria progressiva), listagem paginada em
`TRANSACTIONS_PER_PAGE` e os parciais `form_field.html`/`choice_buttons.html`. A última migration é
`0001_initial`. Ver `proposal.md` para motivação e escopo.

## Goals / Non-Goals

**Goals:**
- Categoria como atributo do lançamento, com isolamento garantido na consulta e no formulário.
- Reaproveitar views genéricas, modal, parciais e estilos existentes.
- Migrar os dados existentes sem perda e de forma reversível.

**Non-Goals:**
- Qualquer agregação por categoria (é da #6) e categoria em entradas.

## Decisions

**1. Um model `Category`, no app `transactions`.**
Campos: `name` (`CharField(40)`), `icon` (`CharField(24)`, a chave do ícone da Lucide, ex.: `utensils`), `color` (`CharField(16)`,
a chave da paleta, ex.: `orange`), `user` (FK anulável, `CASCADE`). `user` nulo = categoria **padrão**
(do sistema); preenchido = personalizada daquele usuário. Um app novo seria um app inteiro para uma
tabela acoplada ao lançamento. Restrições no banco: `UniqueConstraint(Lower("name"), "user")` para
as personalizadas e `UniqueConstraint(Lower("name"), condition=Q(user__isnull=True))` para as padrão
(índice único com NULL não barra duplicata, por isso a segunda).
*Alternativa descartada:* flag `is_default` + user obrigatório com cópia das padrão por usuário —
multiplica linhas e exige criar no cadastro.

**2. `Transaction.category`: FK anulável, `on_delete=PROTECT`.**
Anulável porque a entrada não tem categoria. `PROTECT` impede apagar uma categoria em uso por acidente;
a view de exclusão move os lançamentos para "Outros" e só então apaga, numa transação
(`transaction.atomic`). Não usamos `SET_NULL`: deixaria despesa sem categoria, contra a regra.
A regra "despesa exige categoria, entrada não tem" fica no formulário (`clean`), que zera a
categoria da entrada. Um `CheckConstraint` espelha: `kind = 'income'` OU `category IS NOT NULL`
(a entrada sem categoria é o único caso sem ela exigida pelo banco; entrada com categoria é impedida
só no formulário).

**2a. Ícone e cor: listas fixas num módulo de constantes.**
`transactions/appearance.py` define os 20 ícones (chave da Lucide, nome em português) e as 8 cores (chave,
nome e hex de preenchimento e texto nos modos claro e escuro). Não usamos `choices` no model: trocar a
lista não gera migration, e a validação fica no formulário, que recusa ícone ou cor fora das listas e
abre com a caixa (`package`) e Grafite. No banco vai só a chave do ícone e a chave da cor.
Cores escolhidas dos tokens do tema (Jade `brand-500`, Verde `success-600`, Azul `blue-light-600`, Roxo
`theme-purple-500`, Rosa `theme-pink-500`, Laranja `orange-600`, Âmbar `warning-600`, Grafite `gray-600`);
sem vermelho, que já significa alerta e despesa. O texto do selo é a cor escurecida (claro) ou clareada
(escuro) até 4,5:1 sobre o fundo translúcido da própria cor; um teste calcula o contraste da paleta.
*Alternativas descartadas:* emoji (o desenho varia por sistema, não herda cor e o `<option>` do select
não o mostra como imagem; houve uma versão desta change com Twemoji, abandonada); só cor e nome, como a
demo do TailAdmin (perde o reconhecimento rápido).

**2b. Ícones da Lucide como SVG inline.**
Copiam-se os 20 SVGs da `lucide-static` (versão fixada, licença ISC) para `transactions/icons/<chave>.svg`,
já limpos (sem comentário, `class`, `width` nem `height` na raiz) e com o `LICENSE` ao lado. Um template
tag `category_icon` lê o arquivo (uma vez, em cache) e devolve o SVG inline com `aria-hidden` e as classes
de tamanho; só aceita chave da lista, então nada vindo do usuário vira caminho de arquivo. Inline porque
o traço usa `currentColor` e herda a cor do selo e do tema, o que uma `<img>` não faz. Trocar de
biblioteca depois exige trocar os arquivos, sem migration. A espessura do traço fica numa classe
`.cat-icon` (1,75), em vez de repetida em cada arquivo.

**2c. Cor como classe estática.**
Uma classe `.cat-<chave>` por cor em `frontend/style.css` define variáveis (`--cat-fill`, `--cat-bg`,
`--cat-text`) para o claro e para o escuro (`.dark .cat-<chave>`, como o `dark` do projeto). É CSS fixo,
que o Tailwind sempre compila; classes montadas com texto dinâmico não seriam geradas. O selo
(`.cat-badge`) usa o fundo e a cor do texto dessas variáveis.

**2d. Migration do emoji para o ícone.**
As migrations `0002` a `0004` já foram aplicadas em bancos de desenvolvimento com a coluna `emoji`.
A `0005` renomeia `emoji` para `icon` e converte os valores existentes (🍔 → `utensils` etc.) por um mapa
fixo, com reversa; assim nenhum banco precisa ser refeito e nenhum dado se perde. Depois do merge pode-se
condensar o histórico, se a equipe quiser.

**3. Padrão por data migration; "Outros" achado pelo nome.**
`0002` cria o model e a FK (esquema); `0003` insere as seis padrão (ainda com a coluna `emoji`, convertida na `0005`) e move as despesas existentes para
"Outros"; a reversa de `0003` zera a FK e apaga as padrão. Em código, "Outros" é lido de uma constante
`DEFAULT_CATEGORY_NAME`; o formulário e a exclusão a buscam com `user__isnull=True, name="Outros"`.
Como as padrão não são editáveis pela aplicação, o nome é estável.

**4. Escopo de categorias: um manager/queryset `for_user(user)`.**
`Category.objects.for_user(user)` = `Q(user=user) | Q(user__isnull=True)`, ordenadas (padrão primeiro,
depois por nome). O campo de categoria do formulário usa esse queryset, então id alheio cai em
`invalid_choice` (mensagem em português). As telas de gestão usam `Category.objects.filter(user=...)`
em um `OwnedCategoryMixin`: padrão e alheia caem no mesmo 404.

**5. Formulário.**
`TransactionForm` recebe `user` por `get_form_kwargs` (as views de criação e edição passam
`request.user`). O campo `category` é um `ModelChoiceField` opcional no HTML, mas `clean()` exige para
despesa (erro no campo) e limpa para entrada. `empty_label` "Selecione…". `CategoryForm` valida nome
(strip, vazio, tamanho), o ícone e a cor contra as listas e a unicidade sem diferenciar maiúsculas no `clean_name`, consultando o escopo
do usuário **e** as padrão, para devolver erro de formulário em vez de `IntegrityError`; as
restrições do banco ficam como rede de segurança.

**6. Telas de categorias.**
Rotas sob `transactions:` para manter o app coeso: `categories/` (lista com padrão e personalizadas),
`categories/new/`, `categories/<pk>/edit/`, `categories/<pk>/delete/` (`category-list`,
`category-create`...). `ListView` + `CreateView`/`UpdateView`/`DeleteView` com `LoginRequiredMixin`,
`ModalMixin` e mensagens de sucesso, como nos lançamentos. A lista de categorias não é paginada
(poucas por usuário) e marca as padrão sem ações. Item "Categorias" no menu lateral, com estado ativo.
A confirmação de exclusão mostra `transactions.count` e a exclusão faz o `UPDATE` para "Outros" antes
de apagar, em `atomic`.

**7. Filtro por categoria.**
Parâmetro de consulta `?category=<id>`. A view lê o valor, converte para inteiro e, se existir em
`Category.objects.for_user(user)`, filtra; qualquer outro valor (não numérico, alheio, inexistente) é
ignorado e a listagem sai sem filtro, sem erro. O seletor do filtro (ver 9; GET, enviado pelo botão
"Filtrar", que também funciona sem JavaScript) fica no cabeçalho do cartão. Os links de paginação
passam a ser montados com o filtro (`?category=<id>&page=<n>`) via um parâmetro de contexto
`querystring` sem `page`. O saldo continua `current_balance(user)`, sem filtro. Com filtro e zero
resultados, mostra-se um estado vazio próprio (distinto de "ainda não tem lançamentos").
*Alternativa descartada:* filtro por HTMX/JS — a página já é renderizada no servidor e a #3 descartou
HTMX.

**8. Exibição.**
A linha da listagem mostra a categoria como pílula (ícone e nome na cor da categoria) sob a descrição;
entrada não mostra nada. `select_related("category")` evita N+1.

**9. Seletor flutuante de categoria (select customizado).**
O `<option>` nativo não desenha SVG, então o campo de categoria e o filtro ganham um componente Alpine
(`categorySelect`, em `static/js/category-select.js`, carregado antes do Alpine) por melhoria progressiva:
o HTML traz o `<select>` nativo de verdade, e o componente o esconde (`sr-only`, fora da ordem de Tab) e
desenha por cima um botão com o selo e o nome da escolha e um painel flutuante (`role="listbox"`,
`absolute`, `max-h-60` com rolagem) com uma opção por categoria. Escolher uma opção grava o valor no
`<select>` e dispara `change`, então o envio do formulário não muda nada no servidor. Teclado: Enter,
Espaço ou Seta para baixo abrem; setas, Home e End movem a opção ativa (`aria-activedescendant`); Enter
ou Espaço escolhem; Esc e Tab fecham; clique fora fecha. Sem JavaScript fica o `<select>` nativo, só com
os nomes. Um template tag `category_select` monta o HTML a partir de uma lista de categorias, usado no
formulário e no filtro; as opções vêm do mesmo `Category.objects.for_user`, então nenhuma categoria alheia
aparece. A `<dialog>` do modal recebe `overflow-visible` para a lista não ser cortada.
*Alternativas descartadas:* biblioteca de select (dependência nova para um componente pequeno); manter o
`<select>` nativo com emoji no texto (não mostra a cor nem o ícone).

## Risks / Trade-offs

- **[Despesa existente sem "Outros" na migração]** → `0003` cria as padrão antes de mover; teste de
  migração com dados.
- **[Categoria alheia por id forjado]** → queryset do campo e do filtro é `for_user`; testes de
  isolamento no formulário, no filtro e nas telas.
- **[Duplicata por corrida]** → a validação do formulário é a mensagem amigável; a restrição do banco
  é a garantia (a rara corrida vira erro 500, aceitável nesta escala).
- **[Excluir categoria move lançamentos sem desfazer]** → a confirmação informa a quantidade.
- **[`core`/#6 dependem do nome "Outros"]** → constante única reutilizável.
- **[Licença da Lucide (ISC)]** → manter o texto da licença ao lado dos SVGs e citá-la no README.
- **[Seletor customizado é acessibilidade a mais]** → papéis ARIA, teclado completo e `<select>` nativo
  como base; testes de renderização e conferência no navegador, inclusive dentro do modal.
- **[Cor como única pista]** → ícone e nome sempre aparecem junto da cor; teste de contraste da paleta.

## Migration Plan

`0002` (aditiva: tabela e coluna anulável) e `0003` (dados). Reverter: a reversa de `0003` zera
`category` e remove as padrão; a de `0002` remove a coluna e a tabela. Nada existente muda de formato.
