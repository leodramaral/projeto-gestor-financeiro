# Spec Delta

## ADDED Requirements

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
