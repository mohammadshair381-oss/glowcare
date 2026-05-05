(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function renderSummary() {
    const side = el("checkoutSummary");
    if (!side) return;
    const totals = window.GlowCare.computeCartTotals();
    if (!totals.items.length) {
      side.innerHTML = `<div class="panel"><div class="title" style="font-size:18px;">Cart is empty</div><p style="margin-top:8px;">Add items before checkout.</p><div style="margin-top:12px;"><a class="btn btn--primary" href="shop.html">Shop</a></div></div>`;
      return false;
    }
    side.innerHTML = `
      <div class="panel">
        <div class="title" style="font-size:18px;">Order summary</div>
        <div class="sum" style="margin-top:10px;">
          <div class="sum__row"><span>Subtotal</span><strong>${window.GlowCare.money(totals.subtotal)}</strong></div>
          <div class="sum__row"><span>Discount</span><strong>- ${window.GlowCare.money(totals.discount)}</strong></div>
          <div class="sum__row"><span>Shipping</span><strong>${totals.shipping === 0 ? "Free" : window.GlowCare.money(totals.shipping)}</strong></div>
          <div class="sum__row" style="border-top:1px solid rgba(18,19,24,0.08); padding-top:10px; margin-top:6px;"><span>Total</span><strong>${window.GlowCare.money(totals.total)}</strong></div>
        </div>
      </div>
    `;
    return true;
  }

  function validateShipping(data) {
    const errors = {};
    if (!data.fullName || data.fullName.length < 2) errors.fullName = "Enter full name";
    if (!data.phone || String(data.phone).replace(/\D/g, "").length < 10) errors.phone = "Enter valid phone";
    if (!data.pincode || String(data.pincode).replace(/\D/g, "").length < 6) errors.pincode = "Enter pincode";
    if (!data.address1 || data.address1.length < 5) errors.address1 = "Enter address";
    if (!data.city) errors.city = "Enter city";
    if (!data.state) errors.state = "Enter state";
    return errors;
  }

  function showErrors(errors) {
    document.querySelectorAll("[data-err]").forEach((x) => (x.textContent = ""));
    Object.entries(errors).forEach(([k, v]) => {
      const node = document.querySelector(`[data-err='${k}']`);
      if (node) node.textContent = v;
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("checkoutPage")) return;
    if (!renderSummary()) return;

    const draft = window.GlowCare.getCheckoutDraft();
    const shipping = draft.shipping || {};
    ["fullName", "phone", "email", "pincode", "address1", "address2", "city", "state"].forEach((k) => {
      const input = el(k);
      if (input && shipping[k]) input.value = shipping[k];
    });

    const form = el("shippingForm");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data = {
        fullName: el("fullName")?.value?.trim() || "",
        phone: el("phone")?.value?.trim() || "",
        email: el("email")?.value?.trim() || "",
        pincode: el("pincode")?.value?.trim() || "",
        address1: el("address1")?.value?.trim() || "",
        address2: el("address2")?.value?.trim() || "",
        city: el("city")?.value?.trim() || "",
        state: el("state")?.value?.trim() || "",
      };
      const errors = validateShipping(data);
      showErrors(errors);
      if (Object.keys(errors).length) {
        window.GlowCare.toast("Fix shipping details");
        return;
      }
      window.GlowCare.setCheckoutDraft({ shipping: data });
      window.GlowCare.track("checkout_shipping_saved", { city: data.city, state: data.state });
      window.location.href = "payment.html";
    });
  });
})();

