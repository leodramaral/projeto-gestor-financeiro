# Delta: dashboard

## ADDED Requirements

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

## MODIFIED Requirements

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
