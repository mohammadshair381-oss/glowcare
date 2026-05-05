(() => {
  function el(id) {
    return document.getElementById(id);
  }
  document.addEventListener("DOMContentLoaded", () => {
    if (!el("forgotPage")) return;
    const form = el("forgotForm");
    const err = el("forgotError");
    if (!form) return;
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (err) err.textContent = "";
      const email = el("email")?.value || "";
      const newPassword = el("password")?.value || "";
      const res = window.GlowCare.resetPassword({ email, newPassword });
      if (!res.ok) {
        if (err) err.textContent = res.message;
        window.GlowCare.toast(res.message);
        return;
      }
      window.GlowCare.toast("Password updated");
      window.location.href = "login.html";
    });
  });
})();

