/* GlowCare - Global state + helpers (frontend-only) */

(() => {
  const KEYS = {
    catalog: "glowcare_catalog_v1",
    cart: "glowcare_cart_v1",
    wishlist: "glowcare_wishlist_v1",
    users: "glowcare_users_v1",
    session: "glowcare_session_v1",
    checkoutDraft: "glowcare_checkout_draft_v1",
    orders: "glowcare_orders_v1",
    notifications: "glowcare_notifications_v1",
    funnel: "glowcare_funnel_v1",
    adminMode: "glowcare_admin_mode_v1",
  };

  const COUPONS = {
    GLOW10: { code: "GLOW10", type: "percent", value: 10, label: "10% OFF" },
    FREESHIP: { code: "FREESHIP", type: "ship", value: 0, label: "Free shipping" },
  };

  const SHIPPING = {
    freeAbove: 499,
    base: 49,
  };

  const DEMO_USERS = [
    {
      id: "u_demo",
      name: "Demo User",
      email: "demo@glowcare.example",
      password: "demo123",
      role: "user",
      createdAt: "2026-01-01T00:00:00.000Z",
    },
    {
      id: "u_admin",
      name: "Admin",
      email: "admin@glowcare.example",
      password: "admin123",
      role: "admin",
      createdAt: "2026-01-01T00:00:00.000Z",
    },
  ];

  const DEFAULT_PRODUCT_CATALOG = [
    {
      id: "p_101",
      name: "10% Vitamin C Glow Serum",
      brand: "GlowCare",
      category: "skincare",
      price: 499,
      badge: "Bestseller",
      description: "Brightening serum for a smoother, more even-looking glow.",
      image: "assets/images/products/p1.svg",
      gallery: ["assets/images/products/p1.svg", "assets/images/products/p4.svg", "assets/images/products/p7.svg"],
      rating: 4.6,
      reviewsCount: 1862,
      ingredients: ["Vitamin C", "Ferulic Acid", "Hyaluronic Acid"],
      skinTypeTags: ["all", "oily", "combination"],
      concernTags: ["dullness", "pigmentation"],
      variants: [
        { sku: "SKU-101-A", shade: "Original", sizeMl: 15, stock: 20 },
        { sku: "SKU-101-B", shade: "Original", sizeMl: 30, stock: 12 },
      ],
    },
    {
      id: "p_102",
      name: "SPF 50 PA++++ Gel Sunscreen",
      brand: "GlowCare",
      category: "skincare",
      price: 449,
      badge: "Bestseller",
      description: "Lightweight gel sunscreen with no white cast and a fresh finish.",
      image: "assets/images/products/p2.svg",
      gallery: ["assets/images/products/p2.svg", "assets/images/products/p6.svg", "assets/images/products/p9.svg"],
      rating: 4.5,
      reviewsCount: 2410,
      ingredients: ["UVA/UVB Filters", "Vitamin E", "Aloe"],
      skinTypeTags: ["all", "oily", "combination"],
      concernTags: ["tan", "pigmentation", "dullness"],
      variants: [
        { sku: "SKU-102-A", shade: "Clear", sizeMl: 50, stock: 18 },
        { sku: "SKU-102-B", shade: "Clear", sizeMl: 75, stock: 9 },
      ],
    },
    {
      id: "p_103",
      name: "Barrier Repair Moisturizer (Ceramides)",
      brand: "GlowCare",
      category: "skincare",
      price: 549,
      badge: "Trending",
      description: "Comforting moisturizer to support a healthy-looking skin barrier.",
      image: "assets/images/products/p3.svg",
      gallery: ["assets/images/products/p3.svg", "assets/images/products/p5.svg", "assets/images/products/p7.svg"],
      rating: 4.7,
      reviewsCount: 992,
      ingredients: ["Ceramides", "Panthenol", "Niacinamide"],
      skinTypeTags: ["dry", "normal", "all"],
      concernTags: ["dryness", "barrier"],
      variants: [
        { sku: "SKU-103-A", shade: "Original", sizeMl: 50, stock: 14 },
        { sku: "SKU-103-B", shade: "Original", sizeMl: 100, stock: 7 },
      ],
    },
    {
      id: "p_104",
      name: "Niacinamide + Zinc Pore Serum",
      brand: "GlowCare",
      category: "skincare",
      price: 399,
      badge: "Hot",
      description: "Helps reduce the look of pores and shine for a smoother finish.",
      image: "assets/images/products/p4.svg",
      gallery: ["assets/images/products/p4.svg", "assets/images/products/p1.svg", "assets/images/products/p7.svg"],
      rating: 4.4,
      reviewsCount: 1551,
      ingredients: ["Niacinamide", "Zinc PCA", "Allantoin"],
      skinTypeTags: ["oily", "combination"],
      concernTags: ["pores", "oiliness", "acne"],
      variants: [
        { sku: "SKU-104-A", shade: "Original", sizeMl: 30, stock: 16 },
        { sku: "SKU-104-B", shade: "Original", sizeMl: 60, stock: 5 },
      ],
    },
    {
      id: "p_105",
      name: "Gentle Cream Cleanser",
      brand: "GlowCare",
      category: "skincare",
      price: 299,
      badge: "Gentle",
      description: "Creamy daily cleanser that rinses clean without tightness.",
      image: "assets/images/products/p5.svg",
      gallery: ["assets/images/products/p5.svg", "assets/images/products/p3.svg", "assets/images/products/p2.svg"],
      rating: 4.3,
      reviewsCount: 807,
      ingredients: ["Glycerin", "Oat Extract", "Panthenol"],
      skinTypeTags: ["dry", "sensitive", "all"],
      concernTags: ["dryness", "barrier"],
      variants: [
        { sku: "SKU-105-A", shade: "Original", sizeMl: 100, stock: 22 },
        { sku: "SKU-105-B", shade: "Original", sizeMl: 150, stock: 10 },
      ],
    },
    {
      id: "p_201",
      name: "Lip Balm + SPF",
      brand: "GlowCare",
      category: "makeup",
      price: 249,
      badge: "New",
      description: "Soft, comfortable lips with daily SPF protection.",
      image: "assets/images/products/p6.svg",
      gallery: ["assets/images/products/p6.svg", "assets/images/products/p2.svg"],
      rating: 4.2,
      reviewsCount: 412,
      ingredients: ["Shea Butter", "Vitamin E", "UV Filters"],
      skinTypeTags: ["all"],
      concernTags: ["dryness"],
      variants: [
        { sku: "SKU-201-A", shade: "Clear", sizeMl: 4, stock: 28 },
        { sku: "SKU-201-B", shade: "Rosy", sizeMl: 4, stock: 12 },
      ],
    },
    {
      id: "p_106",
      name: "Hyaluronic Hydration Serum",
      brand: "GlowCare",
      category: "skincare",
      price: 449,
      badge: "Hydrate",
      description: "Bouncy hydration with a weightless, non-sticky feel.",
      image: "assets/images/products/p7.svg",
      gallery: ["assets/images/products/p7.svg", "assets/images/products/p1.svg"],
      rating: 4.5,
      reviewsCount: 1203,
      ingredients: ["Hyaluronic Acid", "Betaine", "Glycerin"],
      skinTypeTags: ["all", "dry", "normal"],
      concernTags: ["dryness", "dullness"],
      variants: [
        { sku: "SKU-106-A", shade: "Original", sizeMl: 30, stock: 15 },
        { sku: "SKU-106-B", shade: "Original", sizeMl: 50, stock: 8 },
      ],
    },
    {
      id: "p_301",
      name: "Smooth Shine Shampoo",
      brand: "GlowCare Hair",
      category: "hair",
      price: 399,
      badge: "New",
      description: "Soft cleanse that leaves hair feeling fresh and smooth.",
      image: "assets/images/products/p8.svg",
      gallery: ["assets/images/products/p8.svg", "assets/images/products/p11.svg"],
      rating: 4.3,
      reviewsCount: 356,
      ingredients: ["Amino Acids", "Pro-Vitamin B5", "Biotin"],
      skinTypeTags: ["all"],
      concernTags: ["frizz", "breakage"],
      variants: [
        { sku: "SKU-301-A", shade: "Original", sizeMl: 200, stock: 12 },
        { sku: "SKU-301-B", shade: "Original", sizeMl: 300, stock: 6 },
      ],
    },
    {
      id: "p_302",
      name: "Barrier Body Lotion",
      brand: "GlowCare Body",
      category: "skincare",
      price: 399,
      badge: "New",
      description: "Long-lasting comfort with a non-sticky, premium finish.",
      image: "assets/images/products/p9.svg",
      gallery: ["assets/images/products/p9.svg", "assets/images/products/p3.svg"],
      rating: 4.4,
      reviewsCount: 289,
      ingredients: ["Ceramides", "Squalane", "Oat"],
      skinTypeTags: ["dry", "normal", "all"],
      concernTags: ["dryness", "barrier"],
      variants: [
        { sku: "SKU-302-A", shade: "Original", sizeMl: 200, stock: 10 },
        { sku: "SKU-302-B", shade: "Original", sizeMl: 400, stock: 5 },
      ],
    },
    {
      id: "p_107",
      name: "Glow Mist Toner",
      brand: "GlowCare",
      category: "skincare",
      price: 349,
      badge: "New",
      description: "Instant refresh for a dewy, comfortable feel.",
      image: "assets/images/products/p10.svg",
      gallery: ["assets/images/products/p10.svg", "assets/images/products/p7.svg"],
      rating: 4.2,
      reviewsCount: 221,
      ingredients: ["Niacinamide", "Rose Water", "Glycerin"],
      skinTypeTags: ["all", "normal", "dry"],
      concernTags: ["dullness", "dryness"],
      variants: [
        { sku: "SKU-107-A", shade: "Original", sizeMl: 100, stock: 13 },
        { sku: "SKU-107-B", shade: "Original", sizeMl: 150, stock: 7 },
      ],
    },
    {
      id: "p_303",
      name: "Soothing Scalp Serum",
      brand: "GlowCare Hair",
      category: "hair",
      price: 549,
      badge: "New",
      description: "Light scalp serum for a comfortable, balanced feel.",
      image: "assets/images/products/p11.svg",
      gallery: ["assets/images/products/p11.svg", "assets/images/products/p8.svg"],
      rating: 4.1,
      reviewsCount: 148,
      ingredients: ["Niacinamide", "Piroctone Olamine", "Panthenol"],
      skinTypeTags: ["all"],
      concernTags: ["flakes", "oiliness"],
      variants: [
        { sku: "SKU-303-A", shade: "Original", sizeMl: 50, stock: 9 },
      ],
    },
    {
      id: "p_401",
      name: "Eau de Parfum (Ocean Bloom)",
      brand: "GlowCare Fragrance",
      category: "fragrance",
      price: 899,
      badge: "New",
      description: "Fresh oceanic notes with a clean, premium dry down.",
      image: "assets/images/products/p12.svg",
      gallery: ["assets/images/products/p12.svg"],
      rating: 4.4,
      reviewsCount: 96,
      ingredients: ["Top: Citrus", "Heart: Marine", "Base: Musk"],
      skinTypeTags: ["all"],
      concernTags: ["long-lasting"],
      variants: [
        { sku: "SKU-401-A", shade: "EDP", sizeMl: 30, stock: 6 },
        { sku: "SKU-401-B", shade: "EDP", sizeMl: 50, stock: 4 },
      ],
    },
  ];

  function safeParse(json, fallback) {
    try {
      if (!json) return fallback;
      return JSON.parse(json);
    } catch {
      return fallback;
    }
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function uid(prefix) {
    const rnd = Math.random().toString(16).slice(2);
    return `${prefix}_${Date.now().toString(16)}_${rnd}`;
  }

  function clampInt(value, min, max) {
    const numberValue = Number.parseInt(String(value ?? ""), 10);
    if (Number.isNaN(numberValue)) return min;
    return Math.max(min, Math.min(max, numberValue));
  }

  function money(n) {
    const v = Number(n) || 0;
    return `₹${v.toFixed(0)}`;
  }

  function ensureToast() {
    let toast = document.getElementById("toast");
    if (toast) return toast;
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    toast.hidden = true;
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.setAttribute("aria-atomic", "true");
    document.body.appendChild(toast);
    return toast;
  }

  function toast(message) {
    const t = ensureToast();
    t.textContent = message;
    t.hidden = false;
    window.clearTimeout(toast._t);
    toast._t = window.setTimeout(() => {
      t.hidden = true;
    }, 1800);
  }

  function track(eventName, payload) {
    const funnel = safeParse(localStorage.getItem(KEYS.funnel), { events: [] });
    funnel.events.push({ id: uid("ev"), at: nowIso(), name: eventName, payload: payload ?? {} });
    funnel.events = funnel.events.slice(-200);
    localStorage.setItem(KEYS.funnel, JSON.stringify(funnel));
  }

  /* ---------- Catalog ---------- */
  function getCatalog() {
    const stored = safeParse(localStorage.getItem(KEYS.catalog), null);
    if (Array.isArray(stored) && stored.length) return stored;
    localStorage.setItem(KEYS.catalog, JSON.stringify(DEFAULT_PRODUCT_CATALOG));
    return DEFAULT_PRODUCT_CATALOG;
  }

  function setCatalog(nextCatalog) {
    localStorage.setItem(KEYS.catalog, JSON.stringify(nextCatalog));
  }

  function getProductById(id) {
    return getCatalog().find((p) => p.id === id) || null;
  }

  function getVariant(product, variantKey) {
    if (!product) return null;
    return product.variants.find((v) => v.sku === variantKey) || null;
  }

  function formatVariantSize(variant) {
    if (!variant) return "Standard";
    const rawSize = variant.size ?? variant.sizeMl;
    const size = Number(rawSize);
    if (!Number.isFinite(size) || size <= 0) return "Standard";
    const unit = String(variant.unit || "ml").trim() || "ml";
    return `${size}${unit}`;
  }

  /* ---------- Wishlist ---------- */
  function getWishlist() {
    return safeParse(localStorage.getItem(KEYS.wishlist), []);
  }
  function setWishlist(next) {
    localStorage.setItem(KEYS.wishlist, JSON.stringify(next));
    updateCounts();
  }
  function isWishlisted(productId) {
    return getWishlist().includes(productId);
  }
  function toggleWishlist(productId) {
    const list = getWishlist();
    const idx = list.indexOf(productId);
    if (idx >= 0) list.splice(idx, 1);
    else list.unshift(productId);
    setWishlist(Array.from(new Set(list)).slice(0, 200));
    track("wishlist_toggle", { productId, state: idx >= 0 ? "removed" : "added" });
    toast(idx >= 0 ? "Removed from wishlist" : "Added to wishlist");
  }

  /* ---------- Cart ---------- */
  function getCart() {
    const cart = safeParse(localStorage.getItem(KEYS.cart), null);
    if (cart && Array.isArray(cart.items)) return cart;
    const fresh = { items: [], coupon: null, updatedAt: nowIso() };
    localStorage.setItem(KEYS.cart, JSON.stringify(fresh));
    return fresh;
  }

  function setCart(nextCart) {
    const safe = nextCart && Array.isArray(nextCart.items) ? nextCart : { items: [] };
    safe.updatedAt = nowIso();
    localStorage.setItem(KEYS.cart, JSON.stringify(safe));
    updateCounts();
  }

  function getCartQtyForVariant(productId, variantKey) {
    return getCart().items
      .filter((i) => i.productId === productId && i.variantKey === variantKey)
      .reduce((sum, i) => sum + (Number(i.qty) || 0), 0);
  }

  function addToCart(productId, variantKey, qty) {
    const product = getProductById(productId);
    if (!product) {
      toast("Product not found");
      return { ok: false, reason: "product_not_found" };
    }
    const variant = getVariant(product, variantKey);
    if (!variant) {
      toast("Select a variant");
      return { ok: false, reason: "variant_missing" };
    }

    const want = clampInt(qty, 1, 10);
    const current = getCartQtyForVariant(productId, variantKey);
    const remaining = Math.max(0, (variant.stock ?? 0) - current);
    if (remaining <= 0) {
      toast("Out of stock");
      return { ok: false, reason: "out_of_stock" };
    }

    const canAdd = Math.min(want, remaining);
    const cart = getCart();
    const idx = cart.items.findIndex((i) => i.productId === productId && i.variantKey === variantKey);
    if (idx >= 0) cart.items[idx].qty = clampInt((cart.items[idx].qty || 0) + canAdd, 1, 999);
    else cart.items.unshift({ id: uid("ci"), productId, variantKey, qty: canAdd, addedAt: nowIso() });
    setCart(cart);
    track("cart_add", { productId, variantKey, qty: canAdd });
    toast(canAdd < want ? `Added ${canAdd}. Limited stock.` : "Added to cart");
    return { ok: true, qtyAdded: canAdd };
  }

  function updateCartQty(itemId, nextQty) {
    const cart = getCart();
    const idx = cart.items.findIndex((i) => i.id === itemId);
    if (idx < 0) return;
    const item = cart.items[idx];
    const product = getProductById(item.productId);
    const variant = getVariant(product, item.variantKey);
    const maxStock = variant?.stock ?? 0;
    const safeQty = clampInt(nextQty, 1, Math.max(1, maxStock));
    cart.items[idx].qty = safeQty;
    setCart(cart);
    track("cart_qty", { itemId, qty: safeQty });
  }

  function removeCartItem(itemId) {
    const cart = getCart();
    cart.items = cart.items.filter((i) => i.id !== itemId);
    setCart(cart);
    track("cart_remove", { itemId });
  }

  function clearCart() {
    setCart({ items: [], coupon: null });
    track("cart_clear");
  }

  function applyCoupon(codeRaw) {
    const code = String(codeRaw || "").trim().toUpperCase();
    const coupon = COUPONS[code] || null;
    const cart = getCart();
    cart.coupon = coupon ? coupon.code : null;
    setCart(cart);
    toast(coupon ? `Applied: ${coupon.label}` : "Invalid coupon");
    track("coupon_apply", { code, ok: !!coupon });
    return coupon;
  }

  function computeCartTotals() {
    const cart = getCart();
    const items = cart.items
      .map((i) => {
        const product = getProductById(i.productId);
        const variant = getVariant(product, i.variantKey);
        if (!product || !variant) return null;
        return {
          ...i,
          product,
          variant,
          line: (Number(product.price) || 0) * (Number(i.qty) || 0),
        };
      })
      .filter(Boolean);

    const subtotal = items.reduce((s, it) => s + (Number(it.line) || 0), 0);
    const coupon = cart.coupon ? COUPONS[cart.coupon] : null;
    const discount = coupon?.type === "percent" ? Math.round((subtotal * coupon.value) / 100) : 0;
    const shipping = coupon?.type === "ship" ? 0 : subtotal >= SHIPPING.freeAbove ? 0 : SHIPPING.base;
    const total = Math.max(0, subtotal - discount + shipping);

    return { items, subtotal, discount, shipping, total, coupon };
  }

  /* ---------- Checkout draft + orders ---------- */
  function getCheckoutDraft() {
    return safeParse(localStorage.getItem(KEYS.checkoutDraft), { shipping: null, updatedAt: null });
  }
  function setCheckoutDraft(next) {
    localStorage.setItem(KEYS.checkoutDraft, JSON.stringify({ ...(next || {}), updatedAt: nowIso() }));
  }

  function getOrders() {
    return safeParse(localStorage.getItem(KEYS.orders), []);
  }
  function setOrders(next) {
    localStorage.setItem(KEYS.orders, JSON.stringify(next));
  }
  function saveOrder(order) {
    const orders = getOrders();
    orders.unshift(order);
    setOrders(orders.slice(0, 200));
  }

  /* ---------- Auth ---------- */
  function getUsers() {
    const stored = safeParse(localStorage.getItem(KEYS.users), null);
    if (Array.isArray(stored) && stored.length) return stored;
    localStorage.setItem(KEYS.users, JSON.stringify(DEMO_USERS));
    return DEMO_USERS;
  }
  function setUsers(next) {
    localStorage.setItem(KEYS.users, JSON.stringify(next));
  }

  function getSession() {
    return safeParse(localStorage.getItem(KEYS.session), { userId: null });
  }
  function setSession(next) {
    localStorage.setItem(KEYS.session, JSON.stringify(next || { userId: null }));
  }
  function getCurrentUser() {
    const session = getSession();
    if (!session?.userId) return null;
    return getUsers().find((u) => u.id === session.userId) || null;
  }

  function signup({ name, email, password }) {
    const e = String(email || "").trim().toLowerCase();
    const p = String(password || "");
    const n = String(name || "").trim();
    if (!n || n.length < 2) return { ok: false, message: "Enter your name" };
    if (!e.includes("@")) return { ok: false, message: "Enter a valid email" };
    if (p.length < 5) return { ok: false, message: "Password must be 5+ characters" };

    const users = getUsers();
    if (users.some((u) => String(u.email).toLowerCase() === e)) return { ok: false, message: "Email already exists" };

    const user = { id: uid("u"), name: n, email: e, password: p, role: "user", createdAt: nowIso() };
    users.unshift(user);
    setUsers(users);
    setSession({ userId: user.id });
    track("auth_signup", { userId: user.id });
    return { ok: true, user };
  }

  function login({ email, password }) {
    const e = String(email || "").trim().toLowerCase();
    const p = String(password || "");
    const user = getUsers().find((u) => String(u.email).toLowerCase() === e && String(u.password) === p);
    if (!user) return { ok: false, message: "Invalid email or password" };
    setSession({ userId: user.id });
    track("auth_login", { userId: user.id });
    return { ok: true, user };
  }

  function logout() {
    setSession({ userId: null });
    localStorage.removeItem(KEYS.adminMode);
    track("auth_logout");
  }

  function resetPassword({ email, newPassword }) {
    const e = String(email || "").trim().toLowerCase();
    const p = String(newPassword || "");
    if (!e.includes("@")) return { ok: false, message: "Enter a valid email" };
    if (p.length < 5) return { ok: false, message: "Password must be 5+ characters" };
    const users = getUsers();
    const idx = users.findIndex((u) => String(u.email).toLowerCase() === e);
    if (idx < 0) return { ok: false, message: "Account not found" };
    users[idx].password = p;
    setUsers(users);
    track("auth_reset", { userId: users[idx].id });
    return { ok: true };
  }

  /* ---------- Components injection ---------- */
  function loadInlineComponentsIfNeeded() {
    if (window.location.protocol !== "file:") return Promise.resolve();
    if (window.GlowCareInlineComponents) return Promise.resolve();

    return new Promise((resolve) => {
      const script = document.createElement("script");
      script.src = "js/inline-components.js";
      script.onload = () => resolve();
      script.onerror = () => resolve();
      document.head.appendChild(script);
    });
  }

  function getInlineComponent(path) {
    const map = window.GlowCareInlineComponents;
    if (!map) return null;
    if (path.endsWith("components/navbar.html") || path.endsWith("components/navbar.xml")) return map.navbar || null;
    if (path.endsWith("components/footer.html") || path.endsWith("components/footer.xml")) return map.footer || null;
    return null;
  }

  async function injectComponent(targetId, path) {
    const target = document.getElementById(targetId);
    if (!target) return;
    try {
      const inline = getInlineComponent(path);
      if (inline) {
        target.innerHTML = inline;
        return;
      }
      const res = await fetch(path, { cache: "no-store" });
      let html = await res.text();
      // Live Server injects reload scripts into fetched HTML/SVG fragments which can break inline SVG markup.
      // Strip *all* script tags + the known comment marker from component HTML before injecting.
      html = html.replace(/<!-- Code injected by live-server -->/g, "");
      html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>\s*/gi, "");
      target.innerHTML = html;
    } catch {
      // ignore
    }
  }

  function updateCounts() {
    const cartCountEl = document.getElementById("cartCount");
    if (cartCountEl) cartCountEl.textContent = String(getCart().items.reduce((s, i) => s + (Number(i.qty) || 0), 0));
    const wishCountEl = document.getElementById("wishlistCount");
    if (wishCountEl) wishCountEl.textContent = String(getWishlist().length);
  }

  function setupMobileNav() {
    const menu = document.getElementById("mobileMenu");
    const menuBtn = document.querySelector("[data-nav='menu']");
    if (!menu || !menuBtn) return;

    function openMenu() {
      menu.hidden = false;
      menuBtn.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    }
    function closeMenu() {
      menu.hidden = true;
      menuBtn.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }

    menuBtn.addEventListener("click", () => (menu.hidden ? openMenu() : closeMenu()));
    menu.addEventListener("click", (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;
      if (target.matches("[data-nav='close']") || target.closest("[data-nav='close']")) closeMenu();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !menu.hidden) closeMenu();
    });
  }

  function setupNavbarSearch() {
    const input = document.getElementById("navSearch");
    const suggest = document.getElementById("navSuggest");
    if (!input || !suggest) return;

    const catalog = getCatalog();
    function close() {
      suggest.hidden = true;
      suggest.innerHTML = "";
    }

    function render(q) {
      const query = String(q || "").trim().toLowerCase();
      if (!query) return close();
      const hits = catalog
        .filter((p) => `${p.name} ${p.brand} ${p.category}`.toLowerCase().includes(query))
        .slice(0, 6);
      suggest.innerHTML = "";
      for (const p of hits) {
        const item = document.createElement("div");
        item.className = "suggest-item";
        item.setAttribute("role", "option");
        item.tabIndex = 0;
        item.innerHTML = `<div><div class="suggest-item__name"></div><div class="suggest-item__meta"></div></div><div class="suggest-item__meta"></div>`;
        item.querySelector(".suggest-item__name").textContent = p.name;
        item.querySelectorAll(".suggest-item__meta")[0].textContent = p.brand;
        item.querySelectorAll(".suggest-item__meta")[1].textContent = money(p.price);
        item.addEventListener("click", () => (window.location.href = `product.html?id=${encodeURIComponent(p.id)}`));
        item.addEventListener("keydown", (e) => {
          if (e.key === "Enter") window.location.href = `product.html?id=${encodeURIComponent(p.id)}`;
        });
        suggest.appendChild(item);
      }
      suggest.hidden = hits.length === 0;
    }

    input.addEventListener("input", () => render(input.value));
    input.addEventListener("focus", () => render(input.value));
    document.addEventListener("click", (e) => {
      const t = e.target;
      if (!(t instanceof Element)) return;
      if (t.closest(".nav-search")) return;
      close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }

  function updateNavbarAuthUI() {
    const user = getCurrentUser();
    const accountLink = document.getElementById("navAccountLink");
    const mobileAccountLink = document.getElementById("mobileAccountLink");
    const loginBtn = document.getElementById("navLoginBtn");

    const current = window.location.pathname.split("/").pop() || "index.html";
    const loginHref = `login.html?next=${encodeURIComponent(current)}`;

    if (accountLink) {
      accountLink.href = user ? "account.html" : loginHref;
      accountLink.setAttribute("aria-label", user ? "Account" : "Login");
    }
    if (mobileAccountLink) {
      mobileAccountLink.href = user ? "account.html" : loginHref;
      mobileAccountLink.textContent = user ? "Account" : "Login";
    }
    if (loginBtn) {
      loginBtn.href = loginHref;
      loginBtn.hidden = Boolean(user);
    }
  }

  function requireAuth(nextUrl) {
    const user = getCurrentUser();
    if (user) return true;
    const next = nextUrl || window.location.pathname.split("/").pop() || "index.html";
    window.location.href = `login.html?next=${encodeURIComponent(next)}`;
    return false;
  }

  function requireAdmin() {
    const user = getCurrentUser();
    const adminMode = localStorage.getItem(KEYS.adminMode) === "1";
    if (user?.role === "admin" && adminMode) return true;
    window.location.href = "account.html";
    return false;
  }

  function setupAdminHotkeys() {
    document.addEventListener("keydown", (e) => {
      const key = String(e.key || "").toLowerCase();
      const isA = key === "a";
      const isU = key === "u";
      const isEsc = e.key === "Escape";
      const withCtrlShift = e.ctrlKey && e.shiftKey;

      if (withCtrlShift && isA) {
        const user = getCurrentUser();
        if (user?.role !== "admin") {
          toast("Admin requires admin login");
          return;
        }
        localStorage.setItem(KEYS.adminMode, "1");
        toast("Admin mode enabled");
        if (!window.location.pathname.endsWith("admin.html")) window.location.href = "admin.html";
      }

      if ((withCtrlShift && isU) || isEsc) {
        if (localStorage.getItem(KEYS.adminMode) === "1") {
          localStorage.removeItem(KEYS.adminMode);
          toast("User mode enabled");
          if (window.location.pathname.endsWith("admin.html")) window.location.href = "account.html";
        }
      }
    });
  }

  function parseQuery() {
    const params = new URLSearchParams(window.location.search);
    const out = {};
    for (const [k, v] of params.entries()) out[k] = v;
    return out;
  }

  function setQuery(next) {
    const params = new URLSearchParams();
    Object.entries(next || {}).forEach(([k, v]) => {
      if (v === null || v === undefined || v === "") return;
      if (Array.isArray(v)) v.forEach((x) => params.append(k, String(x)));
      else params.set(k, String(v));
    });
    const qs = params.toString();
    const url = `${window.location.pathname}${qs ? `?${qs}` : ""}`;
    window.history.replaceState({}, "", url);
  }

  /* ---------- Boot ---------- */
  async function boot() {
    await loadInlineComponentsIfNeeded();
    // Use `.xml` to avoid VS Code Live Server injecting reload scripts into fetched `.html` fragments with inline SVG.
    await injectComponent("appNavbar", "components/navbar.xml");
    await injectComponent("appFooter", "components/footer.xml");
    ensureToast();
    updateCounts();
    updateNavbarAuthUI();
    setupMobileNav();
    setupNavbarSearch();
    setupAdminHotkeys();

    const body = document.body;
    const requireAuthFlag = body?.dataset?.requireAuth === "true";
    const requireAdminFlag = body?.dataset?.requireAdmin === "true";

    if (requireAuthFlag) requireAuth();
    if (requireAdminFlag) requireAdmin();
  }

  document.addEventListener("DOMContentLoaded", () => {
    boot();
  });

  window.GlowCare = {
    KEYS,
    COUPONS,
    SHIPPING,
    DEFAULT_PRODUCT_CATALOG,
    money,
    uid,
    clampInt,
    toast,
    track,
    parseQuery,
    setQuery,
    getCatalog,
    setCatalog,
    getProductById,
    getVariant,
    formatVariantSize,
    getCart,
    setCart,
    addToCart,
    updateCartQty,
    removeCartItem,
    clearCart,
    applyCoupon,
    computeCartTotals,
    getWishlist,
    setWishlist,
    isWishlisted,
    toggleWishlist,
    getCheckoutDraft,
    setCheckoutDraft,
    getOrders,
    saveOrder,
    getUsers,
    getSession,
    getCurrentUser,
    signup,
    login,
    logout,
    resetPassword,
    requireAuth,
    requireAdmin,
  };
})();
