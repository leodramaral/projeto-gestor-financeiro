# transactions Specification

## Purpose
Define como o usuário registra o dinheiro que entra e sai — lançamentos de entrada e despesa — e
como consulta o saldo, corrige e remove esses registros, vendo apenas os próprios.

## Requirements

### Requirement: Saldo atual
A listagem DEVE exibir o saldo atual do usuário: a soma das entradas menos a soma das despesas de
**todos** os seus lançamentos, e não apenas dos da página exibida. A aplicação NÃO DEVE ter cadastro
ou tela separada de saldo inicial: quem precisa partir de um saldo que já existia o registra como uma
entrada comum.

#### Cenário: Conta nova
- **QUANDO** um usuário sem lançamentos abre a listagem pela primeira vez
- **ENTÃO** o saldo atual exibido é R$ 0,00

#### Cenário: Entradas menos despesas
- **QUANDO** o usuário tem entradas e despesas
- **ENTÃO** o saldo atual é a soma das entradas menos a soma das despesas
- **E** ele pode ficar negativo quando as despesas superam as entradas

#### Cenário: Saldo de partida como entrada
- **QUANDO** o usuário registra uma entrada de 1500,00 com a descrição "Saldo inicial"
- **ENTÃO** o saldo atual passa a incluir esses 1500,00

#### Cenário: Todas as páginas
- **QUANDO** os lançamentos ocupam mais de uma página da listagem
- **ENTÃO** o saldo atual considera todos eles, e não muda ao trocar de página

#### Cenário: Saldo de outro usuário
- **QUANDO** dois usuários têm lançamentos diferentes
- **ENTÃO** cada um vê apenas o próprio saldo atual

### Requirement: Registro de lançamento
A aplicação DEVE permitir ao usuário autenticado registrar um lançamento com tipo (entrada ou
despesa), valor, data e descrição, todos obrigatórios. O valor DEVE ser maior que zero e ter no
máximo duas casas decimais; a data DEVE ser válida; a descrição DEVE ter um tamanho máximo
definido. O lançamento DEVE pertencer ao usuário que o criou, e a data DEVE vir preenchida com o dia
de hoje no formulário novo.

#### Cenário: Lançamento válido
- **QUANDO** o usuário envia tipo, valor maior que zero, data válida e descrição
- **ENTÃO** o lançamento é criado e pertence a ele
- **E** ele volta à listagem com uma mensagem de sucesso em português

#### Cenário: Valor no formato brasileiro
- **QUANDO** o usuário informa o valor como `1.234,56`, `1234,56` ou `1234.56`
- **ENTÃO** o lançamento é criado com o valor 1234,56

#### Cenário: Valor com separador de milhar ambíguo
- **QUANDO** o usuário informa um valor como `1.500` ou `0.001`, sem vírgula decimal
- **ENTÃO** nenhum lançamento é criado
- **E** o formulário exibe o erro de valor em português

#### Cenário: Valor zero ou negativo
- **QUANDO** o usuário envia valor 0 ou negativo
- **ENTÃO** nenhum lançamento é criado
- **E** o formulário exibe o erro de valor em português

#### Cenário: Valor com casas decimais demais ou não numérico
- **QUANDO** o usuário envia valor com mais de duas casas decimais ou que não é número
- **ENTÃO** nenhum lançamento é criado
- **E** o formulário exibe o erro de valor em português

#### Cenário: Data inválida
- **QUANDO** o usuário envia uma data inexistente (como 31/02) ou em formato irreconhecível
- **ENTÃO** nenhum lançamento é criado
- **E** o formulário exibe o erro de data em português

#### Cenário: Campo obrigatório ausente
- **QUANDO** o usuário envia o formulário sem tipo, valor, data ou descrição
- **ENTÃO** nenhum lançamento é criado
- **E** cada campo faltante exibe o erro em português

#### Cenário: Escolha do tipo
- **QUANDO** o usuário abre o formulário de lançamento
- **ENTÃO** o tipo é oferecido como dois botões, Entrada e Despesa, sem nenhum deles pré-selecionado

#### Cenário: Tipo inválido
- **QUANDO** o envio traz um tipo diferente de entrada ou despesa
- **ENTÃO** nenhum lançamento é criado

### Requirement: Edição de lançamento
O usuário DEVE poder editar tipo, valor, data e descrição de um lançamento seu, com as mesmas
validações do registro. A edição NÃO DEVE mudar o dono do lançamento.

#### Cenário: Edição válida
- **QUANDO** o usuário altera os campos de um lançamento seu com valores válidos
- **ENTÃO** as alterações são salvas
- **E** ele volta à listagem com uma mensagem de sucesso

#### Cenário: Edição inválida
- **QUANDO** o usuário envia a edição com valor ou data inválidos
- **ENTÃO** o lançamento permanece como estava
- **E** o formulário exibe os erros em português

### Requirement: Exclusão com confirmação
A exclusão de um lançamento DEVE exigir confirmação: abrir a tela de exclusão NÃO DEVE excluir, e
somente o envio da confirmação, por requisição que altera estado e protegida contra CSRF, DEVE
removê-lo.

#### Cenário: Tela de confirmação
- **QUANDO** o usuário pede para excluir um lançamento seu
- **ENTÃO** a página mostra os dados do lançamento e pede confirmação
- **E** nada é excluído

#### Cenário: Confirmar
- **QUANDO** o usuário confirma a exclusão
- **ENTÃO** o lançamento é removido
- **E** ele volta à listagem com uma mensagem de sucesso

#### Cenário: Cancelar
- **QUANDO** o usuário desiste na tela de confirmação
- **ENTÃO** o lançamento permanece e ele volta à listagem

#### Cenário: Exclusão por GET
- **QUANDO** a URL de exclusão é acessada por GET
- **ENTÃO** o lançamento não é excluído

### Requirement: Listagem paginada
A listagem DEVE exibir os lançamentos do usuário ordenados por data decrescente, com desempate
estável (o mais recentemente criado primeiro), em páginas de tamanho fixo, com navegação entre elas.
Cada item DEVE mostrar tipo, valor, data e descrição, e o valor da despesa DEVE ser visualmente
distinto do da entrada. Sem lançamentos, a página DEVE exibir um estado vazio com o convite para
registrar o primeiro.

#### Cenário: Ordem
- **QUANDO** o usuário tem lançamentos com datas diferentes
- **ENTÃO** o de data mais recente aparece primeiro

#### Cenário: Paginação
- **QUANDO** o usuário tem mais lançamentos do que cabem em uma página
- **ENTÃO** a primeira página mostra o tamanho fixo de itens mais recentes
- **E** há navegação para as páginas seguintes, que continuam a ordem

#### Cenário: Navegação numerada
- **QUANDO** a listagem tem mais de uma página
- **ENTÃO** o rodapé mostra "Anterior", "Próxima" e os números das páginas, com a atual destacada
- **E** "Anterior" fica desabilitado na primeira página e "Próxima" na última

#### Cenário: Muitas páginas
- **QUANDO** há mais páginas do que cabem na navegação
- **ENTÃO** as páginas distantes da atual são resumidas por reticências, mantendo a primeira e a última

#### Cenário: Página inexistente
- **QUANDO** o usuário pede uma página que não existe
- **ENTÃO** a resposta é 404

#### Cenário: Estado vazio
- **QUANDO** o usuário não tem lançamentos
- **ENTÃO** a página informa que ainda não há lançamentos e oferece registrar o primeiro

### Requirement: Formulários em janela modal
Registrar, editar e excluir um lançamento DEVEM abrir numa janela modal sobre a listagem, sem sair
dela. Erros de validação DEVEM aparecer dentro da própria janela, que permanece aberta. As mesmas
rotas DEVEM continuar funcionando como páginas completas quando acessadas diretamente ou sem
JavaScript.

#### Cenário: Abrir o formulário em modal
- **QUANDO** o usuário clica em "Novo lançamento", "Editar" ou "Excluir" na listagem
- **ENTÃO** o formulário ou a confirmação abre em uma janela modal sobre a listagem

#### Cenário: Erro de validação na janela
- **QUANDO** o usuário envia o formulário da janela com valor inválido
- **ENTÃO** a janela continua aberta e exibe o erro em português
- **E** nenhum lançamento é criado ou alterado

#### Cenário: Sucesso a partir da janela
- **QUANDO** o usuário envia dados válidos, ou confirma a exclusão, pela janela
- **ENTÃO** a janela fecha e a listagem é exibida atualizada, com a mensagem de sucesso

#### Cenário: Fechar sem alterar
- **QUANDO** o usuário cancela, pressiona Esc ou clica fora da janela
- **ENTÃO** a janela fecha e nada é criado, alterado ou excluído

#### Cenário: Acesso direto à rota
- **QUANDO** o usuário abre diretamente a URL de criação, edição ou exclusão
- **ENTÃO** a tela completa é exibida, com o mesmo formulário e as mesmas validações

### Requirement: Isolamento entre usuários
Cada usuário DEVE ver, editar e excluir apenas os próprios lançamentos, e a listagem e os saldos
DEVEM considerar somente os dados dele. Acessar, editar ou excluir um lançamento de outro usuário
DEVE responder 404, indistinguível do de um lançamento inexistente, e NÃO DEVE alterar nem revelar
dados do lançamento alheio.

#### Cenário: Listagem isolada
- **QUANDO** dois usuários têm lançamentos
- **ENTÃO** a listagem de cada um contém somente os seus

#### Cenário: Edição de lançamento alheio
- **QUANDO** um usuário abre ou envia a edição de um lançamento de outro usuário
- **ENTÃO** a resposta é 404
- **E** o lançamento permanece inalterado

#### Cenário: Exclusão de lançamento alheio
- **QUANDO** um usuário abre ou confirma a exclusão de um lançamento de outro usuário
- **ENTÃO** a resposta é 404
- **E** o lançamento continua existindo

#### Cenário: Lançamento inexistente
- **QUANDO** um usuário acessa o identificador de um lançamento que não existe
- **ENTÃO** a resposta é 404, igual à do lançamento alheio

### Requirement: Telas protegidas por login
Todas as telas e ações de lançamentos DEVEM exigir sessão autenticada.

#### Cenário: Visitante anônimo
- **QUANDO** um visitante sem sessão acessa qualquer rota de lançamentos, por GET ou POST
- **ENTÃO** é redirecionado ao login
- **E** nenhum dado é criado, alterado ou exibido

### Requirement: Categoria do lançamento
Ao registrar ou editar uma **despesa**, o usuário DEVE escolher uma categoria, entre as padrão e as
próprias. A **entrada** NÃO DEVE ter categoria: o valor enviado para ela é ignorado e o lançamento é
salvo sem categoria. Uma categoria de outro usuário ou inexistente DEVE ser recusada. A listagem DEVE
exibir a categoria de cada despesa, com ícone, cor e nome. Os lançamentos anteriores à categorização DEVEM continuar válidos,
com as despesas em "Outros" e as entradas sem categoria.

#### Cenário: Despesa com categoria
- **QUANDO** o usuário registra uma despesa escolhendo "Alimentação"
- **ENTÃO** o lançamento é criado nessa categoria
- **E** a listagem exibe "Alimentação", com o ícone e a cor da categoria, na linha dele

#### Cenário: Despesa sem categoria
- **QUANDO** o usuário envia uma despesa sem categoria
- **ENTÃO** nenhum lançamento é criado
- **E** o formulário exibe o erro de categoria em português

#### Cenário: Entrada ignora a categoria
- **QUANDO** o usuário envia uma entrada, mesmo com uma categoria preenchida
- **ENTÃO** o lançamento é criado sem categoria

#### Cenário: Mudar o tipo na edição
- **QUANDO** o usuário edita uma despesa categorizada trocando o tipo para entrada
- **ENTÃO** a categoria é removida do lançamento
- **E** ao trocar uma entrada para despesa, a categoria passa a ser obrigatória

#### Cenário: Categoria de outro usuário
- **QUANDO** o envio traz o identificador da categoria personalizada de outro usuário
- **ENTÃO** nenhum lançamento é criado ou alterado
- **E** o formulário exibe o erro de categoria em português

#### Cenário: Trocar a categoria
- **QUANDO** o usuário edita uma despesa e escolhe outra categoria
- **ENTÃO** a alteração é salva e a listagem mostra a nova categoria

#### Cenário: Lançamentos anteriores
- **QUANDO** a migração da categorização roda sobre uma base com despesas e entradas existentes
- **ENTÃO** as despesas passam a estar em "Outros" e as entradas ficam sem categoria
- **E** nenhum lançamento é perdido nem tem valor, data ou descrição alterados

### Requirement: Seletor flutuante de categoria
Onde o usuário escolhe uma categoria (formulário de lançamento e filtro da listagem), a aplicação DEVE
oferecer um seletor flutuante que mostra cada opção com o ícone, a cor e o nome da categoria, além de
uma opção vazia ("Selecione…" no formulário, "Todas as categorias" no filtro). O seletor DEVE funcionar
pelo teclado (abrir, navegar pelas opções, escolher e fechar) e expor seus papéis a leitores de tela.
Sem JavaScript, a escolha DEVE continuar possível por um `<select>` nativo com os nomes das categorias.
O valor enviado DEVE ser o mesmo nos dois casos, e as opções DEVEM listar apenas as categorias que o
usuário pode escolher.

#### Cenário: Abrir e escolher
- **QUANDO** o usuário abre o seletor de categoria e escolhe "Transporte"
- **ENTÃO** o seletor passa a mostrar o ícone, a cor e o nome dessa categoria
- **E** o formulário envia o identificador dela

#### Cenário: Opções com ícone e cor
- **QUANDO** o seletor está aberto
- **ENTÃO** cada opção mostra o selo com o ícone e a cor da categoria, seguido do nome
- **E** a opção atual aparece marcada

#### Cenário: Teclado
- **QUANDO** o foco está no seletor e o usuário pressiona Seta para baixo, Enter ou Espaço
- **ENTÃO** a lista abre e ele navega com as setas, escolhe com Enter e fecha com Esc, sem usar o mouse

#### Cenário: Clique fora
- **QUANDO** o seletor está aberto e o usuário clica fora dele
- **ENTÃO** a lista fecha e a escolha anterior é mantida

#### Cenário: Sem JavaScript
- **QUANDO** a página é aberta sem JavaScript
- **ENTÃO** a categoria é escolhida por um `<select>` nativo que envia o mesmo valor

#### Cenário: Dentro do modal
- **QUANDO** o seletor é aberto dentro da janela modal de lançamento
- **ENTÃO** a lista aparece por inteiro, sem ser cortada pela janela

#### Cenário: Só categorias permitidas
- **QUANDO** o seletor é exibido
- **ENTÃO** ele lista as categorias padrão e as do próprio usuário, e nenhuma de outro usuário

### Requirement: Filtro da listagem por categoria
A listagem DEVE permitir filtrar os lançamentos por uma categoria, entre as disponíveis ao usuário, e
o filtro DEVE ser mantido ao navegar entre as páginas. O filtro NÃO DEVE incluir lançamentos de outro
usuário nem alterar o saldo atual, que continua sobre todos os lançamentos. Um filtro com categoria
inexistente, alheia ou malformada NÃO DEVE gerar erro nem revelar dados: a listagem é exibida sem
filtrar.

#### Cenário: Filtrar
- **QUANDO** o usuário escolhe a categoria "Lazer" no filtro
- **ENTÃO** a listagem mostra somente as despesas dele nessa categoria, na mesma ordem

#### Cenário: Paginação com filtro
- **QUANDO** a categoria filtrada tem mais lançamentos do que cabem em uma página
- **ENTÃO** os links de página mantêm o filtro e continuam a ordem

#### Cenário: Limpar o filtro
- **QUANDO** o usuário volta a "Todas as categorias"
- **ENTÃO** a listagem mostra todos os lançamentos dele

#### Cenário: Filtro vazio
- **QUANDO** a categoria filtrada não tem lançamentos do usuário
- **ENTÃO** a página informa que não há lançamentos nessa categoria, com a opção de limpar o filtro

#### Cenário: Saldo com filtro
- **QUANDO** o filtro está ativo
- **ENTÃO** o saldo atual exibido é o mesmo de sem filtro

#### Cenário: Filtro por categoria alheia
- **QUANDO** a URL traz o identificador da categoria personalizada de outro usuário, ou um valor que não é número
- **ENTÃO** a resposta é 200 com a listagem sem filtro, só com os lançamentos do próprio usuário
