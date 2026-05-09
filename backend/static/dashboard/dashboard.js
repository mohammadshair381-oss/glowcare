(() => {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function csrfToken() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return el ? el.value : "";
  }

  function initSortable() {
    const hosts = qsa("[data-sortable]");
    if (!hosts.length || typeof Sortable === "undefined") return;
    hosts.forEach((host) => {
      Sortable.create(host, {
        handle: ".dhandle",
        animation: 150,
        ghostClass: "drow--ghost",
      });
    });
  }

  function initSaveSections() {
    const btn = qs("[data-save-sections]");
    const form = qs("#sectionsForm");
    const list = qs("#sectionsSortable");
    if (!btn || !form || !list) return;

    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]").map((c) => [c.dataset.enabled, c.checked]);

      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));

      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        if (json?.ok) btn.textContent = "Saved";
        else btn.textContent = "Save failed";
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save changes"), 1200);
    });
  }

  function initSaveHero() {
    const btn = qs("[data-save-hero]");
    const form = qs("#heroOrderForm");
    const list = qs("#heroSortable");
    if (!btn || !form || !list) return;
    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]", list).map((c) => [c.dataset.enabled, c.checked]);
      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));
      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        btn.textContent = json?.ok ? "Saved" : "Save failed";
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save order"), 1200);
    });
  }

  function initSaveNav() {
    const btn = qs("[data-save-nav]");
    const form = qs("#navOrderForm");
    const list = qs("#navSortable");
    if (!btn || !form || !list) return;
    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]", list).map((c) => [c.dataset.enabled, c.checked]);
      const deletePairs = qsa("input[data-delete]", list).map((c) => [c.dataset.delete, c.checked]);
      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));
      deletePairs.forEach(([id, val]) => body.set(`delete_${id}`, val ? "1" : "0"));
      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        btn.textContent = json?.ok ? "Saved" : "Save failed";
        if (json?.ok) window.setTimeout(() => window.location.reload(), 350);
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save menu"), 1200);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      initSortable();
      initSaveSections();
      initSaveHero();
      initSaveNav();
    });
  } else {
    initSortable();
    initSaveSections();
    initSaveHero();
    initSaveNav();
  }
})();
