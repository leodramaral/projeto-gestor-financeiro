## ADDED Requirements

### Requirement: Coleta restrita ao projeto
O pytest, rodado na raiz do repositório, NÃO DEVE coletar testes de `worktrees/`, pasta local onde
ficam as worktrees de trabalho. O resultado da suíte DEVE ser o mesmo com ou sem worktrees
presentes.

#### Cenário: Worktree com testes presentes
- **QUANDO** existe `worktrees/<nome>/` com testes e o pytest roda na raiz
- **ENTÃO** nenhum teste de dentro de `worktrees/` é coletado ou executado

#### Cenário: Sem worktrees
- **QUANDO** a pasta `worktrees/` não existe, como no CI
- **ENTÃO** a coleta e o resultado são os mesmos de antes
