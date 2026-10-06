# dashboard Specification

## Purpose
Define o painel inicial do usuário autenticado: um resumo de como está o saldo e gráficos de para
onde o dinheiro vai, calculados no servidor a partir dos lançamentos do próprio usuário.

## Requirements

### Requirement: Painel como página inicial
A rota `/` DEVE exibir o painel do usuário autenticado, renderizado no servidor dentro do layout
TailAdmin, com texto em português do Brasil. Visitante anônimo DEVE ser redirecionado ao login. A
barra lateral DEVE ter o item "Painel" como primeiro do menu, marcado como página atual quando o
painel está aberto.

#### Cenário: Usuário autenticado abre a página inicial
- **QUANDO** um usuário autenticado abre `/`
- **ENTÃO** a resposta é `200` com o painel, e não um redirecionamento
- **E** o item "Painel" da barra lateral está marcado como página atual

#### Cenário: Visitante anônimo
- **QUANDO** um visitante anônimo abre `/`
- **ENTÃO** é redirecionado ao login, preservando o destino

### Requirement: Saldo atual com mensagem de status
O painel DEVE exibir o saldo atual do usuário, calculado do mesmo modo que na listagem de
lançamentos (soma das entradas menos a soma das despesas de todos os lançamentos), acompanhado de
uma mensagem de status quando houver o que dizer. Saldo negativo DEVE ser exibido em vermelho com a
mensagem "Você está no vermelho, cuidado". Saldo positivo DEVE exibir uma mensagem motivacional
("Você está no verde. Continue assim!"), sem o destaque de alerta. Saldo zero NÃO DEVE exibir
mensagem de status.

#### Cenário: Saldo negativo
- **QUANDO** as despesas do usuário superam as entradas
- **ENTÃO** o saldo é exibido em vermelho, com sinal negativo
- **E** a mensagem "Você está no vermelho, cuidado" é exibida

#### Cenário: Saldo zero
- **QUANDO** o usuário tem lançamentos e o saldo é exatamente R$ 0,00
- **ENTÃO** o saldo é exibido sem destaque de alerta
- **E** nenhuma mensagem de status é exibida no cartão

#### Cenário: Saldo positivo
- **QUANDO** as entradas do usuário superam as despesas
- **ENTÃO** o saldo é exibido sem destaque de alerta
- **E** a mensagem "Você está no verde. Continue assim!" é exibida, sem a mensagem de saldo negativo

#### Cenário: Saldo igual ao da listagem
- **QUANDO** o usuário tem lançamentos distribuídos por vários meses
- **ENTÃO** o saldo do painel é igual ao saldo atual da listagem de lançamentos

#### Cenário: Reflexo imediato dos lançamentos
- **QUANDO** o usuário cria, edita ou exclui um lançamento e abre o painel em seguida
- **ENTÃO** o saldo, os cartões e os gráficos já refletem a alteração

### Requirement: Cartões do mês atual
O painel DEVE exibir, para o mês corrente, o total de entradas, o total de despesas e a taxa de
economia (entradas menos despesas, dividido pelas entradas, em porcentagem). Cada total DEVE
mostrar a variação percentual em relação ao mês anterior. Quando não houver base de comparação
(mês anterior com total zero) a variação NÃO DEVE ser exibida, e quando o mês não tiver entradas a
taxa de economia DEVE aparecer como indisponível, sem divisão por zero.

#### Cenário: Totais do mês
- **QUANDO** o usuário tem entradas e despesas no mês corrente
- **ENTÃO** os cartões exibem a soma das entradas e a soma das despesas desse mês
- **E** lançamentos de outros meses não entram nesses totais

#### Cenário: Variação sobre o mês anterior
- **QUANDO** o usuário gastou R$ 100,00 no mês anterior e R$ 150,00 no mês corrente
- **ENTÃO** o cartão de despesas exibe uma alta de 50%

#### Cenário: Mês anterior sem lançamentos
- **QUANDO** o mês anterior não tem entradas (ou despesas)
- **ENTÃO** o cartão correspondente não exibe variação percentual

#### Cenário: Mês sem entradas
- **QUANDO** o mês corrente tem despesas e nenhuma entrada
- **ENTÃO** a taxa de economia aparece como indisponível
- **E** a página responde normalmente

### Requirement: Gastos por categoria no mês
O painel DEVE exibir um gráfico de rosca com as despesas do mês corrente agrupadas por categoria,
usando a cor de cada categoria, acompanhado da lista de categorias com valor e percentual do
total. Entradas NÃO DEVEM entrar nesse gráfico. Quando o mês não tiver despesas, o painel DEVE
exibir uma mensagem no lugar do gráfico.

#### Cenário: Despesas agrupadas por categoria
- **QUANDO** o usuário tem despesas de categorias diferentes no mês corrente
- **ENTÃO** o gráfico tem uma fatia por categoria, com o valor somado das despesas dela
- **E** a soma das fatias é igual ao total de despesas do mês nos cartões

#### Cenário: Valores batem com a listagem
- **QUANDO** o usuário filtra a listagem de lançamentos por uma categoria
- **ENTÃO** a soma das despesas do mês corrente listadas é igual ao valor da fatia dessa categoria

#### Cenário: Mês sem despesas
- **QUANDO** o usuário só tem entradas no mês corrente, ou nenhum lançamento nele
- **ENTÃO** o cartão exibe uma mensagem de que não há gastos no mês
- **E** nenhum gráfico vazio ou quebrado é desenhado

### Requirement: Fluxo de caixa e evolução do saldo
O painel DEVE exibir um gráfico de colunas com o total de entradas e o de despesas de cada um dos
últimos 6 meses (o corrente e os 5 anteriores, em ordem cronológica) e um gráfico de área com o
saldo ao fim de cada um desses meses. O saldo de cada mês DEVE incluir todos os lançamentos
anteriores à janela, e não apenas os dos 6 meses. Meses sem lançamentos DEVEM aparecer com
entradas e despesas zero, e o saldo DEVE se manter. Os rótulos DEVEM estar em português.

#### Cenário: Seis meses com lacunas
- **QUANDO** o usuário só tem lançamentos em 2 dos últimos 6 meses
- **ENTÃO** os gráficos têm 6 pontos, e os meses sem lançamentos têm entradas e despesas zero
- **E** o saldo dos meses vazios repete o saldo do mês anterior

#### Cenário: Saldo acumulado
- **QUANDO** o usuário tem lançamentos anteriores aos últimos 6 meses
- **ENTÃO** o saldo do primeiro mês da janela já inclui esses lançamentos
- **E** o saldo do mês corrente é igual ao saldo atual do painel, quando não há lançamentos com data futura

#### Cenário: Lançamento futuro
- **QUANDO** o usuário tem um lançamento com data depois do fim do mês corrente
- **ENTÃO** ele não aparece nos gráficos de 6 meses

#### Cenário: Valores em reais
- **QUANDO** o usuário passa o ponteiro sobre uma coluna, fatia ou ponto
- **ENTÃO** o valor é exibido em reais no formato brasileiro (`R$ 1.234,56`)

### Requirement: Últimos lançamentos no painel
O painel DEVE listar os 5 lançamentos mais recentes do usuário (mesma ordem da listagem: data e
depois identificador, do mais novo ao mais antigo), com descrição, categoria, data, valor e tipo,
e um link para a listagem completa.

#### Cenário: Lista resumida
- **QUANDO** o usuário tem mais de 5 lançamentos
- **ENTÃO** o painel exibe apenas os 5 mais recentes
- **E** há um link para a listagem completa de lançamentos

### Requirement: Estado vazio
Quando o usuário não tiver nenhum lançamento, o painel DEVE exibir o saldo de R$ 0,00, uma mensagem
convidando a registrar o primeiro lançamento com um atalho para a tela de novo lançamento, e NÃO
DEVE desenhar gráficos.

#### Cenário: Conta nova
- **QUANDO** um usuário sem lançamentos abre o painel
- **ENTÃO** a resposta é `200` com a mensagem de estado vazio e o atalho para o novo lançamento
- **E** nenhum gráfico é inicializado e nenhum erro de JavaScript ocorre

### Requirement: Dados do painel isolados por usuário
Todo valor exibido no painel (saldo, cartões, gráficos e lista) DEVE ser calculado apenas com os
lançamentos do usuário logado. Dados de outros usuários NÃO DEVEM aparecer nem influenciar
totais, percentuais ou a lista. As categorias de outros usuários NÃO DEVEM aparecer nos gráficos.

#### Cenário: Dois usuários com lançamentos
- **QUANDO** dois usuários têm lançamentos diferentes e um deles abre o painel
- **ENTÃO** saldo, totais, fatias, colunas, pontos de saldo e lista vêm só dos lançamentos dele
- **E** o conteúdo da resposta não contém descrições nem categorias do outro usuário

### Requirement: Gráficos servidos localmente, com tema claro e escuro
Os gráficos DEVEM ser desenhados por uma biblioteca de código aberto servida pela própria aplicação (sem CDN), a partir
de dados calculados no servidor e embutidos na página. Os gráficos DEVEM acompanhar o tema claro ou
escuro escolhido pelo usuário, inclusive ao alternar o tema com a página aberta. Se o script dos
gráficos não carregar, a página DEVE continuar mostrando saldo, cartões e lista.

#### Cenário: Alternar o tema
- **QUANDO** o usuário alterna entre tema claro e escuro com o painel aberto
- **ENTÃO** os gráficos passam a usar as cores do novo tema sem recarregar a página

#### Cenário: Sem CDN
- **QUANDO** o painel é carregado
- **ENTÃO** nenhum script é requisitado de domínio externo
