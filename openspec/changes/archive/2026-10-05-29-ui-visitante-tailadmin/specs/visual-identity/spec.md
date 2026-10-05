## ADDED Requirements

### Requirement: Layout das telas de visitante
As telas de entrar, criar conta e recuperação de senha DEVEM usar layout dividido, com o formulário de um lado e um painel
de marca do outro (logo do Gestor Financeiro e frase de apresentação), seguindo o padrão das demos
de Sign In, Sign Up e Reset Password do TailAdmin. Em telas estreitas, o layout dividido DEVE virar coluna única e o painel de
marca NÃO DEVE ser exibido. As telas NÃO DEVEM oferecer login social nem alterar campos, validações,
mensagens ou fluxos existentes. O layout DEVE funcionar nos temas claro e escuro, com o controle de
tema acessível, e o painel de marca NÃO DEVE conter o nome ou o logo "TailAdmin".

#### Cenário: Entrar em tela larga
- **QUANDO** um visitante abre a tela de entrar em uma tela larga
- **ENTÃO** o formulário aparece de um lado e o painel de marca do outro
- **E** os campos, o "Lembrar de mim" e os links de recuperação e de cadastro continuam presentes

#### Cenário: Criar conta em tela larga
- **QUANDO** um visitante abre a tela de criar conta em uma tela larga
- **ENTÃO** a tela usa o mesmo layout dividido da tela de entrar
- **E** os requisitos de senha continuam sendo exibidos durante a digitação

#### Cenário: Tela estreita
- **QUANDO** um visitante abre entrar, criar conta ou recuperar senha em uma tela estreita
- **ENTÃO** apenas o formulário é exibido, em coluna única, sem rolagem horizontal

#### Cenário: Recuperar senha
- **QUANDO** um visitante abre a tela de esqueci minha senha
- **ENTÃO** a tela usa o mesmo layout dividido, com o formulário de um lado e o painel de marca do outro
- **E** há um link para voltar ao login no topo da coluna do formulário

#### Cenário: Sem login social
- **QUANDO** qualquer tela de visitante é exibida
- **ENTÃO** ela não contém botões de login social nem divisor "ou" para eles

#### Cenário: Comportamento preservado
- **QUANDO** o visitante envia entrar, criar conta ou recuperar senha, com dados válidos ou inválidos
- **ENTÃO** o resultado, as mensagens de erro e os redirecionamentos são os mesmos de antes da mudança

#### Cenário: Tema escuro
- **QUANDO** o tema escuro está ativo em qualquer tela de visitante
- **ENTÃO** o painel de marca, o cartão e o fundo decorativo usam cores do tema escuro
- **E** o texto mantém contraste mínimo de 4,5:1
