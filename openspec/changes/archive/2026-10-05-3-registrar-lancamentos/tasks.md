# Tasks

## 1. Modelo de dados

- [x] 1.1 Criar o app `transactions` (registrar em `INSTALLED_APPS`) com o model `Transaction` (`CheckConstraint` amount > 0, índice por usuário e data) e a migration; verificar que `docker compose exec web python manage.py makemigrations --check` passa e que `migrate` roda
- [x] 1.2 Testes de modelo: restrição de valor ≤ 0 recusada pelo banco, `CASCADE` ao excluir o usuário; verificar com `pytest transactions/tests/test_models.py`
- [x] 1.3 Função de saldo atual (agregação condicional sobre todos os lançamentos do usuário); verificar com testes: sem lançamentos, só entradas, só despesas, misto (pode ficar negativo) e isolamento entre usuários

## 2. Formulários

- [x] 2.1 `TransactionForm` (tipo, valor, data, descrição; estilo via `StyledFormMixin`; data padrão = hoje); verificar com testes de formulário: valor 0, negativo, 3 casas decimais, texto, NaN/infinito, vírgula decimal, data inexistente, data em formato inválido, tipo inválido, campos vazios e descrição acima do limite; mensagens de erro em português

## 3. Views, rotas e telas

- [x] 3.1 `OwnedQuerysetMixin` e as views de lista (paginada de 20, ordem `-date, -id`, saldo atual no topo, estado vazio), criação, edição e exclusão (GET confirma, POST exclui), mais as rotas em `transactions/urls.py` incluídas em `config/urls.py`; verificar com testes: lista ordenada e paginada, página inexistente com 404, criação atribui o dono mesmo com `user` forjado no POST, edição não muda o dono, GET na exclusão não apaga, POST apaga, mensagens de sucesso
- [x] 3.2 Sem tela de saldo inicial: o saldo de partida é uma Entrada comum; remover `Account`, a rota `balance`, a view, o formulário e o template, e regenerar a migration só com `Transaction`; verificar com testes que não existem a rota nem o model e que uma Entrada "Saldo inicial" entra no saldo atual da lista
- [x] 3.3 Templates em `templates/transactions/` (lista, formulário, confirmação de exclusão) em português, com CSRF, erros por campo e valor da despesa distinto do da entrada; recompilar o CSS (`docker compose run --rm css npm run build`) se surgirem classes novas; verificar que cada tela renderiza (status 200 e conteúdo esperado)
- [x] 3.4 Home redireciona à lista (mantendo login obrigatório e `name="home"`) e sidebar ganha "Lançamentos" com estado ativo correto; ajustar `core/tests/test_home.py`; verificar que os testes de `core` passam

- [x] 3.5 Máscara no campo de valor: digita-se só números e o campo mostra `1.234,56`, preenchendo da direita para a esquerda; o servidor aceita o milhar apenas quando há vírgula decimal (`1.234,56`), sem reinterpretar `0.001` nem `1.500`; verificar com testes de formulário (milhar válido, `0.001`/`1.500`/`1.2.3,00` ainda rejeitados) e que o HTML do campo traz a máscara; conferir no navegador
- [x] 3.6 Campo "tipo" como dois botões de rádio (Entrada/Despesa) em vez do select, acessível por teclado, sem pré-seleção; verificar com teste que a tela renderiza os dois rádios, que o tipo vazio ainda gera o erro "Escolha o tipo do lançamento." e que o tipo escolhido volta marcado ao reexibir/editar; recompilar o CSS; conferir no navegador

- [x] 3.7 Criação, edição e confirmação de exclusão em janela modal (`<dialog>`) sobre a listagem: as views servem só o fragmento quando a requisição é do modal (`X-Requested-With: XMLHttpRequest`) e a página completa nos demais casos; envio pelo modal devolve o erro dentro dele ou, no sucesso, recarrega a listagem com a mensagem; verificar com testes de view (fragmento sem `<html`, página completa sem o cabeçalho, JSON de sucesso, erro de validação dentro do fragmento, 404 de lançamento alheio, cabeçalho `Vary`) e no navegador (abrir, enviar com erro, enviar, cancelar, Esc, clique fora)

- [x] 3.8 Tabela da listagem no estilo "Basic Table 5" do TailAdmin: cartão com título e botão "Novo lançamento" no cabeçalho, linhas com ícone circular e descrição, data, valor, selo (pílula) de tipo e menu "…" com Editar/Excluir, e rodapé com Anterior/Próxima e páginas numeradas com reticências; verificar com testes (selo e ícone por tipo, menu com os links de edição e exclusão, páginas numeradas com a atual marcada, Anterior desabilitado na primeira página e Próxima na última, reticências em muitas páginas), recompilar o CSS e conferir no navegador em modo claro e escuro e em tela estreita

- [x] 3.9 A sidebar recolhida continua recolhida ao navegar entre páginas (paginação, links, recarregar) em telas de desktop; no celular a gaveta não reabre sozinha; verificar com teste de que o layout base carrega o estado salvo e com teste no navegador: recolher, ir para a página 2 da listagem, recarregar, expandir e navegar de novo, e conferir que em tela estreita a gaveta continua fechada; e que a barra já nasce recolhida, sem animar a cada página (medir os eventos de transição da barra durante o carregamento: nenhum)

## 4. Segurança

- [x] 4.1 Testes de isolamento entre usuários: lista e saldos de cada um só com os próprios dados; GET e POST de edição e exclusão de lançamento alheio retornam 404 e não alteram nem apagam; 404 idêntico ao de id inexistente
- [x] 4.2 Teste que percorre todas as rotas do app como anônimo (GET e POST) e confirma o redirecionamento ao login sem criar, alterar ou excluir dados; teste de CSRF no POST (cliente com `enforce_csrf_checks`)

## 5. Documentação

- [x] 5.1 Atualizar o `README.md` (estado atual: lançamentos implementados; rotas; modelo de dados com `Transaction`); verificar que os comandos documentados rodam como escritos

## 6. Verificação final

- [x] 6.1 `docker compose exec web pytest --cov --cov-report=term-missing` passa e a cobertura não cai; elevar `fail_under` se subir
- [x] 6.2 `uvx pre-commit run --all-files` passa
- [x] 6.3 Manual: com o Compose no ar, registrar uma entrada "Saldo inicial" e uma despesa, conferir o saldo atual, editar, excluir (cancelar e depois confirmar), criar mais de 20 lançamentos e navegar entre as páginas, e com um segundo usuário tentar abrir por URL um lançamento do primeiro (404)
- [x] 6.4 `openspec validate --all` passa (sem `--strict`)
