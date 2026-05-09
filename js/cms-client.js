/* GlowCare CMS client
   Applies theme + announcement + nav/footer from backend CMS on non-home pages.
   Homepage uses script.js (full renderer).
*/

(() => {
  const CMS_API = "/api/v1/homepage/";
  const CACHE_KEY = "glowcare_home_cms_v1";

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  function safeParse(text, fallback) {
    try {
      const v = JSON.parse(text);
      return v ?? fallback;
    } catch {
      return fallback;
    }
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

  async function fetchCMS() {
    try {
      const res = await fetch(CMS_API, { credentials: "same-origin" });
      if (!res.ok) throw new Error("bad_status");
      const data = await res.json();
      if (!data || typeof data !== "object") throw new Error("bad_json");
      localStorage.setItem(CACHE_KEY, JSON.stringify(data));
      return data;
    } catch {
      return safeParse(localStorage.getItem(CACHE_KEY), null);
    }
  }

  function applyTheme(cfg) {
    const tokens = cfg?.theme;
    if (!tokens || typeof tokens !== "object") return;
    const root = document.documentElement;
    Object.entries(tokens).forEach(([k, v]) => {
      if (!k || typeof v !== "string") return;
      root.style.setProperty(k, v);
    });
  }

  function applyAnnouncement(cfg) {
    const host = $("#gcAnnouncement");
    const ann = cfg?.announcement;
    if (!host || !ann) return;
    if (!ann.enabled) {
      host.innerHTML = "";
      document.documentElement.style.setProperty("--gc-ann-height", "0px");
      return;
    }
    host.innerHTML = `
      <div class="gc-ann" ${ann.bg ? `style="background:${escapeAttr(ann.bg)}"` : ""}>
        <div class="gc-container">
          <div class="gc-ann__row">
            <span class="gc-ann__pill">
              <span class="gc-ann__badge">${escapeHtml(ann.badge || "Offer")}</span>
              <span>${escapeHtml(ann.text || "")}</span>
              <a class="gc-ann__cta" href="${escapeAttr(ann.ctaHref || "shop.html")}">${escapeHtml(ann.ctaText || "Shop")}</a>
            </span>
          </div>
        </div>
      </div>
    `;
    requestAnimationFrame(() => {
      const el = $(".gc-ann");
      const h = el ? el.getBoundingClientRect().height : 0;
      document.documentElement.style.setProperty("--gc-ann-height", `${Math.round(h)}px`);
    });
  }

  function applyNav(cfg) {
    const row = $(".navbar__linksRow");
    const links = cfg?.navigation?.links;
    if (!row || !Array.isArray(links) || !links.length) return;
    row.innerHTML = links
      .map((l) => {
        const cls = `navlink${l.pill ? " navlink--pill" : ""}`;
        return `<a class="${cls}" href="${escapeAttr(l.href || "#")}">${escapeHtml(l.label || "Link")}</a>`;
      })
      .join("");
  }

  function applyFooter(cfg) {
    const footer = $(".site-footer");
    const f = cfg?.footer;
    if (!footer || !f) return;
    const about = $(".footer__muted", footer);
    if (about && typeof f.aboutText === "string") about.textContent = f.aboutText;
    const chips = $(".footer__chips", footer);
    if (chips && Array.isArray(f.chips)) chips.innerHTML = f.chips.map((c) => `<span class="footchip">${escapeHtml(c)}</span>`).join("");
  }

  async function init() {
    // Skip on homepage (handled by script.js)
    if ($("#gcHome")) return;
    const cfg = await fetchCMS();
    if (!cfg) return;
    applyTheme(cfg);
    applyAnnouncement(cfg);
    // navbar/footer are injected by js/main.js; wait briefly
    let tries = 0;
    const t = setInterval(() => {
      tries += 1;
      applyNav(cfg);
      applyFooter(cfg);
      if ($(".navbar__linksRow") || tries > 30) clearInterval(t);
    }, 80);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

