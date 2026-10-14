# Delta: screen-design

## ADDED Requirements

### Requirement: Painel documentado com gráficos aproximados
O painel DEVE ter design em `design/dashboard.figcraft`, com a Visão geral em desktop claro,
desktop escuro e mobile claro. Como o FigCraft não executa o Chart.js, os gráficos DEVEM ser
desenhados à mão a partir dos mesmos dados de exemplo do app e a aproximação DEVE estar registrada
como divergência conhecida no `AGENTS.md`. Os números mostrados nos gráficos DEVEM bater com os
dos indicadores: a soma das colunas é igual aos totais do mês, e o último ponto do saldo é igual ao
saldo final. O design NÃO DEVE mostrar gráfico com dado que o código não produziria.

#### Cenário: Painel documentado
- **QUANDO** a pasta `design/` é aberta
- **ENTÃO** existe `design/dashboard.figcraft` com a Visão geral em desktop claro, desktop escuro e mobile claro
- **E** os frames seguem a convenção `dashboard · <viewport> · <tema> · padrão`

#### Cenário: Gráficos batem com os indicadores
- **QUANDO** o frame da Visão geral mostra os indicadores e os gráficos
- **ENTÃO** a soma das entradas e a das despesas das colunas são iguais aos totais dos indicadores
- **E** o último ponto da linha de saldo é igual ao saldo final do bloco de destaque

#### Cenário: Divergência registrada
- **QUANDO** o `AGENTS.md` é aberto
- **ENTÃO** ele registra que os gráficos do design do painel são desenhados à mão a partir de dados de exemplo

## MODIFIED Requirements

### Requirement: Telas implementadas documentadas
Toda tela de usuário já implementada no app DEVE ter design em `design/`, num `.figcraft` por tela ou
fluxo: entrar (`login`), confirmação de conta (`signup_done`, `confirm`, `resend`), recuperação de senha
(`password_reset` e seus passos), lançamentos, categorias, perfil e a Visão geral do painel. Cada tela DEVE
cobrir desktop claro, desktop escuro e mobile claro, e os estados que o código exibe: erro de formulário,
vazio, sucesso, modal aberto e confirmação de exclusão, conforme existirem na tela. As abas Categorias,
Fluxo e saldo e Lançamentos do painel e o estado vazio do painel NÃO ENTRAM por ora. Telas ainda não
implementadas NÃO DEVEM ter design nesta capacidade. E-mails transacionais NÃO SÃO telas do app e ficam fora.

#### Cenário: Entrar documentado
- **QUANDO** a pasta `design/` é aberta
- **ENTÃO** existe `design/login.figcraft` com frames de `login` em desktop claro, desktop escuro e mobile claro
- **E** há o estado com erro de credenciais, com a mensagem real do formulário

#### Cenário: Painel fora do design
- **QUANDO** a pasta `design/` é aberta
- **ENTÃO** existe `design/dashboard.figcraft` com a Visão geral do painel, e só ela
- **E** as abas Categorias, Fluxo e saldo e Lançamentos e o estado vazio do painel ficam fora do design, sem frame

#### Cenário: Lançamento em modal
- **QUANDO** o design de lançamentos é aberto
- **ENTÃO** há o frame da lista, o do formulário de lançamento aberto no modal e o da confirmação de exclusão

#### Cenário: Estado inexistente não é inventado
- **QUANDO** uma tela não tem determinado estado no código (por exemplo, o perfil não tem estado vazio)
- **ENTÃO** o design não cria esse frame
