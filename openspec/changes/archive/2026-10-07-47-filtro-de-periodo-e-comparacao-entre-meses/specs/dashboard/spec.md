# Delta: dashboard

## ADDED Requirements

### Requirement: Seleção do mês
O painel DEVE mostrar sempre um único mês calendário, e esse mês DEVE valer para todos os valores
e gráficos de todas as abas. O padrão, sem parâmetro, é o mês atual. O usuário DEVE poder navegar
para o mês anterior e para o seguinte, e o mês escolhido DEVE ficar na URL (`month=AAAA-MM`), de
modo que recarregar a página ou trocar de aba o preserve. A navegação NÃO DEVE avançar além do mês
atual nem recuar além do mês do primeiro lançamento do usuário, e os controles correspondentes
DEVEM aparecer desativados nesses limites. Mês ausente, mal formado ou inexistente NÃO DEVE gerar
erro: o painel DEVE usar o mês atual. Mês fora dos limites DEVE ser ajustado ao limite mais
próximo. O mês exibido DEVE estar escrito por extenso, em português, junto com o intervalo de
datas.

#### Cenário: Sem parâmetro
- **QUANDO** o usuário abre o painel sem escolher mês
- **ENTÃO** o mês exibido é o mês atual

#### Cenário: Navegar para o mês anterior
- **QUANDO** o usuário aciona "mês anterior" estando em outubro de 2026
- **ENTÃO** o painel exibe setembro de 2026, com a URL em `month=2026-09`
- **E** todos os valores e gráficos passam a ser de setembro

#### Cenário: Limite superior
- **QUANDO** o mês exibido é o mês atual
- **ENTÃO** o controle de mês seguinte está desativado
- **E** abrir `month` com um mês futuro exibe o mês atual

#### Cenário: Limite inferior
- **QUANDO** o primeiro lançamento do usuário é de julho de 2026 e o painel está em julho
- **ENTÃO** o controle de mês anterior está desativado
- **E** abrir `month=2026-03` exibe julho de 2026

#### Cenário: Mês inválido
- **QUANDO** o endereço traz `month=2026-13`, `month=abc` ou `month=` vazio
- **ENTÃO** a resposta é `200` com o mês atual

#### Cenário: Mês preservado entre abas
- **QUANDO** o usuário está em setembro e troca de aba
- **ENTÃO** a nova aba também exibe setembro

#### Cenário: Mês sem lançamentos
- **QUANDO** o usuário tem lançamentos em outros meses, mas nenhum no mês exibido
- **ENTÃO** os cartões mostram R$ 0,00, com o saldo final igual ao saldo inicial
- **E** os blocos de lista e de categorias exibem uma mensagem de que não há lançamentos ou gastos no mês

### Requirement: Abas do painel
O painel DEVE ser dividido em quatro abas, cada uma com rota própria renderizada no servidor: Visão
geral, Categorias, Fluxo e saldo e Lançamentos. A Visão geral DEVE ser a rota `/` e reunir os
cartões, o fluxo de caixa, a evolução do saldo, os gastos por categoria e os últimos lançamentos,
cada bloco com um atalho "Ver detalhes" para a aba do segmento. Os links das abas e dos atalhos
DEVEM carregar o mês exibido. A aba atual DEVE estar marcada como selecionada. Todas as abas
DEVEM exigir login, e um visitante anônimo DEVE ser redirecionado ao login.

#### Cenário: Trocar de aba
- **QUANDO** o usuário está na Visão geral de setembro e abre a aba Categorias
- **ENTÃO** a aba Categorias exibe as despesas de setembro
- **E** a aba Categorias está marcada como selecionada

#### Cenário: Atalho "Ver detalhes"
- **QUANDO** o usuário aciona "Ver detalhes" no bloco de gastos por categoria
- **ENTÃO** abre a aba Categorias, no mesmo mês

#### Cenário: Aba Categorias
- **QUANDO** o usuário abre a aba Categorias
- **ENTÃO** vê a rosca e uma tabela com todas as categorias com despesa no mês, com valor, percentual do total e uma linha de total
- **E** as categorias NÃO são agrupadas em "Outras"

#### Cenário: Aba Fluxo e saldo
- **QUANDO** o usuário abre a aba Fluxo e saldo
- **ENTÃO** vê o resumo do mês (saldo inicial e final) e os gráficos de entradas e despesas por dia e de saldo por dia

#### Cenário: Aba Lançamentos
- **QUANDO** o usuário abre a aba Lançamentos
- **ENTÃO** vê todos os lançamentos do mês, do mais novo ao mais antigo, com data, descrição, categoria e valor
- **E** há um link para a listagem completa de lançamentos

#### Cenário: Visitante anônimo
- **QUANDO** um visitante anônimo abre qualquer aba do painel
- **ENTÃO** é redirecionado ao login, preservando o destino

### Requirement: Saldo inicial e final do mês
O painel DEVE exibir o saldo inicial do mês (soma das entradas menos a soma das despesas de todos
os lançamentos com data anterior ao primeiro dia do mês) e o saldo final (saldo inicial mais as
entradas do mês menos as despesas do mês). O saldo final DEVE vir acompanhado de uma mensagem de
status quando houver o que dizer: saldo negativo DEVE ser exibido em vermelho, com sinal negativo,
e a mensagem "Você está no vermelho, cuidado"; saldo positivo DEVE exibir a mensagem "Você está no
verde. Continue assim!", sem destaque de alerta; saldo zero NÃO DEVE exibir mensagem. A mensagem
DEVE refletir o saldo final do mês exibido, e não o saldo de hoje. Lançamentos com data posterior
a hoje, mas dentro do mês exibido, DEVEM entrar no saldo final.

#### Cenário: Saldo inicial
- **QUANDO** o usuário tem lançamentos em meses anteriores ao exibido
- **ENTÃO** o saldo inicial é a soma das entradas menos as despesas desses lançamentos
- **E** lançamentos do próprio mês e posteriores a ele não entram

#### Cenário: Saldo final
- **QUANDO** o usuário tem entradas e despesas no mês exibido
- **ENTÃO** o saldo final é igual ao saldo inicial mais as entradas menos as despesas do mês

#### Cenário: Saldo negativo
- **QUANDO** o saldo final é menor que zero
- **ENTÃO** é exibido em vermelho, com sinal negativo
- **E** a mensagem "Você está no vermelho, cuidado" é exibida

#### Cenário: Saldo zero
- **QUANDO** o saldo final é exatamente R$ 0,00
- **ENTÃO** é exibido sem destaque de alerta
- **E** nenhuma mensagem de status é exibida

#### Cenário: Saldo positivo
- **QUANDO** o saldo final é maior que zero
- **ENTÃO** é exibido sem destaque de alerta
- **E** a mensagem "Você está no verde. Continue assim!" é exibida, sem a mensagem de saldo negativo

#### Cenário: Mensagem acompanha o mês
- **QUANDO** o usuário navega para um mês em que o saldo final tem sinal diferente do mês atual
- **ENTÃO** a mensagem exibida corresponde ao saldo final do mês navegado

#### Cenário: Saldo igual ao da listagem
- **QUANDO** o usuário não tem lançamentos com data depois do fim do mês exibido
- **ENTÃO** o saldo final é igual ao saldo atual da listagem de lançamentos

#### Cenário: Encadeamento entre meses
- **QUANDO** o usuário compara dois meses seguidos
- **ENTÃO** o saldo inicial de um é igual ao saldo final do anterior

#### Cenário: Reflexo imediato dos lançamentos
- **QUANDO** o usuário cria, edita ou exclui um lançamento e abre o painel em seguida
- **ENTÃO** os cartões, os gráficos e as listas já refletem a alteração

### Requirement: Cartões do mês
O painel DEVE exibir, para o mês exibido, o total de entradas, o total de despesas e a taxa de
economia (entradas menos despesas, dividido pelas entradas, em porcentagem). As entradas e as
despesas DEVEM mostrar a variação percentual em relação ao mês anterior ao exibido, e o nome desse
mês DEVE aparecer junto da variação. Alta de despesa DEVE ser sinalizada como negativa e queda
como positiva; para as entradas, o contrário. Quando não houver base de comparação (mês anterior
com total zero) a variação DEVE aparecer como "sem base", e quando o mês não tiver entradas a taxa
de economia DEVE aparecer como indisponível, sem divisão por zero.

#### Cenário: Totais do mês
- **QUANDO** o usuário tem entradas e despesas no mês exibido
- **ENTÃO** os cartões exibem a soma das entradas e a soma das despesas desse mês
- **E** lançamentos de outros meses não entram nesses totais

#### Cenário: Variação sobre o mês anterior
- **QUANDO** o usuário gastou R$ 100,00 no mês anterior e R$ 150,00 no mês exibido
- **ENTÃO** o cartão de despesas exibe uma alta de 50%, sinalizada como negativa

#### Cenário: Mês anterior sem lançamentos
- **QUANDO** o mês anterior não tem entradas (ou despesas)
- **ENTÃO** o cartão correspondente exibe "sem base" no lugar da variação

#### Cenário: Mês sem entradas
- **QUANDO** o mês exibido tem despesas e nenhuma entrada
- **ENTÃO** a taxa de economia aparece como indisponível
- **E** a página responde normalmente

### Requirement: Explicação do cálculo nos cartões
Cada cartão (saldo inicial, entradas, despesas, saldo final e taxa de economia) DEVE ter um
controle de ajuda "i" que exibe como o número é calculado, com os valores reais do mês exibido. A
explicação DEVE abrir ao passar o ponteiro, ao receber o foco do teclado e ao clicar ou tocar no
controle, e DEVE fechar ao sair do controle, ao clicar fora ou ao pressionar Esc. O controle DEVE
ter nome acessível ("Como é calculado: <cartão>") e estar associado ao texto por
`aria-describedby`, com o texto em `role="tooltip"`.

#### Cenário: Explicação ao passar o ponteiro
- **QUANDO** o usuário passa o ponteiro sobre o controle de ajuda do cartão de despesas
- **ENTÃO** é exibido o texto que diz que a soma é dos lançamentos do tipo despesa do mês
- **E** a fórmula da variação aparece com os valores do mês e do mês anterior

#### Cenário: Explicação por teclado
- **QUANDO** o usuário foca o controle de ajuda de um cartão com a tecla Tab
- **ENTÃO** a mesma explicação é exibida
- **E** pressionar Esc a fecha

#### Cenário: Explicação por toque
- **QUANDO** o usuário toca no controle de ajuda num dispositivo sem ponteiro
- **ENTÃO** a explicação é exibida e permanece até tocar fora

#### Cenário: Taxa de economia indisponível
- **QUANDO** o mês não tem entradas
- **ENTÃO** a explicação da taxa de economia informa que, sem entradas, o valor fica indisponível

### Requirement: Fluxo diário e evolução do saldo do mês
O painel DEVE exibir um gráfico de colunas com o total de entradas e o de despesas de cada dia do
mês exibido, e um gráfico de área com o saldo ao fim de cada dia, ambos do primeiro ao último dia
do mês, inclusive dias com data futura. Dias sem lançamentos DEVEM aparecer com entradas e
despesas zero, e o saldo DEVE se manter. O saldo do primeiro dia DEVE partir do saldo inicial do
mês, e o do último dia DEVE ser igual ao saldo final. Os valores DEVEM aparecer em reais no
formato brasileiro ao passar o ponteiro, e os rótulos DEVEM estar em português.

#### Cenário: Todos os dias do mês
- **QUANDO** o mês exibido é setembro, com 30 dias, e o usuário só tem lançamentos em 3 deles
- **ENTÃO** os gráficos têm 30 pontos, e os dias sem lançamentos têm entradas e despesas zero
- **E** o saldo dos dias vazios repete o saldo do dia anterior

#### Cenário: Fecha com os cartões
- **QUANDO** o usuário abre qualquer mês com lançamentos
- **ENTÃO** a soma das colunas de entradas e a de despesas são iguais aos totais dos cartões
- **E** o último ponto do saldo é igual ao saldo final

#### Cenário: Lançamento futuro dentro do mês
- **QUANDO** o usuário tem um lançamento com data depois de hoje, mas dentro do mês exibido
- **ENTÃO** ele aparece no dia correspondente e entra no saldo final

#### Cenário: Valores em reais
- **QUANDO** o usuário passa o ponteiro sobre uma coluna ou ponto
- **ENTÃO** o valor é exibido em reais no formato brasileiro (`R$ 1.234,56`)

## MODIFIED Requirements

### Requirement: Painel como página inicial
A rota `/` DEVE exibir a Visão geral do painel do usuário autenticado, referente ao mês atual ou
ao mês escolhido, renderizada no servidor dentro do layout TailAdmin, com texto em português do
Brasil. Visitante anônimo DEVE ser redirecionado ao login. A barra lateral DEVE ter o item
"Painel" como primeiro do menu, marcado como página atual quando qualquer aba do painel está
aberta.

#### Cenário: Usuário autenticado abre a página inicial
- **QUANDO** um usuário autenticado abre `/`
- **ENTÃO** a resposta é `200` com a Visão geral do mês atual, e não um redirecionamento
- **E** o item "Painel" da barra lateral está marcado como página atual

#### Cenário: Visitante anônimo
- **QUANDO** um visitante anônimo abre `/`
- **ENTÃO** é redirecionado ao login, preservando o destino

### Requirement: Gastos por categoria no mês
O painel DEVE exibir um gráfico de rosca com as despesas do mês exibido agrupadas por categoria,
usando a cor de cada categoria, acompanhado da lista de categorias com valor e percentual do
total. Na Visão geral, a lista DEVE mostrar as 5 maiores categorias e agrupar as demais em
"Outras"; a aba Categorias DEVE listar todas. Entradas NÃO DEVEM entrar nesse gráfico. Quando o
mês não tiver despesas, o painel DEVE exibir uma mensagem no lugar do gráfico.

#### Cenário: Despesas agrupadas por categoria
- **QUANDO** o usuário tem despesas de categorias diferentes no mês exibido
- **ENTÃO** o gráfico tem uma fatia por categoria, com o valor somado das despesas dela
- **E** a soma das fatias é igual ao total de despesas do mês nos cartões

#### Cenário: Valores batem com a listagem
- **QUANDO** o usuário filtra a listagem de lançamentos por uma categoria
- **ENTÃO** a soma das despesas do mês exibido listadas é igual ao valor da fatia dessa categoria

#### Cenário: Mês sem despesas
- **QUANDO** o usuário só tem entradas no mês exibido, ou nenhum lançamento nele
- **ENTÃO** o cartão exibe uma mensagem de que não há gastos no mês
- **E** nenhum gráfico vazio ou quebrado é desenhado

#### Cenário: Muitas categorias na Visão geral
- **QUANDO** o usuário tem despesas em mais de 5 categorias no mês
- **ENTÃO** a Visão geral mostra as 5 maiores e uma fatia "Outras" com a soma das demais
- **E** a aba Categorias mostra todas, sem "Outras"

### Requirement: Últimos lançamentos no painel
A Visão geral DEVE listar os 5 lançamentos mais recentes do mês exibido (mesma ordem da listagem:
data e depois identificador, do mais novo ao mais antigo), com descrição, categoria, data, valor e
tipo, e um atalho "Ver detalhes" para a aba Lançamentos, do mesmo mês.

#### Cenário: Lista resumida
- **QUANDO** o usuário tem mais de 5 lançamentos no mês exibido
- **ENTÃO** a Visão geral exibe apenas os 5 mais recentes desse mês
- **E** há um atalho para a aba Lançamentos, que lista todos

## REMOVED Requirements

### Requirement: Saldo atual com mensagem de status
**Reason**: O saldo único deu lugar ao saldo inicial e final de cada mês, que explicam o número na tela.
**Migration**: Ver "Saldo inicial e final do mês". As mensagens de status continuam, agora sobre o saldo final do mês exibido.

### Requirement: Cartões do mês atual
**Reason**: Os cartões eram fixos no mês corrente; passam a seguir o mês escolhido.
**Migration**: Ver "Cartões do mês" e "Explicação do cálculo nos cartões".

### Requirement: Fluxo de caixa e evolução do saldo
**Reason**: A janela fixa dos últimos 6 meses deixa de existir; os gráficos passam a mostrar os dias do mês escolhido.
**Migration**: Ver "Fluxo diário e evolução do saldo do mês".
