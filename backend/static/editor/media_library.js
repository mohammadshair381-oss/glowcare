(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  const modal = $("[data-media-modal]");
  const grid = $("[data-media-grid]");
  const fileInp = $("[data-media-file]");
  const titleInp = $("[data-media-title]");
  const altInp = $("[data-media-alt]");
  const kindSel = $("[data-media-kind]");
  const uploadBtn = $("[data-media-upload]");

  const closeBtns = $$("[data-media-close]");

  const state = {
    open: false,
    loading: false,
    items: [],
    onSelect: null,
    accept: null,
  };

  function esc(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function setOpen(next) {
    state.open = !!next;
    if (!modal) return;
    modal.hidden = !state.open;
    document.documentElement.style.overflow = state.open ? "hidden" : "";
  }

  function render() {
    if (!grid) return;
    const accept = state.accept;
    const items = Array.isArray(state.items) ? state.items : [];
    const filtered = accept && Array.isArray(accept) ? items.filter((x) => accept.includes(x.kind)) : items;
    grid.innerHTML = filtered
      .map((a) => {
        const thumb =
          a.kind === "video"
            ? `<video src="${esc(a.url)}" muted playsinline></video>`
            : `<img src="${esc(a.url)}" alt="${esc(a.alt || a.title || "")}" loading="lazy">`;
        return `
          <div class="m-item" data-media-item="${esc(a.id)}">
            <div class="m-thumb">${thumb}</div>
            <div class="m-meta">
              <b title="${esc(a.title || "")}">${esc(a.title || "Untitled")}</b>
              <small>${esc(a.kind || "image")}</small>
              <div class="m-actions">
                <button class="m-mini" type="button" data-media-select="${esc(a.id)}">Select</button>
                <button class="m-mini m-mini--danger" type="button" data-media-del="${esc(a.id)}">Delete</button>
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  async function refresh() {
    if (!window.GCEditor?.api?.get) return;
    state.loading = true;
    try {
      const json = await window.GCEditor.api.get(window.GCEditor.boot?.mediaUrl);
      state.items = Array.isArray(json?.items) ? json.items : [];
      render();
    } catch (e) {
      console.error(e);
    } finally {
      state.loading = false;
    }
  }

  function bootstrapUrls() {
    const boot = window.GCEditor?.boot || null;
    if (!boot?.mediaUrl) return null;
    return boot;
  }

  async function upload() {
    const boot = bootstrapUrls();
    if (!boot?.mediaUrl || !fileInp?.files?.[0]) return;
    const fd = new FormData();
    fd.set("file", fileInp.files[0]);
    fd.set("kind", kindSel?.value || "image");
    fd.set("title", titleInp?.value || "");
    fd.set("alt", altInp?.value || "");
    uploadBtn.textContent = "Uploading…";
    try {
      const res = await fetch(boot.mediaUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": window.GCEditor?.csrf || "" },
        body: fd,
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok || json?.ok === false) throw new Error(json?.error || "bad_status");
      if (json?.item) state.items.unshift(json.item);
      fileInp.value = "";
      titleInp.value = "";
      altInp.value = "";
      render();
    } catch (e) {
      console.error(e);
    } finally {
      uploadBtn.textContent = "Upload";
    }
  }

  async function del(id) {
    const boot = bootstrapUrls();
    if (!boot?.mediaDeleteUrlTmpl) return;
    const url = window.GCEditor.api.withPk(boot.mediaDeleteUrlTmpl, id);
    try {
      const res = await fetch(url, { method: "POST", credentials: "same-origin", headers: { "X-CSRFToken": window.GCEditor.csrf || "" } });
      const json = await res.json().catch(() => ({}));
      if (!res.ok || json?.ok === false) throw new Error("bad_status");
      state.items = state.items.filter((x) => String(x.id) !== String(id));
      render();
    } catch (e) {
      console.error(e);
    }
  }

  function open(opts = {}) {
    state.onSelect = typeof opts.onSelect === "function" ? opts.onSelect : null;
    state.accept = Array.isArray(opts.accept) ? opts.accept : null;
    setOpen(true);
    refresh();
  }

  function close() {
    state.onSelect = null;
    state.accept = null;
    setOpen(false);
  }

  function pick(id) {
    const item = state.items.find((x) => String(x.id) === String(id));
    if (!item) return;
    const cb = state.onSelect;
    close();
    cb?.(item);
  }

  function init() {
    if (!modal) return;
    closeBtns.forEach((b) => b.addEventListener("click", close));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && state.open) close();
    });
    grid?.addEventListener("click", (e) => {
      const sel = e.target.closest?.("[data-media-select]")?.getAttribute("data-media-select");
      const delId = e.target.closest?.("[data-media-del]")?.getAttribute("data-media-del");
      if (sel) {
        pick(sel);
        return;
      }
      if (delId) {
        del(delId);
      }
    });
    uploadBtn?.addEventListener("click", upload);
  }

  window.GCMediaLibrary = { open, close, refresh };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();


window.addEventListener('DOMContentLoaded', () => {

    const modal =
        document.querySelector('.media-library-modal') ||
        document.querySelector('.media-modal') ||
        document.querySelector('#mediaLibrary') ||
        document.querySelector('[data-media-library]');

    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('open', 'active', 'show');

        const closeBtn =
            modal.querySelector('.close') ||
            modal.querySelector('.close-btn') ||
            modal.querySelector('.modal-close') ||
            modal.querySelector('[data-close]');

        function closeModal() {
            modal.style.display = 'none';
            modal.classList.remove('open', 'active', 'show');
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    }
});


window.addEventListener('load', () => {

    const mediaPopup = [...document.querySelectorAll('div')]
        .find(el => el.innerText && el.innerText.includes('Media Library'));

    if (mediaPopup) {
        mediaPopup.style.display = 'none';
    }

});