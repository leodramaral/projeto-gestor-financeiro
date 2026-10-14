# dashboard Specification

## Purpose
Define o painel inicial do usuário autenticado: um resumo de como está o saldo e gráficos de para
onde o dinheiro vai, calculados no servidor a partir dos lançamentos do próprio usuário.

## Requirements

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

### Requirement: Seleção do mês
O painel DEVE mostrar sempre um único mês calendário, e esse mês DEVE valer para todos os valores
e gráficos de todas as abas. O padrão, sem parâmetro, é o mês atual. O usuário DEVE poder navegar
para o mês anterior e para o seguinte e DEVE poder escolher o mês direto num campo de seleção, que
lista os meses do mês do primeiro lançamento do usuário até o mês atual, escritos por extenso, em
português. O atalho "Este mês" DEVE estar sempre presente, ativo quando o mês exibido não é o atual e desativado nele, como o controle de mês seguinte, para o layout do seletor não mudar. O mês escolhido
DEVE ficar na URL (`month=AAAA-MM`), de modo que recarregar a página ou trocar de aba o preserve.
A navegação NÃO DEVE avançar além do mês atual nem recuar além do mês do primeiro lançamento do
usuário, e os controles correspondentes DEVEM aparecer desativados nesses limites. Os controles do
mês (setas, campo e atalho) DEVEM ter área de toque de pelo menos 44 px. Mês ausente, mal formado
ou inexistente NÃO DEVE gerar erro: o painel DEVE usar o mês atual. Mês fora dos limites DEVE ser
ajustado ao limite mais próximo. O mês exibido DEVE estar escrito por extenso, em português, junto
com o intervalo de datas.

#### Cenário: Sem parâmetro
- **QUANDO** o usuário abre o painel sem escolher mês
- **ENTÃO** o mês exibido é o mês atual

#### Cenário: Navegar para o mês anterior
- **QUANDO** o usuário aciona "mês anterior" estando em outubro de 2026
- **ENTÃO** o painel exibe setembro de 2026, com a URL em `month=2026-09`
- **E** todos os valores e gráficos passam a ser de setembro

#### Cenário: Escolher o mês no campo
- **QUANDO** o primeiro lançamento do usuário é de julho de 2026, o mês atual é outubro de 2026 e o usuário escolhe "Agosto de 2026" no campo
- **ENTÃO** o painel exibe agosto de 2026, com a URL em `month=2026-08`
- **E** o campo lista julho, agosto, setembro e outubro de 2026, e só esses

#### Cenário: Atalho para o mês atual
- **QUANDO** o painel está em setembro de 2026 e o mês atual é outubro de 2026
- **ENTÃO** há um atalho "Este mês" ativo que abre outubro de 2026
- **E** quando o mês exibido é o atual o atalho continua no mesmo lugar, desativado

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
Cada indicador do painel (saldo inicial, entradas, despesas, saldo final e taxa de economia) DEVE
ter um controle de ajuda "i" que exibe como o número é calculado, com os valores reais do mês
exibido. O "i" do saldo final fica junto do rótulo do bloco de destaque, e o do saldo inicial,
junto do saldo inicial dentro do bloco. A explicação DEVE abrir ao passar o ponteiro, ao receber o
foco do teclado e ao clicar ou tocar no controle, e DEVE fechar ao sair do controle, ao clicar
fora ou ao pressionar Esc. O controle DEVE ter nome acessível ("Como é calculado: <indicador>") e
estar associado ao texto por `aria-describedby`, com o texto em `role="tooltip"`.

#### Cenário: Explicação ao passar o ponteiro
- **QUANDO** o usuário passa o ponteiro sobre o controle de ajuda do indicador de despesas
- **ENTÃO** é exibido o texto que diz que a soma é dos lançamentos do tipo despesa do mês
- **E** a fórmula da variação aparece com os valores do mês e do mês anterior

#### Cenário: Explicação por teclado
- **QUANDO** o usuário foca o controle de ajuda de um indicador com a tecla Tab
- **ENTÃO** a mesma explicação é exibida
- **E** pressionar Esc a fecha

#### Cenário: Explicação por toque
- **QUANDO** o usuário toca no controle de ajuda num dispositivo sem ponteiro
- **ENTÃO** a explicação é exibida e permanece até tocar fora

#### Cenário: Taxa de economia indisponível
- **QUANDO** o mês não tem entradas
- **ENTÃO** a explicação da taxa de economia informa que, sem entradas, o valor fica indisponível

#### Cenário: Saldo inicial dentro do bloco de destaque
- **QUANDO** o usuário foca o controle de ajuda do saldo inicial, no bloco de destaque
- **ENTÃO** é exibido que o saldo inicial é a soma das entradas menos as despesas anteriores ao primeiro dia do mês

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

### Requirement: Saldo final em destaque
A Visão geral DEVE abrir com um bloco de destaque que mostra o saldo final do mês exibido como o
maior número da tela, a mensagem de status do saldo (conforme "Saldo inicial e final do mês"), o
saldo inicial do mês e a linha do saldo ao fim de cada dia do mês. Saldo negativo DEVE continuar em
vermelho, com sinal negativo, também dentro do bloco. Quando o saldo ficou negativo em algum dia do
mês, o menor saldo DEVE ser marcado na linha, com o valor e o dia. O bloco DEVE mostrar o saldo
final e o saldo inicial mesmo sem a linha, para a página continuar legível se o script dos gráficos
não carregar. A linha DEVE ter um texto alternativo com o menor saldo e o saldo final.

#### Cenário: Saldo final como número principal
- **QUANDO** o usuário abre a Visão geral de um mês com lançamentos
- **ENTÃO** o saldo final aparece no bloco de destaque, em tamanho maior que o de qualquer outro valor da página
- **E** o bloco mostra a mensagem de status do saldo final e o saldo inicial do mês

#### Cenário: Saldo final negativo no bloco
- **QUANDO** o saldo final do mês é menor que zero
- **ENTÃO** o bloco exibe o valor em vermelho, com sinal negativo, e a mensagem "Você está no vermelho, cuidado"

#### Cenário: Menor saldo marcado
- **QUANDO** o saldo ao fim de algum dia do mês é negativo
- **ENTÃO** a linha do bloco marca o dia de menor saldo e informa o valor e a data dele

#### Cenário: Saldo sempre positivo
- **QUANDO** o saldo ao fim de todos os dias do mês é maior ou igual a zero
- **ENTÃO** a linha do bloco é exibida sem marca de menor saldo

#### Cenário: Sem o script dos gráficos
- **QUANDO** o script dos gráficos não carrega
- **ENTÃO** o bloco continua mostrando o saldo final, a mensagem de status e o saldo inicial

### Requirement: Frase da taxa de economia
O indicador de taxa de economia DEVE vir com uma frase em linguagem simples: quando a taxa é maior
ou igual a zero, "Sobrou X% de tudo o que entrou neste mês"; quando é negativa, "Gastou X% a mais
do que entrou neste mês", com X sem sinal. Quando o mês não tem entradas, DEVE continuar valendo a
indisponibilidade da taxa, com a frase "Sem entradas neste mês".

#### Cenário: Taxa positiva
- **QUANDO** o usuário entrou com R$ 1.000,00 e gastou R$ 754,00 no mês exibido
- **ENTÃO** o indicador mostra 24,6% e a frase "Sobrou 24,6% de tudo o que entrou neste mês"

#### Cenário: Taxa negativa
- **QUANDO** o usuário entrou com R$ 1.000,00 e gastou R$ 1.100,00 no mês exibido
- **ENTÃO** o indicador mostra −10,0% e a frase "Gastou 10,0% a mais do que entrou neste mês"

#### Cenário: Mês sem entradas
- **QUANDO** o mês exibido não tem entradas
- **ENTÃO** a taxa aparece como indisponível, com a frase "Sem entradas neste mês"

### Requirement: Fluxo de caixa por semana
O gráfico de fluxo de caixa DEVE oferecer o seletor "Dias | Semanas". Em "Semanas", as entradas e as
despesas DEVEM ser somadas em blocos de 7 dias a partir do dia 1 (1–7, 8–14, 15–21 e 22–28), e o
último bloco DEVE reunir os dias restantes do mês (29 até o fim, quando o mês tem mais de 28
dias). Cada bloco DEVE ser rotulado com "Sem N" e o intervalo de dias. A soma dos blocos DEVE ser
igual aos totais do mês nos indicadores. Em tela estreita (menos de 640 px) o gráfico DEVE abrir em
"Semanas", e nas demais em "Dias". O usuário DEVE poder alternar a visão, e a escolha NÃO precisa
ser guardada entre páginas. Alternar o tema com a página aberta DEVE manter a visão escolhida.

#### Cenário: Semanas somam o mês
- **QUANDO** o usuário escolhe "Semanas" em um mês de 31 dias
- **ENTÃO** o gráfico tem 5 blocos, o último com os dias 29 a 31
- **E** a soma das entradas dos blocos e a das despesas são iguais aos totais do mês

#### Cenário: Fevereiro de 28 dias
- **QUANDO** o mês exibido tem 28 dias e o usuário escolhe "Semanas"
- **ENTÃO** o gráfico tem 4 blocos de 7 dias, sem quinto bloco

#### Cenário: Abertura no celular
- **QUANDO** o painel é aberto em tela com menos de 640 px
- **ENTÃO** o fluxo de caixa abre em "Semanas"
- **E** em tela mais larga abre em "Dias"

#### Cenário: Alternar a visão
- **QUANDO** o usuário aciona "Dias" estando em "Semanas"
- **ENTÃO** o gráfico volta a mostrar uma coluna de entradas e uma de despesas por dia
- **E** o controle indica qual visão está ativa

#### Cenário: Tema alternado
- **QUANDO** o usuário está em "Semanas" e alterna o tema
- **ENTÃO** o gráfico é redesenhado com as cores do novo tema, ainda em "Semanas"

### Requirement: Saldo com o zero marcado
O gráfico de evolução do saldo DEVE marcar o valor zero no eixo e com uma linha de referência. O
trecho do saldo abaixo de zero DEVE ser desenhado em vermelho e o trecho acima de zero na cor de
marca, e a linha NÃO DEVE ser suavizada de modo a mostrar saldo que não existiu em nenhum dia. A
cor NÃO DEVE depender só do saldo do último dia.

#### Cenário: Mergulho no meio do mês
- **QUANDO** o saldo fica negativo do dia 2 ao dia 4 e termina o mês positivo
- **ENTÃO** o trecho do dia 2 ao dia 4 é vermelho e o restante, na cor de marca
- **E** a linha do zero está visível

#### Cenário: Mês inteiro positivo
- **QUANDO** o saldo ao fim de todos os dias é positivo
- **ENTÃO** a linha inteira usa a cor de marca

### Requirement: Resumos em texto dos gráficos
Abaixo do fluxo de caixa a página DEVE trazer uma frase com a maior despesa do mês, no formato
"Maior despesa: dia DD, R$ X (descrição)", em que a maior despesa é o maior lançamento de despesa
do mês e, em empate, o mais recente; sem despesas, "Nenhuma despesa neste mês." Abaixo da evolução
do saldo DEVE trazer "Menor saldo: R$ X em DD/MM · termina o mês em R$ Y", em que o menor saldo é o
menor saldo ao fim de um dia e, em empate, o do dia mais cedo; sem lançamentos no mês, "Sem
lançamentos neste mês; o saldo ficou em R$ X." Os valores DEVEM estar no formato brasileiro e as
frases DEVEM estar na página mesmo sem o script dos gráficos.

#### Cenário: Maior despesa
- **QUANDO** a maior despesa do mês é um lançamento "Aluguel" de R$ 1.500,00 no dia 2
- **ENTÃO** a frase é "Maior despesa: dia 02, R$ 1.500,00 (Aluguel)"

#### Cenário: Descrição com marcação
- **QUANDO** a descrição da maior despesa contém `<b>`
- **ENTÃO** a frase exibe o texto literal, sem interpretá-lo como marcação

#### Cenário: Mês sem despesas
- **QUANDO** o mês exibido só tem entradas
- **ENTÃO** a frase é "Nenhuma despesa neste mês."

#### Cenário: Menor saldo negativo
- **QUANDO** o menor saldo ao fim de um dia é − R$ 1.208,15, no dia 4, e o saldo final é R$ 2.628,75
- **ENTÃO** a frase é "Menor saldo: − R$ 1.208,15 em 04/10 · termina o mês em R$ 2.628,75", para outubro

#### Cenário: Mês sem lançamentos
- **QUANDO** o mês exibido não tem lançamentos e o saldo é R$ 500,00
- **ENTÃO** a frase é "Sem lançamentos neste mês; o saldo ficou em R$ 500,00."

### Requirement: Atalho para novo lançamento no painel
A Visão geral e as demais abas, quando o usuário tem lançamentos, DEVEM ter junto do seletor de mês
um atalho "Novo lançamento" para a tela de novo lançamento. No estado vazio vale o atalho que já
existe.

#### Cenário: Atalho com lançamentos
- **QUANDO** um usuário com lançamentos abre qualquer aba do painel
- **ENTÃO** há um link "Novo lançamento" que abre a tela de novo lançamento

### Requirement: Valores do painel alinhados em coluna
Os valores monetários e as porcentagens do painel (bloco de saldo, indicadores, tabelas e listas)
DEVEM usar algarismos tabulares, para que os dígitos de linhas diferentes fiquem alinhados.

#### Cenário: Algarismos tabulares
- **QUANDO** a Visão geral é exibida
- **ENTÃO** os valores do bloco de saldo, dos indicadores e das listas usam algarismos tabulares
