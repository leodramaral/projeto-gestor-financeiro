# Proposal

## Why

A Issue #5 (Item 3 do MVP/pós-MVP) pede que o usuário entenda **em que gasta o dinheiro**. Hoje um
lançamento só tem tipo, valor, data e descrição: dá para somar o saldo, mas não para agrupar as
despesas. Categorizar é também a base do painel com gráficos (#6, despesas por categoria) e do
assistente de IA (#7), que dependem deste item. Os lançamentos já existem (#3).

## What Changes

- **Categorias padrão** (Alimentação, Transporte, Moradia, Lazer, Saúde, Outros), criadas por
  migration, existentes para todos os usuários e sem edição nem exclusão por eles. Cada uma já vem
  com ícone e cor (utensílios Laranja, carro Azul, casa Jade, controle Roxo, pílula Rosa, caixa
  Grafite).
- **Ícone e cor** em toda categoria, escolhidos de listas fixas: **20 ícones de linha** da
  [Lucide](https://lucide.dev) (licença ISC) e **8 cores** do tema (Jade, Verde, Azul, Roxo, Rosa,
  Laranja, Âmbar, Grafite). O ícone aparece num selo arredondado com o tom da cor, no estilo do
  TailAdmin, e herda a cor do tema nos modos claro e escuro. Os 20 SVGs ficam no repositório, com o
  texto da licença ao lado. Não usamos emoji: o desenho de emoji varia por sistema e não herda cor.
- **Seletor de categoria flutuante** (select customizado) no formulário de lançamento e no filtro da
  listagem: o `<select>` nativo não mostra ícone nem cor nas opções. O seletor novo lista as opções
  com selo e nome, funciona pelo teclado e, sem JavaScript, volta a ser o `<select>` nativo.
- **Categorias personalizadas** do usuário: criar, renomear e excluir, em telas próprias (menu
  "Categorias"). Visíveis só a quem as criou; nome único por usuário (sem diferenciar maiúsculas) e
  que não repete o nome de uma padrão.
- **Escolha da categoria** ao registrar ou editar um lançamento: obrigatória para **despesa**; a
  **entrada** não tem categoria (o campo é ignorado e limpo ao salvar).
- **Lançamentos anteriores** continuam válidos: as despesas já existentes passam para "Outros" por
  migration; as entradas ficam sem categoria.
- **Excluir categoria personalizada em uso** não apaga lançamentos: eles passam para "Outros"
  (decisão tomada aqui, como a Issue manda definir na change), e a confirmação avisa quantos serão
  movidos.
- **Listagem de lançamentos** mostra a categoria de cada despesa e ganha **filtro por categoria**,
  que sobrevive à paginação. O saldo atual continua sobre todos os lançamentos, filtrados ou não.
- Isolamento: o usuário só vê, escolhe, edita e exclui categorias suas (ou as padrão, sem edição).

**Fora do escopo:** gráficos e totais por categoria (#6), categoria em entradas, subcategorias, ícone ou
cor livres (fora das listas fixas), emoji, orçamento por categoria (#8), mesclar categorias, reordenar, busca textual,
múltiplos filtros combinados (período, tipo) e exportação.

## Capabilities

### New Capabilities
- `categories`: categorias padrão e personalizadas, com gestão pelo usuário, unicidade de nome,
  isolamento e destino dos lançamentos ao excluir uma categoria.

### Modified Capabilities
- `transactions`: o lançamento ganha categoria (obrigatória na despesa), a listagem a exibe e filtra
  por ela, e os lançamentos já existentes são migrados.

## Impact

- Código: model `Category` (nome, ícone, cor) e FK `Transaction.category` em `transactions/models.py`, duas migrations
  (esquema e dados), `TransactionForm` (campo e regra), views/URLs/templates de categorias, filtro na
  `TransactionListView`, sidebar, testes.
- Banco: tabela nova `transactions_category`; coluna nova e anulável em `transactions_transaction`;
  data migration que cria as padrão e move as despesas existentes para "Outros".
- Estáticos: 20 SVGs da Lucide em `transactions/icons/` (lidos pelo template tag, com a licença ISC ao
  lado), uma classe de cor por item da paleta em `frontend/style.css` (recompilar o CSS) e o componente
  Alpine do seletor flutuante. Sem dependência nova no `pyproject.toml` ou no `package.json`.
- Documentação: README (rotas, modelo de dados, estrutura e crédito da Lucide, ISC).
- Segurança: validação de entrada, CSRF nos formulários, rotas só com login, consulta sempre filtrada
  pelo dono, e categoria alheia recusada no formulário e respondendo 404 nas telas de gestão.
