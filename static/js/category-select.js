// Floating select for categories. The page ships a real <select>; this component hides it and draws a
// button plus a listbox with an icon and a color for each option. Choosing writes the value back to the
// <select> and fires `change`, so the form posts exactly what it would without JavaScript.
document.addEventListener("alpine:init", function () {
  Alpine.data("categorySelect", function () {
    return {
      enhanced: false,
      open: false,
      active: 0,
      value: "",
      currentHtml: "",

      init() {
        const native = this.$refs.native;
        this.value = native.value;
        this.refresh();
        this.enhanced = true;
        native.addEventListener("change", () => {
          this.value = native.value;
          this.refresh();
        });
      },

      get items() {
        return Array.from(this.$refs.list.querySelectorAll("[role=option]"));
      },

      refresh() {
        const items = this.items;
        const current = items.find((i) => i.dataset.value === this.value) || items[0];
        this.currentHtml = current.innerHTML;
        items.forEach((i) => i.setAttribute("aria-selected", String(i === current)));
      },

      toggle() {
        if (this.open) this.close();
        else this.show();
      },

      show() {
        this.open = true;
        this.setActive(Math.max(0, this.items.findIndex((i) => i.dataset.value === this.value)));
      },

      close() {
        if (!this.open) return;
        this.open = false;
        this.$refs.button.removeAttribute("aria-activedescendant");
      },

      setActive(index) {
        const items = this.items;
        this.active = Math.min(Math.max(index, 0), items.length - 1);
        items.forEach((item, n) => (item.dataset.active = String(n === this.active)));
        const current = items[this.active];
        this.$refs.button.setAttribute("aria-activedescendant", current.id);
        current.scrollIntoView({ block: "nearest" });
      },

      choose(index) {
        const item = this.items[index];
        if (!item) return;
        this.$refs.native.value = item.dataset.value;
        this.$refs.native.dispatchEvent(new Event("change", { bubbles: true }));
        this.close();
      },

      // Focus stays on the button (the select-only combobox pattern); the options are only
      // announced through aria-activedescendant, so there is no focus to lose while the list opens.
      onKey(event) {
        if (!this.open) {
          if (["ArrowDown", "ArrowUp", "Enter", " "].includes(event.key)) {
            event.preventDefault();
            this.show();
          }
          return;
        }
        const handled = {
          ArrowDown: () => this.setActive(this.active + 1),
          ArrowUp: () => this.setActive(this.active - 1),
          Home: () => this.setActive(0),
          End: () => this.setActive(this.items.length - 1),
          Enter: () => this.choose(this.active),
          " ": () => this.choose(this.active),
          // Stops the keystroke here so Esc closes the list, not the modal around it.
          Escape: () => this.close(),
        }[event.key];
        if (handled) {
          event.preventDefault();
          event.stopPropagation();
          handled();
        } else if (event.key === "Tab") {
          this.close();
        }
      },
    };
  });
});
