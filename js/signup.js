(() => {
  function el(id) {
    return document.getElementById(id);
  }
  document.addEventListener("DOMContentLoaded", () => {
    if (!el("signupPage")) return;
    const q = window.GlowCare.parseQuery();
    const next = q.next || "account.html";
    const form = el("signupForm");
    const err = el("signupError");
    if (!form) return;
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (err) err.textContent = "";
      const name = el("name")?.value || "";
      const email = el("email")?.value || "";
      const password = el("password")?.value || "";
      const res = window.GlowCare.signup({ name, email, password });
      if (!res.ok) {
        if (err) err.textContent = res.message;
        window.GlowCare.toast(res.message);
        return;
      }
      window.GlowCare.toast("Account created");
      window.location.href = next;
    });
  });
})();

