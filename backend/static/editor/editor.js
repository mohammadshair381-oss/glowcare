(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  function safeJson(text, fallback) {
    try {
      const v = JSON.parse(text);
      return v ?? fallback;
    } catch {
      return fallback;
    }
  }

  function readBootstrap() {
    const el = $("[data-editor-bootstrap]");
    return el ? safeJson(el.textContent || "{}", {}) : {};
  }

  function readCsrf() {
    const inp = $('form[data-editor-csrf] input[name="csrfmiddlewaretoken"]');
    return inp ? inp.value : "";
  }

  function withPk(tmpl, pk) {
    const s = String(tmpl || "");
    // Templates are rendered as ".../0/" or ".../0/delete/" for easy replacement.
    return s.replace("/0/delete/", `/${pk}/delete/`).replace("/0/", `/${pk}/`);
  }

  function deepClone(obj) {
    return obj ? safeJson(JSON.stringify(obj), obj) : obj;
  }

  function debounce(fn, ms = 80) {
    let t = 0;
    return (...args) => {
      window.clearTimeout(t);
      t = window.setTimeout(() => fn(...args), ms);
    };
  }

  const BOOT = readBootstrap();
  const csrf = readCsrf();

  const shell = $("[data-editor-shell]");
  const statusEl = $("[data-editor-status]");
  const iframe = $("[data-editor-iframe]");
  const saveBtn = $("[data-editor-save]");
  const reloadBtn = $("[data-editor-reload]");
  const searchInp = $("[data-editor-search]");

  function setStatus(text) {
    if (statusEl) statusEl.textContent = text;
  }

  const bus = new EventTarget();
  const on = (name, fn) => bus.addEventListener(name, (e) => fn(e.detail));
  const emit = (name, detail) => bus.dispatchEvent(new CustomEvent(name, { detail }));

  const state = {
    boot: BOOT,
    csrf,
    loaded: false,
    dirty: false,
    saving: false,
    data: null,
    lastSentHash: "",
    previewReady: false,
  };

  function markDirty(next = true) {
    state.dirty = !!next;
    if (saveBtn) saveBtn.textContent = state.saving ? "Saving…" : state.dirty ? "Save*" : "Save";
  }

  async function apiGet(url) {
    const res = await fetch(url, { credentials: "same-origin" });
    if (!res.ok) throw new Error("bad_status");
    return res.json();
  }

  async function apiPostJson(url, payload) {
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": state.csrf,
      },
      body: JSON.stringify(payload || {}),
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok || json?.ok === false) throw new Error(json?.error || "bad_status");
    return json;
  }

  function buildPreviewConfigFromState(s) {
    const out = {
      version: 1,
      theme: s?.theme?.tokens || {},
      announcement: {
        enabled: !!s?.announcement?.enabled,
        badge: s?.announcement?.badge || "",
        text: s?.announcement?.text || "",
        ctaText: s?.announcement?.ctaText || "",
        ctaHref: s?.announcement?.ctaHref || "",
        bg: s?.announcement?.bg || "",
      },
      navigation: {
        links: Array.isArray(s?.navigation?.links)
          ? s.navigation.links
              .filter(Boolean)
              .map((l) => ({ label: l.label || "", href: l.href || "#", pill: !!l.isPill }))
          : [],
      },
      footer: s?.footer || null,
      sections: Array.isArray(s?.sections) ? s.sections.map((x) => ({ id: x.sectionId, enabled: !!x.enabled, title: x.title || "", settings: x.settings || {} })) : [],
      hero: {
        autoplayMs: Number(s?.hero?.autoplayMs || 5200),
        slides: Array.isArray(s?.hero?.slides)
          ? s.hero.slides
              .filter(Boolean)
              .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
              .filter((sl) => sl.enabled !== false)
              .map((sl) => ({
                kicker: sl.kicker || "",
                headline: sl.headline || "",
                headline2: sl.headline2 || "",
                sub: sl.sub || "",
                primary: { label: sl.primaryLabel || "", href: sl.primaryHref || "" },
                secondary: { label: sl.secondaryLabel || "", href: sl.secondaryHref || "" },
                cards: [sl.cardA?.url || "", sl.cardB?.url || "", sl.cardC?.url || ""],
                background: { kind: sl.background?.kind || "", url: sl.background?.url || "" },
                overlayBg: sl.overlayBg || "",
                buttonStyles: sl.buttonStyles || {},
                ribbons: Array.isArray(sl.ribbons) ? sl.ribbons : [],
                meta: Array.isArray(sl.meta) ? sl.meta : [],
              }))
          : [],
      },
      promoStrip: s?.promoStrip
        ? {
            title: s.promoStrip.title || "",
            subtitle: s.promoStrip.subtitle || "",
            pills: Array.isArray(s.promoStrip.pills) ? s.promoStrip.pills : [],
            button: { label: s.promoStrip.buttonLabel || "", href: s.promoStrip.buttonHref || "" },
            bg: s.promoStrip.bg || "",
          }
        : null,
      appBanner: s?.appBanner
        ? {
            title: s.appBanner.title || "",
            subtitle: s.appBanner.subtitle || "",
            stores: Array.isArray(s.appBanner.stores) ? s.appBanner.stores : [],
            bg: s.appBanner.bg || "",
          }
        : null,
      logos: {
        media: Array.isArray(s?.logos)
          ? s.logos
              .filter((x) => x.enabled !== false)
              .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
              .map((x) => ({ name: x.name || "", logo: x.logo?.url || "", href: x.href || "" }))
          : [],
      },
      testimonials: {
        items: Array.isArray(s?.testimonials)
          ? s.testimonials
              .filter((x) => x.enabled !== false)
              .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
              .map((t) => ({ name: t.name || "", meta: t.meta || "", rating: Number(t.rating || 5), text: t.text || "", avatar: t.avatar?.url || "" }))
          : [],
      },
      productSections: {},
    };

    if (Array.isArray(s?.productSections)) {
      s.productSections.forEach((ps) => {
        if (!ps || !ps.kind) return;
        out.productSections[ps.kind] = {
          title: ps.title || "",
          subtitle: ps.subtitle || "",
          viewAllHref: ps.viewAllHref || "",
          tabs: Array.isArray(ps.tabs) ? ps.tabs : [],
        };
      });
    }

    return out;
  }

  function hashLite(obj) {
    const s = JSON.stringify(obj || {});
    let h = 0;
    for (let i = 0; i < s.length; i += 1) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return String(h);
  }

  function postToPreview(type, payload) {
    const win = iframe?.contentWindow;
    if (!win) return;
    win.postMessage({ type, payload }, window.location.origin);
  }

  const sendPreviewDebounced = debounce(() => {
    if (!state.data) return;
    const cfg = buildPreviewConfigFromState(state.data);
    const h = hashLite(cfg);
    if (h === state.lastSentHash) return;
    state.lastSentHash = h;
    postToPreview("gc:cms:update", cfg);
  }, 60);

  function setData(next, opts = { markDirty: false, sendPreview: true }) {
    state.data = next;
    if (opts?.markDirty) markDirty(true);
    emit("gc:state", deepClone(state.data));
    if (opts?.sendPreview) sendPreviewDebounced();
  }

  function patch(fn, opts = { markDirty: true, sendPreview: true }) {
    const next = deepClone(state.data || {});
    fn(next);
    setData(next, opts);
  }

  async function load() {
    setStatus("Loading…");
    const data = await apiGet(state.boot.stateUrl);
    state.loaded = true;
    setStatus("Ready");
    setData(data, { markDirty: false, sendPreview: false });
    // prime preview immediately once iframe is loaded
    sendPreviewDebounced();
    markDirty(false);
  }

  async function saveAll() {
    if (!state.data || state.saving) return;
    state.saving = true;
    markDirty(state.dirty);
    setStatus("Saving…");
    try {
      // Bulk apply: theme, announcement, section order/toggles/settings, promo, app, nav, footer
      const payload = {
        themeTokens: state.data.theme?.tokens || {},
        announcement: state.data.announcement || {},
        sections: Array.isArray(state.data.sections)
          ? state.data.sections
              .slice()
              .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
              .map((s, idx) => ({ sectionId: s.sectionId, enabled: !!s.enabled, title: s.title || "", sortOrder: idx, settings: s.settings || {} }))
          : [],
        promoStrip: state.data.promoStrip || null,
        appBanner: state.data.appBanner || null,
        navigation: {
          links: Array.isArray(state.data.navigation?.links)
            ? state.data.navigation.links
                .slice()
                .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
                .map((l, idx) => ({ label: l.label || "", href: l.href || "#", pill: !!l.isPill, enabled: l.enabled !== false, sortOrder: idx }))
            : [],
        },
        footer: state.data.footer || null,
      };
      await apiPostJson(state.boot.applyUrl, payload);

      // Persist hero slides
      if (Array.isArray(state.data.hero?.slides)) {
        const ordered = state.data.hero.slides.slice().sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
        for (let idx = 0; idx < ordered.length; idx += 1) {
          const sl = ordered[idx];
          if (!sl?.id) continue;
          const url = withPk(state.boot.heroSlideUpdateUrlTmpl, sl.id);
          await apiPostJson(url, {
            enabled: sl.enabled !== false,
            sortOrder: idx,
            kicker: sl.kicker || "",
            headline: sl.headline || "",
            headline2: sl.headline2 || "",
            sub: sl.sub || "",
            primaryLabel: sl.primaryLabel || "",
            primaryHref: sl.primaryHref || "",
            secondaryLabel: sl.secondaryLabel || "",
            secondaryHref: sl.secondaryHref || "",
            overlayBg: sl.overlayBg || "",
            buttonStyles: sl.buttonStyles || {},
            ribbons: Array.isArray(sl.ribbons) ? sl.ribbons : [],
            meta: Array.isArray(sl.meta) ? sl.meta : [],
            backgroundId: sl.background?.id || null,
            cardAId: sl.cardA?.id || null,
            cardBId: sl.cardB?.id || null,
            cardCId: sl.cardC?.id || null,
          });
        }
      }

      // Persist testimonials + logos
      if (Array.isArray(state.data.testimonials)) {
        const ordered = state.data.testimonials.slice().sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
        for (let idx = 0; idx < ordered.length; idx += 1) {
          const t = ordered[idx];
          if (!t?.id) continue;
          await apiPostJson(withPk(state.boot.testimonialUpdateUrlTmpl, t.id), {
            enabled: t.enabled !== false,
            sortOrder: idx,
            name: t.name || "",
            meta: t.meta || "",
            rating: Number(t.rating || 5),
            text: t.text || "",
            avatarId: t.avatar?.id || null,
          });
        }
      }
      if (Array.isArray(state.data.logos)) {
        const ordered = state.data.logos.slice().sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0));
        for (let idx = 0; idx < ordered.length; idx += 1) {
          const l = ordered[idx];
          if (!l?.id) continue;
          await apiPostJson(withPk(state.boot.logoUpdateUrlTmpl, l.id), {
            enabled: l.enabled !== false,
            sortOrder: idx,
            name: l.name || "",
            logoId: l.logo?.id || null,
          });
        }
      }

      // Persist product section edits (tabs etc)
      if (Array.isArray(state.data.productSections)) {
        for (const ps of state.data.productSections) {
          if (!ps?.id) continue;
          const url = withPk(state.boot.productSectionUpdateUrlTmpl, ps.id);
          await apiPostJson(url, {
            enabled: ps.enabled !== false,
            title: ps.title || "",
            subtitle: ps.subtitle || "",
            viewAllHref: ps.viewAllHref || "",
            sortOrder: ps.sortOrder ?? 0,
            tabs: Array.isArray(ps.tabs) ? ps.tabs : [],
          });
        }
      }
      setStatus("Saved");
      markDirty(false);
      window.setTimeout(() => setStatus("Ready"), 900);
    } catch (e) {
      console.error(e);
      setStatus("Save failed");
      window.setTimeout(() => setStatus("Ready"), 1400);
    } finally {
      state.saving = false;
      markDirty(state.dirty);
    }
  }

  function initIframeBridge() {
    if (!iframe) return;
    const onMsg = (ev) => {
      if (ev.origin !== window.location.origin) return;
      const msg = ev.data || {};
      if (msg?.type === "gc:preview:ready") {
        state.previewReady = true;
        setStatus(state.dirty ? "Ready (unsaved)" : "Ready");
        // send current state
        sendPreviewDebounced();
      }
      if (msg?.type === "gc:preview:request") {
        sendPreviewDebounced();
      }
    };
    window.addEventListener("message", onMsg);
    iframe.addEventListener("load", () => {
      state.previewReady = false;
      postToPreview("gc:cms:ping", { at: Date.now() });
      window.setTimeout(() => sendPreviewDebounced(), 250);
    });
  }

  function initActions() {
    if (saveBtn) saveBtn.addEventListener("click", () => saveAll());
    if (reloadBtn)
      reloadBtn.addEventListener("click", () => {
        if (!iframe) return;
        setStatus("Reloading…");
        iframe.contentWindow?.location?.reload?.();
      });

    if (searchInp) {
      searchInp.addEventListener(
        "input",
        debounce(() => emit("gc:search", { q: (searchInp.value || "").trim().toLowerCase() }), 60),
      );
    }

    // Ctrl/Cmd+S to save
    document.addEventListener("keydown", (e) => {
      const isSave = (e.ctrlKey || e.metaKey) && String(e.key || "").toLowerCase() === "s";
      if (!isSave) return;
      e.preventDefault();
      saveAll();
    });
  }

  // public surface for other modules
  window.GCEditor = {
    getState: () => deepClone(state.data),
    setState: (next, opts) => setData(next, opts),
    patch,
    on,
    emit,
    boot: state.boot,
    csrf: state.csrf,
    api: {
      get: apiGet,
      post: apiPostJson,
      withPk,
    },
    preview: {
      sendNow: () => {
        state.lastSentHash = "";
        sendPreviewDebounced();
      },
    },
    ui: {
      setStatus,
      markDirty,
    },
  };

  function boot() {
    if (!shell || !state.boot?.stateUrl) {
      setStatus("Missing config");
      return;
    }
    initIframeBridge();
    initActions();
    load().catch((e) => {
      console.error(e);
      setStatus("Failed");
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
