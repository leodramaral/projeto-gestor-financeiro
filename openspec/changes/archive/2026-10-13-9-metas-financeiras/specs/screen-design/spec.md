## ADDED Requirements

### Requirement: Opções de layout para escolha antes de implementar
Quando uma tela nova admite mais de um layout plausível, o design DEVE oferecer **ao menos duas opções**
no `.figcraft` da tela, cada uma numa página própria nomeada `Opção <letra> — <nome curto>`, com os mesmos
estados e temas mínimos, para o usuário escolher antes de a tela ser implementada. As opções DEVEM diferir
no layout, não no conteúdo: textos, rótulos e dados de exemplo são os mesmos. A escolha DEVE ser registrada
no `design.md` da change, com o motivo. O arquivo versionado DEVE conter só a opção escolhida, com frames na
convenção `<tela> · <viewport> · <tema> · <estado>` (sem a letra da opção no nome); a opção descartada fica
descrita no `design.md`, não no arquivo.

#### Cenário: Duas opções para escolha
- **QUANDO** o design de uma tela nova ainda aguarda a escolha
- **ENTÃO** o `.figcraft` tem uma página por opção, com pelo menos duas
- **E** cada página tem os mesmos frames de estado e tema (por exemplo desktop claro, desktop escuro, mobile claro e estado vazio)

#### Cenário: Escolha registrada
- **QUANDO** o usuário escolhe uma opção
- **ENTÃO** o `design.md` da change registra qual foi e por quê
- **E** a implementação da tela segue o layout escolhido

#### Cenário: Arquivo final só com a escolhida
- **QUANDO** a tela foi implementada e a change vai ser arquivada
- **ENTÃO** `design/<tela>.figcraft` não contém a página da opção descartada
- **E** os nomes dos frames seguem a convenção, sem a letra da opção
