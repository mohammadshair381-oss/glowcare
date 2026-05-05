(() => {
  function el(id) {
    return document.getElementById(id);
  }

  document.addEventListener("DOMContentLoaded", () => {
    if (!el("loginPage")) return;
    const q = window.GlowCare.parseQuery();
    const next = q.next || "account.html";
    const form = el("loginForm");
    const err = el("loginError");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (err) err.textContent = "";
      const email = el("email")?.value || "";
      const password = el("password")?.value || "";
      const res = window.GlowCare.login({ email, password });
      if (!res.ok) {
        if (err) err.textContent = res.message;
        window.GlowCare.toast(res.message);
        return;
      }
      window.GlowCare.toast("Welcome back");
      window.location.href = next;
    });
  });
})();

