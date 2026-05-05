(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function getMethod() {
    return document.querySelector("input[name='payMethod']:checked")?.value || "upi";
  }

  function setActive(method) {
    document.querySelectorAll(".method").forEach((m) => m.classList.toggle("is-active", m.dataset.method === method));
    const upi = el("upiBlock");
    const card = el("cardBlock");
    if (upi) upi.hidden = method !== "upi";
    if (card) card.hidden = method !== "card";

    const btn = el("payNow");
    if (btn) btn.textContent = method === "cod" ? "Place order" : "Pay now";
  }

  function validate(method) {
    const errs = [];
    if (method === "cod") return errs;
    if (method === "upi") {
      const vpa = el("upiVpa")?.value?.trim() || "";
      if (!vpa.includes("@")) errs.push("Enter valid UPI ID");
    }
    if (method === "card") {
      const num = (el("cardNumber")?.value || "").replace(/\s/g, "");
      const exp = el("cardExp")?.value?.trim() || "";
      const cvv = el("cardCvv")?.value?.trim() || "";
      if (num.length < 12) errs.push("Enter valid card number");
      if (!exp.includes("/")) errs.push("Enter expiry (MM/YY)");
      if (cvv.length < 3) errs.push("Enter CVV");
    }
    return errs;
  }

  function simulatePayment() {
    return Math.random() < 0.82;
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("paymentPage")) return;

    const totals = window.GlowCare.computeCartTotals();
    if (!totals.items.length) {
      el("paymentPage").innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">Cart is empty</div><p style="margin-top:6px;">Add items before payment.</p><div style="margin-top:12px;"><a class="btn btn--primary" href="shop.html">Shop</a></div></div></div>`;
      return;
    }

    const draft = window.GlowCare.getCheckoutDraft();
    if (!draft?.shipping) {
      window.location.href = "checkout.html";
      return;
    }

    const side = el("paymentSummary");
    if (side) {
      side.innerHTML = `
        <div class="panel">
          <div class="title" style="font-size:18px;">Payable</div>
          <div class="sum" style="margin-top:10px;">
            <div class="sum__row"><span>Total</span><strong>${window.GlowCare.money(totals.total)}</strong></div>
            <div class="sum__row"><span>Items</span><strong>${totals.items.reduce((s, i) => s + (Number(i.qty) || 0), 0)}</strong></div>
          </div>
          <p class="help" style="margin-top:10px;">Payment is simulated (frontend-only).</p>
        </div>
      `;
    }

    document.querySelectorAll("input[name='payMethod']").forEach((r) => {
      r.addEventListener("change", () => setActive(getMethod()));
    });
    setActive(getMethod());

    const payBtn = el("payNow");
    if (!payBtn) return;
    payBtn.addEventListener("click", async () => {
      const method = getMethod();
      const errs = validate(method);
      if (errs.length) {
        window.GlowCare.toast(errs[0]);
        return;
      }
      payBtn.disabled = true;
      payBtn.textContent = "Processing...";
      window.GlowCare.track("payment_attempt", { method });

      let ok = true;
      if (method !== "cod") {
        await new Promise((r) => setTimeout(r, 900));
        ok = simulatePayment();
        if (!ok) {
          payBtn.disabled = false;
          payBtn.textContent = "Retry payment";
          window.GlowCare.track("payment_failed", { method });
          window.GlowCare.toast("Payment failed. Please retry.");
          return;
        }
      } else {
        await new Promise((r) => setTimeout(r, 350));
      }

      const user = window.GlowCare.getCurrentUser();
      const now = new Date().toISOString();
      const order = {
        id: window.GlowCare.uid("ord"),
        placedAt: now,
        userId: user?.id || null,
        method,
        shipping: draft.shipping,
        totals: { subtotal: totals.subtotal, discount: totals.discount, shipping: totals.shipping, total: totals.total, coupon: totals.coupon?.code || null },
        items: totals.items.map((i) => ({
          productId: i.productId,
          variantKey: i.variantKey,
          qty: i.qty,
          price: i.product.price,
          name: i.product.name,
        })),
        status: method === "cod" ? "unpaid" : "paid",
        fulfillment: "placed",
        timeline:
          method === "cod"
            ? [
                { at: now, label: "Order placed" },
                { at: now, label: "Cash on delivery" },
                { at: now, label: "Payment pending" },
              ]
            : [
                { at: now, label: "Order placed" },
                { at: now, label: "Payment confirmed" },
              ],
      };

      window.GlowCare.saveOrder(order);
      localStorage.setItem("glowcare_last_order_v1", JSON.stringify(order));
      window.GlowCare.clearCart();
      window.GlowCare.track("payment_success", { method, orderId: order.id });
      window.location.href = "success.html";
    });
  });
})();
