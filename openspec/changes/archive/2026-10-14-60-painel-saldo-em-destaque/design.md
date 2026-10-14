# Design

## Context

O painel é renderizado no servidor (`core/views.py` + `templates/core/`), com os números calculados
em `transactions/dashboard.py` e os gráficos desenhados pelo Chart.js a partir de um JSON embutido
na página (`static/js/dashboard-charts.js`). Hoje a Visão geral tem cinco cartões iguais
(`partials/cards.html`), dois gráficos diários, a rosca por categoria e os últimos lançamentos. O
título de toda página autenticada vem do `partials/breadcrumb.html`, incluído em 15 templates, que
renderiza um `h2` e a trilha "Início > título". O tema escuro é a classe `dark` no `<html>`, e as
cores dos gráficos vêm dos tokens `--chart-*` de `frontend/style.css`.

Motivação e escopo: ver `proposal.md`. Os requisitos estão em `specs/`.

## Goals / Non-Goals

**Goals:**
- O saldo final ser o número que o olho acha primeiro, no desktop e no celular.
- Nenhum número novo sem cálculo no servidor: o JavaScript só desenha o que o servidor mandou.
- A página continuar legível sem o script dos gráficos.
- O design versionado e o app dizerem a mesma coisa.

**Non-Goals:**
- Mexer nas quatro abas, na rosca, na lista de últimos lançamentos ou no estado vazio.
- Guardar a visão Dias | Semanas entre páginas.
- Dependência nova, migração ou mudança de modelo.

## Decisions

### D1. Opção B escolhida, e por quê
O usuário escolheu a **B** entre duas propostas desenhadas em `design/dashboard.figcraft`.
- **A, dentro do TailAdmin** (descartada): saldo final num cartão largo com os outros quatro valores
  ao lado, mesmos gráficos, mantendo o breadcrumb. Resolvia os dois problemas centrais sem mudar a
  identidade.
- **B, assinatura discreta** (escolhida): saldo final num bloco jade com a linha do mês, três
  indicadores no lugar de cinco cartões, sem breadcrumb. Motivo: é a que a banca avaliadora tende a
  reconhecer como do produto e não do template, e a linha do saldo dentro do bloco responde "estou
  bem?" sem rolar a página. A inconsistência com as demais telas, que mantinham o breadcrumb, foi
  resolvida removendo o breadcrumb de todo o sistema (D2), por decisão do usuário.

### D2. Cabeçalho de página no lugar do breadcrumb
`partials/breadcrumb.html` é removido e entra `partials/page_title.html`, com o parâmetro `title`,
que renderiza só o `h1` (mesmo estilo do `h2` atual: `text-xl font-semibold`). Os 15 templates
trocam o `include`. O painel não usa o parcial para o cabeçalho completo: ele monta a própria linha
com o `h1` à esquerda e, à direita, o seletor de mês e o atalho "Novo lançamento"
(`dashboard_base.html`). Os modais mantêm o `h2` deles.
- *Alternativa:* manter o parcial com um parâmetro para esconder a trilha. Rejeitada: deixaria o
  código morto e o nome enganoso.

### D3. Semanas são blocos de 7 dias, não semanas do calendário
O servidor agrega as entradas e as despesas em blocos 1–7, 8–14, 15–21, 22–28 e 29–fim, e o JSON
leva `weeks` (rótulos, entradas, despesas) junto de `days`. Motivo: cada bloco tem o mesmo
tamanho, a soma fecha sem depender do dia da semana em que o mês começa e o rótulo ("Sem 1 · 1–7")
é autoexplicativo.
- *Alternativa:* semanas segunda a domingo. Rejeitada: o primeiro e o último bloco ficam parciais e
  o rótulo precisa de datas diferentes por mês.

### D4. Visão Dias | Semanas decidida no cliente, sem persistência
O script abre em "Semanas" quando `matchMedia("(max-width: 639px)")` é verdadeiro e em "Dias" nas
demais telas, e alterna redesenhando o gráfico de fluxo. A visão fica numa variável do script, de
modo que `build()` (chamado ao alternar o tema) a preserve. Não há `localStorage`.
- *Alternativa:* decidir no servidor por `User-Agent`. Rejeitada: frágil e não acompanha a rotação
  do aparelho.

### D5. Gráfico de saldo: linha reta, zero marcado, trecho vermelho
`tension` passa de 0,35 para 0, porque a suavização desenha saldo que não existiu. O zero ganha
linha de referência (`grid.color` por callback) e o rótulo "0" no eixo. A cor da linha usa
`segment.borderColor` (vermelho se um dos extremos do segmento é negativo) e o preenchimento usa
`fill: { target: { value: 0 }, above, below }`. O segmento que cruza o zero fica todo vermelho; o
desenho no design cruza exatamente no zero, e a diferença é de um segmento.

### D6. Linha do bloco de destaque também em Chart.js
O bloco usa um terceiro canvas (`chart-hero`), sem eixos, com a série de saldo diário, a linha do
zero e, quando há saldo negativo, um ponto amarelo no menor saldo. Motivo: reusa o JSON já embutido
e o tratamento de tema. O bloco continua válido sem o script porque os números vêm do servidor.
Em tema escuro o bloco usa a escala `brand-800` a `brand-900` com os textos em `brand-100`; o
design escuro fixa os valores finais.

### D7. Resumos em texto calculados no servidor
`transactions/dashboard.py` ganha um cálculo da maior despesa do mês (maior lançamento, empate pelo
mais recente) e do menor saldo ao fim de um dia (empate pelo dia mais cedo), e o template monta as
duas frases. O Django escapa a descrição. As frases não dependem do script e servem de texto
alternativo dos gráficos.

### D8. Seletor de mês é um `<select>` de meses
O campo é um `<select>` com os meses do primeiro lançamento até o mês atual, enviado por formulário
`GET`, em vez de `input type="month"`, que o Safari de desktop não desenha como seletor. O envio é
automático ao mudar (Alpine, já usado no projeto) e há um botão "Ir" dentro de `<noscript>` como
saída sem JavaScript. As setas continuam links. O atalho "Este mês" está sempre no lugar: ativo fora do mês atual e
desativado nele, para o seletor não mudar de largura nem deslocar o que está ao lado. No celular o
"Novo lançamento" sobe para a linha do título e o atalho desce para a linha da data. Os controles têm `h-11` (44 px).
- *Alternativa:* `input type="month"`. Rejeitada pela compatibilidade.

### D9. Números tabulares pela fonte, sem peso novo
A Outfit tem o recurso `tnum` (verificado em `design/fonts/Outfit[wght].ttf`), então a classe
`tabular-nums` do Tailwind (`font-variant-numeric`) basta. Falta confirmar que o subconjunto latino
servido (`@fontsource-variable/outfit`) preservou o recurso; a tarefa 6.2 verifica e, se não
preservou, o requisito é revisto em vez de ficar sem efeito.

### D10. Explicações do cálculo mantidas
Os cinco "i" continuam: o do saldo final no rótulo do bloco, o do saldo inicial junto da linha
"Começou o mês com…", e um por indicador. Os testes de explicação existentes seguem valendo, e o
`partials/info_button.html` é reaproveitado.

### D11. Design versionado: só a B, com gráficos desenhados à mão
`design/dashboard.figcraft` entra só com a página da opção escolhida, frames
`dashboard · <viewport> · <tema> · padrão`. O arquivo de trabalho tem as duas opções em frames
lado a lado com a letra no nome; antes do commit ele é reduzido à B (a A fica descrita em D1),
ganha o desktop escuro e as correções para bater com o código (o "i" do saldo inicial, a frase da
taxa de economia, o texto do menor saldo igual nos dois tamanhos). Divergências conhecidas a
registrar no `AGENTS.md`: gráficos desenhados à mão a partir dos dados de exemplo; sem estados de
foco e de hover; sem `shadow-theme-*`; o frame é o tamanho da página inteira, não da janela; sem o
estado "Este mês" nem o menu do campo de mês aberto; o campo de mês desenhado como o `<select>`
fechado.

### D12. Saldo negativo troca o fundo jade por um fundo de alerta
A spec manda o saldo negativo continuar em vermelho, e vermelho sobre jade não tem contraste. Quando
o saldo final é negativo, o bloco de destaque deixa o jade e usa o fundo `error-50` (`error-500` a
10% no escuro), com o valor em `error-600` e a mensagem "Você está no vermelho, cuidado". O jade
passa a ser o estado de saldo bom, o que reforça a mensagem. O desenho original só mostrava o
estado positivo; a tarefa 7.5 desenha o negativo.

### D13. "Ver detalhes" do fluxo de caixa vai para o rodapé do cartão
O desenho trocou o "Ver detalhes" do fluxo de caixa pelo seletor Dias | Semanas no cabeçalho, mas a
spec de abas manda todo bloco ter o atalho. O atalho fica no rodapé do cartão, ao lado da frase da
maior despesa, e o desenho é ajustado para refletir isso. O seletor só aparece com o script
carregado: sem ele os botões não teriam efeito.

## Risks / Trade-offs

- **[A regra do `screen-design` é revertida]** → a change reescreve o requisito e registra a
  divergência no `AGENTS.md`; o risco é o desenho do gráfico envelhecer: ele só é revisto quando o
  painel mudar, como as outras telas.
- **[Segmento que cruza o zero fica todo vermelho (D5)]** → aceito; a diferença é de um segmento e
  o menor saldo é marcado por texto.
- **[Linha reta em vez de suave]** → o gráfico fica mais anguloso; é o preço de não mostrar saldo
  que não existiu.
- **[Tirar o breadcrumb afeta 15 templates e 5 desenhos]** → a troca é mecânica e coberta por teste
  de `h1` único e de ausência da trilha; os desenhos entram nas tarefas.
- **[Chart.js em canvas pequeno do bloco (D6)]** → se o desenho ficar fraco em 390 px, o fallback
  é SVG calculado no servidor, sem mudar o requisito.
- **[`tabular-nums` sem efeito se o subconjunto da fonte perdeu o `tnum` (D9)]** → verificado na
  tarefa 6.2.
