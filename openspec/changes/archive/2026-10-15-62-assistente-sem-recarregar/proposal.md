# Proposal

## Why

Na tela do assistente (Issue #62), cada mensagem enviada recarrega a página inteira: o formulário é um `POST` comum e a view responde com redirecionamento para o `GET`. A tela pisca, o scroll volta ao topo e a pergunta só aparece junto com a resposta, de 1 a 2 segundos depois, sem outro retorno visual além do botão desativado. Para um chat, a experiência é fraca. A change `7-assistente-categorias` já está mesclada, então o envio pode ser melhorado agora.

## What Changes

- Melhoria progressiva: **com JavaScript**, o envio acontece sem recarregar a página; **sem JavaScript**, o formulário continua funcionando como hoje (post/redirect/get).
- O Alpine intercepta o envio e faz `fetch` do mesmo `POST` para a mesma rota, sem endpoint novo e sem mudar a lógica da view. A resposta já é a página inteira; o JavaScript troca só as regiões da conversa, do aviso, dos créditos e dos erros do campo.
- A pergunta aparece na hora, como o bloco cinza de sempre, seguida de um indicador de espera do assistente. O campo é limpo, mantém o foco, e a conversa rola até a última mensagem.
- Os avisos deixam de ser uma caixa solta acima do campo e passam a fazer parte do chat, conforme quem fala:
  - **Recusa de assunto, ajuda de cortesia e resposta não confiável** viram um turno efêmero: a pergunta em bolha cinza e a resposta em bolha do assistente. O campo é limpo, e o turno não entra na sessão nem vai ao modelo.
  - **Falha do provedor** (indisponível, limite de taxa, timeout) vira uma linha de erro no chat, com a pergunta marcada como não enviada, e o texto digitado **volta ao campo**.
  - **Erro de validação** continua sob o campo, com o texto mantido.
  - **Créditos esgotados e assistente sem chave** viram uma mensagem dentro da caixa de envio, com o botão desativado (o texto digitado é mantido, pois nada foi consumido).
- O medidor de créditos da caixa é simplificado: a barra, a palavra "Créditos" e o contador de porcentagem usada, que esquenta até o vermelho ao chegar a 100%. Some a repetição "Créditos de hoje: X de Y tokens", e a tela nunca mais diz "tokens" (só "créditos"); os números absolutos ficam para leitor de tela.
- O saldo de créditos é atualizado a cada resposta.
- Acessibilidade: a região da conversa avisa leitores de tela quando uma resposta chega (`aria-live`) e o foco não se perde.
- `design/assistant.figcraft` e a nota de divergências do `AGENTS.md` passam a mostrar o estado de espera, a recusa em bolha, o erro em linha, os créditos esgotados na caixa e o medidor nas quatro cores.

Fora do escopo: mudar os textos dos avisos, streaming da resposta token a token; histórico persistente de conversas; outras mudanças no visual aprovado.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `assistant`: "Pergunta e resposta" ganha o envio sem recarregar a página (degradação sem JavaScript, retorno imediato, atualização dos créditos) e os avisos dentro do chat; "Tela do assistente protegida por login" ganha o estado de espera, o anúncio para leitores de tela e o medidor de créditos; "Créditos diários em tokens" passa a mostrar só "créditos", em porcentagem com cores, e a mensagem de esgotado vai para dentro da caixa.

## Impact

- **Código:** `assistant/views.py` (turno efêmero no lugar de `notice`, estado da caixa, faixa do medidor), `templates/assistant/chat.html` (regiões identificáveis, turnos, indicador de espera, medidor, `aria-live`), um script do componente Alpine em `static/js/` e `assistant/forms.py` (o atalho Enter do campo). A lógica de créditos, histórico e provedor **não muda**.
- **Testes:** `assistant/tests/test_views.py` cobre o que é testável em Python (mesmo fluxo sem JavaScript, ids das regiões e conteúdo trocado); o comportamento do navegador é verificado à mão, nos temas claro e escuro e no celular.
- **Design:** `design/assistant.figcraft` e `AGENTS.md`.
- **Ícones (pedido durante a change):** todos os ícones da interface passam a vir da Lucide, pelo template tag `lucide` e a pasta `core/icons/`; os `.figcraft` das outras telas ainda mostram os ícones antigos.
- **Dependências:** nenhuma nova (Alpine e `fetch` já existem). Sem migração.
