// Gráficos do painel (Chart.js, servido localmente), um ponto por dia do mês. Os dados vêm do
// servidor em <script id="dashboard-data" type="application/json">, só com as partes que a página
// mostra (`days` e/ou `categories`); sem esse elemento ou sem o Chart.js, o
// script não faz nada e o resto da página continua funcionando.
(function () {
  var dataEl = document.getElementById("dashboard-data");
  if (!dataEl || typeof Chart === "undefined") return;

  var data = JSON.parse(dataEl.textContent);
  var root = document.documentElement;
  var charts = [];
  var drawnMode = null;

  var PALETTE = {
    light: { text: "#667085", grid: "#eaecf0", income: "#0f766e", expense: "#f04438", card: "#ffffff" },
    dark: { text: "#98a2b3", grid: "#232a3b", income: "#1ea596", expense: "#f97066", card: "#12161f" },
  };

  var brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

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
        grid: { color: colors.grid },
        border: { display: false },
        ticks: { color: colors.text, callback: axisMoney },
      },
    };
  }

  function tooltip() {
    return {
      callbacks: {
        title: function (items) {
          return items.length ? "Dia " + items[0].label : "";
        },
        label: function (ctx) {
          var label = ctx.dataset.label ? ctx.dataset.label + ": " : "";
          return " " + label + brl.format(ctx.parsed.y);
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

  function build() {
    charts.forEach(function (chart) {
      chart.destroy();
    });
    charts = [];

    var mode = theme();
    drawnMode = mode;
    var colors = PALETTE[mode];
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
    if (cashflow && data.days) {
      charts.push(
        new Chart(cashflow, {
          type: "bar",
          data: {
            labels: data.days,
            datasets: [
              { label: "Entradas", data: data.income, backgroundColor: colors.income, borderRadius: 3, maxBarThickness: 12 },
              { label: "Despesas", data: data.expense, backgroundColor: colors.expense, borderRadius: 3, maxBarThickness: 12 },
            ],
          },
          options: {
            maintainAspectRatio: false,
            plugins: { tooltip: tooltip(), legend: { align: "end", labels: { usePointStyle: true, boxWidth: 8, color: colors.text } } },
            scales: scales(colors),
          },
        })
      );
    }

    var balance = document.getElementById("chart-balance");
    if (balance && data.days) {
      var last = data.balance[data.balance.length - 1];
      var line = last < 0 ? colors.expense : colors.income;
      charts.push(
        new Chart(balance, {
          type: "line",
          data: {
            labels: data.days,
            datasets: [{
              label: "Saldo",
              data: data.balance,
              borderColor: line,
              backgroundColor: areaFill(balance, line),
              fill: true,
              tension: 0.35,
              borderWidth: 2,
              pointRadius: 2,
              pointBackgroundColor: line,
            }],
          },
          options: {
            maintainAspectRatio: false,
            plugins: { tooltip: tooltip(), legend: { display: false } },
            scales: scales(colors),
          },
        })
      );
    }
  }

  build();
  // O tema muda pela classe `dark` no <html>: redesenha com a paleta nova, sem recarregar.
  new MutationObserver(function () {
    if (theme() !== drawnMode) build();
  }).observe(root, { attributes: true, attributeFilter: ["class"] });
})();
