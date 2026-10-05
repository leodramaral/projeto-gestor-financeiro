# Design

## Context

Existe o usuário customizado (`accounts.User`, login por e-mail), o layout TailAdmin com sidebar,
`partials/form_field.html`/`form_errors.html`/`alert.html`, e `StyledFormMixin` em `accounts/forms.py`
com as classes de estilo dos inputs. A home (`core.HomeView`) é um exemplo com `LoginRequiredMixin`.
Não há nenhum model de domínio, e `AGENTS.md` pede que o domínio nasça por change — esta é ela.
Ver `proposal.md` para motivação e escopo.

## Goals / Non-Goals

**Goals:**
- Modelo mínimo e correto para dinheiro (sem `float`), com isolamento por dono garantido na consulta.
- Reaproveitar views genéricas do Django e os parciais/estilos existentes.

**Non-Goals:**
- Categorias, múltiplas contas, filtros, exportação (ver "Fora do escopo" na proposta).

## Decisions

**1. App novo `transactions`, com um model.**
- `Transaction`: `user` (FK, `CASCADE`), `kind` (`TextChoices`: `income`/`expense`), `amount`
  (`DecimalField(14, 2)`), `date` (`DateField`), `description` (`CharField(200)`), `created_at`,
  `updated_at`. `CheckConstraint(amount > 0)` e índice `(user, -date, -id)` para a listagem.
`Transaction` aponta para o **usuário**: o isolamento é `filter(user=request.user)` em um único lugar,
sem join. O tipo é texto (não sinal no valor) para o valor ficar sempre positivo e a regra "valor > 0"
valer igual para os dois tipos.
**Saldo inicial sem model nem tela:** o saldo de partida é uma Entrada comum (ex.: "Saldo inicial").
Um segundo model (`Account`) e uma tela só para um número guardavam a mesma informação que uma entrada
já guarda, e adicionavam rota, formulário, tabela e testes. A Issue pede o "cadastro do saldo inicial";
registrar uma entrada o atende.
*Alternativas descartadas:* `Account` com `initial_balance` e tela própria (versão inicial desta
change, removida: mais código para o mesmo resultado); campo `initial_balance` em `User` (mexe no app
de contas por um dado de domínio). Se um dia houver várias contas, a FK entra por migration aditiva.

**2. Saldo atual calculado no banco, nunca guardado.**
`Sum(amount)` das entradas menos `Sum(amount)` das despesas, via agregação condicional
(`Sum("amount", filter=Q(kind=...))`) sobre **todos** os lançamentos do usuário. Guardar o saldo
exigiria mantê-lo em sincronia a cada criação, edição e exclusão. Por ser calculado, nada diverge.

**3. Valor: `DecimalField` com validação no formulário e no banco.**
`ModelForm` com `MinValueValidator(Decimal("0.01"))` e `max_digits/decimal_places` do model (rejeita
mais de duas casas, NaN e infinito já são recusados pelo `DecimalField` do form). O `CheckConstraint`
é a rede de segurança. A vírgula decimal (`1234,56`) é aceita
(`localize=True`, `LANGUAGE_CODE = "pt-br"`) e o ponto decimal também (`1234.56`). O separador de milhar só
é aceito junto com a vírgula decimal (`1.234,56`, grupos de três dígitos, primeiro grupo sem zero à
esquerda): sem a vírgula, `1.500` ou `0.001` seriam ambíguos e continuam sendo lidos como decimal e
rejeitados. Um `MoneyField` (subclasse de `DecimalField`) remove os pontos nesse único formato antes de
converter. A máscara do campo (Alpine, inline no atributo do input) só formata a digitação como
`1.234,56`; sem JavaScript o campo continua aceitando o texto digitado. A tarefa 2.1 confirma o
comportamento e o teste fixa o que é aceito.

**3a. Tipo como botões.** O campo `kind` usa `RadioSelect` renderizado como dois botões (rádios
visualmente escondidos com `peer-checked`), sem opção vazia e sem pré-seleção: escolher o tipo é um
ato explícito, e o servidor continua exigindo o campo.

**4. Views genéricas com um mixin de dono.**
`ListView` (`paginate_by = 20`, `ordering = ("-date", "-id")`), `CreateView`, `UpdateView`,
`DeleteView`. Um `OwnedQuerysetMixin` filtra `get_queryset()` por `request.user`, de modo que
lançamento alheio e inexistente caem no mesmo 404 do `get_object`. `form_valid` do `CreateView`
atribui `user` (o campo nunca está no formulário, então não é adulterável). Todas herdam
`LoginRequiredMixin` (o `LOGIN_URL` já está configurado). `DeleteView` só exclui no POST; o GET
mostra a confirmação. Mensagens de sucesso via `django.contrib.messages` (já usado no fluxo de
senha). Página inexistente: o 404 padrão do `ListView`.

**4a. Janela modal por melhoria progressiva.**
Criar, editar e excluir abrem num `<dialog>` nativo sobre a listagem. As rotas e as páginas completas
continuam existindo (links reais, abrir a URL direto, sem JavaScript). Um script pequeno
(`static/js/transaction-modal.js`, sem dependência) intercepta o clique nos links marcados com
`data-modal`, busca a mesma URL com `X-Requested-With: XMLHttpRequest` e injeta o fragmento no
`<dialog>`; o Alpine, já carregado, inicializa a máscara no HTML injetado. As views herdam um
`ModalMixin`: com o cabeçalho, o template estende um layout vazio (só o fragmento) e `form_valid`
responde JSON `{"location": ...}` em vez de redirecionar; sem o cabeçalho, nada muda. Erro de
validação volta como fragmento (status 200) e substitui o conteúdo do modal; no sucesso o script
navega para `location`, e a mensagem do `django.contrib.messages` aparece na listagem. Qualquer
resposta inesperada (404, sessão expirada) faz o script navegar para o link original. Como a mesma URL
tem duas respostas, as views enviam `Vary: X-Requested-With` para o navegador não servir o fragmento
em uma navegação normal.
*Alternativas descartadas:* um `<dialog>` por linha com o formulário pré-renderizado (20 formulários por
página sem ganho); HTMX (dependência nova para ~50 linhas de script); rotas de fragmento separadas
(duplicam views e URLs).

**4b. Tabela no estilo do TailAdmin.**
A listagem segue a "Basic Table 5": cartão com cabeçalho (título e ação principal), tabela sem fundo no
cabeçalho, selo de tipo e menu de ações por linha. O menu "…" é um dropdown em Alpine (já carregado),
com os mesmos links `data-modal` — o script do modal continua funcionando sem mudança. A paginação
numerada usa `Paginator.get_elided_page_range` (uma página de cada lado da atual e das pontas), sem
dependência. A busca da referência fica de fora: busca e filtros estão fora do escopo da change.

**5. Rotas e navegação.**
`/transactions/` (lista), `/transactions/new/`, `/transactions/<pk>/edit/`,
`/transactions/<pk>/delete/`, sob `app_name = "transactions"`. A home passa a redirecionar para a lista (`RedirectView`, mantendo `name="home"` e o
login obrigatório), o item "Lançamentos" entra no sidebar e o exemplo "Olá, mundo" sai.
O estado ativo do menu e o link "Início" do sidebar são ajustados no mesmo passo.

**6. Datas.** `DateField` sem hora: a data é a do fato, escolhida pelo usuário, sem conversão de fuso.
O padrão do formulário novo é `timezone.localdate()` (fuso `America/Sao_Paulo`).

## Risks / Trade-offs

- **[Esquecer o filtro por dono numa view futura]** → Todo acesso passa pelo `OwnedQuerysetMixin`;
  testes de isolamento cobrem lista, edição e exclusão (GET e POST) e saldos.
- **[Agregação em toda listagem]** → Um `SUM` por requisição, coberto pelo índice `(user, ...)`; sem
  problema na escala de uso pessoal.
- **[Saldo atual negativo]** → Permitido: despesas podem superar as entradas.
- **[Valor máximo]** → `max_digits=14` limita a ~R$ 999 bilhões; o erro do campo cobre o excesso.

## Migration Plan

Uma migration inicial para o app novo, aditiva (uma tabela). Reverter é remover o app e a tabela;
nada existente muda.
