(() => {
  function el(id) {
    return document.getElementById(id);
  }

  function starRow(rating) {
    const r = Math.round((Number(rating) || 0) * 2) / 2;
    const full = Math.floor(r);
    const half = r - full >= 0.5;
    const empty = 5 - full - (half ? 1 : 0);
    return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
  }

  function renderGallery(product) {
    const main = el("prodMainImg");
    const thumbs = el("prodThumbs");
    if (!main || !thumbs) return;
    main.src = product.gallery?.[0] || product.image;
    main.alt = product.name;

    thumbs.innerHTML = "";
    const list = (product.gallery && product.gallery.length ? product.gallery : [product.image]).slice(0, 8);
    list.forEach((src, idx) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "thumb" + (idx === 0 ? " is-active" : "");
      b.innerHTML = `<img alt="" loading="lazy">`;
      b.querySelector("img").src = src;
      b.addEventListener("click", () => {
        thumbs.querySelectorAll(".thumb").forEach((x) => x.classList.remove("is-active"));
        b.classList.add("is-active");
        main.src = src;
      });
      thumbs.appendChild(b);
    });
  }

  function uniqueBy(arr, keyFn) {
    const seen = new Set();
    const out = [];
    for (const x of arr) {
      const k = keyFn(x);
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(x);
    }
    return out;
  }

  function renderVariants(product) {
    const shadeWrap = el("shadeWrap");
    const sizeWrap = el("sizeWrap");
    const stockMsg = el("stockMsg");
    const addBtn = el("addBtn");
    if (!shadeWrap || !sizeWrap || !stockMsg || !addBtn) return null;

    const variants = product.variants || [];
    const shades = uniqueBy(variants, (v) => v.shade || "Original").map((v) => v.shade || "Original");
    const sizesForShade = (shade) => variants.filter((v) => (v.shade || "Original") === shade);

    let selectedShade = shades[0] || "Original";
    let selectedSku = sizesForShade(selectedShade)[0]?.sku || null;

    function setStock() {
      const variant = window.GlowCare.getVariant(product, selectedSku);
      const inStock = (variant?.stock ?? 0) > 0;
      stockMsg.textContent = inStock ? `In stock • ${variant.stock} left` : "Out of stock";
      addBtn.disabled = !inStock;
    }

    function renderShade() {
      shadeWrap.innerHTML = "";
      shades.forEach((s) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "seg" + (s === selectedShade ? " is-active" : "");
        b.textContent = s;
        b.addEventListener("click", () => {
          selectedShade = s;
          selectedSku = sizesForShade(selectedShade)[0]?.sku || null;
          renderShade();
          renderSize();
          setStock();
        });
        shadeWrap.appendChild(b);
      });
    }

    function renderSize() {
      sizeWrap.innerHTML = "";
      const list = sizesForShade(selectedShade);
      list.forEach((v) => {
        const label = window.GlowCare.formatVariantSize(v);
        const b = document.createElement("button");
        b.type = "button";
        b.className = "seg" + (v.sku === selectedSku ? " is-active" : "");
        b.innerHTML = `<span>${label}</span><small>${window.GlowCare.money(product.price)}</small>`;
        b.addEventListener("click", () => {
          selectedSku = v.sku;
          renderSize();
          setStock();
        });
        sizeWrap.appendChild(b);
      });
    }

    renderShade();
    renderSize();
    setStock();
    return () => selectedSku;
  }

  function renderIngredients(product) {
    const ul = el("ingredientsList");
    if (!ul) return;
    ul.innerHTML = "";
    (product.ingredients || []).slice(0, 10).forEach((x) => {
      const li = document.createElement("li");
      li.textContent = x;
      ul.appendChild(li);
    });
  }

  function renderReviews(product) {
    const wrap = el("reviews");
    const breakdown = el("ratingBreakdown");
    if (!wrap || !breakdown) return;

    const rating = Number(product.rating) || 0;
    const count = Number(product.reviewsCount) || 0;
    el("ratingValue").textContent = rating.toFixed(1);
    el("ratingStars").textContent = starRow(rating);
    el("ratingCount").textContent = `${count} reviews`;

    const bars = [5, 4, 3, 2, 1].map((s) => {
      const frac = Math.max(0.02, Math.min(0.95, (rating / 5) * (s / 5)));
      return { s, frac };
    });
    breakdown.innerHTML = "";
    bars.forEach((b) => {
      const row = document.createElement("div");
      row.className = "barrow";
      row.innerHTML = `<span class="barrow__l">${b.s}★</span><div class="bar"><div class="bar__fill"></div></div><span class="barrow__r">${Math.round(b.frac * 100)}%</span>`;
      row.querySelector(".bar__fill").style.width = `${Math.round(b.frac * 100)}%`;
      breakdown.appendChild(row);
    });

    const pool = [
      { name: "Aarohi", text: "Texture is super light and feels premium. No stickiness.", stars: 5 },
      { name: "Nikhil", text: "Good for daily use. My skin looks calmer in a week.", stars: 4 },
      { name: "Sneha", text: "Packaging is cute. Works well under makeup.", stars: 5 },
      { name: "Riya", text: "Nice glow, but I use it only at night.", stars: 4 },
    ];
    wrap.innerHTML = "";
    pool.slice(0, 3).forEach((r) => {
      const c = document.createElement("div");
      c.className = "review";
      c.innerHTML = `<div class="review__top"><strong></strong><span class="review__stars"></span></div><p class="review__text"></p>`;
      c.querySelector("strong").textContent = r.name;
      c.querySelector(".review__stars").textContent = "★".repeat(r.stars) + "☆".repeat(5 - r.stars);
      c.querySelector(".review__text").textContent = r.text;
      wrap.appendChild(c);
    });
  }

  function renderRelated(product) {
    const rail = el("related");
    if (!rail) return;
    const all = window.GlowCare.getCatalog();
    const list = all
      .filter((p) => p.id !== product.id)
      .filter((p) => p.category === product.category || p.brand === product.brand)
      .slice(0, 6);
    rail.innerHTML = "";
    list.forEach((p) => {
      const card = document.createElement("article");
      card.className = "card";
      const variants = Array.isArray(p.variants) ? p.variants : [];
      const showVariantPick = variants.length > 1;
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
              <div style="display:flex; gap:10px; align-items:center; justify-content:flex-end;">
                ${showVariantPick ? `<select class="select" data-var style="height:38px; padding: 0 10px; border-radius:12px; font-size:12px;"></select>` : ""}
                <button class="mini-btn" type="button">Add</button>
              </div>
            </div>
          </div>
        </a>
      `;
      card.querySelector(".card__title").textContent = p.name;
      card.querySelector(".price").textContent = window.GlowCare.money(p.price);
      const select = card.querySelector("[data-var]");
      if (select && showVariantPick) {
        select.innerHTML = variants.map((v) => `<option value="${v.sku}">${window.GlowCare.formatVariantSize(v)}</option>`).join("");
      }
      card.querySelector(".mini-btn").addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const variantKey = select?.value || variants?.[0]?.sku;
        const v = window.GlowCare.getVariant(p, variantKey);
        if (!v) return window.GlowCare.toast("Variant missing");
        window.GlowCare.addToCart(p.id, v.sku, 1);
      });
      rail.appendChild(card);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("productPage")) return;
    const q = window.GlowCare.parseQuery();
    const id = q.id || "";
    const product = window.GlowCare.getProductById(id);
    if (!product) {
      el("productPage").innerHTML = `<div class="panel empty"><div><div class="title" style="font-size:18px; color: var(--text);">Product not found</div><p style="margin-top:6px;">Try going back to the shop.</p><div style="margin-top:12px;"><a class="btn btn--ghost" href="shop.html">Go to shop</a></div></div></div>`;
      return;
    }

    document.title = `${product.name} | GlowCare`;
    el("bcName").textContent = product.name;
    el("prodName").textContent = product.name;
    el("prodBrand").textContent = `${product.brand} • ${product.category}`;
    el("prodDesc").textContent = product.description;
    el("prodPrice").textContent = window.GlowCare.money(product.price);

    const wishBtn = el("wishBtn");
    if (wishBtn) {
      const sync = () => {
        const on = window.GlowCare.isWishlisted(product.id);
        wishBtn.classList.toggle("is-active", on);
        wishBtn.textContent = on ? "Wishlisted" : "Wishlist";
      };
      wishBtn.addEventListener("click", () => {
        window.GlowCare.toggleWishlist(product.id);
        sync();
      });
      sync();
    }

    renderGallery(product);
    renderIngredients(product);
    renderReviews(product);
    renderRelated(product);

    const getSku = renderVariants(product);
    const addBtn = el("addBtn");
    const qtyInput = el("qty");
    const minus = el("qtyMinus");
    const plus = el("qtyPlus");

    function getQty() {
      return window.GlowCare.clampInt(qtyInput?.value, 1, 10);
    }
    function setQty(next) {
      if (!qtyInput) return;
      qtyInput.value = String(window.GlowCare.clampInt(next, 1, 10));
    }
    if (qtyInput) {
      qtyInput.addEventListener("input", () => setQty(getQty()));
      qtyInput.addEventListener("blur", () => setQty(getQty()));
    }
    if (minus) minus.addEventListener("click", () => setQty(getQty() - 1));
    if (plus) plus.addEventListener("click", () => setQty(getQty() + 1));
    if (addBtn) {
      addBtn.addEventListener("click", () => {
        const sku = getSku ? getSku() : product.variants?.[0]?.sku;
        if (!sku) return window.GlowCare.toast("Variant missing");
        window.GlowCare.addToCart(product.id, sku, getQty());
      });
    }
  });
})();
