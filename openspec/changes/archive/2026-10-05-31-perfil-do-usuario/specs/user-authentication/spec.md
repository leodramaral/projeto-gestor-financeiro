## MODIFIED Requirements

### Requirement: Logout
A aplicação DEVE permitir encerrar a sessão por uma requisição `POST` protegida contra CSRF, acionada
pela ação "Sair" do menu de usuário no cabeçalho, e DEVE levar o usuário ao login. Uma requisição
`GET` NÃO DEVE encerrar a sessão.

#### Cenário: Logout
- **QUANDO** o usuário autenticado aciona "Sair" no menu de usuário
- **ENTÃO** a sessão é encerrada
- **E** ele é redirecionado ao login
- **E** o painel volta a exigir login
