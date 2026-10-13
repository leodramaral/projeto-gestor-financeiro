## ADDED Requirements

### Requirement: Cartão centralizado nas telas de visitante sem painel de marca
As telas de visitante que não usam o layout dividido (confirmação de conta, reenvio da confirmação e as
mensagens de recuperação de senha) DEVEM exibir o cartão **centralizado**, na horizontal e na vertical da
janela, sobre o fundo decorativo em grade, nos temas claro e escuro e em tela larga ou estreita. O cartão
NÃO DEVE ficar encostado no canto superior esquerdo da página.

#### Cenário: Cartão no centro em tela larga
- **QUANDO** um visitante abre a tela "Verifique seu e-mail" em uma tela larga
- **ENTÃO** o cartão aparece no centro da janela, com a marca no topo
- **E** a grade decorativa cobre a janela inteira ao redor dele

#### Cenário: Cartão em tela estreita
- **QUANDO** a mesma tela é aberta em uma tela estreita
- **ENTÃO** o cartão ocupa a largura útil da janela, com margem nas laterais, sem rolagem horizontal
