/* GlowCare Premium Homepage (data-driven, admin-ready)
   - All major sections render from a JSON config (localStorage)
   - Catalog/cart uses existing window.GlowCare from js/main.js
*/

(() => {
  const CMS_KEY = "glowcare_home_cms_v1";
  const CMS_API = "/api/v1/homepage/";
  const STATIC_BASE =
    (typeof window !== "undefined" && window.GLOWCARE_STATIC_BASE) ||
    (document.querySelector('meta[name="gc-static-base"]')?.getAttribute("content") || "");

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

  function safeParse(text, fallback) {
    try {
      const v = JSON.parse(text);
      return v ?? fallback;
    } catch {
      return fallback;
    }
  }

  function setCssVars(vars) {
    if (!vars || typeof vars !== "object") return;
    const root = document.documentElement;
    Object.entries(vars).forEach(([k, v]) => {
      if (!k || typeof v !== "string") return;
      root.style.setProperty(k, v);
    });
  }

  function svgIcon(name) {
    if (name === "arrow") {
      return `<svg class="gc-btn__icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    }
    if (name === "eye") {
      return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" fill="none" stroke="currentColor" stroke-width="2"/></svg>`;
    }
    if (name === "heart") {
      return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-4.6-9.5-8.7C.6 9.2 2.2 6 5.6 6c1.9 0 3.3 1 4.4 2.3C11.1 7 12.5 6 14.4 6c3.4 0 5 3.2 3.1 6.3C19 16.4 12 21 12 21Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>`;
    }
    if (name === "play") {
      return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 7v10l10-5-10-5Z"/></svg>`;
    }
    return "";
  }

  const DEFAULT_CMS = {
    version: 1,
    theme: {
      "--brand": "#ff2e7a",
      "--gc-accent": "#ff2e7a",
      "--gc-accent-2": "#8a5bff",
    },
    announcement: {
      enabled: false,
      badge: "",
      text: "",
      ctaText: "",
      ctaHref: "",
    },
    navigation: {
      // Admin-ready: override navbar links without editing components/navbar.html
      links: [],
    },
    footer: {
      aboutText: "",
      chips: [],
      columns: [],
      bottomLeft: "",
      bottomRight: "",
    },
    sections: [
      { id: "hero", enabled: true },
      { id: "bestsellers", enabled: true },
      { id: "promoStrip", enabled: true },
      { id: "newArrivals", enabled: true },
      { id: "appBanner", enabled: true },
      { id: "skinConcerns", enabled: true },
      { id: "reels", enabled: true },
      { id: "features", enabled: true },
      { id: "story", enabled: true },
      { id: "logos", enabled: true },
      { id: "testimonials", enabled: true },
    ],
    hero: {
      autoplayMs: 5200,
      slides: [],
    },
    productSections: {
      bestsellers: {
        title: "",
        subtitle: "",
        viewAllHref: "",
        tabs: [],
      },
      newArrivals: {
        title: "",
        subtitle: "",
        viewAllHref: "",
        tabs: [],
      },
    },
    promoStrip: {
      title: "",
      subtitle: "",
      pills: [],
      button: { label: "", href: "" },
    },
    appBanner: {
      title: "",
      subtitle: "",
      stores: [],
    },
    skinConcerns: {
      title: "",
      subtitle: "",
      tabs: [],
    },
    reels: {
      title: "",
      subtitle: "",
      items: [],
    },
    features: {
      title: "",
      subtitle: "",
      cards: [],
    },
    story: {
      title: "",
      subtitle: "",
      button: { label: "", href: "" },
      image: "",
    },
    logos: {
      title: "",
      subtitle: "",
      items: [],
    },
    testimonials: {
      title: "",
      subtitle: "",
      items: [],
    },
  };

  function getCMS() {
    const stored = safeParse(localStorage.getItem(CMS_KEY), null);
    if (!stored || typeof stored !== "object") return structuredClone(DEFAULT_CMS);
    const merged = structuredClone(DEFAULT_CMS);
    // shallow merge at top level + known branches; safe and admin-friendly
    Object.assign(merged, stored);
    merged.theme = { ...DEFAULT_CMS.theme, ...(stored.theme || {}) };
    merged.announcement = { ...DEFAULT_CMS.announcement, ...(stored.announcement || {}) };
    merged.navigation = { ...DEFAULT_CMS.navigation, ...(stored.navigation || {}) };
    merged.hero = { ...DEFAULT_CMS.hero, ...(stored.hero || {}) };
    merged.productSections = { ...DEFAULT_CMS.productSections, ...(stored.productSections || {}) };
    merged.promoStrip = { ...DEFAULT_CMS.promoStrip, ...(stored.promoStrip || {}) };
    merged.appBanner = { ...DEFAULT_CMS.appBanner, ...(stored.appBanner || {}) };
    merged.skinConcerns = { ...DEFAULT_CMS.skinConcerns, ...(stored.skinConcerns || {}) };
    merged.reels = { ...DEFAULT_CMS.reels, ...(stored.reels || {}) };
    merged.features = { ...DEFAULT_CMS.features, ...(stored.features || {}) };
    merged.story = { ...DEFAULT_CMS.story, ...(stored.story || {}) };
    merged.logos = { ...DEFAULT_CMS.logos, ...(stored.logos || {}) };
    merged.testimonials = { ...DEFAULT_CMS.testimonials, ...(stored.testimonials || {}) };
    merged.footer = { ...DEFAULT_CMS.footer, ...(stored.footer || {}) };
    return merged;
  }

  async function loadCMSFromAPI() {
    try {
      const res = await fetch(CMS_API, { credentials: "same-origin" });
      if (!res.ok) throw new Error("bad_status");
      const data = await res.json();
      if (!data || typeof data !== "object") throw new Error("bad_json");
      // Cache for offline preview
      localStorage.setItem(CMS_KEY, JSON.stringify(data));
      // Merge API payload over defaults to ensure missing keys don't break UI
      const merged = getCMS();
      Object.assign(merged, data);
      merged.theme = { ...DEFAULT_CMS.theme, ...(data.theme || {}) };
      merged.announcement = { ...DEFAULT_CMS.announcement, ...(data.announcement || {}) };
      merged.navigation = { ...DEFAULT_CMS.navigation, ...(data.navigation || {}) };
      merged.footer = { ...DEFAULT_CMS.footer, ...(data.footer || {}) };
      merged.sections = Array.isArray(data.sections) ? data.sections : merged.sections;
      merged.hero = { ...DEFAULT_CMS.hero, ...(data.hero || {}) };
      merged.productSections = { ...DEFAULT_CMS.productSections, ...(data.productSections || {}) };
      if (data.promoStrip) merged.promoStrip = { ...DEFAULT_CMS.promoStrip, ...(data.promoStrip || {}) };
      else {
        // auto-hide promo section if backend says none visible
        merged.sections = (merged.sections || []).map((s) => (s.id === "promoStrip" ? { ...s, enabled: false } : s));
      }
      if (data.appBanner) merged.appBanner = { ...DEFAULT_CMS.appBanner, ...(data.appBanner || {}) };
      if (data.logos) merged.logos = { ...DEFAULT_CMS.logos, ...(data.logos || {}) };
      if (data.testimonials) merged.testimonials = { ...DEFAULT_CMS.testimonials, ...(data.testimonials || {}) };
      return merged;
    } catch {
      return null;
    }
  }

  function persistDefaultOnce() {
    const existing = localStorage.getItem(CMS_KEY);
    if (existing) return;
    localStorage.setItem(CMS_KEY, JSON.stringify(DEFAULT_CMS));
  }

  function renderAnnouncement(cfg) {
    const host = $("#gcAnnouncement");
    if (!host) return;
    if (!cfg.announcement?.enabled) {
      host.innerHTML = "";
      document.documentElement.style.setProperty("--gc-ann-height", "0px");
      return;
    }
    host.innerHTML = `
      <div class="gc-ann" ${cfg.announcement.bg ? `style="background:${escapeAttr(cfg.announcement.bg)}"` : ""}>
        <div class="gc-container">
          <div class="gc-ann__row">
            <span class="gc-ann__pill">
              <span class="gc-ann__badge">${escapeHtml(cfg.announcement.badge || "Offer")}</span>
              <span>${escapeHtml(cfg.announcement.text || "")}</span>
              <a class="gc-ann__cta" href="${escapeAttr(cfg.announcement.ctaHref || "shop.html")}">${escapeHtml(cfg.announcement.ctaText || "Shop")}</a>
            </span>
          </div>
        </div>
      </div>
    `;
    // Keep navbar sticky below announcement
    requestAnimationFrame(() => {
      const ann = $(".gc-ann");
      const h = ann ? ann.getBoundingClientRect().height : 0;
      document.documentElement.style.setProperty("--gc-ann-height", `${Math.round(h)}px`);
    });
  }

  function updateNavFromCMS(cfg) {
    // Navbar is injected by js/main.js; wait for it.
    const attempt = () => {
      const row = $(".navbar__linksRow");
      if (!row) return false;
      const links = cfg.navigation?.links || [];
      if (!Array.isArray(links) || links.length === 0) return true;

      row.innerHTML = links
        .map((l) => {
          const cls = `navlink${l.pill ? " navlink--pill" : ""}`;
          return `<a class="${cls}" href="${escapeAttr(l.href || "#")}">${escapeHtml(l.label || "Link")}</a>`;
        })
        .join("");
      return true;
    };

    let tries = 0;
    const t = setInterval(() => {
      tries += 1;
      if (attempt() || tries > 30) clearInterval(t);
    }, 60);
  }

  function updateFooterFromCMS(cfg) {
    const attempt = () => {
      const footer = $(".site-footer");
      if (!footer) return false;
      const f = cfg.footer;
      if (!f) return true;

      const about = $(".footer__muted", footer);
      if (about && typeof f.aboutText === "string") about.textContent = f.aboutText;

      const chips = $(".footer__chips", footer);
      if (chips && Array.isArray(f.chips)) chips.innerHTML = f.chips.map((c) => `<span class="footchip">${escapeHtml(c)}</span>`).join("");

      const grid = $(".footer__grid", footer);
      const cols = Array.isArray(f.columns) ? f.columns : [];
      if (grid && cols.length) {
        // Keep first column (brand/about) intact, rebuild remaining up to 3
        const first = grid.children?.[0];
        const rebuilt = document.createElement("div");
        rebuilt.className = "container footer__grid";
        if (first) rebuilt.appendChild(first.cloneNode(true));

        cols.slice(0, 3).forEach((col) => {
          const colEl = document.createElement("div");
          colEl.innerHTML = `
            <h3 class="footer__title">${escapeHtml(col.title || "")}</h3>
            ${(col.links || []).map((l) => `<a class="footer__link" href="${escapeAttr(l.href || "#")}">${escapeHtml(l.label || "")}</a>`).join("")}
            ${col.muted ? `<p class="footer__muted">${escapeHtml(col.muted)}</p>` : ""}
            ${
              Array.isArray(col.social) && col.social.length
                ? `<div class="footer__social">${col.social
                    .map((s) => `<a class="social" href="${escapeAttr(s.href || "#")}" aria-label="${escapeAttr(s.aria || s.label || "Social")}">${escapeHtml(s.label || "")}</a>`)
                    .join("")}</div>`
                : ""
            }
          `;
          rebuilt.appendChild(colEl);
        });

        grid.replaceWith(rebuilt);
      }

      const bottom = $(".footer__bottom", footer);
      if (bottom) {
        const ps = $$("p", bottom);
        if (ps[0] && typeof f.bottomLeft === "string") ps[0].textContent = f.bottomLeft;
        if (ps[1] && typeof f.bottomRight === "string") ps[1].textContent = f.bottomRight;
      }
      return true;
    };

    let tries = 0;
    const t = setInterval(() => {
      tries += 1;
      if (attempt() || tries > 30) clearInterval(t);
    }, 80);
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replaceAll("\n", " ");
  }

  function withStaticBase(url) {
    const u = String(url || "");
    if (!u) return "";
    if (u.startsWith("http") || u.startsWith("/") || u.startsWith("data:")) return u;
    if (!STATIC_BASE) return u;
    if (u.startsWith("assets/") || u.startsWith("css/") || u.startsWith("js/") || u.startsWith("components/") || u === "style.css" || u === "script.js") {
      return `${STATIC_BASE}${u}`;
    }
    return u;
  }

  function renderHome(cfg) {
    const host = $("#gcHome");
    if (!host) return;
    host.innerHTML = "";
    const enabled = new Map((cfg.sections || []).map((s) => [s.id, s.enabled !== false]));

    const order = (cfg.sections || []).map((s) => s.id);
    const renderers = {
      hero: () => renderHero(cfg),
      bestsellers: () => renderProductSection(cfg, "bestsellers"),
      promoStrip: () => renderPromoStrip(cfg),
      newArrivals: () => renderProductSection(cfg, "newArrivals"),
      appBanner: () => renderAppBanner(cfg),
      skinConcerns: () => renderSkinConcerns(cfg),
      reels: () => renderReels(cfg),
      features: () => renderFeatures(cfg),
      story: () => renderStory(cfg),
      logos: () => renderLogos(cfg),
      testimonials: () => renderTestimonials(cfg),
    };

    order.forEach((id) => {
      if (!enabled.get(id)) return;
      const fn = renderers[id];
      if (!fn) return;
      host.appendChild(fn());
    });

    attachRevealObserver();
  }

  function getSection(cfg, id) {
    const list = Array.isArray(cfg.sections) ? cfg.sections : [];
    return list.find((s) => s.id === id) || null;
  }

  function sectionTitle(cfg, id, fallback) {
    const s = getSection(cfg, id);
    return (s?.title || "").trim() || fallback || "";
  }

  function sectionSubtitle(cfg, id, fallback) {
    const s = getSection(cfg, id);
    const sub = s?.settings?.subtitle;
    return (String(sub || "").trim() || fallback || "").trim();
  }

  function sectionBg(cfg, id) {
    const s = getSection(cfg, id);
    const bg = s?.settings?.bg;
    return typeof bg === "string" && bg.trim() ? bg.trim() : "";
  }

  function sectionWrap(inner, { muted = false, tight = false } = {}) {
    const sec = document.createElement("section");
    sec.className = `gc-section${muted ? " gc-section--muted" : ""}${tight ? " gc-section--tight" : ""}`;
    sec.appendChild(inner);
    return sec;
  }

  function applySectionBg(secEl, cfg, id) {
    if (!secEl) return;
    const bg = sectionBg(cfg, id);
    if (bg) secEl.style.background = bg;
  }

  function headBlockHtml(title, subtitle, actionHtml = "") {
    return `
      <div class="gc-head" data-gc-reveal>
        <div>
          <div class="gc-title">${escapeHtml(title || "")}</div>
          ${subtitle ? `<div class="gc-sub">${escapeHtml(subtitle)}</div>` : ""}
        </div>
        ${actionHtml ? `<div class="gc-actions">${actionHtml}</div>` : `<div></div>`}
      </div>
    `;
  }

  function renderHero(cfg) {
    const secInner = document.createElement("div");
    secInner.className = "gc-container";
    const slides = cfg.hero?.slides || [];
    secInner.innerHTML = `
      <section class="gc-hero" aria-label="Hero">
        <div class="gc-hero__frame" data-gc-reveal>
          <div class="swiper gc-heroSwiper">
            <div class="swiper-wrapper">
              ${slides
                .map((s) => {
                  const overlayBg = typeof s.overlayBg === "string" ? s.overlayBg.trim() : "";
                  const bgKind = s.background?.kind || s.backgroundKind || "";
                  const bgUrlRaw = s.background?.url || s.backgroundUrl || "";
                  const bgUrl = withStaticBase(bgUrlRaw);
                  const btnStyles = s.buttonStyles && typeof s.buttonStyles === "object" ? s.buttonStyles : {};
                  const pv = String(btnStyles.primaryVariant || "primary");
                  const sv = String(btnStyles.secondaryVariant || "ghost");
                  const primaryCls = pv === "ghost" ? "gc-btn--ghost" : "gc-btn--primary";
                  const secondaryCls = sv === "primary" ? "gc-btn--primary" : "gc-btn--ghost";

                  const ribbons = Array.isArray(s.ribbons) ? s.ribbons : [];
                  const ribHTML = ribbons
                    .map((r) => `<span class="gc-rib"><span>${escapeHtml(r.label || "")}</span> <b>${escapeHtml(r.value || "")}</b></span>`)
                    .join("");
                  const ribTrack = `<div class="gc-marquee"><div class="gc-marquee__track">${ribHTML}${ribHTML}</div></div>`;
                  const meta = Array.isArray(s.meta) ? s.meta : [];
                  const metaHTML = meta
                    .map(
                      (m) => `
                        <div class="gc-badge">
                          <span class="gc-badge__ic" aria-hidden="true"></span>
                          <div>
                            <b>${escapeHtml(m.title || "")}</b>
                            <span>${escapeHtml(m.desc || "")}</span>
                          </div>
                        </div>
                      `,
                    )
                    .join("");
                  const cards = Array.isArray(s.cards) ? s.cards : [];
                  const [a, b, c] = [cards[0], cards[1], cards[2]];
                  const bgMedia =
                    bgUrl && String(bgKind).toLowerCase() === "video"
                      ? `<video class="gc-hero__media" autoplay muted loop playsinline preload="metadata" src="${escapeAttr(bgUrl)}"></video>`
                      : bgUrl
                        ? `<div class="gc-hero__media" style="background-image:url('${escapeAttr(bgUrl)}')"></div>`
                        : "";
                  return `
                    <div class="swiper-slide">
                      ${bgMedia}
                      <div class="gc-hero__bg" ${overlayBg ? `style="background:${escapeAttr(overlayBg)}"` : ""}></div>
                      <div class="gc-hero__grid" aria-hidden="true"></div>
                      <div class="gc-hero__inner">
                        <div>
                          <div class="gc-hero__kicker" data-swiper-parallax="-140">
                            <span class="gc-hero__kdot" aria-hidden="true"></span>
                            <span>${escapeHtml(s.kicker || "")}</span>
                          </div>
                          <div class="gc-hero__h1" data-swiper-parallax="-220">
                            ${escapeHtml(s.headline || "")}
                            <span class="gc-hero__accent">${escapeHtml(s.headline2 || "")}</span>
                          </div>
                          <div class="gc-hero__p" data-swiper-parallax="-160">${escapeHtml(s.sub || "")}</div>
                          <div class="gc-hero__cta" data-swiper-parallax="-120">
                            <a class="gc-btn ${primaryCls}" data-magnetic href="${escapeAttr(s.primary?.href || "shop.html")}">
                              ${escapeHtml(s.primary?.label || "Shop now")}
                              ${svgIcon("arrow")}
                            </a>
                            <a class="gc-btn ${secondaryCls}" data-magnetic href="${escapeAttr(s.secondary?.href || "shop.html")}">
                              ${escapeHtml(s.secondary?.label || "Explore")}
                            </a>
                          </div>
                          <div class="gc-hero__meta" data-swiper-parallax="-100">${metaHTML}</div>
                        </div>

                        <div class="gc-hero__visual" aria-hidden="true" data-swiper-parallax="90">
                          <div class="gc-hero__stack">
                            <div class="gc-hero__ring"></div>
                            <div class="gc-hero__card" data-pos="a"><img loading="lazy" src="${escapeAttr(withStaticBase(a || "assets/images/products/p1.svg"))}" alt=""></div>
                            <div class="gc-hero__card" data-pos="b"><img loading="lazy" src="${escapeAttr(withStaticBase(b || "assets/images/products/p2.svg"))}" alt=""></div>
                            <div class="gc-hero__card" data-pos="c"><img loading="lazy" src="${escapeAttr(withStaticBase(c || "assets/images/products/p3.svg"))}" alt=""></div>
                          </div>
                        </div>
                      </div>
                      <div class="gc-hero__ribbon" aria-label="Promotions">${ribTrack}</div>
                    </div>
                  `;
                })
                .join("")}
            </div>

            <div class="swiper-button-prev" aria-label="Previous slide"></div>
            <div class="swiper-button-next" aria-label="Next slide"></div>
            <div class="swiper-pagination" aria-label="Hero pagination"></div>
          </div>
        </div>
      </section>
    `;

    const wrap = document.createElement("div");
    wrap.appendChild(secInner);

    queueMicrotask(() => initHeroSwiper(cfg));
    return wrap;
  }

  function initHeroSwiper(cfg) {
    const el = $(".gc-heroSwiper");
    if (!el || typeof Swiper === "undefined") return;
    const ms = clamp(Number(cfg.hero?.autoplayMs || 5200), 2500, 12000);
    const swiper = new Swiper(el, {
      loop: true,
      speed: 900,
      grabCursor: true,
      parallax: true,
      autoplay: { delay: ms, disableOnInteraction: false, pauseOnMouseEnter: true },
      pagination: { el: ".gc-hero .swiper-pagination", clickable: true },
      navigation: { nextEl: ".gc-hero .swiper-button-next", prevEl: ".gc-hero .swiper-button-prev" },
      effect: "creative",
      creativeEffect: {
        prev: { shadow: true, translate: ["-8%", 0, -200], opacity: 0.35, scale: 0.98 },
        next: { shadow: true, translate: ["8%", 0, -200], opacity: 0.35, scale: 0.98 },
      },
    });
    // Smooth reset of autoplay after swipe
    el.addEventListener("pointerdown", () => swiper.autoplay?.stop?.(), { passive: true });
    el.addEventListener("pointerup", () => swiper.autoplay?.start?.(), { passive: true });
  }

  function starSvg(filled) {
    const fill = filled ? "rgba(255,46,122,.95)" : "rgba(18,19,24,.16)";
    return `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="${fill}" d="M12 17.3 18.2 21l-1.7-7.1L22 9.2l-7.2-.6L12 2 9.2 8.6 2 9.2l5.5 4.7L5.8 21z"/></svg>`;
  }

  function getCatalog() {
    const gc = window.GlowCare;
    if (!gc?.Catalog?.getCatalog) return [];
    return gc.Catalog.getCatalog() || [];
  }

  function productMatches(p, filter) {
    if (!filter) return true;
    const badge = (filter.badge || "").toLowerCase();
    const category = (filter.category || "").toLowerCase();
    const concern = (filter.concern || "").toLowerCase();
    const search = (filter.search || "").toLowerCase();

    if (badge && String(p.badge || "").toLowerCase() !== badge) return false;
    if (category && String(p.category || "").toLowerCase() !== category) return false;
    if (concern) {
      const tags = (p.concernTags || []).map((t) => String(t).toLowerCase());
      if (!tags.includes(concern)) return false;
    }
    if (search) {
      const hay = `${p.name || ""} ${p.description || ""} ${p.brand || ""}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  }

  function pickProducts(filter, limit = 10) {
    const all = getCatalog();
    const filtered = all.filter((p) => productMatches(p, filter));
    // if nothing found, degrade gracefully: use catalog slice
    const out = (filtered.length ? filtered : all).slice(0, limit);
    return out;
  }

  function renderProductCard(p) {
    const price = Number(p.price || 0);
    const rating = clamp(Number(p.rating || 0), 0, 5);
    const stars = Array.from({ length: 5 })
      .map((_, i) => starSvg(rating >= i + 1 - 0.25))
      .join("");

    const swatches = ["#ff2e7a", "#8a5bff", "#39d3c1", "#ffb703"].slice(0, (p.variants?.length || 3));
    const variantKey = p.variants?.[0]?.sku || p.variants?.[0]?.variantKey || "";

    return `
      <article class="gc-card" data-tilt data-product="${escapeAttr(p.id)}" data-variant="${escapeAttr(variantKey)}">
        <div class="gc-card__media">
          <div class="gc-badgeTop">
            <span class="gc-chip gc-chip--hot">${escapeHtml(p.badge || "Pick")}</span>
          </div>
          <button class="gc-quick" type="button" data-quick aria-label="Quick view">
            ${svgIcon("eye")}
          </button>
          <img class="gc-card__img" loading="lazy" decoding="async" src="${escapeAttr(withStaticBase(p.image || ""))}" alt="${escapeAttr(p.name || "Product")}">
        </div>
        <div class="gc-card__body">
          <div class="gc-card__name">${escapeHtml(p.name || "")}</div>
          <div class="gc-card__desc">${escapeHtml(p.description || "")}</div>
          <div class="gc-card__row">
            <div class="gc-price"><b>₹${price}</b> <small>MRP</small></div>
            <div class="gc-rating" aria-label="Rating ${rating.toFixed(1)} out of 5">
              <span class="gc-stars" aria-hidden="true">${stars}</span>
              <span>${rating.toFixed(1)}</span>
            </div>
          </div>
          <div class="gc-swatches" aria-label="Shade swatches">
            ${swatches.map((c) => `<span class="gc-swatch" style="background:${c}" title="Shade" aria-hidden="true"></span>`).join("")}
          </div>
          <div class="gc-card__cta">
            <button class="gc-add" type="button" data-add data-magnetic>
              Add to cart
            </button>
            <button class="gc-wish" type="button" data-wish aria-label="Add to wishlist">
              ${svgIcon("heart")}
            </button>
          </div>
        </div>
      </article>
    `;
  }

  function renderRailSkeleton(count = 6) {
    return Array.from({ length: count })
      .map(
        () => `
          <div class="swiper-slide">
            <div class="gc-skel">
              <div class="gc-skel__top"></div>
              <div class="gc-skel__body">
                <div class="gc-skel__line sm"></div>
                <div class="gc-skel__line"></div>
                <div class="gc-skel__line xs"></div>
              </div>
            </div>
          </div>
        `,
      )
      .join("");
  }

  function renderProductRail({ railId, products }) {
    const slides = products.map((p) => `<div class="swiper-slide">${renderProductCard(p)}</div>`).join("");
    return `
      <div class="gc-rail" data-gc-reveal>
        <div class="swiper gc-railSwiper" data-rail="${escapeAttr(railId)}">
          <div class="swiper-wrapper">
            ${renderRailSkeleton(7)}
          </div>
          <div class="swiper-button-prev" data-prev="${escapeAttr(railId)}" aria-label="Previous"></div>
          <div class="swiper-button-next" data-next="${escapeAttr(railId)}" aria-label="Next"></div>
          <div class="swiper-pagination" data-page="${escapeAttr(railId)}" aria-label="Pagination"></div>
        </div>
      </div>
    `;
  }

  function initRailSwiper(railId) {
    const el = $(`.gc-railSwiper[data-rail="${CSS.escape(railId)}"]`);
    if (!el || typeof Swiper === "undefined") return null;
    return new Swiper(el, {
      loop: false,
      speed: 700,
      spaceBetween: 14,
      grabCursor: true,
      watchSlidesProgress: true,
      navigation: {
        nextEl: `[data-next="${railId}"]`,
        prevEl: `[data-prev="${railId}"]`,
      },
      pagination: { el: `[data-page="${railId}"]`, clickable: true },
      breakpoints: {
        0: { slidesPerView: 1.15, spaceBetween: 12 },
        520: { slidesPerView: 2.15, spaceBetween: 14 },
        980: { slidesPerView: 4, spaceBetween: 16 },
      },
    });
  }

  function hydrateRail(railId, products) {
    const wrap = $(`.gc-railSwiper[data-rail="${CSS.escape(railId)}"] .swiper-wrapper`);
    if (!wrap) return;
    wrap.innerHTML = products.map((p) => `<div class="swiper-slide">${renderProductCard(p)}</div>`).join("");
  }

  function renderProductSection(cfg, key) {
    const data = cfg.productSections?.[key];
    const secInner = document.createElement("div");
    secInner.className = "";

    const tabs = data?.tabs || [];
    const railId = `rail_${key}`;
    const secId = key === "bestsellers" ? "bestsellers" : "newArrivals";
    const action = `<a class="gc-btn gc-btn--ghost" data-magnetic href="${escapeAttr(data?.viewAllHref || "shop.html")}">View all ${svgIcon("arrow")}</a>`;

    secInner.innerHTML = `
      <div class="gc-container">
        ${headBlockHtml(sectionTitle(cfg, secId, data?.title || ""), sectionSubtitle(cfg, secId, data?.subtitle || ""), action)}
        <div class="gc-tabs" role="tablist" aria-label="${escapeAttr(data?.title || "Tabs")}" data-tabs="${escapeAttr(key)}" data-gc-reveal>
          ${tabs
            .map((t, idx) => {
              const sel = idx === 0 ? "true" : "false";
              return `<button class="gc-tab" type="button" role="tab" aria-selected="${sel}" data-tab="${escapeAttr(t.id)}">${escapeHtml(t.label || "")}</button>`;
            })
            .join("")}
        </div>
        ${renderProductRail({ railId, products: [] })}
      </div>
    `;

    const sec = sectionWrap(secInner, { muted: key === "bestsellers" });
    applySectionBg(sec, cfg, secId);

    queueMicrotask(() => {
      const first = tabs[0]?.filter || null;
      const products = pickProducts(first, 10);
      hydrateRail(railId, products);
      const swiper = initRailSwiper(railId);
      // When hydrated after init, update.
      queueMicrotask(() => swiper?.update?.());

      initTabs(key, tabs, railId, swiper);
    });

    return sec;
  }

  function initTabs(key, tabs, railId, swiper) {
    const root = $(`[data-tabs="${CSS.escape(key)}"]`);
    if (!root) return;
    root.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-tab]");
      if (!btn) return;
      const tabId = btn.getAttribute("data-tab");
      $$(".gc-tab", root).forEach((b) => b.setAttribute("aria-selected", b === btn ? "true" : "false"));
      const def = tabs.find((t) => t.id === tabId);
      const products = pickProducts(def?.filter || null, 10);
      hydrateRail(railId, products);
      swiper?.update?.();
      swiper?.slideTo?.(0, 0);
    });
  }

  function renderPromoStrip(cfg) {
    const data = cfg.promoStrip || {};
    const secInner = document.createElement("div");
    secInner.className = "gc-container";
    const bg = data.bg ? `style="background:${escapeAttr(data.bg)}"` : "";
    secInner.innerHTML = `
      <div class="gc-strip" data-gc-reveal ${bg}>
        <div class="gc-strip__row">
          <div>
            <div class="gc-strip__title">${escapeHtml(data.title || "")}</div>
            <div class="gc-sub" style="color: rgba(18,19,24,.64); margin-top:6px;">${escapeHtml(data.subtitle || "")}</div>
            <div class="gc-pills" style="margin-top:12px;">
              ${(data.pills || []).map((p) => `<span class="gc-pill">${escapeHtml(p)}</span>`).join("")}
            </div>
          </div>
          <div class="gc-actions">
            <a class="gc-btn gc-btn--primary" data-magnetic href="${escapeAttr(data.button?.href || "shop.html")}">
              ${escapeHtml(data.button?.label || "Shop")}
              ${svgIcon("arrow")}
            </a>
          </div>
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner, { tight: true });
    applySectionBg(sec, cfg, "promoStrip");
    return sec;
  }

  function renderAppBanner(cfg) {
    const data = cfg.appBanner || {};
    const secInner = document.createElement("div");
    secInner.className = "gc-container";
    const storeIcon = (kind) => {
      if (kind === "apple") {
        return `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.6 13.1c0 2.9 2.5 3.9 2.6 3.9-.02.07-.4 1.4-1.3 2.8-.78 1.2-1.6 2.4-2.9 2.4-1.3 0-1.7-.76-3.2-.76-1.5 0-2 .74-3.2.78-1.3.05-2.3-1.3-3.1-2.5C3.7 19 2.4 15.1 3.8 12c.7-1.5 2-2.5 3.5-2.5 1.3 0 2.5.87 3.2.87.7 0 2.1-1.07 3.6-.91.6.03 2.2.25 3.2 1.8-.08.05-1.9 1.1-1.9 2.9ZM14.7 2.4c.7-.85 1.2-2 1.1-3.2-1 .04-2.2.68-2.9 1.5-.64.74-1.2 1.9-1 3.1 1.1.08 2.2-.56 2.8-1.4Z"/></svg>`;
      }
      return `<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3.5 2.9c-.7.4-1.2 1.1-1.2 1.9v14.4c0 .8.5 1.5 1.2 1.9l9.4-9.2-9.4-9Zm11.1 9.4 2.6-2.6-3.3-1.9-2.9 2.9 3.6 1.6Zm3.2 1.9-2.9-1.3-3.8 3.8 3.3 3.3 3.4-2c.5-.3.8-.8.8-1.4 0-.5-.3-1-.8-1.3Zm-.6-5.2-2.8 2.8 2.8 1.2 2.5-1.4c.5-.3.8-.8.8-1.4 0-.5-.3-1-.8-1.3L17.2 9Z"/></svg>`;
    };
    const bg = data.bg ? `style="background:${escapeAttr(data.bg)}"` : "";
    secInner.innerHTML = `
      <div class="gc-app" data-gc-reveal ${bg}>
        <div class="gc-app__row">
          <div class="gc-app__left">
            <h3>${escapeHtml(data.title || "")}</h3>
            <p>${escapeHtml(data.subtitle || "")}</p>
          </div>
          <div class="gc-storeBtns">
            ${(data.stores || [])
              .map(
                (s) => `
                  <a class="gc-store" data-magnetic href="${escapeAttr(s.href || "#")}" aria-label="${escapeAttr(s.title || "Store")}">
                    ${storeIcon(s.kind)}
                    <span>
                      <small>${escapeHtml(s.label || "")}</small>
                      <b>${escapeHtml(s.title || "")}</b>
                    </span>
                  </a>
                `,
              )
              .join("")}
          </div>
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner, { tight: true });
    applySectionBg(sec, cfg, "appBanner");
    return sec;
  }

  function renderSkinConcerns(cfg) {
    const fromPS = cfg.productSections?.skinConcerns;
    const data = (fromPS && typeof fromPS === "object" ? { ...cfg.skinConcerns, ...fromPS } : cfg.skinConcerns) || {};
    const secInner = document.createElement("div");
    secInner.className = "";
    const railId = "rail_concerns";
    const tabs = data.tabs || [];
    const action = `<a class="gc-btn gc-btn--ghost" data-magnetic href="shop.html?category=skincare">Shop skincare ${svgIcon("arrow")}</a>`;
    secInner.innerHTML = `
      <div class="gc-container">
        ${headBlockHtml(sectionTitle(cfg, "skinConcerns", data.title || ""), sectionSubtitle(cfg, "skinConcerns", data.subtitle || ""), action)}
        <div class="gc-tabs" role="tablist" aria-label="Skin concern tabs" data-tabs="concerns" data-gc-reveal>
          ${tabs
            .map((t, idx) => {
              const sel = idx === 0 ? "true" : "false";
              return `<button class="gc-tab" type="button" role="tab" aria-selected="${sel}" data-tab="${escapeAttr(t.id)}">${escapeHtml(t.label || "")}</button>`;
            })
            .join("")}
        </div>
        ${renderProductRail({ railId, products: [] })}
      </div>
    `;
    const sec = sectionWrap(secInner);
    applySectionBg(sec, cfg, "skinConcerns");
    queueMicrotask(() => {
      const first = tabs[0]?.filter || null;
      const products = pickProducts(first, 10);
      hydrateRail(railId, products);
      const swiper = initRailSwiper(railId);
      queueMicrotask(() => swiper?.update?.());
      initTabs("concerns", tabs, railId, swiper);
    });
    return sec;
  }

  function renderReels(cfg) {
    const data = cfg.reels || {};
    const secSettings = getSection(cfg, "reels")?.settings || {};
    const secInner = document.createElement("div");
    secInner.className = "";
    const items = Array.isArray(secSettings.items) && secSettings.items.length ? secSettings.items : Array.isArray(data.items) && data.items.length ? data.items : pickProducts(null, 8).slice(0, 8).map((p) => ({
      title: p.name,
      productImage: p.image,
      href: `product.html?id=${encodeURIComponent(String(p.id))}`,
    }));
    secInner.innerHTML = `
      <div class="gc-container gc-reels">
        ${headBlockHtml(sectionTitle(cfg, "reels", data.title || ""), sectionSubtitle(cfg, "reels", data.subtitle || ""), `<a class="gc-btn gc-btn--ghost" data-magnetic href="shop.html">View all ${svgIcon("arrow")}</a>`)}
        <div class="gc-rail" data-gc-reveal>
          <div class="swiper gc-reelsSwiper">
            <div class="swiper-wrapper">
              ${(items || [])
                .map(
                  (r) => `
                    <div class="swiper-slide">
                      <div class="gc-reel">
                        <div class="gc-reel__media">
                          <img loading="lazy" src="${escapeAttr(withStaticBase(r.productImage || "assets/images/products/p1.svg"))}" alt="">
                          <div class="gc-reel__cta">
                            <div><b>${escapeHtml(r.title || "")}</b><div class="gc-sub" style="margin-top:2px;">Tap to quick view</div></div>
                            <a class="gc-play" data-magnetic href="${escapeAttr(r.href || "shop.html")}" aria-label="Open">${svgIcon("play")}</a>
                          </div>
                        </div>
                      </div>
                    </div>
                  `,
                )
                .join("")}
            </div>
          </div>
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner, { muted: true });
    applySectionBg(sec, cfg, "reels");
    queueMicrotask(() => {
      const el = $(".gc-reelsSwiper");
      if (!el || typeof Swiper === "undefined") return;
      new Swiper(el, {
        loop: false,
        speed: 700,
        spaceBetween: 14,
        grabCursor: true,
        breakpoints: {
          0: { slidesPerView: 1.15, spaceBetween: 12 },
          520: { slidesPerView: 2.15, spaceBetween: 14 },
          980: { slidesPerView: 5, spaceBetween: 16 },
        },
      });
    });
    return sec;
  }

  function renderFeatures(cfg) {
    const data = cfg.features || {};
    const secSettings = getSection(cfg, "features")?.settings || {};
    const cards = Array.isArray(secSettings.cards) ? secSettings.cards : Array.isArray(data.cards) ? data.cards : [];
    const secInner = document.createElement("div");
    secInner.className = "";
    secInner.innerHTML = `
      <div class="gc-container">
        ${headBlockHtml(sectionTitle(cfg, "features", data.title || ""), sectionSubtitle(cfg, "features", data.subtitle || ""), "")}
        <div class="gc-features" data-gc-reveal>
          ${(cards || [])
            .map(
              (c) => `
                <div class="gc-feature">
                  <div class="gc-fi" aria-hidden="true"></div>
                  <b>${escapeHtml(c.title || "")}</b>
                  <p>${escapeHtml(c.desc || "")}</p>
                </div>
              `,
            )
            .join("")}
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner);
    applySectionBg(sec, cfg, "features");
    return sec;
  }

  function renderStory(cfg) {
    const data = cfg.story || {};
    const secSettings = getSection(cfg, "story")?.settings || {};
    const secInner = document.createElement("div");
    secInner.className = "gc-container";
    const title = sectionTitle(cfg, "story", data.title || "");
    const subtitle = sectionSubtitle(cfg, "story", data.subtitle || "");
    const buttonLabel = secSettings.buttonLabel || data.button?.label || "Read more";
    const buttonHref = secSettings.buttonHref || data.button?.href || "about.html";
    const image = secSettings.imageUrl || data.image || "";
    secInner.innerHTML = `
      <div class="gc-story" data-gc-reveal>
        <div class="gc-story__row">
          <div class="gc-story__copy">
            <div class="gc-title">${escapeHtml(title || "")}</div>
            <p class="gc-sub">${escapeHtml(subtitle || "")}</p>
            <div style="margin-top:16px;">
              <a class="gc-btn gc-btn--primary" data-magnetic href="${escapeAttr(buttonHref)}">
                ${escapeHtml(buttonLabel)}
                ${svgIcon("arrow")}
              </a>
            </div>
          </div>
          <div class="gc-story__art" aria-hidden="true">
            <img loading="lazy" src="${escapeAttr(withStaticBase(image))}" alt="">
          </div>
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner);
    applySectionBg(sec, cfg, "story");
    return sec;
  }

  function renderLogos(cfg) {
    const data = cfg.logos || {};
    const media = Array.isArray(data.media) ? data.media : [];
    const map = new Map(media.map((m) => [m.name, m.logo]));
    const secInner = document.createElement("div");
    secInner.className = "";
    secInner.innerHTML = `
      <div class="gc-container">
        ${headBlockHtml(sectionTitle(cfg, "logos", data.title || ""), sectionSubtitle(cfg, "logos", data.subtitle || ""), "")}
        <div class="gc-logos" data-gc-reveal>
          ${(data.items || [])
            .map((l) => {
              const src = withStaticBase(map.get(l) || "");
              return src
                ? `<div class="gc-logo"><img loading="lazy" alt="${escapeAttr(l)}" src="${escapeAttr(src)}" style="max-width: 72%; max-height: 72%;"></div>`
                : `<div class="gc-logo">${escapeHtml(l)}</div>`;
            })
            .join("")}
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner, { tight: true, muted: true });
    applySectionBg(sec, cfg, "logos");
    return sec;
  }

  function renderTestimonials(cfg) {
    const data = cfg.testimonials || {};
    const secInner = document.createElement("div");
    secInner.className = "";
    secInner.innerHTML = `
      <div class="gc-container">
        ${headBlockHtml(sectionTitle(cfg, "testimonials", data.title || ""), sectionSubtitle(cfg, "testimonials", data.subtitle || ""), "")}
        <div class="gc-rail" data-gc-reveal>
          <div class="swiper gc-testSwiper">
            <div class="swiper-wrapper">
              ${(data.items || [])
                .map((t) => {
                  const r = clamp(Number(t.rating || 0), 0, 5);
                  const stars = Array.from({ length: 5 })
                    .map((_, i) => starSvg(r >= i + 1 - 0.25))
                    .join("");
                  const ava = withStaticBase(t.avatar || "");
                  return `
                    <div class="swiper-slide">
                      <article class="gc-test">
                        <div class="gc-test__top">
                          ${ava ? `<img class="gc-ava" alt="" src="${escapeAttr(ava)}">` : `<div class="gc-ava" aria-hidden="true"></div>`}
                          <div>
                            <div class="gc-test__name">${escapeHtml(t.name || "")}</div>
                            <div class="gc-test__meta">${escapeHtml(t.meta || "")}</div>
                          </div>
                        </div>
                        <div class="gc-rating" style="margin-top:10px;">
                          <span class="gc-stars" aria-hidden="true">${stars}</span>
                          <span>${r.toFixed(1)}</span>
                        </div>
                        <p class="gc-test__body">${escapeHtml(t.text || "")}</p>
                        <div class="gc-test__foot">
                          <span>Verified purchase</span>
                          <a href="shop.html" class="gc-ann__cta">Shop routine</a>
                        </div>
                      </article>
                    </div>
                  `;
                })
                .join("")}
            </div>
          </div>
        </div>
      </div>
    `;
    const sec = sectionWrap(secInner);
    applySectionBg(sec, cfg, "testimonials");
    queueMicrotask(() => {
      const el = $(".gc-testSwiper");
      if (!el || typeof Swiper === "undefined") return;
      new Swiper(el, {
        loop: false,
        speed: 700,
        spaceBetween: 14,
        grabCursor: true,
        breakpoints: {
          0: { slidesPerView: 1.05, spaceBetween: 12 },
          520: { slidesPerView: 2.05, spaceBetween: 14 },
          980: { slidesPerView: 4, spaceBetween: 16 },
        },
      });
    });
    return sec;
  }

  function attachGlobalInteractions() {
    if (window.__GC_INTERACTIONS_ATTACHED) return;
    window.__GC_INTERACTIONS_ATTACHED = true;
    // scroll progress
    const bar = $("#gcScrollProgress");
    const onScroll = () => {
      if (!bar) return;
      const h = document.documentElement;
      const max = Math.max(1, h.scrollHeight - h.clientHeight);
      const pct = (h.scrollTop / max) * 100;
      bar.style.width = `${pct}%`;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    // mouse spotlight + magnetic hover lighting
    const spot = $("#gcSpotlight");
    window.addEventListener(
      "pointermove",
      (e) => {
        if (!spot) return;
        spot.style.transform = `translate3d(${e.clientX - 240}px, ${e.clientY - 180}px, 0)`;
      },
      { passive: true },
    );

    // delegate buttons lighting coordinates
    document.addEventListener(
      "pointermove",
      (e) => {
        const btn = e.target.closest?.(".gc-btn, .gc-add");
        if (!btn) return;
        const r = btn.getBoundingClientRect();
        const mx = ((e.clientX - r.left) / Math.max(1, r.width)) * 100;
        const my = ((e.clientY - r.top) / Math.max(1, r.height)) * 100;
        btn.style.setProperty("--mx", `${mx}%`);
        btn.style.setProperty("--my", `${my}%`);
      },
      { passive: true },
    );

    // magnetic
    document.addEventListener(
      "pointermove",
      (e) => {
        const el = e.target.closest?.("[data-magnetic]");
        if (!el) return;
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) / Math.max(1, r.width);
        const dy = (e.clientY - (r.top + r.height / 2)) / Math.max(1, r.height);
        el.style.transform = `translate3d(${dx * 6}px, ${dy * 6}px, 0)`;
      },
      { passive: true },
    );
    document.addEventListener(
      "pointerleave",
      (e) => {
        const el = e.target.closest?.("[data-magnetic]");
        if (!el) return;
        el.style.transform = "";
      },
      { passive: true, capture: true },
    );

    // product tilt + quick view / cart
    document.addEventListener(
      "pointermove",
      (e) => {
        const card = e.target.closest?.("[data-tilt]");
        if (!card) return;
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / Math.max(1, r.width);
        const py = (e.clientY - r.top) / Math.max(1, r.height);
        const rx = (0.5 - py) * 8;
        const ry = (px - 0.5) * 10;
        card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-2px)`;
      },
      { passive: true },
    );
    document.addEventListener(
      "pointerleave",
      (e) => {
        const card = e.target.closest?.("[data-tilt]");
        if (!card) return;
        card.style.transform = "";
      },
      { passive: true, capture: true },
    );

    document.addEventListener("click", (e) => {
      const add = e.target.closest?.("[data-add]");
      const quick = e.target.closest?.("[data-quick]");
      const wish = e.target.closest?.("[data-wish]");

      if (add) {
        const card = add.closest?.("[data-product]");
        if (!card) return;
        const productId = card.getAttribute("data-product");
        const variantKey = card.getAttribute("data-variant");
        const res = window.GlowCare?.Cart?.addToCart?.(productId, variantKey, 1);
        if (res?.ok) {
          add.dataset.added = "1";
          add.textContent = "Added";
          window.setTimeout(() => {
            add.dataset.added = "0";
            add.textContent = "Add to cart";
          }, 1200);
        }
        return;
      }

      if (wish) {
        const card = wish.closest?.("[data-product]");
        if (!card) return;
        const productId = card.getAttribute("data-product");
        const res = window.GlowCare?.Wishlist?.toggleWishlist?.(productId);
        if (res?.ok) {
          wish.style.transform = "scale(1.06)";
          window.setTimeout(() => (wish.style.transform = ""), 180);
        }
        return;
      }

      if (quick) {
        const card = quick.closest?.("[data-product]");
        if (!card) return;
        const productId = card.getAttribute("data-product");
        openQuickView(productId);
      }
    });
  }

  function ensureModal() {
    let modal = $("#gcQuickModal");
    if (modal) return modal;
    modal = document.createElement("dialog");
    modal.className = "gc-modal";
    modal.id = "gcQuickModal";
    modal.innerHTML = `
      <div class="gc-modal__backdrop" data-close></div>
      <div class="gc-modal__panel" role="document" aria-label="Quick view">
        <div class="gc-modal__top">
          <b id="gcModalTitle">Quick view</b>
          <button class="gc-x" type="button" data-close aria-label="Close">✕</button>
        </div>
        <div class="gc-modal__grid">
          <div class="gc-modal__img"><img id="gcModalImg" alt=""></div>
          <div>
            <div class="gc-rating" id="gcModalRating"></div>
            <div class="gc-price" style="margin-top:8px;" id="gcModalPrice"></div>
            <p class="gc-modal__desc" id="gcModalDesc"></p>
            <div style="margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;">
              <a class="gc-btn gc-btn--primary" data-magnetic id="gcModalShop" href="shop.html">Open product ${svgIcon("arrow")}</a>
              <button class="gc-btn gc-btn--ghost" data-magnetic id="gcModalAdd" type="button">Add to cart</button>
            </div>
            <div style="margin-top:12px;">
              <div class="gc-sub">Key ingredients</div>
              <ul id="gcModalList"></ul>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.addEventListener("click", (e) => {
      if (e.target.closest?.("[data-close]")) closeModal(modal);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.hasAttribute("open")) closeModal(modal);
    });
    return modal;
  }

  function openQuickView(productId) {
    const p = window.GlowCare?.Catalog?.getProductById?.(productId);
    if (!p) return;
    const modal = ensureModal();
    $("#gcModalTitle").textContent = p.name || "Product";
    $("#gcModalImg").src = withStaticBase(p.image || "");
    $("#gcModalImg").alt = p.name || "Product image";
    $("#gcModalDesc").textContent = p.description || "";
    const rating = clamp(Number(p.rating || 0), 0, 5);
    const stars = Array.from({ length: 5 })
      .map((_, i) => starSvg(rating >= i + 1 - 0.25))
      .join("");
    $("#gcModalRating").innerHTML = `<span class="gc-stars" aria-hidden="true">${stars}</span><span>${rating.toFixed(1)}</span>`;
    $("#gcModalPrice").innerHTML = `<b>₹${Number(p.price || 0)}</b> <small>MRP</small>`;
    $("#gcModalShop").href = `product.html?id=${encodeURIComponent(p.id)}`;

    const list = $("#gcModalList");
    list.innerHTML = (p.ingredients || []).slice(0, 5).map((i) => `<li>${escapeHtml(i)}</li>`).join("");

    const addBtn = $("#gcModalAdd");
    addBtn.onclick = () => {
      const variantKey = p.variants?.[0]?.sku || "";
      window.GlowCare?.Cart?.addToCart?.(p.id, variantKey, 1);
      addBtn.textContent = "Added";
      window.setTimeout(() => (addBtn.textContent = "Add to cart"), 1200);
    };

    try {
      modal.setAttribute("open", "");
      document.body.style.overflow = "hidden";
    } catch {
      modal.setAttribute("open", "");
    }
  }

  function closeModal(modal) {
    modal.removeAttribute("open");
    document.body.style.overflow = "";
  }

  function attachRevealObserver() {
    const els = $$("[data-gc-reveal]");
    if (!("IntersectionObserver" in window)) {
      els.forEach((el) => el.classList.add("is-in"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            en.target.classList.add("is-in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.14, rootMargin: "40px 0px -10% 0px" },
    );
    els.forEach((el) => io.observe(el));
  }

  function seedFX() {
    const blobs = $("#gcBlobs");
    const particles = $("#gcParticles");
    if (blobs && blobs.childElementCount === 0) {
      const b1 = document.createElement("div");
      b1.className = "gc-blob";
      b1.style.left = "-10%";
      b1.style.top = "10%";
      blobs.appendChild(b1);

      const b2 = document.createElement("div");
      b2.className = "gc-blob";
      b2.dataset.variant = "2";
      b2.style.right = "-14%";
      b2.style.top = "32%";
      blobs.appendChild(b2);

      const b3 = document.createElement("div");
      b3.className = "gc-blob";
      b3.style.left = "14%";
      b3.style.bottom = "-18%";
      b3.style.opacity = ".14";
      b3.style.animationDuration = "16s";
      blobs.appendChild(b3);
    }

    if (particles && particles.childElementCount === 0) {
      const count = 26;
      for (let i = 0; i < count; i += 1) {
        const p = document.createElement("span");
        p.className = "gc-particle";
        p.style.left = `${Math.random() * 100}%`;
        p.style.top = `${20 + Math.random() * 100}%`;
        p.style.opacity = String(0.12 + Math.random() * 0.25);
        p.style.animationDuration = `${8 + Math.random() * 10}s`;
        p.style.animationDelay = `${Math.random() * 6}s`;
        particles.appendChild(p);
      }
    }
  }

  function applyConfig(cfg) {
    const safe = cfg && typeof cfg === "object" ? cfg : getCMS();
    setCssVars(safe.theme);
    seedFX();
    renderAnnouncement(safe);
    updateNavFromCMS(safe);
    updateFooterFromCMS(safe);
    renderHome(safe);
    attachGlobalInteractions();
  }

  async function init() {
    persistDefaultOnce();
    const previewMode = !!window.__GC_PREVIEW_MODE;
    const apiCfg = previewMode ? null : await loadCMSFromAPI();
    const cfg = apiCfg || getCMS();
    applyConfig(cfg);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  // Expose for future admin integration
  window.GlowCareCMS = {
    key: CMS_KEY,
    get: () => getCMS(),
    set: (next) => localStorage.setItem(CMS_KEY, JSON.stringify(next)),
    reset: () => localStorage.setItem(CMS_KEY, JSON.stringify(DEFAULT_CMS)),
  };

  // Used by dashboard Visual Editor iframe to apply live changes without refresh
  window.GlowCareHomepage = {
    apply: (cfg) => applyConfig(cfg),
    get: () => getCMS(),
  };
})();
