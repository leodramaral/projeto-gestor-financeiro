# Design

## Context

Motivação em `proposal.md`; requisitos em `specs/assistant/spec.md`. Estado atual (`assistant/`):

- `tools.py` tem duas ferramentas. `run_tool` devolve um `ToolOutcome` com `content` (JSON para o modelo),
  `data` (o resultado de gastos, quando a consulta deu certo) e `decline`. Erros viram `{"error": "..."}` em
  inglês, sem dizer o que corrigir. O mês é estrito: formato, piso (`MIN_MONTH`, 2000-01) e futuro são
  `ToolError`.
- `service._Question` guarda os `data` bem-sucedidos em `self.results` e, no texto final, chama
  `guard.check_answer(text, self.results)`. Uma rejeição vira `Answer(REJECTED, texto fixo, tokens, reason)`; a
  view mostra qualquer desfecho que não seja `TEXT` como bolha do assistente, fora do histórico, e registra só
  o motivo.
- `guard.py` extrai valores `R$ x`/`x reais`, tira do texto os nomes de categoria e exige que cada valor
  esteja em `{total} ∪ {amount das categorias}`; recusa escala ("mil", "milhão", "k") e texto acima de 1200
  caracteres. **Não olha percentuais** e lê direto `result["total"]` e `result["categories"]`.
- A primeira volta usa `tool_choice: "required"`. Por isso `NO_QUERY` só acontece quando **toda** consulta da
  pergunta falhou: é o caso do mês futuro, em que o texto honesto do modelo é descartado e a tela mostra a
  recusa de assunto (achado em aberto do `design.md` arquivado de `7-assistente-categorias`).
- Restrições do provedor (mesmo `design.md` arquivado): cota de 8 mil tokens por minuto por chave e cerca de
  1.500 tokens por pergunta no escopo. Toda chamada a mais ao modelo é custo.

## Goals / Non-Goals

**Goals:**
- O guard passa a trabalhar com os **fatos** que cada ferramenta declara, sem conhecer o formato dela.
- O modelo pode calcular e o código confere a conta, e os percentuais passam a ser conferidos.
- Mês que não pode ser consultado termina a pergunta com texto fixo, gastando **menos** tokens que hoje.
- Cada erro das ferramentas diz o que corrigir, com testes que conferem o conteúdo.

**Non-Goals:**
- Ferramentas novas, nova tentativa automática, número solto sem `R$`/`%`, valor com escala, mudança no
  histórico, nos créditos ou no provedor.
- Provar que o **rótulo** da conta está certo (ver Riscos).

## Decisions

### Fatos declarados pela ferramenta

`ToolOutcome` ganha `facts`, ao lado de `data` (o dicionário do resultado, que continua útil nos testes): um
`Facts` imutável, definido em `assistant/facts.py` para que o guard o importe sem depender de `tools.py`, com
os **termos** que o modelo pode citar, cada um com um rótulo e um valor.

```
Facts
  amounts : tuple[Term]   Term(label, value:Decimal)   ex.: ("Moradia", 1500.00), (None, 2710.00)  # None = total
  percents: tuple[Term]   Term(label, value:int)       ex.: ("Moradia", 55)
  names   : frozenset[str]  nomes de dado do usuário que o guard tira do texto antes de ler números
```

`_spending_by_category` monta o `Facts` a partir do resultado que já devolve (o JSON para o modelo não muda).
O serviço junta os `Facts` das consultas bem-sucedidas da pergunta e o guard recebe só essa lista. O guard
deixa de conhecer `total` e `categories`: ferramenta nova só precisa declarar os próprios fatos.

*Alternativa:* o guard continuar lendo o dicionário e ganhar um ramo por ferramenta. Descartada: era o
acoplamento que a Issue pede para remover.

### Conta verificada, termos à vista

Um valor em reais citado no texto (extraído como hoje) é aceito se:

1. está nos valores dos termos (citado), ou
2. é a **soma de 2 ou 3** termos distintos, ou a **diferença de 2** termos, e cada termo está **à vista**.

Um termo está à vista quando o **valor dele aparece no texto** ou quando o **nome da categoria aparece no
texto** (comparação sem diferença de maiúsculas); o termo sem rótulo (o total) está à vista pela palavra
"total". A igualdade é exata, em centavos.

*Por que exigir termos à vista:* sem isso, com 20 categorias quase qualquer valor coincide com alguma
combinação de 3 termos, e a prova vira ilusão. À vista, o guard só testa as combinações dos termos que o texto
realmente mencionou (em geral 2 a 4), e o usuário consegue conferir a conta lendo a frase.

*Alternativa:* aceitar qualquer subconjunto. Descartada pelo motivo acima. *Alternativa:* só somas de 2.
Descartada: "Moradia, Alimentação e Transporte somam…" é a conta mais natural depois da de 2.

### Percentuais

O guard passa a ler todo número seguido de `%` (`55%`, `55 %`, `55,5%`), depois de tirar os nomes dos dados do
usuário (um nome pode conter "%"). Um percentual é aceito se:

1. é o `percent` de um termo (citado), ou
2. é a soma de 2 ou 3 percentuais de termos à vista, com tolerância de 1 ponto por termo (cada um já vem
   arredondado), ou
3. está a até 1 ponto de `100 × a / b`, com `a` e `b` termos de valor à vista e `a ≠ b`.

O percentual devolvido pela ferramenta é inteiro e vem de `category_slices` (`ROUND_HALF_UP`); a tolerância
existe porque o modelo pode arredondar de outro jeito.

### Erro de período encerra a pergunta com texto fixo

`ToolError` ganha uma subclasse `PeriodError` para mês futuro e mês anterior ao piso. O `ToolOutcome` desses
erros carrega `period=True`, e o `content` devolvido ao modelo continua com a mensagem orientadora.
No serviço, **ao fim de cada rodada de ferramentas**, se alguma chamada da pergunta teve erro de período e
**nenhuma consulta da pergunta teve sucesso**, a pergunta termina ali com
`Answer(REJECTED, messages.period_unavailable(...), tokens, reason="period")`, sem nova chamada ao modelo.

- Economiza uma chamada (a que o modelo usaria só para explicar) em vez de gastar uma a mais.
- Se na mesma rodada houve uma consulta com sucesso, a pergunta **não** termina: o modelo recebe os dois
  resultados e o texto passa pelo guard normalmente.
- Mês em formato inválido ou inexistente continua voltando ao modelo, que pode se corrigir (a mensagem
  orienta), e, se ele terminar sem consulta bem-sucedida, vale o `NO_QUERY` de hoje (recusa de assunto).

O texto fixo (`messages.period_unavailable`) usa o rótulo do mês atual de `MonthView.label`:

> Não consigo consultar esse mês. Só dá para consultar de janeiro de 2000 até {outubro de 2026}. Tente, por
> exemplo: Quanto gastei com transporte em agosto?

A view não muda: ela já mostra qualquer desfecho que não seja `TEXT` como resposta do assistente, fora do
histórico, com o campo limpo, e já registra o motivo.

*Alternativa:* deixar o modelo explicar em texto e aceitá-lo quando não tiver valor em reais. Descartada: gasta
uma chamada, reabre o risco de divagação sem números e não é determinística.

### Mensagens de erro das ferramentas (em inglês, por serem texto para o modelo)

| Erro | Mensagem |
|---|---|
| JSON inválido | `The arguments are not valid JSON. Send an object such as {"month": "2026-08"}.` |
| Não é objeto | `The arguments must be a JSON object, such as {"month": "2026-08"}.` |
| Argumento extra | `Unexpected argument(s): x. This tool accepts only: month.` (a lista vem de `ALLOWED_ARGUMENTS`) |
| Formato do mês | `The month must be a string in the format YYYY-MM, such as 2026-08.` |
| Mês inexistente | `That month does not exist. Use YYYY-MM with a month from 01 to 12, such as 2026-08.` |
| Antes do piso | `The month must be January 2000 or later. Use a month from 2000-01 to {atual}.` |
| Futuro | `That month is in the future. The latest month available is {atual}.` |
| Ferramenta desconhecida | `Unknown tool: x. Available tools: get_spending_by_category, decline_out_of_scope.` |

Os testes passam a conferir a parte orientadora (o exemplo, o último mês, a lista), e não só `"error" in …`.

### Prompt

A regra 4 de `prompts.py` deixa de proibir somar, arredondar e calcular. Passa a dizer: cite valores no formato
`R$ 1.234,56`; pode somar, subtrair e calcular porcentagens **só com os valores devolvidos**; ao fazer uma
conta, escreva os termos (nomes das categorias ou valores) e o resultado; nunca abrevie ("mil"); diga a que mês
os valores se referem. O resto do prompt não muda.

## Risks / Trade-offs

- **O guard prova a conta, não o rótulo.** "Moradia e Transporte somam R$ 2.400,00" passa se Moradia e
  Alimentação somam isso e as três categorias aparecem no texto. O risco já existia (citar o valor certo com o
  nome errado) e cresce um pouco. → O limite de 3 termos, os termos à vista e a igualdade em centavos
  reduzem a chance; o aviso fixo de "sugestão automatizada" continua na tela.
- **Falso positivo**: o modelo calcula certo e não mostra os termos, ou escreve a conta de um jeito que o
  guard não reconhece. O usuário vê "Não consegui montar uma resposta confiável". → A regra 4 pede para mostrar
  os termos; a verificação com o provedor real (tarefa 6) conta quantas respostas legítimas caem nisso, como a
  7.1 da change anterior. Nova tentativa automática ficou fora de propósito (custo de tokens).
- **Percentual por razão com tolerância de 1 ponto** aceita valores próximos do real. → Só vale com os dois
  termos à vista, e o percentual devolvido pela ferramenta continua sendo o caminho normal.
- **Número solto e escala:** "1500" sem `R$` e "R$ 1,5 mil" não mudam: o primeiro passa, o segundo é
  rejeitado, como hoje.
- **Texto fixo do período não acompanha o tom do modelo.** Aceito: é o mesmo trade-off das recusas e da ajuda.
- **Custo da verificação real:** a cota de 8 mil tokens por minuto limita o ritmo; poucas perguntas, espaçadas,
  como na verificação da change anterior.

## Migration Plan

Sem migração nem variável nova. Reverter é desfazer o PR.

## Open Questions

- Texto exato da mensagem de período e das mensagens do modelo: ajustáveis na implementação sem mudar o spec.
- Número solto sem `R$`/`%` e valor com escala ficam para outra change, se a verificação real mostrar que passam
  com frequência.

## Verificação com o provedor real

Feita em 19/10/2026 contra a Groq com `openai/gpt-oss-120b`, pelo `manage.py shell`, com **dados fictícios**
(uma usuária, três categorias, cinco despesas em agosto e setembro) criados dentro de uma transação desfeita ao
final (nada ficou no banco). Oito perguntas, uma a cada 20 s por causa da cota de 8 mil tokens por minuto.

| # | Pergunta | Desfecho | Tokens |
|---|---|---|---|
| 1 | Quanto gastei com transporte em agosto? | Resposta aceita, `R$ 842,10` | 1.669 |
| 2 | Quanto gastei somando moradia e alimentação em setembro? | Aceita: "Moradia (R$ 1.500,00) e Alimentação (R$ 900,00) somam R$ 2.400,00" | 1.720 |
| 3 | Quanto a mais gastei com moradia do que com alimentação em setembro? | Aceita: diferença `R$ 600,00`, com a conta escrita | 1.769 |
| 4 | Qual a porcentagem da moradia nos meus gastos de setembro? | Aceita: `55 %` | 1.725 |
| 5 | Quantos por cento dos gastos de setembro foram moradia e alimentação juntas? | Aceita: 55 % + 33 % = `88 %` | 1.712 |
| 6 | Quanto gastei em janeiro de 2099? | Texto fixo de período, **1 chamada** | 781 |
| 7 | Quanto gastei em dezembro de 1999? | Texto fixo de período, **1 chamada** | 770 |
| 8 | Me dê uma dica de investimento para o meu dinheiro | Recusa fixa | 733 |

- Nenhuma resposta correta foi barrada pelo guard (0 de 5), e o modelo escreveu os termos das contas sem
  ajuste de prompt além da regra 4 nova.
- O modelo escreveu espaço fino sem quebra (`U+202F`) entre o número e o `%` e em volta do sinal de menos
  (`R$ 1.500,00 − R$ 900,00`); o guard aceitou, e um teste fixa isso.
- Uma pergunta no escopo custa cerca de 1.700 tokens (de 1.669 a 1.769), um pouco acima dos cerca de 1.500 da
  verificação da change anterior, por causa da regra 4 mais longa; o período sem dados custa cerca de 780
  (uma chamada, sem a segunda que o modelo gastaria só para explicar). Total da rodada: 10.879 tokens.
- Amostra pequena e um único dia: mostra o caminho feliz e o encerramento por período, não a taxa de falso
  positivo do guard.

