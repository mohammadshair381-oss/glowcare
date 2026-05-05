(() => {
  function observe() {
    const items = Array.from(document.querySelectorAll("[data-animate]"));
    if (!items.length) return;
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          const el = e.target;
          const kind = el.getAttribute("data-animate") || "rise-in";
          el.classList.add(kind);
          obs.unobserve(el);
        }
      },
      { root: null, threshold: 0.12 }
    );
    items.forEach((el) => obs.observe(el));
  }
  document.addEventListener("DOMContentLoaded", observe);
})();

