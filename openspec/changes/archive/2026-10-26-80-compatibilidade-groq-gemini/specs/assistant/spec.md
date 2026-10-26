## MODIFIED Requirements

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
forte em 100%. Junto dos créditos, a caixa DEVE mostrar uma label com o nome do modelo em uso (o
valor de `LLM_MODEL`, sem outro texto visível ao lado), que NÃO DEVE aparecer quando o assistente está indisponível por falta de chave; a tela NUNCA
DEVE mostrar a chave nem o endereço-base do provedor. A região da conversa DEVE avisar leitores de tela quando uma mensagem nova chega, sem reler as anteriores, e o indicador
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
- **E** a label do modelo é lida como "Modelo em uso: <nome>"

#### Cenário: Medidor de créditos em cores
- **QUANDO** o uso do dia é 40%, 75%, 95% ou 100% do teto
- **ENTÃO** a barra e o contador aparecem em verde, laranja, vermelho e vermelho forte, respectivamente
- **E** a tela mostra "Créditos" e a porcentagem, e em nenhum lugar a palavra "tokens"

#### Cenário: Modelo em uso na caixa
- **QUANDO** um usuário autenticado abre `/assistant/` com `LLM_MODEL` igual a `openai/gpt-oss-120b`
- **ENTÃO** a caixa de pergunta mostra, junto dos créditos, a label com `openai/gpt-oss-120b`, sem a palavra "Modelo"
- **E** a tela não mostra a chave nem o endereço-base do provedor

#### Cenário: Modelo trocado por configuração
- **QUANDO** `LLM_MODEL` passa a outro valor e a aplicação é reiniciada
- **ENTÃO** a label mostra o novo nome, sem alteração de código

#### Cenário: Sem chave, sem label do modelo
- **QUANDO** a aplicação roda sem `LLM_API_KEY` e o usuário abre `/assistant/`
- **ENTÃO** a caixa mostra a mensagem de indisponibilidade e não mostra a label do modelo

#### Cenário: Nome do modelo longo no celular
- **QUANDO** o nome do modelo não cabe na largura da caixa
- **ENTÃO** a label é cortada com reticências, sem quebrar a linha dos créditos nem do botão de envio
- **E** o nome completo continua disponível ao passar o mouse e para leitor de tela

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


### Requirement: Provedor configurável por ambiente
A chave, o endereço-base e o modelo do provedor DEVEM vir das variáveis de ambiente `LLM_API_KEY`,
`LLM_BASE_URL` e `LLM_MODEL`, sem chave no código nem no repositório e sem valor padrão para a chave. Trocar
de provedor compatível NÃO DEVE exigir mudança de código. Os provedores **Groq** e **Gemini** DEVEM
funcionar de ponta a ponta, inclusive nas perguntas que consultam dados (mais de uma chamada ao modelo), e
um provedor só DEVE ser tratado como compatível depois de testado com o provedor real. Quando o provedor
devolve, junto de uma chamada de ferramenta, dados próprios além dos campos padrão, a aplicação DEVE
devolvê-los, sem alteração, na mensagem do assistente enviada na rodada seguinte; sem dados extras, a mensagem
NÃO DEVE mudar. O `README.md` (seção de configuração) e o `.env.example` DEVEM listar os provedores
testados, com o endereço-base, o modelo de exemplo e a origem da chave de cada um, e dizer que só eles foram
testados. Os testes automatizados NÃO DEVEM fazer chamada de rede ao provedor.

#### Cenário: Troca de provedor
- **QUANDO** `LLM_BASE_URL` e `LLM_MODEL` apontam para outro provedor compatível
- **ENTÃO** a aplicação usa o novo endereço e o novo modelo sem alteração de código

#### Cenário: Provedor que devolve dados próprios na chamada de ferramenta
- **QUANDO** o provedor responde com uma chamada de ferramenta que traz um campo extra (como a assinatura de raciocínio do Gemini)
- **ENTÃO** a mensagem do assistente enviada na rodada seguinte traz esse campo, com o mesmo valor, na mesma chamada
- **E** a pergunta termina com a resposta do modelo, sem erro do provedor

#### Cenário: Provedor sem dados extras
- **QUANDO** o provedor responde com uma chamada de ferramenta sem campos além dos padrão
- **ENTÃO** a mensagem do assistente enviada na rodada seguinte traz só `id`, `type` e a função com nome e argumentos

#### Cenário: Provedores verificados
- **QUANDO** a aplicação roda com a Groq ou com o Gemini e o usuário faz uma pergunta que consulta gastos
- **ENTÃO** a resposta é exibida, citando valores devolvidos pela ferramenta

#### Cenário: Provedores documentados
- **QUANDO** alguém lê a seção de configuração do `README.md` e o `.env.example`
- **ENTÃO** encontra, para a Groq e para o Gemini, o `LLM_BASE_URL`, um `LLM_MODEL` de exemplo e onde criar a chave
- **E** encontra a informação de que só esses dois provedores foram testados

#### Cenário: Chave fora do repositório
- **QUANDO** o repositório é inspecionado
- **ENTÃO** `.env.example` traz `LLM_API_KEY` em branco
- **E** nenhum arquivo versionado contém uma chave real

#### Cenário: Suíte sem rede
- **QUANDO** a suíte de testes roda
- **ENTÃO** nenhuma chamada ao provedor real é feita, e uma tentativa de criar o cliente real falha o teste
