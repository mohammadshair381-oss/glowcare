(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function render() {
    const grid = el("wishlistGrid");
    if (!grid) return;
    const ids = window.GlowCare.getWishlist();
    const catalog = window.GlowCare.getCatalog();
    const list = ids.map((id) => catalog.find((p) => p.id === id)).filter(Boolean);
    grid.innerHTML = "";
    if (!list.length) {
      grid.innerHTML = `<div class="panel empty" style="grid-column: 1 / -1;">
        <div><div class="title" style="font-size:18px; color: var(--text);">No wishlist items</div><p style="margin-top:6px;">Tap “Wishlist” on any product to save it.</p><div style="margin-top:12px;"><a class="btn btn--primary" href="shop.html">Browse products</a></div></div>
      </div>`;
      return;
    }
    list.forEach((p) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = `
        <a href="product.html?id=${encodeURIComponent(p.id)}" aria-label="View ${p.name}">
          <div class="card__media">
            <div class="card__badge">${p.badge || "New"}</div>
            <img src="${p.image}" alt="${p.name}" loading="lazy">
          </div>
          <div class="card__body">
            <div class="card__title"></div>
            <div class="card__row">
              <div class="price"></div>
              <button class="mini-btn" type="button">Remove</button>
            </div>
          </div>
        </a>
      `;
      card.querySelector(".card__title").textContent = p.name;
      card.querySelector(".price").textContent = window.GlowCare.money(p.price);
      card.querySelector(".mini-btn").addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        window.GlowCare.toggleWishlist(p.id);
        render();
      });
      grid.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("wishlistPage")) return;
    render();
  });
})();

