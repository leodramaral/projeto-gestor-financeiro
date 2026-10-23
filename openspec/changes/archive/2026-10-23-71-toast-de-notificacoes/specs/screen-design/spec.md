# Spec Delta

## ADDED Requirements

### Requirement: Toast de notificação documentado
O toast é global e NÃO pertence a uma tela, então o design DEVE ter um arquivo próprio,
`design/toast.figcraft`, com os quatro níveis (sucesso, erro, aviso e informação) em desktop claro, desktop
escuro e mobile claro, e a pilha recolhida com vários toasts em cartas. Os quadros desse arquivo DEVEM ser
nomeados `toast · <viewport> · <tema> · <estado>` (o toast é um componente, não uma rota) e podem ser
recortes sobre o fundo da página. O toast de sucesso em contexto DEVE aparecer também em
`design/transactions.figcraft`, na tela de lançamentos, em desktop claro, desktop escuro e mobile claro. O
texto do sucesso DEVE ser o real do app ("Lançamento registrado."); os textos dos demais níveis DEVEM ser de
exemplo claramente fictício. O design DEVE ser mostrado ao usuário e validado antes da implementação. As
divergências em relação ao app (animação, pausa ao passar o mouse e a pilha expandida, que o desenho
estático não mostra) DEVEM estar registradas no `AGENTS.md`.

#### Cenário: Quatro níveis no design
- **QUANDO** `design/toast.figcraft` é aberto
- **ENTÃO** há quadros dos toasts de sucesso, erro, aviso e informação, cada um com seu ícone e sua cor

#### Cenário: Temas e viewports
- **QUANDO** os quadros de níveis do toast são listados
- **ENTÃO** há o desktop claro, o desktop escuro e o mobile claro

#### Cenário: Pilha de toasts
- **QUANDO** `design/toast.figcraft` é aberto
- **ENTÃO** há um quadro com a pilha recolhida (o toast mais novo à frente e as cartas de trás)
- **E** a pilha expandida não tem quadro e consta como divergência registrada

#### Cenário: Toast em contexto
- **QUANDO** o design de lançamentos é aberto
- **ENTÃO** há quadros da listagem com o toast de sucesso sobre o conteúdo, no topo à direita, em desktop claro, desktop escuro e mobile claro

#### Cenário: Texto real do sucesso
- **QUANDO** o quadro do toast de sucesso é inspecionado
- **ENTÃO** o texto é "Lançamento registrado.", o mesmo da view
