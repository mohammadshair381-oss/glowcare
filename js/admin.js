(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function safeParse(json, fallback) {
    try {
      const v = JSON.parse(json);
      return v === null || v === undefined ? fallback : v;
    } catch {
      return fallback;
    }
  }

  function getOrders() {
    return safeParse(localStorage.getItem(window.GlowCare.KEYS.orders) || "[]", []);
  }

  function setOrders(next) {
    localStorage.setItem(window.GlowCare.KEYS.orders, JSON.stringify(next || []));
  }

  function getOrderById(id) {
    if (!id) return null;
    return getOrders().find((o) => o.id === id) || null;
  }

  function money(n) {
    return window.GlowCare.money(Number(n) || 0);
  }

  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function invoiceHtml(order) {
    const ship = order?.shipping || {};
    const items = Array.isArray(order?.items) ? order.items : [];
    const totals = order?.totals || {};
    const placed = order?.placedAt ? new Date(order.placedAt).toLocaleString() : "";

    const rows = items
      .map((it) => {
        const qty = Number(it.qty) || 0;
        const price = Number(it.price) || 0;
        const line = qty * price;
        return `<tr>
          <td>${esc(it.name || it.productId || "-")}</td>
          <td style="text-align:right;">${qty}</td>
          <td style="text-align:right;">${esc(money(price))}</td>
          <td style="text-align:right;">${esc(money(line))}</td>
        </tr>`;
      })
      .join("");

    const paymentLabel = `${String(order?.method || "").toUpperCase()} • ${String(order?.status || "-").toUpperCase()}`;

    return `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Invoice ${esc(order?.id || "")}</title>
  <style>
    :root { --text:#121318; --sub:#5a5f6b; --line: rgba(18,19,24,0.12); }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; color: var(--text); }
    .page { padding: 28px; max-width: 900px; margin: 0 auto; }
    .top { display:flex; justify-content: space-between; gap: 20px; flex-wrap: wrap; align-items:flex-start; }
    h1 { margin: 0; font-size: 22px; letter-spacing: -0.01em; }
    .muted { color: var(--sub); font-size: 13px; line-height: 1.5; }
    .box { border: 1px solid var(--line); border-radius: 14px; padding: 14px; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
    table { width:100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 8px; vertical-align: top; }
    th { text-align:left; font-size: 12px; letter-spacing: 0.02em; text-transform: uppercase; color: var(--sub); }
    .totals { margin-top: 14px; display:grid; gap: 6px; max-width: 360px; margin-left:auto; }
    .row { display:flex; justify-content: space-between; gap: 12px; }
    .row strong { font-weight: 900; }
    .hr { height: 1px; background: var(--line); margin: 14px 0; }
    @media print { .no-print { display:none; } body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
  </style>
</head>
<body>
  <div class="page">
    <div class="top">
      <div>
        <h1>GlowCare Invoice</h1>
        <div class="muted">Order: <strong>${esc(order?.id || "-")}</strong><br>${esc(placed)}</div>
      </div>
      <div class="box">
        <div class="muted">Payment</div>
        <div style="font-weight:900; margin-top:4px;">${esc(paymentLabel)}</div>
        <div class="muted" style="margin-top:8px;">Fulfillment: <strong>${esc(order?.fulfillment || "-")}</strong></div>
      </div>
    </div>

    <div class="grid">
      <div class="box">
        <div class="muted">Bill to</div>
        <div style="font-weight:900; margin-top:4px;">${esc(ship.fullName || "-")}</div>
        <div class="muted" style="margin-top:6px;">
          ${esc(ship.phone || "")}${ship.email ? ` • ${esc(ship.email)}` : ""}<br>
          ${esc(ship.address1 || "")}${ship.address2 ? `, ${esc(ship.address2)}` : ""}<br>
          ${esc(ship.city || "")}${ship.state ? `, ${esc(ship.state)}` : ""} ${esc(ship.pincode || "")}
        </div>
      </div>
      <div class="box">
        <div class="muted">Notes</div>
        <div class="muted" style="margin-top:6px;">Frontend-only demo invoice. Use browser print to save as PDF.</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Item</th>
          <th style="text-align:right;">Qty</th>
          <th style="text-align:right;">Price</th>
          <th style="text-align:right;">Amount</th>
        </tr>
      </thead>
      <tbody>
        ${rows || `<tr><td colspan="4" class="muted">No items</td></tr>`}
      </tbody>
    </table>

    <div class="totals">
      <div class="row"><span class="muted">Subtotal</span><strong>${esc(money(totals.subtotal))}</strong></div>
      <div class="row"><span class="muted">Discount</span><strong>- ${esc(money(totals.discount))}</strong></div>
      <div class="row"><span class="muted">Shipping</span><strong>${Number(totals.shipping) === 0 ? "Free" : esc(money(totals.shipping))}</strong></div>
      <div class="hr"></div>
      <div class="row"><span style="font-weight:900;">Total</span><strong>${esc(money(totals.total))}</strong></div>
    </div>

    <div class="no-print" style="margin-top:16px; display:flex; gap:10px; justify-content:flex-end;">
      <button onclick="window.print()" style="height:42px; padding:0 14px; border-radius:12px; border:1px solid var(--line); background:#fff; font-weight:900; cursor:pointer;">Print / Save PDF</button>
      <button onclick="window.close()" style="height:42px; padding:0 14px; border-radius:12px; border:1px solid var(--line); background:#fff; font-weight:900; cursor:pointer;">Close</button>
    </div>
  </div>
</body>
</html>`;
  }

  function openInvoice(order) {
    const w = window.open("", "_blank");
    if (!w) {
      window.GlowCare.toast("Allow popups to generate bill");
      return;
    }
    w.document.open();
    w.document.write(invoiceHtml(order));
    w.document.close();
    w.focus();
  }

  let selectedOrderId = null;

  function renderOrderManager(order) {
    const wrap = el("omWrap");
    const hint = el("omHint");
    if (!wrap || !hint) return;

    if (!order) {
      wrap.hidden = true;
      hint.hidden = false;
      return;
    }

    hint.hidden = true;
    wrap.hidden = false;

    el("omOrderId").textContent = order.id;
    el("omPayment").value = order.status === "paid" ? "paid" : "unpaid";
    el("omFulfillment").value = order.fulfillment || "placed";

    const ship = order.shipping || {};
    el("omShipTo").textContent = `${ship.fullName || "—"} • ${ship.city || ""}${ship.state ? `, ${ship.state}` : ""} ${ship.pincode || ""}`;

    const itemsWrap = el("omItems");
    if (itemsWrap) {
      itemsWrap.innerHTML = "";
      (order.items || []).slice(0, 20).forEach((it) => {
        const row = document.createElement("div");
        row.className = "tag";
        const qty = Number(it.qty) || 0;
        const price = Number(it.price) || 0;
        row.textContent = `${it.name || it.productId || "Item"} × ${qty} • ${money(qty * price)}`;
        itemsWrap.appendChild(row);
      });
    }
  }

  function render() {
    const tableBody = el("adminProducts");
    const ordersBody = el("adminOrders");
    if (!tableBody || !ordersBody) return;

    const catalog = window.GlowCare.getCatalog();
    tableBody.innerHTML = "";
    catalog.forEach((p) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="tag">${p.id}</span></td>
        <td>${p.name}</td>
        <td>${p.brand}</td>
        <td>${p.category}</td>
        <td>${window.GlowCare.money(p.price)}</td>
        <td><div class="actions">
          <button class="btn btn--ghost tiny" type="button" data-act="edit">Edit</button>
          <button class="btn btn--ghost tiny" type="button" data-act="del">Delete</button>
        </div></td>
      `;
      tr.querySelector("[data-act='edit']").addEventListener("click", () => fillForm(p));
      tr.querySelector("[data-act='del']").addEventListener("click", () => {
        const next = catalog.filter((x) => x.id !== p.id);
        window.GlowCare.setCatalog(next);
        window.GlowCare.toast("Deleted product");
        render();
      });
      tableBody.appendChild(tr);
    });

    const orders = getOrders();
    ordersBody.innerHTML = "";
    orders.slice(0, 50).forEach((o) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="tag">${o.id}</span></td>
        <td>${new Date(o.placedAt).toLocaleString()}</td>
        <td>${o.userId || "-"}</td>
        <td>${String(o.method || "").toUpperCase()}</td>
        <td>${money(o.totals?.total || 0)}</td>
        <td>${String(o.status || "-").toUpperCase()}</td>
        <td>${String(o.fulfillment || "-").toUpperCase()}</td>
        <td>
          <div class="actions">
            <button class="btn btn--ghost tiny" type="button" data-act="view">View</button>
            <button class="btn btn--ghost tiny" type="button" data-act="bill">Bill</button>
          </div>
        </td>
      `;
      tr.querySelector("[data-act='view']").addEventListener("click", () => {
        selectedOrderId = o.id;
        renderOrderManager(getOrderById(selectedOrderId));
      });
      tr.querySelector("[data-act='bill']").addEventListener("click", () => openInvoice(o));
      tr.addEventListener("click", () => {
        selectedOrderId = o.id;
        renderOrderManager(getOrderById(selectedOrderId));
      });
      ordersBody.appendChild(tr);
    });

    renderOrderManager(getOrderById(selectedOrderId));
  }

  function fillForm(product) {
    el("pid").value = product?.id || "";
    el("name").value = product?.name || "";
    el("brand").value = product?.brand || "";
    el("category").value = product?.category || "skincare";
    el("price").value = String(product?.price || "");
    el("badge").value = product?.badge || "";
    el("description").value = product?.description || "";
    el("image").value = product?.image || "";
    const v = product?.variants?.[0] || null;
    el("variantSize").value = v ? String(v.size ?? v.sizeMl ?? "") : "";
    el("variantUnit").value = v?.unit || "ml";
  }

  function buildProductFromForm() {
    const id = el("pid").value.trim() || window.GlowCare.uid("p");
    const name = el("name").value.trim();
    const brand = el("brand").value.trim();
    const category = el("category").value;
    const price = Number(el("price").value || 0);
    const badge = el("badge").value.trim();
    const description = el("description").value.trim();
    const image = el("image").value.trim() || "assets/images/products/p1.svg";
    const size = Number(el("variantSize")?.value || 0);
    const unit = String(el("variantUnit")?.value || "ml").trim() || "ml";
    if (!name || !brand || !category || !Number.isFinite(price) || price <= 0) return null;

    return {
      id,
      name,
      brand,
      category,
      price: Math.round(price),
      badge,
      description,
      image,
      gallery: [image],
      rating: 4.3,
      reviewsCount: 0,
      ingredients: ["Glycerin"],
      skinTypeTags: ["all"],
      concernTags: [],
      variants: [{ sku: `${id}-A`, shade: "Original", size: Number.isFinite(size) && size > 0 ? Math.round(size) : 50, unit, stock: 10 }],
    };
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("adminPage")) return;
    if (!window.GlowCare.requireAdmin()) return;

    fillForm(null);
    render();

    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        window.GlowCare.logout();
        window.GlowCare.toast("Logged out");
        window.location.href = "index.html";
      });
    }

    el("newBtn").addEventListener("click", () => fillForm(null));

    const form = el("productForm");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const p = buildProductFromForm();
      if (!p) {
        window.GlowCare.toast("Fill required fields");
        return;
      }
      const catalog = window.GlowCare.getCatalog();
      const idx = catalog.findIndex((x) => x.id === p.id);
      if (idx >= 0) catalog[idx] = { ...catalog[idx], ...p };
      else catalog.unshift(p);
      window.GlowCare.setCatalog(catalog);
      window.GlowCare.toast(idx >= 0 ? "Updated product" : "Added product");
      render();
    });

    const omSave = el("omSave");
    if (omSave) {
      omSave.addEventListener("click", () => {
        const order = getOrderById(selectedOrderId);
        if (!order) return window.GlowCare.toast("Select an order first");

        const nextPayment = el("omPayment")?.value || "unpaid";
        const nextFulfillment = el("omFulfillment")?.value || "placed";

        const nextStatus = nextPayment === "paid" ? "paid" : "unpaid";
        const changedPayment = nextStatus !== order.status;
        const changedFulfillment = nextFulfillment !== (order.fulfillment || "placed");

        const updated = {
          ...order,
          status: nextStatus,
          fulfillment: nextFulfillment,
          timeline: Array.isArray(order.timeline) ? order.timeline.slice() : [],
        };
        const now = new Date().toISOString();
        if (changedPayment) updated.timeline.unshift({ at: now, label: `Admin: marked ${nextStatus}` });
        if (changedFulfillment) updated.timeline.unshift({ at: now, label: `Admin: ${nextFulfillment}` });

        const orders = getOrders();
        const idx = orders.findIndex((x) => x.id === order.id);
        if (idx >= 0) orders[idx] = updated;
        setOrders(orders);

        window.GlowCare.toast("Order updated");
        render();
      });
    }

    const omBill = el("omBill");
    if (omBill) {
      omBill.addEventListener("click", () => {
        const order = getOrderById(selectedOrderId);
        if (!order) return window.GlowCare.toast("Select an order first");
        openInvoice(order);
      });
    }
  });
})();
