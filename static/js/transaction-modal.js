// Opens the transaction screens in a <dialog>. Links stay real pages: without this script, or on
// ctrl/middle-click, they behave as normal navigation.
(function () {
  const dialog = document.getElementById("transaction-modal");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const body = document.getElementById("transaction-modal-body");
  const headers = { "X-Requested-With": "XMLHttpRequest" };
  let currentUrl = null;

  function show(html) {
    body.innerHTML = html;
    if (!dialog.open) dialog.showModal();
    const first = body.querySelector("input:not([type=hidden]):not(.sr-only), button[type=submit]");
    if (first) first.focus();
  }

  async function open(url) {
    currentUrl = url;
    try {
      const response = await fetch(url, { headers, credentials: "same-origin" });
      if (!response.ok || response.redirected) throw new Error("unexpected response");
      show(await response.text());
    } catch (error) {
      window.location.assign(url);
    }
  }

  async function submit(form) {
    try {
      const response = await fetch(currentUrl, {
        method: "POST",
        headers,
        body: new FormData(form),
        credentials: "same-origin",
      });
      if (!response.ok || response.redirected) throw new Error("unexpected response");
      if ((response.headers.get("Content-Type") || "").includes("application/json")) {
        window.location.assign((await response.json()).location);
      } else {
        show(await response.text());
      }
    } catch (error) {
      window.location.assign(currentUrl);
    }
  }

  document.addEventListener("click", function (event) {
    if (event.defaultPrevented || event.button !== 0) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const closer = event.target.closest("[data-modal-close]");
    if (closer && dialog.contains(closer)) {
      event.preventDefault();
      dialog.close();
      return;
    }
    const link = event.target.closest("a[data-modal]");
    if (link) {
      event.preventDefault();
      open(link.href);
    }
  });

  body.addEventListener("submit", function (event) {
    event.preventDefault();
    submit(event.target);
  });

  // A click on the backdrop lands on the <dialog> itself, not on its content.
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", function () {
    body.innerHTML = "";
  });
})();
