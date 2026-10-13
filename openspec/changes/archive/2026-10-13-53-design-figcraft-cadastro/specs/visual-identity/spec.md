## ADDED Requirements

### Requirement: Fonte de marca servida pelo projeto
A aplicação DEVE servir a fonte de marca (Outfit) a partir do próprio projeto, em todas as telas, e NÃO
DEVE depender de rede externa nem de a fonte estar instalada no computador de quem acessa. A fonte DEVE
ser entregue pelo build do frontend, como o CSS e o Alpine, com a licença da fonte preservada no pacote de
origem. Se o arquivo da fonte não carregar, o texto DEVE continuar legível na fonte do sistema.

#### Cenário: Visitante sem a fonte instalada
- **QUANDO** um visitante sem a Outfit instalada abre qualquer tela
- **ENTÃO** o navegador baixa a fonte do próprio app, sem requisição a outro domínio
- **E** o texto é exibido em Outfit

#### Cenário: Build sem rede
- **QUANDO** o frontend é construído sem acesso à internet depois da instalação das dependências
- **ENTÃO** o build conclui e a fonte está em `static/dist/fonts/`

#### Cenário: Fonte indisponível
- **QUANDO** o arquivo da fonte não carrega
- **ENTÃO** o texto continua legível na fonte do sistema
- **E** nenhuma tela fica sem texto enquanto a fonte carrega
