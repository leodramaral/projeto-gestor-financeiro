// Gráficos do painel (Chart.js, servido localmente). Os dados vêm do servidor em
// <script id="dashboard-data" type="application/json">, só com as partes que a página mostra
// (`days`, `weeks`, `lowest` e/ou `categories`); sem esse elemento ou sem o Chart.js, o script não
// faz nada e o resto da página continua funcionando.
(function () {
  var dataEl = document.getElementById("dashboard-data");
  if (!dataEl || typeof Chart === "undefined") return;

  var data = JSON.parse(dataEl.textContent);
  var root = document.documentElement;
  var charts = [];
  var drawnMode = null;
  // Em tela estreita o fluxo de caixa abre por semana (62 barras não cabem em 390 px); a escolha do
  // usuário vale só enquanto a página está aberta.
  var flowView = window.matchMedia("(max-width: 639px)").matches ? "weeks" : "days";

  // Colors come from the --chart-* tokens in frontend/style.css, so the palette has one home and
  // follows the theme class on <html>.
  function palette() {
    var style = getComputedStyle(root);
    function token(name) {
      return style.getPropertyValue(name).trim();
    }
    return {
      text: token("--chart-text"),
      grid: token("--chart-grid"),
      income: token("--chart-income"),
      expense: token("--chart-expense"),
      card: token("--chart-card"),
      heroLine: token("--chart-hero-line"),
      heroFill: token("--chart-hero-fill"),
      heroZero: token("--chart-hero-zero"),
      heroMark: token("--chart-hero-mark"),
      heroText: token("--chart-hero-text"),
      alertText: token("--chart-alert-text"),
    };
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) Chart.defaults.animation = false;

  var brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

  function money(value) {
    return (value < 0 ? "− " : "") + brl.format(Math.abs(value));
  }

  function theme() {
    return root.classList.contains("dark") ? "dark" : "light";
  }

  function axisMoney(value) {
    var abs = Math.abs(value);
    if (abs >= 1000) return (value / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mil";
    return value.toLocaleString("pt-BR");
  }

  function scales(colors) {
    return {
      x: { grid: { display: false }, border: { display: false }, ticks: { color: colors.text, maxRotation: 0, autoSkipPadding: 8 } },
      y: {
        beginAtZero: true,
        // O zero é a referência do gráfico: ganha a linha mais forte.
        grid: {
          color: function (ctx) { return ctx.tick && ctx.tick.value === 0 ? colors.text : colors.grid; },
        },
        border: { display: false },
        ticks: { color: colors.text, callback: axisMoney },
      },
    };
  }

  function tooltip(titlePrefix) {
    return {
      callbacks: {
        title: function (items) {
          if (!items.length) return "";
          var label = items[0].label;
          return Array.isArray(label) ? label.join(" · ") : titlePrefix + label;
        },
        label: function (ctx) {
          var label = ctx.dataset.label ? ctx.dataset.label + ": " : "";
          return " " + label + money(ctx.parsed.y);
        },
      },
    };
  }

  function areaFill(canvas, color) {
    var ctx = canvas.getContext("2d");
    var gradient = ctx.createLinearGradient(0, 0, 0, canvas.height || 256);
    gradient.addColorStop(0, color + "55");
    gradient.addColorStop(1, color + "00");
    return gradient;
  }

  function cashflowChart(canvas, colors) {
    var weekly = flowView === "weeks";
    return new Chart(canvas, {
      type: "bar",
      data: {
        labels: weekly ? data.weeks.labels : data.days,
        datasets: [
          { label: "Entradas", data: weekly ? data.weeks.income : data.income, backgroundColor: colors.income, borderRadius: 3, maxBarThickness: weekly ? 28 : 12 },
          { label: "Despesas", data: weekly ? data.weeks.expense : data.expense, backgroundColor: colors.expense, borderRadius: 3, maxBarThickness: weekly ? 28 : 12 },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: { tooltip: tooltip("Dia "), legend: { align: "end", labels: { usePointStyle: true, boxWidth: 8, color: colors.text } } },
        scales: scales(colors),
      },
    });
  }

  // Saldo em linhas retas (a suavização desenharia saldo que não existiu): o trecho abaixo de zero é
  // vermelho e o de cima, da cor de marca. Um segmento que cruza o zero fica vermelho inteiro.
  function balanceChart(canvas, colors) {
    return new Chart(canvas, {
      type: "line",
      data: {
        labels: data.days,
        datasets: [{
          label: "Saldo",
          data: data.balance,
          borderColor: colors.income,
          backgroundColor: colors.income + "26",
          fill: { target: { value: 0 }, above: colors.income + "26", below: colors.expense + "40" },
          tension: 0,
          borderWidth: 2,
          pointRadius: 2,
          pointBackgroundColor: function (ctx) { return ctx.parsed && ctx.parsed.y < 0 ? colors.expense : colors.income; },
          pointBorderColor: function (ctx) { return ctx.parsed && ctx.parsed.y < 0 ? colors.expense : colors.income; },
          segment: {
            borderColor: function (ctx) { return ctx.p0.parsed.y < 0 || ctx.p1.parsed.y < 0 ? colors.expense : colors.income; },
          },
        }],
      },
      options: {
        maintainAspectRatio: false,
        plugins: { tooltip: tooltip("Dia "), legend: { display: false } },
        scales: scales(colors),
      },
    });
  }

  // A linha do bloco de destaque: o saldo do mês sem eixos, com o zero e, se o saldo ficou
  // negativo, o ponto de menor saldo com o valor e a data (o texto também está na página).
  function heroChart(canvas, colors) {
    var alert = canvas.dataset.tone === "alert";
    var line = alert ? colors.expense : colors.heroLine;
    var zero = alert ? colors.grid : colors.heroZero;
    var mark = alert ? colors.expense : colors.heroMark;
    var text = alert ? colors.alertText : colors.heroText;
    var lowest = data.balance[data.lowest];
    var marks = lowest < 0 ? data.balance.map(function (_, i) { return i === data.lowest ? lowest : null; }) : [];
    var datasets = [
      { label: "Saldo", data: data.balance, borderColor: line, backgroundColor: alert ? colors.expense + "26" : colors.heroFill, fill: "start", tension: 0, borderWidth: 2.5, pointRadius: 0 },
      { label: "Zero", data: data.balance.map(function () { return 0; }), borderColor: zero, borderDash: [4, 4], borderWidth: 1, pointRadius: 0, fill: false },
    ];
    if (marks.length) {
      datasets.push({ label: "Menor saldo", data: marks, borderColor: mark, backgroundColor: mark, showLine: false, pointRadius: 5, pointHoverRadius: 6 });
    }
    var label = "Menor saldo: " + money(lowest) + " (" + (canvas.dataset.lowestLabel || "") + ")";
    return new Chart(canvas, {
      type: "line",
      data: { labels: data.days, datasets: datasets },
      options: {
        maintainAspectRatio: false,
        layout: { padding: { top: 8, bottom: 4, right: 6 } },
        plugins: { legend: { display: false }, tooltip: { filter: function (item) { return item.dataset.label === "Saldo"; }, callbacks: tooltip("Dia ").callbacks } },
        scales: { x: { display: false }, y: { display: false, beginAtZero: true } },
      },
      plugins: marks.length ? [{
        id: "lowestLabel",
        afterDatasetsDraw: function (chart) {
          var point = chart.getDatasetMeta(2).data[data.lowest];
          if (!point) return;
          var ctx = chart.ctx;
          ctx.save();
          ctx.font = "500 12px " + Chart.defaults.font.family;
          ctx.fillStyle = text;
          ctx.textBaseline = "middle";
          var width = ctx.measureText(label).width;
          var x = point.x + 10;
          if (x + width > chart.chartArea.right) x = chart.chartArea.right - width;
          // Abaixo do ponto, ou acima dele quando o ponto está rente à base e o texto cairia fora.
          var y = point.y + 12 > chart.chartArea.bottom - 2 ? point.y - 14 : point.y + 12;
          ctx.fillText(label, x, y);
          ctx.restore();
        },
      }] : [],
    });
  }

  function build() {
    charts.forEach(function (chart) {
      chart.destroy();
    });
    charts = [];

    var mode = theme();
    drawnMode = mode;
    var colors = palette();
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.color = colors.text;

    var donut = document.getElementById("chart-categories");
    if (donut && data.categories && data.categories.length) {
      charts.push(
        new Chart(donut, {
          type: "doughnut",
          data: {
            labels: data.categories.map(function (c) { return c.name; }),
            datasets: [{
              data: data.categories.map(function (c) { return c.amount; }),
              backgroundColor: data.categories.map(function (c) { return c[mode]; }),
              borderColor: colors.card,
              borderWidth: 3,
            }],
          },
          options: {
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: {
              legend: { display: false },
              tooltip: { callbacks: { label: function (ctx) { return " " + ctx.label + ": " + brl.format(ctx.parsed); } } },
            },
          },
        })
      );
    }

    var cashflow = document.getElementById("chart-cashflow");
    if (cashflow && data.days) charts.push(cashflowChart(cashflow, colors));

    var balance = document.getElementById("chart-balance");
    if (balance && data.days) charts.push(balanceChart(balance, colors));

    var hero = document.getElementById("chart-hero");
    if (hero && data.days) charts.push(heroChart(hero, colors));
  }

  // O seletor Dias | Semanas só aparece com o script carregado: sem ele os botões não fariam nada.
  function bindFlowToggle() {
    var toggle = document.querySelector("[data-flow-toggle]");
    if (!toggle || !data.weeks) return;
    toggle.classList.remove("hidden");
    toggle.classList.add("flex");
    var buttons = toggle.querySelectorAll("[data-flow-view]");
    function sync() {
      buttons.forEach(function (button) {
        button.setAttribute("aria-pressed", String(button.dataset.flowView === flowView));
      });
    }
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        if (button.dataset.flowView === flowView) return;
        flowView = button.dataset.flowView;
        sync();
        build();
      });
    });
    sync();
  }

  bindFlowToggle();
  build();
  // O tema muda pela classe `dark` no <html>: redesenha com a paleta nova, sem recarregar.
  new MutationObserver(function () {
    if (theme() !== drawnMode) build();
  }).observe(root, { attributes: true, attributeFilter: ["class"] });
})();
