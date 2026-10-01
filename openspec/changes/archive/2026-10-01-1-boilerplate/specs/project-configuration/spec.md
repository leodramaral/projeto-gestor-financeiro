## ADDED Requirements

### Requirement: Configuração por ambiente
A aplicação DEVE ter um módulo de configuração comum e um módulo por ambiente (`dev`, `test`,
`prod`), e `DJANGO_SETTINGS_MODULE` DEVE escolher qual deles vale em cada execução.

#### Cenário: Ambiente de produção
- **QUANDO** a aplicação inicia com `DJANGO_SETTINGS_MODULE=config.settings.prod`
- **ENTÃO** `DEBUG` está desligado
- **E** `ALLOWED_HOSTS` vem da variável de ambiente

#### Cenário: Ambiente de desenvolvimento
- **QUANDO** a aplicação inicia com `DJANGO_SETTINGS_MODULE=config.settings.dev`
- **ENTÃO** `DEBUG` está ligado

### Requirement: Segredos somente por variável de ambiente
A aplicação NÃO DEVE conter segredo no código nem no repositório, e DEVE falhar ao iniciar quando
uma variável obrigatória estiver ausente.

#### Cenário: Variável obrigatória ausente
- **QUANDO** a aplicação inicia sem `SECRET_KEY` ou sem `DATABASE_URL`
- **ENTÃO** ela encerra com erro
- **E** a mensagem informa qual variável falta, sem exibir valores
