# categories Specification

## Purpose
Permite classificar as despesas do usuário em categorias, padrão do sistema ou criadas por ele, para
que ele entenda em que gasta o dinheiro.

## Requirements

### Requirement: Categorias padrão
O sistema DEVE oferecer a todos os usuários as categorias padrão Alimentação, Transporte, Moradia,
Lazer, Saúde e Outros, cada uma com ícone e cor definidos. O usuário NÃO DEVE poder editar nem excluir
uma categoria padrão.

#### Cenário: Todos veem as padrão
- **QUANDO** um usuário, inclusive recém-cadastrado, abre a lista de categorias
- **ENTÃO** as seis categorias padrão aparecem, marcadas como padrão
- **E** cada uma exibe seu ícone e sua cor (Alimentação utensílios Laranja, Transporte carro Azul, Moradia casa Jade, Lazer controle Roxo, Saúde pílula Rosa, Outros caixa Grafite)

#### Cenário: Edição de categoria padrão
- **QUANDO** um usuário tenta editar ou excluir uma categoria padrão, por GET ou POST
- **ENTÃO** a resposta é 404
- **E** a categoria permanece inalterada

### Requirement: Categorias personalizadas
O usuário autenticado DEVE poder criar, renomear e excluir categorias personalizadas, que pertencem a
ele. O nome é obrigatório, com tamanho máximo definido, sem espaços nas pontas, e DEVE ser único para
o usuário sem diferenciar maiúsculas de minúsculas, nem repetir o nome de uma categoria padrão. Dois
usuários diferentes PODEM ter categorias personalizadas com o mesmo nome.

#### Cenário: Criar categoria
- **QUANDO** o usuário envia o nome "Pets", ainda inexistente para ele
- **ENTÃO** a categoria é criada e pertence a ele
- **E** ele volta à lista de categorias com uma mensagem de sucesso em português

#### Cenário: Nome repetido
- **QUANDO** o usuário envia "pets" já tendo "Pets"
- **ENTÃO** nenhuma categoria é criada
- **E** o formulário exibe o erro de nome em português

#### Cenário: Nome igual ao de uma padrão
- **QUANDO** o usuário envia "alimentação"
- **ENTÃO** nenhuma categoria é criada
- **E** o formulário exibe o erro de nome em português

#### Cenário: Nome vazio ou longo demais
- **QUANDO** o usuário envia nome vazio, só com espaços ou acima do tamanho máximo
- **ENTÃO** nenhuma categoria é criada
- **E** o formulário exibe o erro de nome em português

#### Cenário: Mesmo nome em outro usuário
- **QUANDO** outro usuário já tem uma categoria "Pets" e este cria "Pets"
- **ENTÃO** a categoria é criada

#### Cenário: Renomear
- **QUANDO** o usuário renomeia uma categoria sua para um nome válido
- **ENTÃO** o novo nome vale também nos lançamentos que já a usam

### Requirement: Ícone e cor da categoria
Toda categoria DEVE ter um ícone e uma cor, escolhidos pelo usuário entre listas fixas: 20 ícones de
linha (utensílios, carro, casa, controle de videogame, pílula, caixa, carrinho de compras, capelo de
formatura, camiseta, pata, mala, presente, lâmpada, celular, cartão, xícara de café, haltere, claquete,
bebê e recibo) e 8 cores (Jade, Verde, Azul, Roxo, Rosa, Laranja, Âmbar e Grafite). O formulário DEVE
abrir já com um valor inicial (caixa e Grafite). Ícone ou cor fora das listas DEVEM ser recusados. A
categoria DEVE aparecer com ícone, cor e nome, de modo que a cor nunca seja a única forma de
identificá-la, e o texto e o ícone sobre a cor DEVEM manter contraste mínimo de 4,5:1 nos modos claro
e escuro. O ícone DEVE ser desenhado como imagem decorativa, ocultada de leitores de tela, porque o nome
da categoria sempre o acompanha.

#### Cenário: Escolher ícone e cor
- **QUANDO** o usuário cria a categoria "Pets" com o ícone de pata e a cor Âmbar
- **ENTÃO** a categoria é criada com esse ícone e essa cor
- **E** a lista de categorias a exibe com o ícone, a cor e o nome

#### Cenário: Valores iniciais
- **QUANDO** o usuário abre o formulário de nova categoria
- **ENTÃO** o ícone de caixa e a cor Grafite já vêm selecionados

#### Cenário: Ícone fora da lista
- **QUANDO** o envio traz um ícone que não está entre os 20 (por exemplo `rocket`) ou um emoji no lugar da chave
- **ENTÃO** nenhuma categoria é criada ou alterada
- **E** o formulário exibe o erro de ícone em português

#### Cenário: Cor fora da lista
- **QUANDO** o envio traz uma cor que não está entre as 8 (por exemplo `red` ou `#ff0000`)
- **ENTÃO** nenhuma categoria é criada ou alterada
- **E** o formulário exibe o erro de cor em português

#### Cenário: Trocar ícone e cor
- **QUANDO** o usuário altera o ícone e a cor de uma categoria sua
- **ENTÃO** a mudança vale também nos lançamentos que já a usam

### Requirement: Isolamento das categorias
Cada usuário DEVE ver, escolher, editar e excluir apenas as próprias categorias personalizadas, além de
ver e escolher as padrão. Acessar, editar ou excluir a categoria personalizada de outro usuário, ou
uma inexistente, DEVE responder 404, sem alterar nem revelar dados dela.

#### Cenário: Lista isolada
- **QUANDO** dois usuários têm categorias personalizadas
- **ENTÃO** a lista de cada um contém as padrão e somente as suas

#### Cenário: Categoria alheia
- **QUANDO** um usuário abre ou envia a edição ou a exclusão da categoria de outro usuário
- **ENTÃO** a resposta é 404, igual à de uma categoria inexistente
- **E** a categoria permanece inalterada

### Requirement: Exclusão de categoria em uso
A exclusão de uma categoria personalizada DEVE exigir confirmação por requisição que altera estado e
protegida contra CSRF, e NÃO DEVE apagar lançamentos: os lançamentos que a usam DEVEM passar para a
categoria padrão "Outros". A tela de confirmação DEVE informar quantos lançamentos serão movidos.

#### Cenário: Confirmação
- **QUANDO** o usuário pede para excluir uma categoria sua
- **ENTÃO** a página pede confirmação e informa quantos lançamentos usam a categoria
- **E** nada é excluído

#### Cenário: Categoria em uso
- **QUANDO** o usuário confirma a exclusão de uma categoria usada por 3 despesas
- **ENTÃO** a categoria é removida
- **E** as 3 despesas continuam existindo, agora em "Outros"

#### Cenário: Categoria sem uso
- **QUANDO** o usuário confirma a exclusão de uma categoria sem lançamentos
- **ENTÃO** a categoria é removida e ele volta à lista com uma mensagem de sucesso

#### Cenário: Exclusão por GET
- **QUANDO** a URL de exclusão é acessada por GET
- **ENTÃO** a categoria não é excluída

### Requirement: Telas de categorias protegidas por login
Todas as telas e ações de categorias DEVEM exigir sessão autenticada.

#### Cenário: Visitante anônimo
- **QUANDO** um visitante sem sessão acessa qualquer rota de categorias, por GET ou POST
- **ENTÃO** é redirecionado ao login
- **E** nenhum dado é criado, alterado ou exibido
