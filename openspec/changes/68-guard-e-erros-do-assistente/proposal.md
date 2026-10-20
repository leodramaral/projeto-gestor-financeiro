# Proposal

## Why

Issue #68. O assistente (beta, só gastos por categoria) tem dois problemas que a verificação da change
`7-assistente-categorias` já deixou registrados (`design.md` arquivado, "Verificação com o provedor real" e
"Riscos"):

- **Pergunta sobre mês futuro mostra a mensagem errada.** O modelo chama a ferramenta, recebe o erro e
  explica em texto, mas o guard descarta o texto (nenhuma consulta bem-sucedida) e a tela mostra a recusa de
  assunto, que não descreve o problema. Além disso, as mensagens de erro devolvidas ao modelo dizem o que deu
  errado, mas quase nunca o que corrigir, e os testes só conferem que "há um erro".
- **O guard de valores é rígido e incompleto.** Ele só aceita o valor em reais que a ferramenta devolveu: uma
  soma ou diferença legítima ("Moradia e Alimentação somam R$ 2.400,00") é barrada, e o prompt proíbe o
  modelo de calcular. Em compensação, **percentuais não são conferidos** ("Moradia pesa 80%" passa mesmo que a
  ferramenta tenha devolvido 55), e o guard lê direto o formato de uma única ferramenta.

## What Changes

- **Mensagens de erro das ferramentas** passam a dizer ao modelo o que corrigir (formato esperado, último mês
  consultável, ferramentas e argumentos disponíveis), e os testes passam a conferir o conteúdo de cada uma.
- **Período sem dados:** mês futuro ou anterior ao piso encerra a pergunta com um **texto fixo do app** (sem
  texto do modelo e sem nova chamada), que diz até quando dá para consultar. No lugar da recusa de assunto.
- **Guard desacoplado:** cada ferramenta declara os fatos que o modelo pode citar (valores, percentuais e nomes
  de dado do usuário), e o guard trabalha só com eles.
- **O modelo pode calcular e o código confere a conta:** um valor em reais é aceito se for citado, soma de até
  três valores devolvidos ou diferença de dois, e os termos da conta precisam estar à vista no texto.
- **Percentuais passam a ser conferidos:** aceitos se citados ou se forem a razão de dois valores devolvidos, com
  tolerância de arredondamento.
- **Prompt:** a regra que proibia somar e calcular é trocada por uma que permite calcular a partir dos valores
  devolvidos e pede para mostrar os termos da conta.
- `design/assistant.figcraft` ganha o estado "período sem dados".

Fora do escopo:

- **Ferramentas novas** (resumo do mês, comparação entre meses, lançamentos, metas): só depois do guard; Issue
  própria.
- **Nova tentativa automática** quando o guard barra a resposta: cada tentativa é uma chamada a mais ao modelo
  e a cota do provedor limita os tokens por minuto.
- Número solto sem `R$` ou `%` e valor com escala ("R$ 1,5 mil", continua rejeitado).
- Resumo e sugestão proativos, escrita pelo assistente, histórico persistido e modelo de reserva.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `assistant`: "Consulta de gastos por categoria isolada por usuário" ganha mensagens de erro que orientam a
  correção e o encerramento com texto fixo para período sem dados; "Resposta ancorada nos dados" passa a
  aceitar cálculo verificável, a conferir percentuais e a tratar a consulta que falhou por período com o texto
  fixo.

## Impact

- **Código:** `assistant/tools.py` (mensagens, fatos por ferramenta, erro de período), `assistant/guard.py`
  (valores derivados, percentuais, entrada pelos fatos), `assistant/service.py` (encerramento por período sem
  dados), `assistant/prompts.py` (regra de cálculo) e `assistant/messages.py` (texto fixo novo). A reserva de
  créditos, o histórico e o provedor **não mudam**.
- **Testes:** `assistant/tests/test_tools.py`, `test_guard.py` e `test_service.py`; tudo com o cliente falso,
  sem chamar o provedor.
- **Design:** `design/assistant.figcraft` e a nota de divergências do `AGENTS.md`.
- **Dependências e migração:** nenhuma.
