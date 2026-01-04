
// navbar.js
(function () {
  const NAV_HOST_ID = "navbar";

  // Initialize once the navbar HTML is present
  function initWhenReady() {
    const host = document.getElementById(NAV_HOST_ID);
    if (!host) return;

    if (host.children.length) {
      initNav(host);
      return;
    }
    // If injected after load, observe and init once children arrive
    const mo = new MutationObserver(() => {
      if (host.children.length) {
        mo.disconnect();
        initNav(host);
      }
    });
    mo.observe(host, { childList: true });
  }

  function initNav(host) {
    // Shortcuts
    const q = (sel, el = host) => el.querySelector(sel);
    const qa = (sel, el = host) => Array.from(el.querySelectorAll(sel));

    // Hide home button if on Dashboard page
    const currentPage = window.location.pathname.split('/').pop().toLowerCase();
    const homeBtn = q('#esk-form-home');
    if (homeBtn && (currentPage === 'dashboard.html' || currentPage === 'dashboard' || currentPage === '')) {
      homeBtn.style.display = 'none';
    }

    function getMenu(btn) {
      const id = btn.getAttribute("aria-controls");
      return id ? q("#" + id) : null;
    }

    function closeAll(exceptId) {
      qa("[data-menu]").forEach((btn) => {
        const menu = getMenu(btn);
        if (!menu) return;
        const keep = exceptId && menu.id === exceptId;
        btn.setAttribute("aria-expanded", keep ? "true" : "false");
        menu.hidden = !keep;
      });
    }

    // Wire dropdowns
    qa("[data-menu]").forEach((btn) => {
      const menu = getMenu(btn);
      if (!menu) return;
      btn.setAttribute("aria-expanded", "false");
      menu.hidden = true;

      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const isOpen = btn.getAttribute("aria-expanded") === "true";
        closeAll();
        btn.setAttribute("aria-expanded", isOpen ? "false" : "true");
        menu.hidden = isOpen;
      });
    });

    // Close on outside click / ESC
    document.addEventListener("click", (e) => {
      if (!host.contains(e.target)) closeAll();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeAll();
    });

    // ----- Language -----
    const langBtn = q('[data-menu="lang"]');
    const langMenu = langBtn ? getMenu(langBtn) : null;

    function setLangButtonLabel(lang) {
      if (!langBtn) return;
      langBtn.innerHTML = (lang === "es" ? "Español" : "English") + " ▾";
    }

    function applyLanguage(lang) {
      localStorage.setItem("eskala_lang", lang);
      setLangButtonLabel(lang);

      // Call page-level language change (if defined)
      if (typeof window.setLanguage === "function") {
        try {
          window.setLanguage(lang);
        } catch {}
      }

      // ---- Logout text translation ----
      const logoutBtn = host.querySelector('[data-action="logout"]');
      if (logoutBtn) {
        const text = logoutBtn.getAttribute("data-" + lang);
        if (text) logoutBtn.textContent = text;
      }
    }

    // Use saved language on load
    const savedLang = localStorage.getItem("eskala_lang") || "en";
    setLangButtonLabel(savedLang);
    // Ask page to render that language (dashboard exposes setLanguage)
    if (typeof window.setLanguage === "function") {
      try {
        window.setLanguage(savedLang);
      } catch {}
    }

    if (langMenu) {
      langMenu.addEventListener("click", (e) => {
        const item = e.target.closest("[data-lang]");
        if (!item) return;
        e.preventDefault();
        applyLanguage(item.getAttribute("data-lang") || "en");
        closeAll();
      });
    }

    // Page can tell navbar language changed
    document.addEventListener("eskala:language", (evt) => {
      const lang = (evt.detail && evt.detail.lang) || "en";
      applyLanguage(lang);
    });

    // ----- Logout -----
    host.addEventListener("click", (e) => {
      const item = e.target.closest('[data-action="logout"]');
      if (!item) return;
      e.preventDefault();
      try {
        localStorage.removeItem("eskala_user");
      } catch {}
      window.location.href = "/web/Landing.html"; // adjust if needed
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWhenReady);
  } else {
    initWhenReady();
  }
})();