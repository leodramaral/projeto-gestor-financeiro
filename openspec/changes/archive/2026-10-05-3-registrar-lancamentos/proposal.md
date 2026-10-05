# Proposal

## Why

O sistema já identifica o usuário (#2), mas ainda não guarda nada financeiro: ninguém consegue
registrar o dinheiro que entra e sai. A Issue #3 (Item 2 do MVP) entrega o núcleo do domínio — saldo
inicial e lançamentos de entrada e despesa — sobre o qual o resumo de status financeiro e as
funcionalidades pós-MVP vão se apoiar. A dependência (saber de quem é o lançamento) já existe.

## What Changes

- Registro de **lançamento** com tipo (entrada ou despesa), valor, data e descrição.
- Edição e exclusão de um lançamento; a exclusão pede confirmação numa tela própria.
- Listagem paginada, da data mais recente para a mais antiga, com o saldo atual (entradas −
  despesas) no topo.
- O saldo de partida não tem tela própria: o usuário registra uma **Entrada** comum (por exemplo,
  "Saldo inicial"). Atende o "cadastro do saldo inicial" da Issue sem um segundo modelo.
- Validação: valor maior que zero, com no máximo duas casas decimais; data válida; descrição
  obrigatória e com tamanho limitado.
- **Isolamento por usuário:** cada usuário só vê, edita e exclui os próprios lançamentos; acesso a
  lançamento alheio (ou inexistente) responde 404. Todas as telas exigem login.
- A barra lateral recolhida continua recolhida ao navegar entre páginas (hoje volta a abrir a cada
  carregamento, o que a paginação da listagem expõe).
- Entrada "Lançamentos" no menu lateral; o início (`/`) passa a levar à listagem.

**Fora do escopo:** categorização de custos, resumo/painel com gráficos e indicadores de status
financeiro (itens próprios do MVP e do pós-MVP); múltiplas contas ou carteiras por usuário; campo ou tela dedicada de saldo inicial; moedas
além do real; busca, filtros e ordenação alternativa; lançamentos recorrentes ou parcelados;
anexos; importação/exportação; exclusão lógica (lixeira) e histórico de alterações.

## Capabilities

### New Capabilities
- `transactions`: registro, edição, exclusão com confirmação e listagem paginada de lançamentos, com
  saldo atual, validação de entrada e isolamento entre usuários.

### Modified Capabilities
- `frontend-layout`: a barra lateral recolhida mantém o estado ao navegar entre páginas.

## Impact

- Código: app novo `transactions` (model `Transaction` + migration, formulários, views,
  URLs, testes); `config/settings/base.py` (app instalado, tamanho da página); `config/urls.py`;
  `core` (a home redireciona à listagem); `templates/transactions/` (listagem, formulário,
  confirmação de exclusão) e o item de menu em `templates/partials/sidebar.html`.
- Banco: uma tabela nova (`transactions_transaction`); nenhuma tabela existente muda.
- Sem dependência nova. Recompilar o CSS se surgirem classes Tailwind novas.
- Documentação: README (estado atual e modelo de dados).
- Segurança: validação de entrada, CSRF nos formulários, rotas protegidas por login e consulta
  sempre filtrada pelo dono.
