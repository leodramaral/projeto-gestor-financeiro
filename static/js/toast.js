// Toast notifications: `window.toast.success|error|warning|info(text)` for scripts, and the messages the
// server queued (`django.contrib.messages`) for pages. Both end in the same stack of cards, drawn from the
// `<template data-toast-level>` models the layouts render (partials/alert.html), so there is one markup.
//
// The stack of cards (the newest in front, the older ones peeking out behind, spreading out when the
// pointer or the focus is on them) is adapted from the toast of Pines UI, https://devdojo.com/pines
// (MIT, Copyright (c) DevDojo; licence in frontend/PINES-LICENSE). The code is rewritten: the text always
// goes in as text, never as HTML, and the stack is a list that Alpine draws, with the geometry in CSS
// variables (see `.toast-item` in frontend/style.css).
(function () {
  const LEVELS = ["success", "error", "warning", "info"];
  const DURATION = 5000; // errors have no timer: they stay until the user closes them
  const EXIT = 300; // ms; keep in sync with the transition of `.toast-item`
  const GAP = 12; // px between cards when the stack is spread out
  const PEEK = 12; // px of each older card showing below the one in front
  const SCALE_STEP = 0.05;
  const VISIBLE = 3; // cards drawn while the stack is collapsed

  // Calls made before Alpine started wait here; the component drains them in `init`.
  const pending = [];
  let ready = false;

  function show(level, text) {
    if (!ready) {
      pending.push({ level, text });
      return;
    }
    window.dispatchEvent(new CustomEvent("toast:show", { detail: { level, text } }));
  }

  window.toast = {
    show,
    success: (text) => show("success", text),
    error: (text) => show("error", text),
    warning: (text) => show("warning", text),
    info: (text) => show("info", text),
  };

  function reducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  document.addEventListener("alpine:init", function () {
    Alpine.data("toastStack", function () {
      // Kept out of the reactive state. `this.$root` is resolved from the element that is running the
      // directive, and for a card that element is gone as soon as the card leaves the list.
      let root = null;
      let observer = null;

      return {
        toasts: [], // newest first: index 0 is the card in front
        heights: {}, // natural height of each card, by id
        hover: false,
        focused: false,
        nextId: 1,

        init() {
          root = this.$root;
          this.raise();
          observer = new ResizeObserver(() => this.measure());
          window.addEventListener("toast:show", (event) => {
            this.add(event.detail.level, event.detail.text);
          });
          document.querySelectorAll("[data-toast]").forEach((el) => {
            this.add(el.dataset.level, el.textContent);
          });
          ready = true;
          pending.splice(0).forEach((call) => show(call.level, call.text));
        },

        // Puts the stack in the top layer of the browser, above a modal <dialog>, which no z-index can
        // beat. Showing it again moves it above whatever opened since. Without support for the Popover
        // API the stack stays a fixed box, as the CSS draws it.
        raise() {
          if (!root.showPopover) return;
          if (root.matches(":popover-open")) root.hidePopover();
          root.showPopover();
        },

        add(level, text) {
          this.raise();
          const known = LEVELS.includes(level) ? level : "info";
          const toast = {
            id: this.nextId++,
            level: known,
            text: String(text),
            shown: false,
            leaving: false,
            remaining: known === "error" ? 0 : DURATION,
            timer: null,
            startedAt: 0,
          };
          this.toasts.unshift(toast);
          // Alpine reacts to changes made through its own proxy, not to the object created above.
          const item = this.toasts[0];
          // Two frames: the card is drawn once in its entering position, then moves to its place.
          requestAnimationFrame(() => requestAnimationFrame(() => (item.shown = true)));
          this.schedule(item);
        },

        // Draws the card of a toast: a copy of the model of its level, with the text set as text.
        mount(el, toast) {
          const model = document.querySelector(`template[data-toast-level="${toast.level}"]`);
          const card = model.content.firstElementChild.cloneNode(true);
          card.querySelector("[data-toast-text]").textContent = toast.text;
          card.querySelector("[data-toast-close]").addEventListener("click", () => {
            this.dismiss(toast.id);
          });
          el.appendChild(card);
          observer.observe(card);
          this.measure();
        },

        measure() {
          const heights = {};
          root.querySelectorAll("[data-toast-id]").forEach((el) => {
            const card = el.firstElementChild;
            if (card) heights[el.dataset.toastId] = card.offsetHeight;
          });
          this.heights = heights;
        },

        // --- time -----------------------------------------------------------------------------
        get expanded() {
          return this.toasts.length > 0 && (this.hover || this.focused);
        },

        schedule(toast) {
          if (toast.remaining <= 0 || toast.leaving || this.expanded) return;
          toast.startedAt = Date.now();
          toast.timer = setTimeout(() => this.dismiss(toast.id), toast.remaining);
        },

        pause() {
          this.toasts.forEach((toast) => {
            if (toast.timer === null) return;
            clearTimeout(toast.timer);
            toast.timer = null;
            toast.remaining -= Date.now() - toast.startedAt;
          });
        },

        resume() {
          this.toasts.forEach((toast) => {
            if (toast.timer === null) this.schedule(toast);
          });
        },

        enter() {
          this.hover = true;
          this.pause();
        },

        leave() {
          this.hover = false;
          this.resume();
        },

        focusIn() {
          this.focused = true;
          this.pause();
        },

        focusOut(event) {
          if (root.contains(event.relatedTarget)) return;
          this.focused = false;
          this.resume();
        },

        dismiss(id) {
          const toast = this.toasts.find((item) => item.id === id);
          if (!toast || toast.leaving) return;
          clearTimeout(toast.timer);
          toast.timer = null;
          toast.frozenStyle = this.itemStyle(toast); // it fades out where it is, the others close up
          const hadFocus = root.contains(document.activeElement);
          toast.leaving = true;
          const remove = () => {
            this.toasts = this.toasts.filter((item) => item.id !== id);
            this.$nextTick(() => {
              // The closed card took the focus with it: hand it to the next one, if any.
              if (hadFocus && this.toasts.length > 0) {
                root.querySelector("[data-toast-close]").focus();
              }
              this.focused = root.contains(document.activeElement);
              if (this.toasts.length === 0) this.hover = false;
              this.measure();
              this.resume();
            });
          };
          if (reducedMotion()) remove();
          else setTimeout(remove, EXIT);
        },

        // --- geometry -------------------------------------------------------------------------
        // Cards that are leaving do not count: the others close up as soon as one starts to go.
        get live() {
          return this.toasts.filter((toast) => !toast.leaving);
        },

        frontHeight() {
          const front = this.live[0];
          return (front && this.heights[front.id]) || 0;
        },

        get stackHeight() {
          const live = this.live;
          if (live.length === 0) return 0;
          if (!this.expanded) return this.frontHeight() + (Math.min(live.length, VISIBLE) - 1) * PEEK;
          return live.reduce((sum, toast) => sum + (this.heights[toast.id] || 0), 0) + GAP * (live.length - 1);
        },

        // Position of the card in the stack (leaving cards keep the place they had).
        position(toast) {
          const live = this.live;
          const index = live.indexOf(toast);
          return index === -1 ? 0 : index;
        },

        itemStyle(toast) {
          if (toast.leaving && toast.frozenStyle) return toast.frozenStyle;
          const index = this.position(toast);
          let y;
          let scale = 1;
          if (this.expanded) {
            y = this.live
              .slice(0, index)
              .reduce((sum, other) => sum + (this.heights[other.id] || 0) + GAP, 0);
          } else {
            y = index * PEEK;
            scale = 1 - index * SCALE_STEP;
          }
          let style = `--y: ${y}px; --s: ${scale}; z-index: ${100 - index};`;
          if (!this.expanded && index > 0) style += ` height: ${this.frontHeight()}px;`;
          return style;
        },

        itemClass(toast) {
          const index = this.position(toast);
          return {
            "is-hidden": !toast.shown || toast.leaving,
            "is-folded": !this.expanded && index > 0,
            "is-behind": !this.expanded && index >= VISIBLE,
          };
        },
      };
    });
  });
})();
