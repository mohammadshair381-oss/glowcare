(() => {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contactForm");
    if (!form) return;
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      window.GlowCare.toast("Message sent (demo)");
      form.reset();
      window.GlowCare.track("contact_submit");
    });
  });
})();

