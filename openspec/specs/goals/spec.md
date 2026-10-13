# goals Specification

## Purpose
Permite ao usuário definir metas financeiras com valor-alvo e prazo opcional, registrar quanto já guardou
e acompanhar o progresso por uma barra, para se organizar em direção a um objetivo (ex.: poupar R$ 500).

## Requirements

### Requirement: Criação de meta
O usuário autenticado DEVE poder criar uma meta informando nome, valor-alvo e, opcionalmente, um prazo.
O nome é obrigatório, sem espaços nas pontas e com tamanho máximo definido. O valor-alvo DEVE ser maior que
zero, com até duas casas decimais, e aceita a entrada no formato brasileiro (`1.234,56`). O prazo, se
informado, NÃO DEVE estar no passado (hoje é válido). Uma meta nova começa com valor guardado zero e ativa.
As mensagens de erro e de sucesso DEVEM ser em português.

#### Cenário: Meta com prazo
- **QUANDO** o usuário envia nome "Reserva de emergência", valor-alvo "500,00" e um prazo futuro
- **ENTÃO** a meta é criada, pertence a ele, está ativa e tem valor guardado `0,00`
- **E** ele volta à lista de metas com uma mensagem de sucesso

#### Cenário: Meta sem prazo
- **QUANDO** o usuário envia nome e valor-alvo válidos e deixa o prazo em branco
- **ENTÃO** a meta é criada sem prazo

#### Cenário: Valor-alvo inválido
- **QUANDO** o usuário envia valor-alvo vazio, zero, negativo, não numérico ou com mais de duas casas decimais
- **ENTÃO** nenhuma meta é criada
- **E** o formulário exibe o erro do valor em português

#### Cenário: Prazo no passado
- **QUANDO** o usuário envia um prazo anterior a hoje
- **ENTÃO** nenhuma meta é criada
- **E** o formulário exibe o erro do prazo em português

#### Cenário: Nome vazio ou longo demais
- **QUANDO** o usuário envia nome vazio, só com espaços ou acima do tamanho máximo
- **ENTÃO** nenhuma meta é criada
- **E** o formulário exibe o erro do nome em português

### Requirement: Registro de progresso
O usuário DEVE poder informar o total já guardado em uma meta sua, um valor maior ou igual a zero com até
duas casas decimais. O valor guardado PODE superar o valor-alvo. Registrar progresso NÃO DEVE criar
lançamento nem alterar o saldo do usuário. Ao editar uma meta cujo prazo já venceu, o prazo só é revalidado
se o usuário o alterar, para que o progresso de uma meta atrasada ainda possa ser registrado.

#### Cenário: Registrar quanto foi guardado
- **QUANDO** o usuário informa que já guardou "200,00" em uma meta de "500,00"
- **ENTÃO** o valor guardado da meta passa a ser `200,00`
- **E** nenhum lançamento é criado e o saldo não muda

#### Cenário: Valor guardado negativo
- **QUANDO** o usuário informa um valor guardado negativo
- **ENTÃO** o valor guardado não é alterado
- **E** o formulário exibe o erro em português

#### Cenário: Progresso em meta com prazo vencido
- **QUANDO** o usuário registra progresso em uma meta cujo prazo já passou, sem alterar o prazo
- **ENTÃO** o progresso é salvo

#### Cenário: Prazo alterado para o passado
- **QUANDO** o usuário altera o prazo de uma meta para uma data anterior a hoje
- **ENTÃO** a alteração é recusada com o erro do prazo em português

### Requirement: Barra de progresso
Cada meta DEVE exibir uma barra de progresso proporcional a valor guardado ÷ valor-alvo, limitada a 100 %.
A tela DEVE mostrar também o percentual (inteiro, limitado a 100 %), o valor guardado e o valor-alvo. A
barra DEVE ter nome acessível e valor para tecnologia assistiva (papel `progressbar`, com valor entre 0 e 100).

#### Cenário: Meta pela metade
- **QUANDO** uma meta de "500,00" tem "250,00" guardados
- **ENTÃO** a barra e o percentual mostram 50 %

#### Cenário: Meta superada
- **QUANDO** uma meta de "500,00" tem "800,00" guardados
- **ENTÃO** a barra e o percentual mostram 100 %, nunca mais
- **E** o valor guardado exibido continua `R$ 800,00`

#### Cenário: Meta sem progresso
- **QUANDO** uma meta tem valor guardado zero
- **ENTÃO** a barra mostra 0 %

### Requirement: Concluir e reabrir meta
O usuário DEVE poder marcar uma meta sua como concluída, o que a move para as concluídas e registra o
momento da conclusão, e DEVE poder reabri-la, o que a devolve às ativas. Concluir NÃO exige que o valor
guardado tenha atingido o alvo. As duas ações DEVEM ser feitas por POST.

#### Cenário: Marcar como concluída
- **QUANDO** o usuário marca uma meta ativa como concluída
- **ENTÃO** a meta passa a aparecer só entre as concluídas
- **E** uma mensagem de sucesso em português é exibida

#### Cenário: Concluir sem atingir o alvo
- **QUANDO** o usuário conclui uma meta com valor guardado abaixo do alvo
- **ENTÃO** a meta é concluída e a barra continua refletindo o valor guardado real

#### Cenário: Reabrir
- **QUANDO** o usuário reabre uma meta concluída
- **ENTÃO** ela volta a aparecer só entre as ativas, sem data de conclusão

#### Cenário: Concluir exige POST
- **QUANDO** o usuário abre a rota de concluir por GET
- **ENTÃO** a meta não é alterada

### Requirement: Listagem de metas ativas e concluídas
A tela de metas DEVE listar separadamente as metas ativas e as concluídas. As ativas aparecem com prazo mais
próximo primeiro, as sem prazo depois, e empate pela criação mais recente; as concluídas aparecem pela
conclusão mais recente. Uma meta ativa com prazo vencido DEVE ser sinalizada como atrasada. Sem nenhuma meta,
a tela DEVE exibir um estado vazio com a ação de criar a primeira.

#### Cenário: Ativas e concluídas separadas
- **QUANDO** o usuário tem duas metas ativas e uma concluída
- **ENTÃO** a tela mostra as duas ativas numa seção e a concluída em outra
- **E** nenhuma meta aparece nas duas

#### Cenário: Ordem das ativas
- **QUANDO** o usuário tem metas ativas com prazos diferentes e uma sem prazo
- **ENTÃO** a de prazo mais próximo vem primeiro e a sem prazo vem por último

#### Cenário: Meta atrasada
- **QUANDO** uma meta ativa tem prazo anterior a hoje
- **ENTÃO** a tela a sinaliza como atrasada

#### Cenário: Sem metas
- **QUANDO** o usuário não tem nenhuma meta
- **ENTÃO** a tela exibe o estado vazio com a ação de criar a primeira meta

#### Cenário: Sem concluídas
- **QUANDO** o usuário só tem metas ativas
- **ENTÃO** a seção de concluídas não é exibida

### Requirement: Edição e exclusão de meta
O usuário DEVE poder editar nome, valor-alvo, valor guardado e prazo de uma meta sua, e excluí-la depois de
uma tela de confirmação. A exclusão NÃO DEVE afetar nenhum outro dado do usuário.

#### Cenário: Editar
- **QUANDO** o usuário altera o valor-alvo de uma meta com dados válidos
- **ENTÃO** a meta é atualizada e a barra passa a refletir o novo alvo

#### Cenário: Excluir com confirmação
- **QUANDO** o usuário confirma a exclusão de uma meta
- **ENTÃO** a meta deixa de existir
- **E** seus lançamentos e saldo permanecem iguais

#### Cenário: Excluir por GET
- **QUANDO** o usuário abre a rota de exclusão por GET
- **ENTÃO** a tela pede confirmação e a meta continua existindo

### Requirement: Isolamento das metas
Cada usuário DEVE ver, editar, concluir, reabrir e excluir apenas as próprias metas. O acesso à meta de outro
usuário, por qualquer rota e método, DEVE responder 404, e a meta NÃO DEVE ser alterada.

#### Cenário: Listagem isolada
- **QUANDO** dois usuários têm metas
- **ENTÃO** cada um vê só as suas na lista

#### Cenário: Meta de outro usuário
- **QUANDO** um usuário tenta editar, concluir, reabrir ou excluir a meta de outro, por GET ou POST
- **ENTÃO** a resposta é 404
- **E** a meta permanece inalterada

### Requirement: Telas de metas protegidas por login
Todas as telas e ações de metas DEVEM exigir sessão autenticada, e todo envio DEVE exigir o token CSRF.

#### Cenário: Visitante sem sessão
- **QUANDO** um visitante sem sessão acessa qualquer rota de metas, por GET ou POST
- **ENTÃO** é redirecionado ao login
- **E** nenhuma meta é criada nem alterada

### Requirement: Acesso pela barra lateral
A barra lateral DEVE ter o item "Metas", que leva à lista de metas e fica destacado enquanto o usuário está em
qualquer tela de metas.

#### Cenário: Item ativo
- **QUANDO** o usuário está em qualquer tela de metas
- **ENTÃO** o item "Metas" da barra lateral aparece como ativo e os demais, inativos

### Requirement: Seletor de data no prazo
O campo `Prazo` DEVE oferecer um calendário para escolher a data, com textos em português do Brasil, que abre
ao acionar o campo ou o ícone de calendário, também dentro do modal, e que funciona nos temas claro e escuro.
A data é exibida como `dd/mm/aaaa` e enviada ao servidor em formato ISO. O calendário NÃO DEVE permitir
escolher um dia anterior a hoje, exceto para manter o prazo já vencido de uma meta existente. Sem JavaScript,
o campo DEVE continuar sendo um campo de data comum. A validação do servidor NÃO DEVE depender do calendário.

#### Cenário: Escolher a data no calendário
- **QUANDO** o usuário aciona o campo `Prazo` e clica em um dia futuro do calendário
- **ENTÃO** o campo mostra a data como `dd/mm/aaaa`
- **E** ao salvar, a meta recebe aquele prazo

#### Cenário: Dias passados bloqueados
- **QUANDO** o calendário de uma meta nova está aberto
- **ENTÃO** os dias anteriores a hoje aparecem desabilitados e não podem ser escolhidos

#### Cenário: Prazo vencido preservado na edição
- **QUANDO** o usuário edita uma meta cujo prazo já passou
- **ENTÃO** o campo mostra o prazo atual
- **E** salvar sem tocar no campo mantém esse prazo

#### Cenário: Sem JavaScript
- **QUANDO** a página de nova meta é aberta sem JavaScript
- **ENTÃO** o campo `Prazo` é um campo de data comum e o envio funciona

### Requirement: Formulários de meta em modal
Criar, editar e excluir uma meta DEVE abrir em modal sobre a lista, como nos lançamentos e nas categorias, e
DEVE funcionar também como página inteira quando o JavaScript não estiver disponível.

#### Cenário: Modal
- **QUANDO** o usuário aciona "Nova meta" com JavaScript ativo
- **ENTÃO** o formulário abre em modal sobre a lista
- **E** ao salvar com sucesso ele volta à lista com a mensagem de sucesso

#### Cenário: Sem JavaScript
- **QUANDO** o usuário abre a rota de nova meta como página
- **ENTÃO** o formulário aparece numa página completa e o envio funciona do mesmo jeito
