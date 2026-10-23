# Spec Delta

## MODIFIED Requirements

### Requirement: Falha amigável do provedor
Timeout, indisponibilidade, limite de taxa (HTTP 429) ou resposta inválida do provedor, e ausência da chave
configurada, DEVEM resultar em uma mensagem amigável em português na própria tela, com status de página
normal, sem página de erro e sem exibir detalhes técnicos. O restante da aplicação DEVE continuar
funcionando. A aplicação NÃO DEVE registrar em log o conteúdo de perguntas, respostas, argumentos de
ferramentas ou dados financeiros, somente metadados. Os metadados permitidos são: um identificador curto da
pergunta, a rodada, o modelo, o motivo de parada, os tokens, a duração, o nome da ferramenta e o resultado
dela (ok, recusa ou erro), o tipo da falha, o status e, **somente nos erros 4xx do provedor**, a mensagem de
erro que ele devolve. Essa mensagem DEVE ser truncada, sem quebras de linha e com a chave de API mascarada;
nos demais erros nenhuma mensagem do provedor é registrada. Para diagnosticar uma falha, o log DEVE permitir
saber em qual rodada ela ocorreu e por quê, sem reproduzir a chamada.

#### Cenário: Limite de taxa do provedor
- **QUANDO** o provedor responde 429
- **ENTÃO** a tela pede para aguardar alguns segundos e tentar de novo
- **E** a página responde normalmente

#### Cenário: Timeout ou indisponibilidade
- **QUANDO** o provedor não responde a tempo ou fica indisponível
- **ENTÃO** a tela mostra que o assistente está indisponível no momento
- **E** a pergunta digitada continua no campo

#### Cenário: Sem chave configurada
- **QUANDO** a aplicação roda sem `LLM_API_KEY`
- **ENTÃO** a tela do assistente informa que ele está indisponível
- **E** o restante da aplicação funciona

#### Cenário: Log sem conteúdo
- **QUANDO** uma pergunta falha ou é respondida
- **ENTÃO** nenhuma linha de log contém a pergunta, a resposta, os argumentos das ferramentas nem os valores
- **E** o log registra apenas os metadados permitidos

#### Cenário: Falha identificada pela rodada e pelo motivo
- **QUANDO** o provedor responde 400 na segunda rodada de uma pergunta, com uma mensagem de erro
- **ENTÃO** o log da falha traz o tipo, o status 400, a rodada 2, o modelo, a duração e a mensagem do provedor
- **E** a tela mostra só a mensagem amigável de indisponibilidade

#### Cenário: Mensagem do provedor só nos erros 4xx
- **QUANDO** o provedor responde 503 com uma mensagem de erro
- **ENTÃO** o log da falha traz o tipo, o status e a rodada
- **E** a mensagem do provedor não é registrada

#### Cenário: Mensagem do provedor truncada e sem a chave
- **QUANDO** o provedor responde 400 com uma mensagem longa que contém a chave de API
- **ENTÃO** o log traz a mensagem cortada no limite, em uma só linha
- **E** a chave aparece mascarada

#### Cenário: Uma linha por chamada ao modelo e por ferramenta
- **QUANDO** uma pergunta usa a ferramenta de consulta e o modelo responde na segunda rodada
- **ENTÃO** o log traz uma linha por chamada ao modelo, com rodada, modelo, motivo de parada, tokens e duração
- **E** uma linha da ferramenta, com o nome e o resultado, sem argumentos
- **E** todas essas linhas levam o mesmo identificador da pergunta

#### Cenário: Resumo da pergunta
- **QUANDO** uma pergunta termina, com resposta, recusa ou falha
- **ENTÃO** o log traz uma linha de resumo com o identificador, o resultado, as rodadas, os tokens e a duração
