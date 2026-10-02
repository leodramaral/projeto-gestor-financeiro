# transactional-email Specification

## Purpose
Define como a aplicação envia e-mail transacional (confirmação de conta, redefinição de senha) em
cada ambiente, e como a equipe valida o envio sem depender de um provedor real.

## Requirements

### Requirement: Caixa de entrada local em desenvolvimento
O ambiente local DEVE subir, junto com `docker compose up`, uma caixa de entrada que recebe todo
e-mail enviado pela aplicação e o exibe em uma interface web. Nenhum e-mail enviado em
desenvolvimento DEVE sair da máquina, e a interface NÃO DEVE ser exposta fora de `127.0.0.1`.

#### Cenário: E-mail enviado em desenvolvimento
- **QUANDO** a aplicação envia um e-mail com o ambiente local no ar
- **ENTÃO** a mensagem aparece na interface da caixa de entrada em `127.0.0.1:8025`
- **E** nenhum destinatário real recebe a mensagem

### Requirement: Configuração de e-mail por ambiente
A aplicação DEVE usar entrega por SMTP para a caixa local em desenvolvimento, entrega em memória
nos testes e entrega por SMTP configurada por variáveis de ambiente em produção. Os testes NÃO
DEVEM depender de serviço de e-mail em execução.

#### Cenário: Execução dos testes
- **QUANDO** a suíte de testes roda sem a caixa de entrada local
- **ENTÃO** os testes que enviam e-mail passam
- **E** a mensagem enviada pode ser inspecionada pelo teste

### Requirement: Produção exige configuração de e-mail
Em produção, a aplicação DEVE validar a configuração de e-mail ao iniciar e NÃO DEVE subir sem o
servidor SMTP, as credenciais e o remetente padrão. Credenciais NÃO DEVEM ter valor padrão nem ser
versionadas, e a mensagem de erro NÃO DEVE exibir o valor de nenhuma variável.

#### Cenário: Servidor SMTP ausente em produção
- **QUANDO** a aplicação inicia em produção sem a variável do servidor SMTP
- **ENTÃO** ela encerra com erro
- **E** a mensagem informa qual variável falta, sem exibir valores

#### Cenário: Variável vazia em produção
- **QUANDO** a aplicação inicia em produção com alguma variável de e-mail definida como vazia
- **ENTÃO** ela encerra com erro informando qual variável está vazia, sem exibir valores

#### Cenário: Credencial ou remetente ausente em produção
- **QUANDO** a aplicação inicia em produção sem a senha SMTP ou sem o remetente padrão
- **ENTÃO** ela encerra com erro informando qual variável falta

### Requirement: Links absolutos em e-mails
A aplicação DEVE montar links presentes em e-mails a partir de uma URL base configurável, para
que sejam corretos mesmo quando o e-mail é enviado fora de uma requisição web. Em produção a URL
base é obrigatória, não pode ser vazia e NÃO DEVE ter valor padrão.

#### Cenário: Link em e-mail de desenvolvimento
- **QUANDO** a aplicação envia um e-mail com um link em desenvolvimento
- **ENTÃO** o link começa por `http://127.0.0.1:8000`

#### Cenário: URL base ausente em produção
- **QUANDO** a aplicação inicia em produção sem a URL base
- **ENTÃO** ela encerra com erro informando qual variável falta

### Requirement: Envio de e-mail a partir de templates
A aplicação DEVE oferecer um modo único de enviar e-mail renderizado a partir de templates, com
versão em texto puro e versão em HTML, em português do Brasil e com layout-base compartilhado. A
versão em texto DEVE ser sempre enviada, para clientes que não exibem HTML.

#### Cenário: Mensagem com texto e HTML
- **QUANDO** um e-mail é enviado a partir de um template
- **ENTÃO** a mensagem contém a parte em texto puro e a parte em HTML
- **E** o assunto e o corpo estão em português do Brasil

#### Cenário: Conteúdo escapado
- **QUANDO** o contexto do e-mail contém caracteres de marcação HTML
- **ENTÃO** a versão em HTML os escapa
- **E** a versão em texto os mantém literais

### Requirement: Validação do envio por comando
A aplicação DEVE oferecer um comando de linha que envia um e-mail de teste a um endereço
informado, para validar a configuração de ponta a ponta. O comando NÃO DEVE exibir credenciais.

#### Cenário: E-mail de teste em desenvolvimento
- **QUANDO** o desenvolvedor roda o comando de e-mail de teste com um endereço
- **ENTÃO** o e-mail aparece na caixa de entrada local
- **E** o comando termina com sucesso

#### Cenário: Falha na entrega
- **QUANDO** o comando roda e o servidor SMTP está inacessível
- **ENTÃO** o comando termina com erro e uma mensagem que identifica a falha de conexão
