// Calendar (flatpickr) for every `input[data-datepicker]`. The input stays a plain date field in the
// HTML, so without this script (or without flatpickr) the browser's own picker is used. The visible
// field shows dd/mm/aaaa; the real one, hidden, is sent as yyyy-mm-dd.
//
// The transaction/goal modal injects HTML with innerHTML, which never runs <script> tags, so a
// MutationObserver starts the calendar on fields that show up later too.
(function () {
  if (typeof flatpickr === "undefined") return;

  // Lucide chevron-left / chevron-right (the same icons as `core/icons/`, which a template tag cannot reach here).
  const ARROW = (path) =>
    '<svg class="stroke-current" width="24" height="24" viewBox="0 0 24 24" fill="none" ' +
    'xmlns="http://www.w3.org/2000/svg"><path d="' + path + '" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function localIso(date) {
    return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" + pad(date.getDate());
  }

  function setup(input) {
    if (input.dataset.datepickerReady) return;
    input.dataset.datepickerReady = "1";
    // An overdue deadline already saved must stay selectable, or flatpickr would drop it.
    const overdue = input.value !== "" && input.value < localIso(new Date());
    flatpickr(input, {
      locale: "pt",
      dateFormat: "Y-m-d",
      altInput: true,
      altFormat: "d/m/Y",
      ariaDateFormat: "j \\d\\e F \\d\\e Y",
      allowInput: true,
      // static keeps the calendar next to the field, inside the <dialog> (a calendar appended to
      // <body> would open behind it: the dialog is in the top layer).
      static: true,
      disableMobile: true,
      monthSelectorType: "static",
      minDate: overdue ? null : "today",
      prevArrow: ARROW("m15 18-6-6 6-6"),
      nextArrow: ARROW("m9 18 6-6-6-6"),
      onOpen: function (selectedDates, dateStr, instance) {
        // Not enough room below the field (typical inside the modal): open above it instead.
        const room = window.innerHeight - instance.altInput.getBoundingClientRect().bottom;
        const need = instance.calendarContainer.offsetHeight + 16;
        const above = room < need && instance.altInput.getBoundingClientRect().top > need;
        instance.calendarContainer.classList.toggle("flip-up", above);
      },
      onReady: function (selectedDates, dateStr, instance) {
        // The label pointed at the (now hidden) real input: point it at the visible one.
        const visible = instance.altInput;
        visible.id = input.id + "_display";
        visible.placeholder = "dd/mm/aaaa";
        const label = document.querySelector('label[for="' + input.id + '"]');
        if (label) label.htmlFor = visible.id;
      },
    });
  }

  function scan(root) {
    root.querySelectorAll("input[data-datepicker]").forEach(setup);
  }

  scan(document);
  new MutationObserver(function (mutations) {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType !== 1) continue;
        if (node.matches("input[data-datepicker]")) setup(node);
        else scan(node);
      }
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
