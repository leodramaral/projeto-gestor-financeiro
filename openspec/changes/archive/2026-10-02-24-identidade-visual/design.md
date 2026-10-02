# Design

## Context

O layout deriva do TailAdmin Free (MIT): `templates/base.html` (painel) e `templates/base_auth.html`
(visitante, da #2). A cor de marca vive nos tokens `--color-brand-*` de `frontend/style.css`
(Tailwind 4, `@theme`); todos os componentes usam `bg-brand-500`, `text-brand-500` etc., então
trocar a escala troca o produto inteiro. O logo é um SVG de **traçados** (o nome "TailAdmin" está
desenhado, não é texto), repetido em `sidebar.html`, `header.html` (mobile) e `base_auth.html`. O
tema já existe no painel: a chave `darkMode` do `localStorage`, a classe `dark` no `<html>` e um
botão em `header.html`; o `base_auth.html` só lê a chave, sem controle. Os e-mails usam o azul
`#465fff` inline, fora do CSS. Não há ferramenta de imagem no ambiente (nem ImageMagick, nem Pillow).

## Goals / Non-Goals

**Goals:**
- Uma única fonte de marca e de controle de tema, usada por painel e visitante.
- Paleta verde com contraste verificado por teste, não só "parece bom".

**Non-Goals:**
- Nova biblioteca de ícones, redesenho do painel, tema pelo sistema operacional.

## Decisions

1. **Marca como parcial, com o nome em texto HTML.** `partials/brand.html` renderiza o ícone (SVG
   inline) mais o nome "Gestor Financeiro" como texto. Texto herda a cor do tema
   (`text-gray-900 dark:text-white`), dispensando o par `logo.svg`/`logo-dark.svg`, e é
   selecionável. Parâmetro `compact` mostra só o ícone (barra recolhida). Alternativa descartada:
   redesenhar o nome como traçados SVG (sem ferramenta no ambiente e sem ganho).
2. **Símbolo escolhido: "G de moeda" em quadrado arredondado** (variação 4 da prévia). Um quadrado
   de cantos arredondados (`rx=12` em 48×48) com um G aberto e dois traços curtos, no topo e na base,
   como as pontas do cifrão `$`. Geometria (viewBox 0 0 48 48): arco do G de raio 11,5 centrado em
   (24, 24), do ângulo −50° até 0°, mais a barra até x=25; traços em `x=24` de y=8 a 12,5 e de
   y=35,5 a 40; todos com `stroke-width` 4,2 e pontas arredondadas. O círculo do arco deve ser
   **exato** e centrado: um centro deslocado faz o traço do topo vazar para dentro do G (defeito já
   visto na prévia). Cores: no tema claro, fundo `brand-500` e G branco; no escuro, fundo `brand-300`
   e G `brand-700`. O mesmo desenho, sem texto, vale para o favicon. Prévia aprovada:
   https://claude.ai/artifact/ACr5jYBCJC7o5BPfKsu4Mm (variação 4, cor Jade).
3. **Arquivos antigos removidos.** `logo.svg`, `logo-dark.svg`, `logo-icon.svg` e `favicon.ico`
   saem; entra `static/images/logo/logo-icon.svg` (novo ícone) e `static/images/favicon.svg`.
4. **Cor de marca: Jade (verde-azulado), escala fixada.** Substituir apenas `--color-brand-25…950`
   em `style.css`, no mesmo formato:
   `25 #f7fefd`, `50 #f0fdfa`, `100 #ccfbf1`, `200 #99f6e4`, `300 #2dd4bf`, `400 #1ea596`,
   `500 #0f766e`, `600 #115e59`, `700 #134e4a`, `800 #0f3d3a`, `900 #0b2e2b`, `950 #062220`.
   O `brand-500` é escuro de propósito (texto branco precisa de ≥ 4,5:1) e, para o salto até o
   `brand-300` não ser abrupto, o `brand-400` é um tom intermediário entre os dois: de 300 a 500 a
   luminosidade cai em passos parecidos (≈ 14, 16 e 17 pontos de L*), em vez de pular do verde vivo
   direto para o escuro. Contraste (fórmula WCAG): texto branco sobre `brand-500` 5,47:1 e sobre
   `brand-600` 7,58:1; `brand-600` como texto sobre branco 7,58:1; `brand-400` como texto sobre
   `gray-900` 5,81:1; o G `brand-700` sobre o fundo `brand-300` do ícone escuro 5,09:1. Efeito no
   escuro: textos e links com `dark:text-brand-400` ficam um pouco mais discretos do que na prévia
   (5,8:1 em vez de 9,5:1), ainda acima da meta. Os tokens `success-*` (verde puro) permanecem:
   alerta de sucesso e destaque de marca ficam em matizes diferentes, o que ajuda a distingui-los.
   Alternativa descartada: Floresta, Esmeralda e Folha (verdes mais puros), preteridas na prévia.
5. **Contraste verificado em teste.** Um teste Python lê os tokens de `frontend/style.css`, calcula
   a razão de contraste (fórmula WCAG) dos pares acima e falha abaixo de 4,5. Também falha se
   `brand-500` ainda for o azul antigo. Assim a regra da spec é executável.
6. **Controle de tema em parcial.** Extrair o botão de `header.html` para
   `partials/theme_toggle.html` (com `aria-label` "Alternar tema") e usá-lo no header e em
   `base_auth.html`. O `base_auth.html` ganha o `x-data` de `darkMode`, o mesmo contrato do painel
   (`localStorage.darkMode` + classe `dark` em `<html>`), então a escolha é compartilhada sem código
   novo. Posição nas telas de visitante: canto superior direito da página.
7. **Aplicar o tema sem piscar, com tolerância a falha.** O script inline do `<head>` já existe em
   `base.html` e `base_auth.html`; vira um único `partials/theme_init.html` incluído nos dois, com
   `try/catch` (armazenamento bloqueado → tema claro). A gravação no clique também fica em
   `try/catch`.
8. **Tema padrão claro.** Mantido o comportamento atual (sem escolha salva = claro). Seguir
   `prefers-color-scheme` é uma melhoria possível, mas muda comportamento já entregue e foi deixada
   fora do escopo.
9. **E-mails.** O CSS inline dos e-mails não lê tokens: trocar `#465fff` pelo hex de `brand-500` em
   `email/base.html`, `confirm_account.html`, `password_reset.html` e `test_message.html`. Um teste
   garante que nenhum template contém o azul antigo nem "TailAdmin" no texto exibido.
10. **Atribuição preservada.** Comentários de licença em `base.html` e `frontend/TAILADMIN-LICENSE`
    ficam; só o que o usuário vê é trocado. Comentários de código e README podem citar o TailAdmin.

## Risks / Trade-offs

- [Contraste insuficiente no jade] → teste automatizado de razão WCAG bloqueia a mudança.
- [Verde de marca e verde de sucesso parecidos] → aceito; sucesso sempre vem com ícone e texto, e
  pode ganhar outro tom depois sem afetar a marca.
- [Favicon só em SVG não aparece em navegadores muito antigos] → aceito; sem impacto funcional.
- [CSS compilado fica desatualizado] → `docker compose run --rm css npm run build` faz parte das
  tarefas; classes novas só existem após recompilar.
- [Verificação visual não é automatizável por completo] → tarefa manual explícita nos dois temas,
  com o Playwright MCP quando disponível.
