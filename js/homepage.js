(() => {
  function renderCard(product) {
    const card = document.createElement("article");
    card.className = "card";
    const variants = Array.isArray(product.variants) ? product.variants : [];
    const showVariantPick = variants.length > 1;
    card.innerHTML = `
      <a href="product.html?id=${encodeURIComponent(product.id)}" aria-label="View ${product.name}">
        <div class="card__media">
          <div class="card__badge">${product.badge || "New"}</div>
          <img src="${product.image}" alt="${product.name}" loading="lazy">
        </div>
        <div class="card__body">
          <div class="card__title"></div>
          <div class="card__sub"></div>
          <div class="card__row">
            <div class="price"></div>
            <div style="display:flex; gap:10px; align-items:center; justify-content:flex-end;">
              ${showVariantPick ? `<select class="select" data-var style="height:38px; padding: 0 10px; border-radius:12px; font-size:12px;"></select>` : ""}
              <button type="button" class="mini-btn">Add</button>
            </div>
          </div>
        </div>
      </a>
    `;
    card.querySelector(".card__title").textContent = product.name;
    card.querySelector(".card__sub").textContent = `${product.brand} • ${product.category}`;
    card.querySelector(".price").textContent = window.GlowCare.money(product.price);
    const select = card.querySelector("[data-var]");
    if (select && showVariantPick) {
      select.innerHTML = variants.map((v) => `<option value="${v.sku}">${window.GlowCare.formatVariantSize(v)}</option>`).join("");
    }
    card.querySelector(".mini-btn").addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const variantKey = select?.value || variants?.[0]?.sku;
      const variant = window.GlowCare.getVariant(product, variantKey);
      if (!variant) return window.GlowCare.toast("Variant missing");
      window.GlowCare.addToCart(product.id, variant.sku, 1);
    });
    return card;
  }

  function setupCountdown() {
    const h = document.getElementById("cdH");
    const m = document.getElementById("cdM");
    const s = document.getElementById("cdS");
    if (!h || !m || !s) return;
    const endsAt = new Date();
    endsAt.setHours(endsAt.getHours() + 6);
    function tick() {
      const diff = Math.max(0, endsAt.getTime() - Date.now());
      const totalSeconds = Math.floor(diff / 1000);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      h.textContent = String(hours).padStart(2, "0");
      m.textContent = String(minutes).padStart(2, "0");
      s.textContent = String(seconds).padStart(2, "0");
    }
    tick();
    window.setInterval(tick, 1000);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const best = document.getElementById("homeBestsellers");
    const newArrivals = document.getElementById("homeNewArrivals");
    if (!best && !newArrivals) return;
    const catalog = window.GlowCare.getCatalog();
    if (best) {
      const list = catalog.filter((p) => String(p.badge).toLowerCase().includes("best")).slice(0, 8);
      best.innerHTML = "";
      list.forEach((p) => best.appendChild(renderCard(p)));
    }
    if (newArrivals) {
      const list = catalog.filter((p) => String(p.badge).toLowerCase().includes("new")).slice(0, 8);
      newArrivals.innerHTML = "";
      list.forEach((p) => newArrivals.appendChild(renderCard(p)));
    }
    setupCountdown();
  });
})();
