# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Pessoas físicas que querem controlar o próprio dinheiro. Três perfis, com peso parecido e menor
que o do uso central: a pessoa leiga que organiza as finanças no dia a dia, o jovem adulto que
faz o primeiro controle financeiro (uso frequente pelo celular) e a banca avaliadora do projeto
acadêmico, que avalia o app em apresentação. O trabalho é lançar entradas e despesas, categorizar
custos, acompanhar metas e conferir no painel mensal para onde o dinheiro vai.

## Product Purpose

Aplicação web para controle de finanças pessoais: a pessoa se cadastra, registra saldo e despesas
e acompanha a própria situação financeira. Existe como projeto acadêmico de estudo; sucesso é
cobrir o escopo (MVP concluído na `v0.1.0`; pós-MVP em andamento) com qualidade, de ponta a ponta.

## Positioning

Controle simples (lançamentos, categorias, metas, painel) com um assistente de gestão com IA
previsto no pós-MVP. A simplicidade é o diferencial declarado; a IA ainda não existe.

## Operating Context

Aplicação renderizada no servidor (Django + templates, Tailwind CSS 4, Alpine.js, Chart.js),
layout base TailAdmin com marca própria, texto em português do Brasil. Roda em Docker. Telas de
visitante (login, cadastro, confirmação e recuperação de senha) e telas autenticadas (painel,
lançamentos, categorias, metas, perfil). Desenhos de tela em `design/` (FigCraft).

## Capabilities and Constraints

- Hoje: cadastro, login, recuperação de senha, perfil, lançamentos (entradas e despesas),
  categorias, painel com gráficos (rosca por categoria, filtro de período) e metas financeiras.
- Pós-MVP pendente: tarefas, previsão de orçamento, assistente com IA, planos de serviço,
  relatórios e exportação, deploy em cloud.
- Domínio só entra por change do OpenSpec (ver `AGENTS.md`); o contrato do que existe está em
  `openspec/specs/`.
- Projeto acadêmico: nunca apresentar como produto financeiro real nem para gerir dinheiro real.

## Brand Commitments

Nome "Gestor Financeiro", marca própria (logo, ícone, favicon) em todas as telas e e-mails. Cor de
marca é o verde-azulado "jade" (escala completa, claro e escuro). Não exibir "TailAdmin" em
nenhuma tela, título ou e-mail. Fonte Outfit. Ver `openspec/specs/visual-identity/`.

## Evidence on Hand

Specs vivas em `openspec/specs/`, designs de tela em `design/*.figcraft`, CSS em
`frontend/style.css`. Não há usuários reais, métricas, depoimentos nem casos de uso medidos:
não inventar.

## Product Principles

- Simplicidade primeiro: cada tela serve uma tarefa financeira clara, sem jargão.
- Honestidade sobre o que é: projeto de estudo, sem promessa de dinheiro real.
- Os números do usuário são o conteúdo; o painel os torna legíveis de relance.
- Uso móvel e desktop com a mesma qualidade, claro e escuro.

## Accessibility & Inclusion

WCAG AA: contraste mínimo de 4,5:1 (texto e cor de marca) e navegação por teclado. Mobile-first
(telas também desenhadas em 390 px). Tema claro e escuro obrigatórios em todas as telas.
