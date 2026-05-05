(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function renderProfile(user) {
    el("acctName").textContent = user.name;
    el("acctEmail").textContent = user.email;
    el("acctRole").textContent = user.role === "admin" ? "Admin" : "Customer";
  }

  function renderOrders(user) {
    const wrap = el("ordersList");
    if (!wrap) return;
    const orders = window.GlowCare.getOrders().filter((o) => o.userId === user.id);
    wrap.innerHTML = "";
    if (!orders.length) {
      wrap.innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">No orders yet</div><p style="margin-top:6px;">Your orders will appear here after checkout.</p><div style="margin-top:12px;"><a class="btn btn--primary" href="shop.html">Shop now</a></div></div></div>`;
      return;
    }
    orders.slice(0, 12).forEach((o) => {
      const card = document.createElement("div");
      card.className = "panel";
      const items = (o.items || []).reduce((s, i) => s + (Number(i.qty) || 0), 0);
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
          <div>
            <div class="title" style="font-size:16px;">Order ${o.id}</div>
            <p style="margin-top:4px;">${new Date(o.placedAt).toLocaleString()} • ${items} item(s)</p>
          </div>
          <div class="title" style="font-size:16px;">${window.GlowCare.money(o.totals?.total || 0)}</div>
        </div>
        <div class="timeline">
          ${(o.timeline || []).slice(0, 4).map((t) => `<span class="chip2">${t.label}</span>`).join("")}
        </div>
      `;
      wrap.appendChild(card);
    });
  }

  function renderNotifications(user) {
    const wrap = el("notifList");
    if (!wrap) return;
    const ns = (() => {
      try {
        return JSON.parse(localStorage.getItem(window.GlowCare.KEYS.notifications) || "[]");
      } catch {
        return [];
      }
    })();
    const list = ns.filter((n) => !n.userId || n.userId === user.id).slice(0, 20);
    wrap.innerHTML = "";
    if (!list.length) {
      wrap.innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">No notifications</div><p style="margin-top:6px;">You’re all caught up.</p></div></div>`;
      return;
    }
    list.forEach((n) => {
      const card = document.createElement("div");
      card.className = "panel";
      card.innerHTML = `<div class="title" style="font-size:14px;">${n.title || "Update"}</div><p style="margin-top:6px;">${n.body || ""}</p>`;
      wrap.appendChild(card);
    });
  }

  function renderFunnel() {
    const wrap = el("funnelStats");
    if (!wrap) return;
    const f = (() => {
      try {
        return JSON.parse(localStorage.getItem(window.GlowCare.KEYS.funnel) || "{\"events\":[]}");
      } catch {
        return { events: [] };
      }
    })();
    const by = {};
    (f.events || []).forEach((e) => {
      by[e.name] = (by[e.name] || 0) + 1;
    });
    const top = Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 8);
    wrap.innerHTML = "";
    if (!top.length) {
      wrap.innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">No activity yet</div><p style="margin-top:6px;">Browse products to generate events.</p></div></div>`;
      return;
    }
    const card = document.createElement("div");
    card.className = "panel";
    card.innerHTML = `<div class="title" style="font-size:16px;">Funnel stats (local)</div><div style="margin-top:10px; display:grid; gap:8px;"></div>`;
    const list = card.querySelector("div:last-child");
    top.forEach(([k, v]) => {
      const row = document.createElement("div");
      row.style.display = "flex";
      row.style.justifyContent = "space-between";
      row.style.gap = "12px";
      row.innerHTML = `<span style="color:var(--sub); font-size:14px;">${k}</span><strong style="color:var(--text);">${v}</strong>`;
      list.appendChild(row);
    });
    wrap.appendChild(card);
  }

  function setupTabs() {
    const buttons = Array.from(document.querySelectorAll("[data-acct-tab]"));
    const panels = Array.from(document.querySelectorAll("[data-acct-panel]"));
    if (!buttons.length || !panels.length) return;
    function open(key) {
      buttons.forEach((b) => b.classList.toggle("is-active", b.dataset.acctTab === key));
      panels.forEach((p) => (p.hidden = p.dataset.acctPanel !== key));
    }
    buttons.forEach((b) => b.addEventListener("click", () => open(b.dataset.acctTab)));
    open(buttons[0].dataset.acctTab);
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("accountPage")) return;
    const user = window.GlowCare.getCurrentUser();
    if (!user) {
      window.location.href = `login.html?next=${encodeURIComponent("account.html")}`;
      return;
    }
    renderProfile(user);
    renderOrders(user);
    renderNotifications(user);
    renderFunnel();
    setupTabs();

    const logoutBtn = el("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        window.GlowCare.logout();
        window.GlowCare.toast("Logged out");
        window.location.href = "index.html";
      });
    }
  });
})();

