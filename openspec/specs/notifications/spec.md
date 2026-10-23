# notifications Specification

## Purpose
Define o toast global de notificações: o aviso transitório e reutilizável que confirma uma ação do
usuário (ou comunica um resultado) em qualquer tela, sem ocupar espaço no fluxo da página.

## Requirements

### Requirement: Toast global no lugar do alerta estático
Toda mensagem emitida pelo servidor para o usuário (sucesso de lançamento, categoria, meta e
redefinição de senha) DEVE ser exibida como toast, e NÃO DEVE mais aparecer como alerta no fluxo da
página. O toast DEVE aparecer no topo à direita, sobre o conteúdo, sem deslocá-lo, e a mensagem DEVE
ser o texto em português já existente, sem alteração.

#### Cenário: Lançamento registrado
- **QUANDO** o usuário registra um lançamento
- **ENTÃO** a listagem é exibida atualizada e o toast "Lançamento registrado." aparece no topo à direita
- **E** nenhum alerta é inserido acima do conteúdo da página

#### Cenário: Mesma apresentação em todas as telas
- **QUANDO** uma mensagem de sucesso é emitida em Lançamentos, Categorias, Metas ou Login
- **ENTÃO** ela é exibida como o mesmo toast, com a mesma aparência e o mesmo comportamento

#### Cenário: Tela futura sem código extra
- **QUANDO** uma tela nova estende o layout base e a view emite uma mensagem
- **ENTÃO** o toast é exibido sem que a tela inclua laço ou parcial de mensagens

#### Cenário: Várias mensagens
- **QUANDO** mais de uma mensagem é emitida na mesma requisição
- **ENTÃO** todas são exibidas como toasts empilhados no topo à direita, nenhuma se perde

### Requirement: Níveis de notificação
O toast DEVE suportar quatro níveis: sucesso, erro, aviso e informação. Cada nível DEVE ter ícone da
Lucide e cor do TailAdmin próprios, nos temas claro e escuro. O nível da mensagem do servidor DEVE
vir do nível da mensagem do Django (`success`, `error`, `warning`, `info`); um nível desconhecido ou
ausente DEVE ser tratado como informação.

#### Cenário: Aparência por nível
- **QUANDO** um toast de cada nível é exibido
- **ENTÃO** cada um mostra seu ícone e sua cor (verde, vermelho, laranja e azul), legíveis no tema claro e no escuro

#### Cenário: Nível do servidor
- **QUANDO** a view emite uma mensagem de erro, aviso ou info
- **ENTÃO** o toast usa a aparência do nível correspondente

#### Cenário: Nível desconhecido
- **QUANDO** a mensagem chega com um nível que o toast não conhece
- **ENTÃO** ela é exibida como informação

### Requirement: Notificação a partir do JavaScript
A aplicação DEVE oferecer uma API JavaScript global para exibir um toast sem recarregar a página, com
o nível e o texto como entrada. O texto NÃO DEVE ser interpretado como HTML.

#### Cenário: Aviso sem recarregar
- **QUANDO** um script da página aciona o toast com nível e texto
- **ENTÃO** o toast aparece sem recarregar a página, igual ao do servidor

#### Cenário: Texto não é HTML
- **QUANDO** o texto contém marcação HTML (por exemplo `<b>x</b>`)
- **ENTÃO** o toast mostra os caracteres literais, sem renderizar a marcação

### Requirement: Duração e interação
O toast de sucesso, aviso e informação DEVE sumir sozinho após cerca de 5 segundos; o de erro NÃO DEVE
sumir sozinho. Todo toast DEVE ter botão de fechar, com rótulo em português e ícone da Lucide. A
contagem do tempo DEVE pausar enquanto o ponteiro estiver sobre os toasts ou o foco do teclado estiver
dentro deles, e recomeçar ao sair.

#### Cenário: Some sozinho
- **QUANDO** um toast de sucesso é exibido e o usuário não interage
- **ENTÃO** ele some após cerca de 5 segundos

#### Cenário: Erro permanece
- **QUANDO** um toast de erro é exibido e o usuário não interage
- **ENTÃO** ele permanece até ser fechado

#### Cenário: Fechar
- **QUANDO** o usuário aciona o botão de fechar, por clique ou pelo teclado
- **ENTÃO** o toast some imediatamente

#### Cenário: Pausa ao passar o mouse
- **QUANDO** o ponteiro está sobre um toast de sucesso
- **ENTÃO** ele não some enquanto o ponteiro permanecer ali

#### Cenário: Pausa ao focar pelo teclado
- **QUANDO** o foco do teclado está no botão de fechar de um toast de sucesso
- **ENTÃO** ele não some enquanto o foco permanecer ali

### Requirement: Empilhamento dos toasts
Quando houver mais de um toast, eles DEVEM ficar empilhados em cartas no topo à direita, com o mais novo
à frente e no máximo três cartas visíveis. Ao passar o mouse ou focar dentro da pilha, ela DEVE se expandir e
mostrar todos os toasts por inteiro; ao sair, DEVE voltar a se recolher. Fechar um toast NÃO DEVE fechar os
demais.

#### Cenário: Pilha recolhida
- **QUANDO** quatro toasts estão na tela e o usuário não interage
- **ENTÃO** o mais novo aparece à frente e atrás dele aparecem no máximo mais duas cartas

#### Cenário: Pilha expandida
- **QUANDO** o usuário passa o mouse sobre a pilha
- **ENTÃO** todos os toasts aparecem por inteiro, um sob o outro
- **E** ao tirar o mouse a pilha volta a se recolher

#### Cenário: Fechar um dos toasts
- **QUANDO** o usuário fecha um toast da pilha
- **ENTÃO** só ele some e os demais permanecem, reorganizados

### Requirement: Acessibilidade do toast
O toast DEVE ser anunciado por leitores de tela sem tirar o foco do usuário: sucesso e informação de
forma educada (`role="status"`), erro e aviso de forma assertiva (`role="alert"`). O botão de fechar
DEVE ser alcançável pelo teclado. As animações DEVEM ser desativadas quando o usuário prefere menos
movimento. O texto DEVE manter contraste legível nos dois temas.

#### Cenário: Anúncio de sucesso
- **QUANDO** um toast de sucesso aparece
- **ENTÃO** o leitor de tela o anuncia sem interromper a leitura em curso e o foco não muda

#### Cenário: Anúncio de erro
- **QUANDO** um toast de erro aparece
- **ENTÃO** o leitor de tela o anuncia de imediato

#### Cenário: Menos movimento
- **QUANDO** o sistema do usuário pede redução de movimento
- **ENTÃO** o toast aparece e some sem animação de deslizar

### Requirement: Funcionamento sem JavaScript
Com o JavaScript desativado, a mensagem do servidor DEVE continuar visível, no formato do alerta
estático, para que nenhuma confirmação se perca.

#### Cenário: JavaScript desativado
- **QUANDO** o usuário registra um lançamento com o JavaScript desativado
- **ENTÃO** a listagem exibe a mensagem "Lançamento registrado." como alerta no topo do conteúdo

### Requirement: Avisos inline permanecem inline
Os erros de formulário (erro geral e erros por campo) e os erros exibidos no chat do assistente NÃO
DEVEM virar toast: continuam exibidos junto do contexto, exatamente como antes.

#### Cenário: Erro de validação
- **QUANDO** o usuário envia um formulário com valor inválido
- **ENTÃO** o erro aparece sob o campo ou na caixa do formulário, e nenhum toast é exibido

#### Cenário: Falha do assistente
- **QUANDO** o provedor do assistente falha
- **ENTÃO** a linha de erro aparece no chat, e nenhum toast é exibido

### Requirement: Sem rede externa
O código do toast DEVE ser servido pela própria aplicação, sem CDN nem rede em tempo de execução, e NÃO
DEVE depender de biblioteca de terceiros além das já usadas pelo projeto.

#### Cenário: Sem rede externa
- **QUANDO** qualquer página com toast é carregada
- **ENTÃO** todos os arquivos do toast vêm de `/static/` e nenhuma requisição vai a domínio externo
