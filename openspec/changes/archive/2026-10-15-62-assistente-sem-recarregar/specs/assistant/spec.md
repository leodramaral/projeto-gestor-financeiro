# Spec Delta

## MODIFIED Requirements

### Requirement: Pergunta e resposta
O usuário DEVE poder enviar uma pergunta em texto, e a aplicação DEVE exibir a resposta do assistente na
mesma tela. A pergunta DEVE ser obrigatória, sem contar espaços nas pontas, e ter no máximo 500
caracteres. O envio DEVE ser protegido contra CSRF e só por POST. A resposta DEVE ser exibida como texto
simples, escapado, sem interpretar HTML nem marcação vinda do modelo. Com JavaScript, o envio DEVE
acontecer sem recarregar a página, pela mesma rota e com as mesmas regras de validação, créditos e
histórico do envio sem JavaScript: a pergunta DEVE aparecer na conversa imediatamente, com um indicador de
espera do assistente, o campo DEVE ser limpo e manter o foco, e a conversa DEVE rolar até a última mensagem.
Quando a resposta chegar, a conversa, os erros do campo, a mensagem da caixa e os créditos do dia DEVEM
refletir o resultado. Sem JavaScript, o formulário DEVE continuar funcionando, com redirecionamento para a
tela após o envio.

Os avisos DEVEM fazer parte do chat conforme quem fala, e NÃO DEVEM aparecer como caixa solta fora dele:
a recusa de assunto, a ajuda de cortesia e a mensagem de resposta não confiável DEVEM aparecer como uma
resposta do assistente, abaixo da pergunta, e o campo DEVE ser limpo; a falha do provedor DEVE aparecer como
uma linha de erro na conversa, sem a marca "Assistente", com a pergunta marcada como não enviada, e o texto
digitado DEVE voltar ao campo; o erro de validação DEVE aparecer sob o campo, com o texto mantido; créditos
esgotados e assistente sem chave DEVEM aparecer como mensagem dentro da caixa de envio, com o botão de envio
desativado e o texto mantido. A pergunta e o texto desses avisos NÃO DEVEM entrar na sessão nem ser enviados
ao modelo, e DEVEM sumir ao recarregar a tela ou ao enviar a próxima pergunta.

#### Cenário: Pergunta dentro do escopo
- **QUANDO** o usuário pergunta "quanto gastei com alimentação este mês?"
- **ENTÃO** o assistente consulta os gastos por categoria do mês
- **E** a resposta exibida cita o valor da categoria Alimentação desse mês

#### Cenário: Pergunta vazia
- **QUANDO** o usuário envia a pergunta vazia ou só com espaços
- **ENTÃO** nenhuma chamada ao provedor é feita
- **E** a tela exibe o erro do campo em português

#### Cenário: Pergunta longa demais
- **QUANDO** o usuário envia uma pergunta com mais de 500 caracteres
- **ENTÃO** nenhuma chamada ao provedor é feita
- **E** a tela exibe o erro do campo em português, mantendo o texto digitado

#### Cenário: Marcação na resposta
- **QUANDO** a resposta do modelo contém `<script>` ou HTML
- **ENTÃO** a tela mostra o texto literal, sem executar nem renderizar a marcação

#### Cenário: Envio por GET
- **QUANDO** a rota de envio é acessada por GET
- **ENTÃO** nenhuma pergunta é enviada ao provedor

#### Cenário: Envio sem recarregar a página
- **QUANDO** o usuário, com JavaScript, envia uma pergunta válida
- **ENTÃO** a página não recarrega
- **E** a pergunta aparece de imediato na conversa, seguida do indicador de espera do assistente
- **E** o campo é limpo e continua com o foco
- **E** ao chegar a resposta, ela aparece na conversa no lugar do indicador e a conversa rola até ela

#### Cenário: Créditos atualizados após a resposta
- **QUANDO** uma resposta chega sem recarregar a página
- **ENTÃO** os créditos do dia exibidos refletem o consumo daquela pergunta

#### Cenário: Recusa, cortesia ou resposta não confiável no chat
- **QUANDO** a pergunta é recusada por estar fora do escopo, é cortesia ou a resposta é rejeitada pelas checagens
- **ENTÃO** a pergunta aparece como bolha do usuário e o texto fixo, como resposta do assistente, na conversa
- **E** o campo é limpo e continua com o foco
- **E** nem a pergunta nem o texto entram no histórico, e somem ao recarregar a tela

#### Cenário: Falha do provedor no chat
- **QUANDO** o provedor falha, está indisponível, limita a taxa ou excede o tempo
- **ENTÃO** a conversa mostra a pergunta marcada como não enviada, com o aviso em uma linha de erro
- **E** o texto digitado volta ao campo, com o foco
- **E** o indicador de espera some e a pergunta não entra no histórico

#### Cenário: Aviso sem caixa solta
- **QUANDO** qualquer aviso da tela é exibido
- **ENTÃO** ele aparece na conversa, sob o campo ou dentro da caixa de envio
- **E** nenhuma caixa de aviso aparece acima da caixa de envio

#### Cenário: Erro de validação do campo
- **QUANDO**, com JavaScript, o usuário envia uma pergunta com mais de 500 caracteres
- **ENTÃO** o erro do campo aparece sob ele, sem recarregar a página
- **E** o texto digitado é mantido

#### Cenário: Sem JavaScript
- **QUANDO** o navegador não executa JavaScript e o usuário envia uma pergunta
- **ENTÃO** o formulário é enviado por POST e a aplicação redireciona para a tela com a resposta
- **E** a conversa, os avisos e os créditos aparecem como antes

#### Cenário: Duplo envio
- **QUANDO** o usuário envia de novo, por Enter ou clique, enquanto uma pergunta está em andamento
- **ENTÃO** nenhum segundo envio é feito

### Requirement: Tela do assistente protegida por login
A aplicação DEVE servir a tela do assistente em `/assistant/` apenas ao usuário autenticado, com um item
"Assistente" na barra lateral, marcado com o selo "BETA". Visitante sem sessão DEVE ser redirecionado para a entrada, e nenhuma consulta
ao provedor DEVE acontecer para ele. A tela DEVE ter o título "Assistente", sem breadcrumb, e todo texto
exibido DEVE estar em português do Brasil. O layout DEVE seguir o de um chat: as mensagens ocupam a área
central, a pergunta do usuário em um bloco à direita e a resposta do assistente em texto corrido sob a marca
"Assistente"; a caixa de pergunta fica no rodapé da tela, com os créditos do dia dentro dela e o aviso fixo
abaixo; e o botão "Nova conversa" fica no topo, só quando há conversa. O campo de pergunta DEVE ter o nome
acessível "Sua pergunta" e o botão de envio, que só mostra um ícone, o nome acessível "Enviar". A caixa DEVE mostrar os créditos do dia como uma barra com a palavra "Créditos" e o
contador de porcentagem usada, sem repetir o uso em números na tela, e a cor da barra e do contador DEVE
esquentar conforme o uso sobe: verde da marca até 69%, laranja de 70% a 89%, vermelho de 90% a 99% e vermelho
forte em 100%. A região da conversa DEVE avisar leitores de tela quando uma mensagem nova chega, sem reler as anteriores, e o indicador
de espera do assistente DEVE ter um nome acessível.

#### Cenário: Visitante sem login
- **QUANDO** um visitante abre `/assistant/` ou envia uma pergunta para ela
- **ENTÃO** ele é redirecionado para a entrada
- **E** nenhuma chamada ao provedor é feita

#### Cenário: Usuário autenticado
- **QUANDO** um usuário autenticado abre `/assistant/`
- **ENTÃO** vê o campo de pergunta, o aviso fixo e os créditos do dia
- **E** o item "Assistente" aparece ativo na barra lateral

#### Cenário: Conversa vazia
- **QUANDO** o usuário abre a tela sem conversa em andamento
- **ENTÃO** ela convida a perguntar com uma pergunta de exemplo completa, como "Quanto gastei com
  transporte em agosto?"
- **E** o botão "Nova conversa" não aparece

#### Cenário: Nomes acessíveis
- **QUANDO** um leitor de tela percorre a tela
- **ENTÃO** o campo de pergunta se chama "Sua pergunta"
- **E** o botão de envio se chama "Enviar"
- **E** a barra de créditos informa a porcentagem usada e, em texto para leitor de tela, o uso e o total do dia

#### Cenário: Medidor de créditos em cores
- **QUANDO** o uso do dia é 40%, 75%, 95% ou 100% do teto
- **ENTÃO** a barra e o contador aparecem em verde, laranja, vermelho e vermelho forte, respectivamente
- **E** a tela mostra "Créditos" e a porcentagem, e em nenhum lugar a palavra "tokens"

#### Cenário: Conversa em andamento
- **QUANDO** há mensagens na conversa
- **ENTÃO** a pergunta do usuário e a resposta do assistente aparecem em ordem, identificadas para leitores
  de tela
- **E** o botão "Nova conversa" aparece no topo

#### Cenário: Resposta anunciada
- **QUANDO**, com JavaScript, a resposta do assistente chega à conversa
- **ENTÃO** a região da conversa a anuncia a leitores de tela como uma região viva educada
- **E** o foco permanece no campo de pergunta

#### Cenário: Indicador de espera acessível
- **QUANDO** a pergunta foi enviada e a resposta ainda não chegou
- **ENTÃO** o indicador de espera informa a leitores de tela que o assistente está respondendo
- **E** a animação do indicador respeita a preferência por movimento reduzido

### Requirement: Créditos diários em tokens
A aplicação DEVE contar os tokens consumidos por cada usuário em cada dia, somando o consumo informado pelo
provedor em todas as chamadas de cada pergunta, e DEVE ter um teto diário de tokens por usuário vindo da
variável de ambiente `LLM_DAILY_TOKEN_LIMIT`. A checagem DEVE ocorrer antes de chamar o provedor e reservar créditos
para a pergunta em andamento, de modo que perguntas paralelas do mesmo usuário não passem todas pelo mesmo
saldo, e a reserva DEVE ser trocada pelo consumo real ao fim: com o teto atingido, NÃO DEVE haver chamada. A tela DEVE mostrar os créditos do dia como porcentagem
usada do teto, chamando-os apenas de "créditos", sem a palavra "tokens", e DEVE desativar o envio e avisar dentro da caixa quando o teto for atingido, inclusive ao abrir a tela já no teto. O dia DEVE
seguir o fuso `America/Sao_Paulo`. Chamada que falha sem informar consumo NÃO DEVE gastar créditos, e o
consumo de chamadas que deram certo antes de uma falha DEVE ser contado.

#### Cenário: Consumo somado
- **QUANDO** uma pergunta faz duas chamadas ao modelo, de 900 e 1.300 tokens
- **ENTÃO** 2.200 tokens são acrescentados ao uso do usuário no dia

#### Cenário: Créditos esgotados
- **QUANDO** o uso do dia do usuário já alcançou o teto
- **ENTÃO** a pergunta não chama o provedor
- **E** a caixa de envio avisa em português que os créditos de hoje acabaram, com o botão de envio desativado e o texto digitado mantido

#### Cenário: Tela aberta já sem créditos
- **QUANDO** o usuário abre a tela com o uso do dia no teto
- **ENTÃO** o medidor aparece em vermelho forte, a caixa traz o aviso de créditos esgotados e o envio está desativado

#### Cenário: Novo dia
- **QUANDO** o dia local muda
- **ENTÃO** o uso do usuário volta a zero para o novo dia

#### Cenário: Falha sem consumo informado
- **QUANDO** o provedor falha sem devolver o consumo
- **ENTÃO** o uso do dia do usuário não muda

#### Cenário: Falha depois de uma volta bem-sucedida
- **QUANDO** a primeira chamada de uma pergunta consome 900 tokens e a segunda falha
- **ENTÃO** os 900 tokens são contados no uso do dia

#### Cenário: Resposta inesperada do provedor
- **QUANDO** o provedor devolve uma resposta malformada ou o cliente não pode ser criado
- **ENTÃO** a tela mostra o aviso de indisponível, com status 200, e não uma página de erro
- **E** os tokens das chamadas anteriores da pergunta são contados no uso do dia

#### Cenário: Perguntas paralelas
- **QUANDO** uma pergunta do usuário está em andamento e outra chega antes de ela terminar, com o saldo do dia perto do teto
- **ENTÃO** os créditos reservados pela primeira contam para a segunda, que pode ser barrada sem chamar o provedor
- **E** ao fim da primeira a reserva é trocada pelo consumo real, também quando ela falha

#### Cenário: Resposta cortada pelo limite de saída
- **QUANDO** o provedor encerra a resposta por limite de tokens de saída
- **ENTÃO** a tela mostra o aviso de indisponível, o texto cortado não é exibido nem guardado na conversa
- **E** os tokens gastos são contados no uso do dia

#### Cenário: Recusa consome créditos
- **QUANDO** uma pergunta é recusada pela ferramenta de recusa
- **ENTÃO** os tokens da chamada que a recusou são contados no uso do dia

#### Cenário: Usuários independentes
- **QUANDO** dois usuários perguntam no mesmo dia
- **ENTÃO** cada um tem o próprio uso e o próprio saldo
