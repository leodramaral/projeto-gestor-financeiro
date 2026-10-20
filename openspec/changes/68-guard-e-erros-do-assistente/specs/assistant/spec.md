# Spec Delta

## MODIFIED Requirements

### Requirement: Consulta de gastos por categoria isolada por usuário
O assistente DEVE obter os dados por uma única ferramenta de dados, a de gastos por categoria, que devolve, para um
mês, o total e, por categoria, nome, valor e porcentagem das despesas. A ferramenta DEVE usar sempre o
usuário autenticado e NÃO DEVE aceitar identificação de usuário vinda do modelo. O mês DEVE ser `AAAA-MM`
e, quando omitido, o mês atual. Mês em formato inválido, anterior a janeiro de 2000 ou futuro DEVE gerar erro devolvido ao modelo, sem
consulta ao banco. Todo erro devolvido ao modelo (mês, argumentos, ferramenta desconhecida) DEVE dizer o que
corrigir: o formato esperado com um exemplo, o primeiro e o último mês consultáveis, os argumentos aceitos ou as
ferramentas disponíveis. O prompt enviado ao modelo DEVE conter apenas dados agregados do usuário autenticado.

#### Cenário: Mês informado
- **QUANDO** o modelo pede os gastos de `2026-08`
- **ENTÃO** a ferramenta devolve o total e os gastos por categoria de agosto de 2026
- **E** só entram despesas do usuário autenticado

#### Cenário: Mês omitido
- **QUANDO** o modelo chama a ferramenta sem mês
- **ENTÃO** ela usa o mês atual

#### Cenário: Mês sem despesas
- **QUANDO** o usuário não tem despesas no mês pedido
- **ENTÃO** a ferramenta devolve total zero e nenhuma categoria

#### Cenário: Mês inválido, anterior ao piso ou futuro
- **QUANDO** o modelo pede `2026-13`, `agosto`, `0001-01`, `2024-12` ou um mês depois do atual
- **ENTÃO** a ferramenta devolve um erro ao modelo
- **E** nenhuma consulta ao banco é feita

#### Cenário: Erro que orienta a correção
- **QUANDO** o modelo pede `agosto`, `2026-13`, um mês futuro, um argumento que não existe ou uma ferramenta
  que não existe
- **ENTÃO** o erro devolvido diz o formato esperado com um exemplo, o último mês consultável, os argumentos
  aceitos ou as ferramentas disponíveis, respectivamente

#### Cenário: Dados de outro usuário
- **QUANDO** dois usuários têm despesas no mesmo mês e o primeiro pergunta
- **ENTÃO** nenhum valor, categoria ou lançamento do segundo aparece na ferramenta nem no prompt

#### Cenário: Usuário forjado
- **QUANDO** o modelo passa um identificador de usuário nos argumentos da ferramenta
- **ENTÃO** o argumento é recusado e os dados continuam sendo os do usuário autenticado

### Requirement: Resposta ancorada nos dados
A aplicação DEVE aceitar o texto final do modelo apenas se, naquela pergunta, a ferramenta de gastos por
categoria foi chamada e devolveu um resultado com sucesso. O modelo PODE calcular a partir dos valores
devolvidos, e a aplicação DEVE conferir a conta. Todo valor em reais citado no texto (como `R$ 1.234,56`,
escrito com algarismos) DEVE constar dos resultados da ferramenta daquela pergunta, como total ou como valor de
categoria, ou DEVE ser a soma de dois ou três desses valores ou a diferença de dois deles. O nome de uma
categoria citado no texto não conta como valor. Os termos de uma conta DEVEM estar à vista no texto: cada um
aparece como valor ou pelo nome da categoria (ou pela palavra "total", para o total). Todo percentual citado
(como `55%`) DEVE constar dos resultados ou ser a razão entre dois valores devolvidos, ou a soma de percentuais
devolvidos, com tolerância de arredondamento. Valor arredondado com "mil", "milhão" ou "k" NÃO DEVE ser aceito,
e o texto DEVE ter no máximo 1200 caracteres. O texto que falhar em qualquer dessas checagens NÃO DEVE ser
exibido: a aplicação DEVE mostrar uma mensagem fixa no lugar, a de recusa de assunto quando não houve consulta
bem-sucedida e a de resposta não confiável nos demais casos, sem repetir a chamada. Quando a pergunta pede um
mês futuro ou anterior a janeiro de 2000 e nenhuma consulta da pergunta teve sucesso, a aplicação DEVE encerrar
a pergunta sem nova chamada ao modelo e mostrar um texto fixo que diz que o mês não pode ser consultado e até
quando dá para consultar, no lugar da recusa de assunto.

#### Cenário: Resposta com consulta e valores certos
- **QUANDO** o modelo consulta os gastos de agosto e responde citando `R$ 842,10`, valor da categoria
  Transporte devolvido pela ferramenta
- **ENTÃO** a resposta é exibida

#### Cenário: Soma verificável
- **QUANDO** o modelo cita `R$ 2.400,00` como a soma de Moradia (`R$ 1.500,00`) e Alimentação (`R$ 900,00`),
  valores devolvidos pela ferramenta, e as duas categorias aparecem no texto
- **ENTÃO** a resposta é exibida

#### Cenário: Diferença verificável
- **QUANDO** o modelo cita `R$ 600,00` como a diferença entre Moradia (`R$ 1.500,00`) e Alimentação
  (`R$ 900,00`), e as duas categorias aparecem no texto
- **ENTÃO** a resposta é exibida

#### Cenário: Conta que não confere
- **QUANDO** o texto cita `R$ 600,00` como a diferença entre Moradia e Transporte (`R$ 310,00`), cuja diferença é
  `R$ 1.190,00`
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Termos fora de vista
- **QUANDO** o texto cita um valor que é a soma de dois valores devolvidos, mas nem o valor nem o nome de
  nenhuma das duas categorias aparecem no texto
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Percentual devolvido
- **QUANDO** o texto diz que Moradia pesa `55%` e a ferramenta devolveu 55 para ela
- **ENTÃO** a resposta é exibida

#### Cenário: Percentual calculado
- **QUANDO** o texto diz que Moradia e Alimentação pesam juntas `88%` e a ferramenta devolveu 55 e 33 para elas
- **ENTÃO** a resposta é exibida
- **E** o mesmo vale para um percentual que seja a razão entre dois valores devolvidos, como `Alimentação` sobre
  `Moradia`, com tolerância de arredondamento

#### Cenário: Percentual que não confere
- **QUANDO** o texto diz que Moradia pesa `80%` e a ferramenta devolveu 55 para ela
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Texto sem consulta
- **QUANDO** o modelo responde em texto sem ter chamado a ferramenta de gastos nem a de recusa
- **ENTÃO** o texto do modelo não é exibido
- **E** a tela mostra o texto fixo de recusa de assunto

#### Cenário: Consulta que falhou
- **QUANDO** a ferramenta devolveu apenas erro de argumento (por exemplo, mês em formato inválido, e não de
  período) e o modelo responde em texto
- **ENTÃO** o texto do modelo não é exibido
- **E** a tela mostra o texto fixo de recusa de assunto

#### Cenário: Mês futuro
- **QUANDO** o usuário pergunta sobre um mês depois do atual e a ferramenta devolve o erro de mês futuro
- **ENTÃO** a pergunta termina sem nova chamada ao modelo
- **E** a tela mostra, como resposta do assistente, o texto fixo que diz que o mês não pode ser consultado e
  que dá para consultar de janeiro de 2000 até o mês atual
- **E** nem a pergunta nem o texto entram no histórico, e os tokens gastos são contados no uso do dia

#### Cenário: Mês anterior ao piso
- **QUANDO** o usuário pergunta sobre um mês anterior a janeiro de 2000
- **ENTÃO** a tela mostra o mesmo texto fixo de período não consultável, sem nova chamada ao modelo

#### Cenário: Um mês válido e um futuro na mesma rodada
- **QUANDO** o modelo consulta, na mesma rodada, um mês com sucesso e um mês futuro com erro
- **ENTÃO** a pergunta não é encerrada pelo erro de período
- **E** o modelo recebe os dois resultados e o texto final é conferido normalmente

#### Cenário: Valor que não consta do resultado
- **QUANDO** o texto do modelo cita `R$ 900,00` e nenhum total nem categoria devolvido pela ferramenta
  tem esse valor, nem ele se obtém por conta com valores devolvidos
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Valor arredondado ou abreviado
- **QUANDO** o texto cita `R$ 1,5 mil`
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Valor de outra pergunta
- **QUANDO** o texto cita um valor que só aparecia no resultado de uma pergunta anterior da conversa
- **ENTÃO** o texto não é exibido, pois só vale o resultado da pergunta atual

#### Cenário: Resposta longa demais
- **QUANDO** o texto do modelo passa de 1200 caracteres
- **ENTÃO** o texto não é exibido
- **E** a tela mostra a mensagem fixa de resposta não confiável

#### Cenário: Texto rejeitado ainda gasta créditos
- **QUANDO** um texto é rejeitado pelas checagens
- **ENTÃO** os tokens das chamadas feitas são contados no uso do dia
