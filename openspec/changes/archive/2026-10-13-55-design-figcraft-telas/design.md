# Design

## Context

- A Issue #53 criou `design/`, a convenção de nomes, a fonte em `design/fonts/` e o `design/signup.figcraft`
  (5 frames). Esta change repete o processo para as demais telas já implementadas; nenhuma infraestrutura nova.
- Telas existentes (rotas em `accounts/urls.py`, `core/urls.py` e `transactions/urls.py`):
  - **Visitante** (`base_auth_split.html`): `login`, `signup_done`, `confirm` (resultado), `resend` e
    `resend_done`, `password_reset`, `password_reset_done`, `password_reset_confirm`.
  - **Painel** (`base.html`, `dashboard_base.html`): `home`, `dashboard_categories` e `dashboard_flow`
    têm gráfico (Chart.js); `dashboard_transactions` e o estado vazio só fazem sentido junto deles. O
    painel inteiro **fica fora**.
  - **Lançamentos** (`transactions/`): lista com filtro por categoria, formulário em modal, confirmação de
    exclusão. **Categorias**: lista, formulário em modal e confirmação de exclusão. **Perfil**: `profile`.
- O design só trabalha com o que o código exibe; os textos vêm dos templates e de `accounts/forms.py`.

## Goals / Non-Goals

**Goals:**
- Um `.figcraft` por tela ou fluxo, fiel ao código, com tema claro e escuro e o mobile.
- Dado de exemplo fictício e coerente entre as telas autenticadas.

**Non-Goals:**
- Telas novas, mudança de template/view/model além da correção de `base_auth.html`, e-mails, PNGs versionados, protótipo com transições.

## Decisions

- **Agrupamento em seis arquivos**, um por tela ou fluxo, porque o `.figcraft` é binário e um arquivo
  único cresceria e geraria conflito de merge a cada ajuste: `login`, `account-confirmation`
  (`signup_done`, `confirm`, `resend`, `resend_done`), `password-reset` (os três passos), `transactions` (lista, modal, exclusão), `categories` (lista, modal, exclusão) e
  `profile`. Alternativa descartada: um arquivo por rota (mais de 15 arquivos, com cabeçalho repetido).
- **Frame e arquivo pelo nome da rota em inglês**, como a spec exige; rotas com hífen viram `_`
  (`category_list`, `transaction_create`, `password_reset_done`). O PNG segue a regra existente, com `-` no lugar de `_` e do separador.
- **Matriz de temas e viewports:** desktop claro, desktop escuro e mobile claro para toda tela; os estados
  extras (erro, vazio, modal, exclusão) só em desktop claro e, quando o layout muda de forma relevante,
  em mobile claro. Isso espelha o cadastro (#53) e limita o tamanho dos arquivos. Estado que o código não
  tem não é desenhado.
- **Geração por script, fora do repositório:** o `.figcraft` é um zip com `document.json`, e o FigCraft só
  recalcula o auto layout ao editar um valor, então os arquivos foram gerados por um script de apoio que
  monta o JSON a partir dos tokens do CSS, reaproveita a logo, o painel de marca e o botão de tema do
  `signup.figcraft`, importa os ícones SVG do app (Lucide e os do TailAdmin) e roda o motor do FigCraft para
  calcular o layout (`figcraft-cli run`). Como na #53, o gerador **não é versionado**: a fonte é o
  `.figcraft`, que se edita no app ou pelo MCP. Cada tela foi conferida contra a captura do app (diferença de
  pixels abaixo de 1% no desktop e de 2% no mobile, na maior parte texto e foco).
- **O painel fica fora por inteiro:** o FigCraft não executa o Chart.js, e aproximar rosca, barras e linhas
  com formas daria um desenho que parece o app e não é. Sem os gráficos, o que sobraria do painel (seletor
  de mês, abas, a aba de lançamentos e o estado vazio, que fala de gráficos) mostraria só a casca e
  repetiria a lista de `transactions`. Um `dashboard.figcraft` chegou a ser feito e foi descartado. Se o painel
  for desejado, vira Issue nova.
- **Dado de exemplo:** usuário `Maria Silva` (`maria@exemplo.com`), um mês fixo e uma lista curta de
  lançamentos (salário, aluguel, mercado, transporte, lazer) com valores iguais onde a mesma lista aparece. As categorias usam os nomes e cores do app (`transactions` fornece as
  padrão). O mesmo conjunto alimenta lançamentos e categorias (a contagem de "Lançamentos" por
  categoria sai dele).
- **Verificação por captura:** para cada tela, tirar a captura do app com o Playwright (usuário de teste
  do banco de dev, mesmos dados) e comparar com o `screenshot` do frame, como na #53. O que divergir e não
  for limite da ferramenta é corrigido no design.
- **Divergências conhecidas** vão para a convenção do `AGENTS.md`, como na #53, em vez de numa nova
  seção: ausência de foco e hover, menu de ações aberto desenhado só onde a spec o
  exige, sombras (`shadow-theme-*`) quando o FigCraft não as reproduzir.

- **O defeito de `base_auth.html` é corrigido aqui, não registrado como divergência.** O design revelou o
  erro de digitação `relativeflex`; consertá-lo é uma troca de classe (`relative flex`) e deixa app e design
  iguais. A alternativa, desenhar o defeito ou listá-lo no `AGENTS.md`, deixaria o design menos fiel à
  intenção e a divergência sem prazo para acabar. O teste confere que a classe ficou correta.

## Risks / Trade-offs

- [Volume: ~12 telas × 3 variações ≈ 45 frames] → as tasks são por arquivo e cada uma é verificável
  sozinha; dá para fechar o PR em partes sem deixar a spec descumprida só se todas entrarem, então a change
  só arquiva com os seis arquivos.
- [Design e app divergem depois] → a spec e o `AGENTS.md` já exigem atualizar o design na mesma change que
  muda a tela; nenhuma mudança nova aqui.
- [Dado de exemplo incoerente entre telas] → conjunto único definido na task 1.1 e reutilizado.
- [`.figcraft` binário: o PR não mostra o diff] → mesmo custo aceito na #53; quem revisa exporta os PNGs
  (`design/png/`, não versionado).
- [A ferramenta é alpha] → salvar o arquivo a cada tela concluída e conferir com `figcraft-cli info`.

## Migration Plan

Só adiciona arquivos em `design/` e texto no `AGENTS.md`. Rollback: reverter o commit; o app não é afetado.
