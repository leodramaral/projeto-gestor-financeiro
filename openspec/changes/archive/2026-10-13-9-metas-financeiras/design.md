# Design

## Context

- A Issue #9 é a única pendente de domínio que depende só do Item 1 (contas). Lançamentos e categorias já
  existem na app `transactions` (`Category`, `Transaction`, `ModalMixin`, `MoneyField`, `static/js/transaction-modal.js`);
  as telas deles são o padrão visual a seguir (`templates/transactions/*`, cartão `rounded-2xl border`,
  botão `bg-brand-500`, modal em `<dialog>`).
- O design vive em `design/<tela>.figcraft` (convenção no `AGENTS.md`, spec `screen-design`; fonte Outfit
  instalada; MCP `figcraft` registrado). Aqui o fluxo se inverte em relação à #53/#55: a tela **ainda não
  existe**, então o design vem antes do código e o código o segue; ao final, o app é conferido contra ele.
- Ainda não há como tocar o domínio fora de uma change; esta é a change que autoriza `goals`.

## Goals / Non-Goals

**Goals:**
- Duas opções de layout para a lista de metas, comparáveis lado a lado, para o usuário escolher.
- Metas com regras testadas no model e no formulário, isoladas por usuário, sem dependência nova.

**Non-Goals:**
- Integrar metas a lançamentos, saldo ou painel; histórico de aportes; notificações de prazo (ver proposal).

## Decisions

### Design: duas opções no FigCraft (decisão do usuário pendente)

Um arquivo `design/goals.figcraft` com duas páginas, cada uma com os mesmos 5 frames de lista:
`desktop claro · com metas` (ativas e concluídas), `desktop escuro · com metas`,
`mobile claro · com metas`, `desktop claro · vazio` e `mobile claro · vazio`.
Uma terceira página, **comum**, tem o modal de meta (`desktop claro · modal padrão`,
`desktop claro · modal com erros`, `mobile claro · modal padrão`) e a confirmação de exclusão. O formulário
não é opção: tem os mesmos campos nas duas.

Dado de exemplo (hoje é 13/10/2026, usuária `Maria Silva`): **Reserva de emergência** R$ 3.250,00 de
R$ 5.000,00 (65 %), prazo 31/12/2026; **Viagem de fim de ano** R$ 600,00 de R$ 2.400,00 (25 %), prazo
15/12/2026; **Presente da Ana** R$ 120,00 de R$ 300,00 (40 %), prazo 30/09/2026 (**atrasada**); **Trocar de
celular** R$ 90,00 de R$ 1.800,00 (5 %), sem prazo; concluída: **Curso de inglês** R$ 500,00 de R$ 500,00
(100 %), concluída em 02/10/2026. Textos de produto propostos: título `Metas`, botão `Nova meta`, seções
`Ativas` e `Concluídas`, ações `Registrar progresso`, `Marcar como concluída`, `Reabrir`, `Editar`,
`Excluir`, selos `Atrasada` e `Sem prazo`, vazio `Você ainda não tem metas.` /
`Defina um objetivo, como poupar R$ 500.` / `Criar a primeira meta`.

- **Opção A — Cartões.** Grade de cartões (1 coluna no mobile, 2 no `md`, 3 no `xl`). Cada cartão: nome e
  selo de prazo no topo, percentual grande, barra, `R$ guardado de R$ alvo` e, no rodapé, o botão
  `Registrar progresso` e o menu `⋯` (Editar, Marcar como concluída, Excluir). Concluídas: mesma grade,
  cartão esmaecido com ícone de check e a ação `Reabrir`. Mostra mais por meta e é mais visual; ocupa mais
  espaço com muitas metas.
- **Opção B — Lista em linhas.** Um cartão com tabela, como a de lançamentos: colunas Meta (nome + prazo),
  Progresso (barra fina com percentual), Guardado / Alvo e o menu `⋯`; no mobile a linha vira nome, barra e
  valores empilhados. Concluídas em segunda tabela abaixo, com título `Concluídas`. Compacta e consistente
  com Lançamentos; a barra pesa menos.
- **Alternativa descartada: abas Ativas/Concluídas.** Esconderia as concluídas atrás de um clique e exigiria
  estado na URL ou JavaScript; a spec as quer separadas na mesma tela.

Textos do formulário desenhados na página comum (a implementação e `goals/forms.py` devem repeti-los):
rótulos `Nome`, `Valor-alvo`, `Valor já guardado` (ajuda `Total que você já separou para esta meta.`) e
`Prazo` (placeholder `dd/mm/aaaa`, ajuda `Opcional.`); erros `Informe o nome da meta.`,
`O valor deve ser maior que zero.` e `O prazo não pode estar no passado.`; ações `Salvar` e `Cancelar`;
confirmação `Tem certeza de que deseja excluir esta meta? Esta ação não pode ser desfeita.` com Nome,
Valor-alvo, Valor guardado e Prazo, e `Excluir`. O modal de progresso (`Registrar progresso`) mostra o nome
da meta e só o campo `Valor já guardado`.

Frames finais de `design/goals.figcraft` (só a Opção B): página `goals` com `desktop · claro · com metas`,
`desktop · claro · vazio`, `desktop · escuro · com metas`, `mobile · claro · com metas` e
`mobile · claro · vazio`; página `goals — modais` com `desktop · claro · modal padrão`, `modal calendário` (seletor de data aberto), `modal com erros`,
`modal progresso`, `exclusão` e `mobile · claro · modal padrão` (todos prefixados por `goals · `).

Divergências do desenho (limites da ferramenta ou do processo): sem foco, hover nem `shadow-theme-*`; o
ícone de `Metas` (alvo) e o de tema (lua/sol) são desenhados à mão, não o SVG do app; o frame é o tamanho da
janela (1440×900 ou 390×844), sem a rolagem; o ícone de hambúrguer do cabeçalho é outro; o campo de data
mostra `dd/mm/aaaa` (o do navegador segue o idioma dele); o fundo dos modais é a
casca da tela só com o título, sem a lista; menu `⋯` aberto não é desenhado (as ações dele vêm do texto acima).
O design foi gerado por um script (comandos do `figcraft-cli run`), então o arquivo não usa componentes do
FigCraft: cabeçalho e barra lateral são camadas repetidas em cada frame.

**Escolha do usuário: Opção B — Lista em linhas** (13/10/2026). Fica consistente com a lista de Lançamentos
e é mais compacta. A **Opção A — Cartões** (grade de 3 colunas com percentual grande, barra e botão em cada
cartão; mais visual, mas ocupa mais espaço com muitas metas) foi descartada e sai do `.figcraft` na tarefa 6.1.
Como a Opção B só mostra o botão `Registrar progresso` no desktop e no mobile as ações ficam no menu `⋯`, o
menu de cada meta DEVE conter `Registrar progresso`, `Editar`, `Marcar como concluída` (ou `Reabrir`, nas
concluídas) e `Excluir`.

### Modelo de dados

`goals.Goal`: `user` (FK `CASCADE`, `related_name="goals"`), `name` (`CharField(60)`), `target_amount` e
`saved_amount` (`DecimalField(14, 2)`, o segundo com padrão `0`), `deadline` (`DateField`, nulo),
`completed_at` (`DateTimeField`, nulo), `created_at`, `updated_at`. Restrições no banco: `target_amount > 0`
e `saved_amount >= 0`. Índice em `(user, completed_at)`.

- **Concluída = `completed_at` preenchido**, em vez de um booleano: uma coluna só, já dá a ordem das
  concluídas e a data para exibir. Alternativa descartada: enum de status (só há dois estados).
- **Valor guardado é o total, não uma soma de aportes**: simples, corrigível por edição e é o que a Issue
  pede ("quanto já foi guardado"). Alternativa descartada: model `Contribution` com histórico (custo de tela,
  de migração e de regra sem exigência na Issue); fica registrada como possível evolução.
- **Progresso derivado**, nunca gravado: propriedade `progress_percent = min(100, saved * 100 // target)`
  (inteiro, piso, assim `99,9 %` não vira 100 e só quem atingiu o alvo mostra 100). `is_overdue` = ativa e
  `deadline < hoje local`. Datas com `timezone.localdate()`.
- **Dinheiro** com `MoneyField` e `MONEY_MASK_ATTRS` de `transactions.forms` (formato `1.234,56`, máscara
  em centavos); importados, não copiados.

### Formulários e regras

- `GoalForm` (nome, valor-alvo, valor guardado, prazo): nome com `strip`; alvo ≥ 0,01; guardado ≥ 0;
  **prazo no passado só é recusado se o campo mudou** (`"deadline" in changed_data`), assim registrar
  progresso numa meta atrasada não obriga a mudar o prazo. Mensagens em português no padrão de
  `TransactionForm`.
- `GoalProgressForm` (só `saved_amount`): é o "Registrar progresso" do cartão/linha, para não abrir o
  formulário inteiro. Mesma validação do campo.

### Views, rotas e reaproveitamento

- App `goals/` com rotas sob `/goals/`: `""` (lista), `new/`, `<id>/edit/`, `<id>/progress/`,
  `<id>/delete/`, `<id>/complete/` e `<id>/reopen/` (as duas últimas só POST; GET responde 405 sem alterar).
  Namespace `goals`.
- Todas com `LoginRequiredMixin` e queryset `Goal.objects.filter(user=request.user)`: meta alheia é 404, como
  `OwnedQuerysetMixin` em `transactions`. A lista traz `active` (prazo asc com nulos por último, depois
  `-created_at`) e `completed` (`-completed_at`).
- Modal: `ModalMixin` é **importado** de `transactions.views` e o `transaction-modal.js` é reusado (os ids
  `transaction-modal` e `transaction-modal-body` servem à página de metas sem mudança). Alternativa descartada:
  mover o mixin e o script para `core` agora — refatoração de código existente sem relação com a Issue; vira
  Issue se um terceiro uso aparecer.
- Barra de progresso: `div role="progressbar"` com `aria-valuenow`, `aria-valuemin/max` e `aria-label`, e
  largura por `style="width: N%"` (não há CSP no projeto). Cores `bg-brand-500` e, concluída, `bg-success-500`.
- Barra lateral: item "Metas" em `templates/partials/sidebar.html`, ativo por
  `request.resolver_match.app_name == 'goals'`.

### Seletor de data (flatpickr)

- **flatpickr 4.6.13** (MIT), o mesmo que o TailAdmin usa na página de formulários. Dependência npm exata,
  copiada para `static/dist/` por `scripts/copy-alpine.mjs` (JS e locale `pt`); o CSS base entra no
  `frontend/style.css` por `@import` e os ajustes de tema (claro/escuro, cores da marca) são portados do
  CSS do TailAdmin, só a parte de data única. Alternativa descartada: `<input type="date">` nativo (o
  visual muda por navegador e não segue o tema).
- **Melhoria progressiva:** o widget continua `type="date"` no servidor; `static/js/datepicker.js` inicializa
  todo `input[data-datepicker]`, inclusive os que chegam no modal (o modal injeta HTML, que não executa
  `<script>`; um `MutationObserver` cobre isso). Opções: `altInput` com `d/m/Y` na tela e `Y-m-d` no envio,
  `static: true` (o calendário fica dentro do `<dialog>`, que está no topo da pilha), locale `pt`.
- **`minDate` = hoje só quando vale:** se o campo já tem um prazo anterior a hoje (meta atrasada), o JS não
  aplica `minDate`, senão o flatpickr descartaria o valor. A regra de verdade continua no formulário.
- O campo tem um parcial próprio (`goals/partials/date_field.html`) com o ícone de calendário à direita.

### Verificação do design contra o app

Depois de implementado, o Playwright captura a tela no app (usuário de teste do banco de dev, com o dado de
exemplo acima) e compara com o `screenshot` dos frames da opção escolhida; divergência que não seja limite
da ferramenta é corrigida no design ou no código. A página da opção descartada e a de frames temporários são
removidas do `.figcraft` antes de arquivar (spec `screen-design`).

## Risks / Trade-offs

- [Escolha demora e bloqueia a implementação] → a seção 1 é pequena e termina na escolha; o resto do plano
  não depende de qual opção ganha (a spec descreve comportamento, não layout).
- [Valor guardado como total pode ser sobrescrito por engano] → tela de progresso mostra o valor atual
  preenchido; histórico de aportes fica como evolução possível.
- [`ModalMixin` importado de outra app acopla `goals` a `transactions`] → acoplamento já aceito para o
  `StyledFormMixin` de `accounts`; refatorar só com um terceiro uso.
- [`.figcraft` binário: o PR não mostra o diff] → mesmo custo aceito em #53 e #55; quem revisa exporta os
  PNGs (`design/png/`, não versionado).
- [FigCraft é alpha e pode não reproduzir sombras ou foco] → divergências registradas no `AGENTS.md`, como
  nas changes de design anteriores.
- [Cobertura cair abaixo do piso] → testes de model, forms, views, isolamento e sidebar escritos junto com o
  código, conferidos com `pytest --cov`.

## Migration Plan

Migration `goals/0001_initial` cria `goals_goal` (tabela nova, sem dados a migrar). Rollback: reverter o
commit e `migrate goals zero`; nenhuma tabela existente é tocada. Em worktree, `docker compose up -d` migra o
banco da worktree.
