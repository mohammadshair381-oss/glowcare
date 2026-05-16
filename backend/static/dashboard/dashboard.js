(() => {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  function csrfToken() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return el ? el.value : "";
  }

  function initSortable() {
    const hosts = qsa("[data-sortable]");
    if (!hosts.length || typeof Sortable === "undefined") return;
    hosts.forEach((host) => {
      Sortable.create(host, {
        handle: ".dhandle",
        animation: 150,
        ghostClass: "drow--ghost",
      });
    });
  }

  function initSaveSections() {
    const btn = qs("[data-save-sections]");
    const form = qs("#sectionsForm");
    const list = qs("#sectionsSortable");
    if (!btn || !form || !list) return;

    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]").map((c) => [c.dataset.enabled, c.checked]);

      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));

      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        if (json?.ok) btn.textContent = "Saved";
        else btn.textContent = "Save failed";
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save changes"), 1200);
    });
  }

  function initSaveHero() {
    const btn = qs("[data-save-hero]");
    const form = qs("#heroOrderForm");
    const list = qs("#heroSortable");
    if (!btn || !form || !list) return;
    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]", list).map((c) => [c.dataset.enabled, c.checked]);
      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));
      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        btn.textContent = json?.ok ? "Saved" : "Save failed";
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save order"), 1200);
    });
  }

  function initSaveNav() {
    const btn = qs("[data-save-nav]");
    const form = qs("#navOrderForm");
    const list = qs("#navSortable");
    if (!btn || !form || !list) return;
    btn.addEventListener("click", async () => {
      const order = qsa(".ditem", list).map((el) => el.dataset.id);
      const enabledPairs = qsa("input[data-enabled]", list).map((c) => [c.dataset.enabled, c.checked]);
      const deletePairs = qsa("input[data-delete]", list).map((c) => [c.dataset.delete, c.checked]);
      const body = new URLSearchParams();
      body.set("csrfmiddlewaretoken", csrfToken());
      order.forEach((id) => body.append("order[]", id));
      enabledPairs.forEach(([id, val]) => body.set(`enabled_${id}`, val ? "1" : "0"));
      deletePairs.forEach(([id, val]) => body.set(`delete_${id}`, val ? "1" : "0"));
      btn.textContent = "Saving…";
      try {
        const res = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body });
        const json = await res.json();
        btn.textContent = json?.ok ? "Saved" : "Save failed";
        if (json?.ok) window.setTimeout(() => window.location.reload(), 350);
      } catch {
        btn.textContent = "Save failed";
      }
      setTimeout(() => (btn.textContent = "Save menu"), 1200);
    });
  }

  function initAssetsManager() {
    const uploadForm = qs("[data-assets-upload]");
    const grid = qs("[data-assets-grid]");
    if (!uploadForm || !grid) return;
    if (uploadForm.dataset.assetsInit === "1") return;
    uploadForm.dataset.assetsInit = "1";

    const drop = qs("[data-assets-drop]", uploadForm);
    const fileInput = qs("[data-assets-file]", uploadForm);
    const pickBtn = qs("[data-assets-pick]", uploadForm);
    const progressHost = qs("[data-assets-progress]", uploadForm);
    const progressBar = qs("[data-assets-progress-bar]", uploadForm);
    const progressText = qs("[data-assets-progress-text]", uploadForm);
    const contextSel = qs("[data-assets-context]", uploadForm);
    const productsOnly = qsa("[data-assets-products-only]", uploadForm);

    const searchInput = qs("[data-assets-search]");
    const filterBtns = qsa("[data-assets-kind]");

    const modal = qs("[data-assets-modal]");
    const modalTitle = qs("[data-assets-modal-title]");
    const modalBody = qs("[data-assets-modal-body]");
    const modalFoot = qs("[data-assets-modal-foot]");
    const modalClose = qs("[data-assets-modal-close]");

    let activeKind = "all";
    let searchQ = "";

    function setProductsOnlyVisible() {
      const isProducts = (contextSel?.value || "") === "products";
      productsOnly.forEach((el) => (el.hidden = !isProducts));
    }

    function openModal({ title, bodyNode, footNode }) {
      if (!modal || !modalTitle || !modalBody) return;
      modalTitle.textContent = title || "Details";
      modalBody.innerHTML = "";
      if (bodyNode) modalBody.appendChild(bodyNode);
      if (modalFoot) {
        modalFoot.innerHTML = "";
        if (footNode) {
          modalFoot.hidden = false;
          modalFoot.appendChild(footNode);
        } else {
          modalFoot.hidden = true;
        }
      }
      modal.hidden = false;
      // Prevent background scroll while modal is open; reset on close.
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      if (!modal) return;
      modal.hidden = true;
      document.body.style.overflow = "";
      // Stop any playing media to avoid "stuck" focus/overlay sensations.
      try {
        qsa("video", modalBody || modal).forEach((v) => v.pause());
      } catch {}
      if (modalBody) modalBody.innerHTML = "";
      if (modalFoot) modalFoot.innerHTML = "";
    }

    modalClose?.addEventListener("click", closeModal);
    modal?.addEventListener("click", (e) => {
      if (e.target === modal) closeModal();
    });
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal && !modal.hidden) closeModal();
    });

    function setProgress(pct, text) {
      if (!progressHost || !progressBar || !progressText) return;
      progressHost.hidden = false;
      progressBar.style.width = `${Math.max(0, Math.min(100, pct || 0))}%`;
      progressText.textContent = text || "";
    }

    function hideProgress() {
      if (!progressHost || !progressBar) return;
      progressHost.hidden = true;
      progressBar.style.width = "0%";
    }

    function updateCounters(counts) {
      const t = qs("[data-asset-count-total]");
      const i = qs("[data-asset-count-images]");
      const v = qs("[data-asset-count-videos]");
      if (t && typeof counts?.total === "number") t.textContent = counts.total;
      if (i && typeof counts?.images === "number") i.textContent = counts.images;
      if (v && typeof counts?.videos === "number") v.textContent = counts.videos;
    }

    function assetCard(item) {
      const wrap = document.createElement("div");
      wrap.dataset.assetId = String(item.id);
      wrap.dataset.assetKind = item.kind;
      wrap.dataset.assetUrl = item.url;
      wrap.dataset.assetTitle = item.title || "";
      wrap.style.border = "1px solid rgba(255,255,255,.10)";
      wrap.style.background = "rgba(0,0,0,.18)";
      wrap.style.borderRadius = "18px";
      wrap.style.overflow = "hidden";

      const thumb = document.createElement("div");
      thumb.style.aspectRatio = "1 / 1";
      thumb.style.display = "grid";
      thumb.style.placeItems = "center";
      thumb.style.background = "rgba(255,255,255,.04)";

      if (item.kind === "image") {
        const img = document.createElement("img");
        img.src = item.url;
        img.alt = "";
        img.loading = "lazy";
        img.style.maxWidth = "92%";
        img.style.maxHeight = "92%";
        thumb.appendChild(img);
      } else {
        const b = document.createElement("div");
        b.className = "dmuted";
        b.style.margin = "0";
        b.textContent = "Video";
        thumb.appendChild(b);
      }

      const meta = document.createElement("div");
      meta.style.padding = "10px";
      const t = document.createElement("div");
      t.style.fontWeight = "900";
      t.style.fontSize = "12px";
      t.style.whiteSpace = "nowrap";
      t.style.overflow = "hidden";
      t.style.textOverflow = "ellipsis";
      t.textContent = item.title || item.filename || item.url;
      const u = document.createElement("div");
      u.className = "dhelp";
      u.style.marginTop = "6px";
      u.style.wordBreak = "break-all";
      u.textContent = item.url;

      const actions = document.createElement("div");
      actions.style.marginTop = "10px";
      actions.style.display = "flex";
      actions.style.gap = "8px";
      actions.style.flexWrap = "wrap";

      const p = document.createElement("button");
      p.type = "button";
      p.className = "dbtn";
      p.dataset.assetPreview = "1";
      p.textContent = "Preview";
      const c = document.createElement("button");
      c.type = "button";
      c.className = "dbtn";
      c.dataset.assetCopy = "1";
      c.textContent = "Copy URL";
      const d = document.createElement("button");
      d.type = "button";
      d.className = "dbtn";
      d.dataset.assetDelete = "1";
      d.textContent = "Delete";
      actions.appendChild(p);
      actions.appendChild(c);
      actions.appendChild(d);

      meta.appendChild(t);
      meta.appendChild(u);
      meta.appendChild(actions);

      wrap.appendChild(thumb);
      wrap.appendChild(meta);
      return wrap;
    }

    async function reloadAssets() {
      const params = new URLSearchParams();
      if (searchQ) params.set("q", searchQ);
      if (activeKind !== "all") params.set("kind", activeKind);
      const base = uploadForm.dataset.assetsListUrl || "/dashboard/assets/api/list/";
      const apiUrl = `${base}?${params}`;

      try {
        const res = await fetch(apiUrl, { headers: { "Accept": "application/json" } });
        const json = await res.json();
        if (!json?.ok) return;
        updateCounters(json.counts);
        grid.innerHTML = "";
        (json.items || []).forEach((it) => grid.appendChild(assetCard(it)));
      } catch {
        // ignore
      }
    }

    function setActiveFilter(kind) {
      activeKind = kind;
      filterBtns.forEach((b) => {
        const k = b.dataset.assetsKind;
        if (k === activeKind) b.classList.add("dbtn--primary");
        else b.classList.remove("dbtn--primary");
      });
      reloadAssets();
    }

    filterBtns.forEach((b) => b.addEventListener("click", () => setActiveFilter(b.dataset.assetsKind || "all")));

    let searchTimer = null;
    searchInput?.addEventListener("input", () => {
      searchQ = (searchInput.value || "").trim();
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(reloadAssets, 260);
    });

    function handleGridClick(e) {
      const btn = e.target.closest("button");
      if (!btn) return;
      const card = btn.closest("[data-asset-id]");
      if (!card) return;
      const assetId = card.dataset.assetId;
      const assetUrl = card.dataset.assetUrl;
      const assetKind = card.dataset.assetKind;
      const assetTitle = card.dataset.assetTitle || "Asset";

      if (btn.dataset.assetCopy !== undefined) {
        (async () => {
          try {
            await navigator.clipboard.writeText(assetUrl);
            btn.textContent = "Copied";
          } catch {
            window.prompt("Copy asset URL:", assetUrl);
          }
          window.setTimeout(() => (btn.textContent = "Copy URL"), 900);
        })();
        return;
      }

      if (btn.dataset.assetPreview !== undefined) {
        const body = document.createElement("div");
        body.style.display = "grid";
        body.style.placeItems = "center";
        body.style.gap = "10px";
        if (assetKind === "video") {
          const v = document.createElement("video");
          v.controls = true;
          v.src = assetUrl;
          v.style.maxWidth = "100%";
          v.style.maxHeight = "62vh";
          body.appendChild(v);
        } else {
          const img = document.createElement("img");
          img.src = assetUrl;
          img.alt = "";
          img.style.maxWidth = "100%";
          img.style.maxHeight = "62vh";
          img.style.borderRadius = "18px";
          img.style.border = "1px solid rgba(255,255,255,.12)";
          body.appendChild(img);
        }
        const help = document.createElement("div");
        help.className = "dhelp";
        help.style.wordBreak = "break-all";
        help.textContent = assetUrl;
        body.appendChild(help);
        openModal({ title: assetTitle, bodyNode: body });
        return;
      }

      if (btn.dataset.assetDelete !== undefined) {
        const body = document.createElement("div");
        body.innerHTML = `
          <div style="font-weight:950; letter-spacing:-0.03em;">Delete this asset?</div>
          <div class="dhelp" style="margin-top:6px;">This action cannot be undone. If the asset is currently in use, deletion will be blocked.</div>
          <div class="dhelp" style="margin-top:10px; word-break:break-all;">${assetUrl}</div>
        `;

        const foot = document.createElement("div");
        const cancel = document.createElement("button");
        cancel.type = "button";
        cancel.className = "dbtn";
        cancel.textContent = "Cancel";
        cancel.addEventListener("click", closeModal);
        const confirm = document.createElement("button");
        confirm.type = "button";
        confirm.className = "dbtn dbtn--primary";
        confirm.textContent = "Delete";
        confirm.addEventListener("click", async () => {
          confirm.textContent = "Deleting…";
          try {
            const delBase = uploadForm.dataset.assetsDeleteBase || "/dashboard/assets/api/";
            const res = await fetch(`${delBase}${assetId}/delete/`, {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: new URLSearchParams({ csrfmiddlewaretoken: csrfToken() }),
            });
            const json = await res.json();
            if (json?.ok) {
              closeModal();
              await reloadAssets();
              return;
            }
            if (json?.error === "in_use" && json?.usage) {
              const u = json.usage;
              const w = document.createElement("div");
              w.innerHTML = `<div style="font-weight:950; letter-spacing:-0.03em;">Asset is in use</div>
                <div class="dhelp" style="margin-top:6px;">Unlink it from the items below, then try again.</div>`;
              const pre = document.createElement("pre");
              pre.style.whiteSpace = "pre-wrap";
              pre.style.wordBreak = "break-word";
              pre.style.marginTop = "12px";
              pre.style.padding = "12px";
              pre.style.borderRadius = "18px";
              pre.style.border = "1px solid rgba(255,255,255,.12)";
              pre.style.background = "rgba(0,0,0,.20)";
              pre.textContent = JSON.stringify(u, null, 2);
              w.appendChild(pre);
              openModal({ title: "Deletion blocked", bodyNode: w });
              return;
            }
            confirm.textContent = "Delete failed";
          } catch {
            confirm.textContent = "Delete failed";
          }
          window.setTimeout(() => (confirm.textContent = "Delete"), 1000);
        });
        foot.appendChild(cancel);
        foot.appendChild(confirm);
        openModal({ title: "Confirm deletion", bodyNode: body, footNode: foot });
      }
    }

    grid.addEventListener("click", handleGridClick);

    function uploadFiles(files) {
      if (!files || !files.length) return;
      const fd = new FormData(uploadForm);
      // FormData(uploadForm) doesn't include hidden <input type=file> unless it has files
      files.forEach((f) => fd.append("files", f));

      const xhr = new XMLHttpRequest();
      xhr.open("POST", uploadForm.action, true);
      xhr.upload.addEventListener("progress", (evt) => {
        if (!evt.lengthComputable) return;
        const pct = Math.round((evt.loaded / evt.total) * 100);
        setProgress(pct, `Uploading… ${pct}%`);
      });
      xhr.addEventListener("load", async () => {
        try {
          const json = JSON.parse(xhr.responseText || "{}");
          if (json?.ok) {
            setProgress(100, "Upload complete");
            await reloadAssets();
          } else {
            setProgress(0, "Upload failed");
          }
        } catch {
          setProgress(0, "Upload failed");
        }
        window.setTimeout(hideProgress, 700);
      });
      xhr.addEventListener("error", () => {
        setProgress(0, "Upload failed");
        window.setTimeout(hideProgress, 900);
      });

      setProgress(0, "Starting upload…");
      xhr.send(fd);
    }

    pickBtn?.addEventListener("click", () => fileInput?.click());
    fileInput?.addEventListener("change", () => uploadFiles(Array.from(fileInput.files || [])));

    ["dragenter", "dragover"].forEach((ev) =>
      drop?.addEventListener(ev, (e) => {
        e.preventDefault();
        e.stopPropagation();
        drop.classList.add("dassets__drop--active");
      })
    );
    ["dragleave", "drop"].forEach((ev) =>
      drop?.addEventListener(ev, (e) => {
        e.preventDefault();
        e.stopPropagation();
        drop.classList.remove("dassets__drop--active");
      })
    );
    drop?.addEventListener("drop", (e) => {
      const files = Array.from(e.dataTransfer?.files || []);
      uploadFiles(files);
    });

    contextSel?.addEventListener("change", setProductsOnlyVisible);
    setProductsOnlyVisible();
    setActiveFilter("all");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      initSortable();
      initSaveSections();
      initSaveHero();
      initSaveNav();
      initAssetsManager();
    });
  } else {
    initSortable();
    initSaveSections();
    initSaveHero();
    initSaveNav();
    initAssetsManager();
  }
})();
