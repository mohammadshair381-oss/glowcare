(() => {
  const state = {
    q: "",
    sort: "popular",
    brand: [],
    category: "",
    skin: [],
    concern: [],
    badge: "",
    min: "",
    max: "",
  };

  function normalizeFromQuery() {
    const q = window.GlowCare.parseQuery();
    state.q = q.q || "";
    state.sort = q.sort || "popular";
    state.category = q.category || "";
    state.badge = q.badge || "";
    state.min = q.min || "";
    state.max = q.max || "";
    state.brand = Array.isArray(q.brand) ? q.brand : q.brand ? [q.brand] : [];
    state.skin = Array.isArray(q.skin) ? q.skin : q.skin ? [q.skin] : [];
    state.concern = Array.isArray(q.concern) ? q.concern : q.concern ? [q.concern] : [];
  }

  function writeQuery() {
    window.GlowCare.setQuery({
      q: state.q || "",
      sort: state.sort || "popular",
      category: state.category || "",
      badge: state.badge || "",
      min: state.min || "",
      max: state.max || "",
      brand: state.brand,
      skin: state.skin,
      concern: state.concern,
    });
  }

  function scorePopular(p) {
    return (Number(p.rating) || 0) * 1000 + (Number(p.reviewsCount) || 0);
  }

  function applyFilters(catalog) {
    let list = catalog.slice();

    if (state.q) {
      const q = state.q.toLowerCase();
      list = list.filter((p) => `${p.name} ${p.brand} ${p.category} ${p.description}`.toLowerCase().includes(q));
    }
    if (state.category) list = list.filter((p) => p.category === state.category);
    if (state.badge) list = list.filter((p) => String(p.badge || "").toLowerCase().includes(String(state.badge).toLowerCase()));

    if (state.brand.length) {
      const set = new Set(state.brand.map(String));
      list = list.filter((p) => set.has(String(p.brand)));
    }
    if (state.skin.length) {
      const set = new Set(state.skin.map(String));
      list = list.filter((p) => (p.skinTypeTags || []).some((t) => set.has(String(t))));
    }
    if (state.concern.length) {
      const set = new Set(state.concern.map(String));
      list = list.filter((p) => (p.concernTags || []).some((t) => set.has(String(t))));
    }

    const min = state.min !== "" ? Number(state.min) : null;
    const max = state.max !== "" ? Number(state.max) : null;
    if (Number.isFinite(min)) list = list.filter((p) => (Number(p.price) || 0) >= min);
    if (Number.isFinite(max)) list = list.filter((p) => (Number(p.price) || 0) <= max);

    if (state.sort === "price_asc") list.sort((a, b) => (a.price || 0) - (b.price || 0));
    if (state.sort === "price_desc") list.sort((a, b) => (b.price || 0) - (a.price || 0));
    if (state.sort === "rating") list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    if (state.sort === "popular") list.sort((a, b) => scorePopular(b) - scorePopular(a));

    return list;
  }

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

  function render() {
    const catalog = window.GlowCare.getCatalog();
    const list = applyFilters(catalog);

    const grid = document.getElementById("shopGrid");
    const meta = document.getElementById("shopMeta");
    if (!grid) return;

    if (meta) meta.textContent = `${list.length} product${list.length === 1 ? "" : "s"}`;

    grid.innerHTML = "";
    if (!list.length) {
      grid.innerHTML = `<div class="panel empty" style="grid-column: 1 / -1;">
        <div>
          <div class="title" style="font-size:18px; color: var(--text);">No results</div>
          <p style="margin-top:6px;">Try clearing filters or searching with a different keyword.</p>
        </div>
      </div>`;
      return;
    }
    list.forEach((p) => grid.appendChild(renderCard(p)));
  }

  function setChecked(name, values) {
    const set = new Set(values.map(String));
    document.querySelectorAll(`input[name='${name}']`).forEach((el) => {
      el.checked = set.has(String(el.value));
    });
  }

  function setupUI() {
    normalizeFromQuery();

    const q = document.getElementById("shopQ");
    const sort = document.getElementById("shopSort");
    const min = document.getElementById("minPrice");
    const max = document.getElementById("maxPrice");
    const category = document.getElementById("categorySelect");

    if (q) q.value = state.q;
    if (sort) sort.value = state.sort;
    if (min) min.value = state.min;
    if (max) max.value = state.max;
    if (category) category.value = state.category;

    setChecked("brand", state.brand);
    setChecked("skin", state.skin);
    setChecked("concern", state.concern);

    document.addEventListener("change", (e) => {
      const t = e.target;
      if (!(t instanceof HTMLInputElement || t instanceof HTMLSelectElement)) return;

      if (t.id === "shopSort") state.sort = t.value;
      if (t.id === "minPrice") state.min = t.value;
      if (t.id === "maxPrice") state.max = t.value;
      if (t.id === "categorySelect") state.category = t.value;

      if (t instanceof HTMLInputElement && t.name === "brand") {
        const all = Array.from(document.querySelectorAll("input[name='brand']:checked")).map((x) => x.value);
        state.brand = all;
      }
      if (t instanceof HTMLInputElement && t.name === "skin") {
        const all = Array.from(document.querySelectorAll("input[name='skin']:checked")).map((x) => x.value);
        state.skin = all;
      }
      if (t instanceof HTMLInputElement && t.name === "concern") {
        const all = Array.from(document.querySelectorAll("input[name='concern']:checked")).map((x) => x.value);
        state.concern = all;
      }

      writeQuery();
      render();
    });

    if (q) {
      q.addEventListener("input", () => {
        state.q = q.value;
        writeQuery();
        render();
      });
    }

    const clearBtn = document.getElementById("clearFilters");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        window.location.href = "shop.html";
      });
    }
  }

  function renderSkeleton() {
    const grid = document.getElementById("shopGrid");
    if (!grid) return;
    grid.innerHTML = "";
    for (let i = 0; i < 8; i++) {
      const sk = document.createElement("div");
      sk.className = "card";
      sk.innerHTML = `
        <div class="card__media skeleton"></div>
        <div class="card__body">
          <div class="skeleton" style="height:14px; border-radius:10px;"></div>
          <div class="skeleton" style="height:12px; border-radius:10px; width: 70%;"></div>
          <div class="card__row">
            <div class="skeleton" style="height:14px; border-radius:10px; width: 40%;"></div>
            <div class="skeleton" style="height:38px; border-radius:12px; width: 90px;"></div>
          </div>
        </div>
      `;
      grid.appendChild(sk);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!document.getElementById("shopGrid")) return;
    renderSkeleton();
    setupUI();
    window.setTimeout(render, 280);
  });
})();
