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
    const first =
      body.querySelector("[autofocus]") ||
      body.querySelector("input:not([type=hidden]), button[type=submit]");
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

  // Locked from the click until the response turns into a new fragment (or the page navigates),
  // so a double click or a repeated Enter cannot post the same transaction twice.
  let submitting = false;

  async function submit(form) {
    if (submitting) return;
    submitting = true;
    const button = form.querySelector("button[type=submit]");
    if (button) button.disabled = true;
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
        submitting = false;
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

  // A click on the backdrop lands on the <dialog> itself, not on its content. Only close when the
  // press also started there: a text selection dragged out of the form ends on the backdrop too.
  let pressedOnBackdrop = false;
  dialog.addEventListener("mousedown", function (event) {
    pressedOnBackdrop = event.target === dialog;
  });
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog && pressedOnBackdrop) dialog.close();
    pressedOnBackdrop = false;
  });
  dialog.addEventListener("close", function () {
    body.innerHTML = "";
  });
})();
