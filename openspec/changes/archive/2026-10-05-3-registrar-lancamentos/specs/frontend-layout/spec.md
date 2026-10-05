# Spec Delta

## ADDED Requirements

### Requirement: Estado da barra lateral preservado entre páginas
Em telas de desktop, a barra lateral DEVE manter entre as navegações o estado escolhido pelo
usuário (recolhida ou expandida). Em telas estreitas, onde a barra é uma gaveta, ela NÃO DEVE
reabrir sozinha ao navegar. Quando o navegador não permite guardar a preferência, a barra DEVE
voltar ao estado padrão (expandida) sem erro.

#### Cenário: Recolhida continua recolhida
- **QUANDO** o usuário recolhe a barra lateral no desktop e navega para outra página ou recarrega
- **ENTÃO** a barra continua recolhida

#### Cenário: Sem animação ao carregar
- **QUANDO** uma página carrega com a barra lateral recolhida
- **ENTÃO** a barra já é desenhada recolhida desde a primeira pintura
- **E** nenhuma animação de recolhimento acontece durante o carregamento

#### Cenário: Expandir de novo
- **QUANDO** o usuário expande a barra recolhida e navega para outra página
- **ENTÃO** a barra continua expandida

#### Cenário: Gaveta no celular
- **QUANDO** o usuário abre e fecha a gaveta da barra em tela estreita e navega para outra página
- **ENTÃO** a gaveta permanece fechada

#### Cenário: Preferência indisponível
- **QUANDO** o navegador bloqueia o armazenamento local
- **ENTÃO** a página carrega com a barra expandida e sem erro
