// Sends the assistant's question without reloading the page. The page works without this script (a plain
// POST with a redirect); with it, the same POST goes through `fetch` and the answer, already rendered by the
// server in the response, replaces a few regions of the page. Nothing else on the page is touched, so the
// focus stays in the field.
document.addEventListener("alpine:init", function () {
  const REGIONS = [
    "chat-conversation",
    "chat-actions",
    "chat-field-errors",
    "chat-composer-notice",
    "chat-credits",
  ];

  function reducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  // The layout scrolls inside a wrapper, not the window: find the nearest scrollable ancestor.
  function scroller() {
    for (let el = document.getElementById("chat-conversation"); el; el = el.parentElement) {
      if (/(auto|scroll)/.test(getComputedStyle(el).overflowY) && el.scrollHeight > el.clientHeight) {
        return el;
      }
    }
    return document.scrollingElement;
  }

  function scrollToEnd() {
    const box = scroller();
    box.scrollTo({ top: box.scrollHeight, behavior: reducedMotion() ? "auto" : "smooth" });
  }

  function cloneTemplate(id) {
    return document.getElementById(id).content.cloneNode(true);
  }

  Alpine.data("assistantChat", function () {
    return {
      sending: false,
      blocked: false,

      init() {
        this.blocked = document.getElementById("chat-state").dataset.blocked === "true";
      },

      get busy() {
        return this.sending || this.blocked;
      },

      async send(event) {
        if (this.busy) {
          event.preventDefault();
          return;
        }
        if (!window.fetch || !window.FormData || !window.DOMParser) {
          this.sending = true; // no script path: the browser posts the form itself
          return;
        }
        event.preventDefault();
        const form = event.target;
        const field = form.elements.question;
        const text = field.value;
        const body = new FormData(form);
        this.sending = true;
        const pending = text.trim() ? this.showPending(text) : [];
        field.value = "";
        field.focus();
        try {
          await this.submit(form, body, field, text);
        } catch (error) {
          this.fail(pending, field, text);
        } finally {
          this.sending = false;
        }
      },

      showPending(text) {
        const conversation = document.getElementById("chat-conversation");
        let list = conversation.querySelector("ol");
        if (!list) {
          list = document.createElement("ol");
          list.className = "w-full max-w-3xl space-y-6";
          conversation.replaceChildren(list);
        }
        conversation.classList.remove("justify-center");
        const fragment = cloneTemplate("chat-pending");
        fragment.querySelector("[data-question]").textContent = text;
        const items = Array.from(fragment.children);
        list.append(...items);
        scrollToEnd();
        return items;
      },

      async submit(form, body, field, text) {
        const response = await fetch(form.action || window.location.href, {
          method: "POST",
          body: body,
          credentials: "same-origin",
        });
        if (new URL(response.url).pathname !== window.location.pathname) {
          window.location.assign(response.url); // the session ended: the login page
          return;
        }
        if (!response.ok) throw new Error("status " + response.status);
        const page = new DOMParser().parseFromString(await response.text(), "text/html");
        const state = page.getElementById("chat-state");
        if (!state || !REGIONS.every((id) => page.getElementById(id))) throw new Error("regions");
        for (const id of REGIONS) {
          const current = document.getElementById(id);
          const incoming = page.getElementById(id);
          current.className = incoming.className;
          current.innerHTML = incoming.innerHTML;
        }
        this.blocked = state.dataset.blocked === "true";
        if (state.dataset.restore === "true") field.value = text;
        scrollToEnd();
      },

      fail(pending, field, text) {
        pending.forEach((item) => item.remove());
        field.value = text;
        const list = document.querySelector("#chat-conversation ol");
        if (list) list.append(cloneTemplate("chat-network-error"));
        scrollToEnd();
      },
    };
  });
});
