(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function render() {
    const wrap = el("cartItems");
    const side = el("cartSummary");
    if (!wrap || !side) return;

    const totals = window.GlowCare.computeCartTotals();
    wrap.innerHTML = "";

    if (!totals.items.length) {
      wrap.innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">Your cart is empty</div><p style="margin-top:6px;">Explore bestselling skincare and build your routine.</p><div style="margin-top:12px;"><a class="btn btn--primary" href="shop.html">Shop now</a></div></div></div>`;
      side.innerHTML = `<div class="panel"><div class="title" style="font-size:18px;">Summary</div><p style="margin-top:8px;">Add items to see totals.</p></div>`;
      return;
    }

    totals.items.forEach((it) => {
      const row = document.createElement("div");
      row.className = "cart-item";
      row.innerHTML = `
        <img class="cart-item__img" alt="" loading="lazy">
        <div>
          <div class="cart-item__title"></div>
          <div class="cart-item__meta"></div>
          <div class="cart-item__row">
            <div class="price"></div>
            <div class="qty" aria-label="Quantity">
              <button class="qty__btn" type="button" aria-label="Decrease">&#8722;</button>
              <input class="qty__input" inputmode="numeric" value="${it.qty}" aria-label="Quantity input">
              <button class="qty__btn" type="button" aria-label="Increase">+</button>
            </div>
          </div>
          <div class="cart-item__row">
            <button class="btn btn--ghost tiny" type="button" data-act="remove">Remove</button>
          </div>
        </div>
      `;
      row.querySelector("img").src = it.product.image;
      row.querySelector(".cart-item__title").textContent = it.product.name;
      row.querySelector(".cart-item__meta").textContent = `${it.variant.shade || "Original"} • ${window.GlowCare.formatVariantSize(it.variant)}`;
      row.querySelector(".price").textContent = window.GlowCare.money(it.product.price);

      const [minus, input, plus] = row.querySelectorAll(".qty__btn, .qty__input");
      minus.addEventListener("click", () => {
        window.GlowCare.updateCartQty(it.id, (Number(input.value) || 1) - 1);
        render();
      });
      plus.addEventListener("click", () => {
        window.GlowCare.updateCartQty(it.id, (Number(input.value) || 1) + 1);
        render();
      });
      input.addEventListener("blur", () => {
        window.GlowCare.updateCartQty(it.id, Number(input.value) || 1);
        render();
      });

      row.querySelector("[data-act='remove']").addEventListener("click", () => {
        window.GlowCare.removeCartItem(it.id);
        render();
      });

      wrap.appendChild(row);
    });

    side.innerHTML = `
      <div class="panel">
        <div class="title" style="font-size:18px;">Order summary</div>
        <div class="sum">
          <div class="sum__row"><span>Subtotal</span><strong>${window.GlowCare.money(totals.subtotal)}</strong></div>
          <div class="sum__row"><span>Discount</span><strong>- ${window.GlowCare.money(totals.discount)}</strong></div>
          <div class="sum__row"><span>Shipping</span><strong>${totals.shipping === 0 ? "Free" : window.GlowCare.money(totals.shipping)}</strong></div>
          <div class="sum__row" style="border-top:1px solid rgba(18,19,24,0.08); padding-top:10px; margin-top:6px;"><span>Total</span><strong>${window.GlowCare.money(totals.total)}</strong></div>
        </div>

        <div class="coupon">
          <input class="input" id="couponCode" placeholder="Coupon code (GLOW10)">
          <button class="btn btn--ghost tiny" type="button" id="applyCoupon">Apply</button>
        </div>
        <p class="help">Free shipping above ₹${window.GlowCare.SHIPPING.freeAbove}.</p>

        <div style="display:grid; gap:10px; margin-top:12px;">
          <button class="btn btn--primary btn--full" type="button" id="checkoutBtn"></button>
          <button class="btn btn--ghost btn--full" type="button" id="clearCart">Clear cart</button>
        </div>
      </div>
    `;

    const couponInput = el("couponCode");
    const applyBtn = el("applyCoupon");
    if (applyBtn && couponInput) applyBtn.addEventListener("click", () => window.GlowCare.applyCoupon(couponInput.value));

    const checkoutBtn = el("checkoutBtn");
    const user = window.GlowCare.getCurrentUser();
    if (checkoutBtn) {
      checkoutBtn.textContent = user ? "Checkout" : "Login to checkout";
      checkoutBtn.addEventListener("click", () => {
        if (!user) {
          window.location.href = `login.html?next=${encodeURIComponent("checkout.html")}`;
          return;
        }
        window.location.href = "checkout.html";
      });
    }
    const clearBtn = el("clearCart");
    if (clearBtn) clearBtn.addEventListener("click", () => { window.GlowCare.clearCart(); render(); });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("cartPage")) return;
    render();
  });
})();
