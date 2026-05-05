(() => {
  function el(id) {
    return document.getElementById(id);
  }
  document.addEventListener("DOMContentLoaded", () => {
    if (!el("successPage")) return;
    const last = (() => {
      try {
        return JSON.parse(localStorage.getItem("glowcare_last_order_v1") || "null");
      } catch {
        return null;
      }
    })();
    const wrap = el("orderSummary");
    if (!wrap) return;
    if (!last) {
      wrap.innerHTML = `<div class="order__row"><span>Order</span><strong>Not found</strong></div>`;
      return;
    }
    el("orderId").textContent = last.id;
    wrap.innerHTML = `
      <div class="order__row"><span>Total</span><strong>${window.GlowCare.money(last.totals?.total || 0)}</strong></div>
      <div class="order__row"><span>Payment</span><strong>${String(last.method || "").toUpperCase()}</strong></div>
      <div class="order__row"><span>Status</span><strong>${String(last.status || "-").toUpperCase()}</strong></div>
      <div class="order__row"><span>Ship to</span><strong>${last.shipping?.city || ""}, ${last.shipping?.state || ""}</strong></div>
      <div class="order__row"><span>Items</span><strong>${(last.items || []).reduce((s, i) => s + (Number(i.qty) || 0), 0)}</strong></div>
    `;
  });
})();
