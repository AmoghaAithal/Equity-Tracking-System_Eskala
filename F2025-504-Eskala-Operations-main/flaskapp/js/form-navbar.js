(function () {
  /* ---------- Config ---------- */
  const ROLE_KEY = "eskala_role"; // Persistent role key
  const LANG_KEY = "eskala_lang"; // Language preference key
  const DEFAULT_HOME = "/web/Dashboard.html"; // Fallback destination

  /* ---------- Role helpers ---------- */
  function normalizeRole(r) {
    if (!r) return "";
    const up = String(r).trim().toUpperCase();
    const map = {
      BANK_PARTNER: "PARTNER",
      PARTNERS: "PARTNER",
      PARTNER: "PARTNER",
      ADMIN: "STAFF",
      STAFF: "STAFF",
    };
    return map[up] || up;
  }

  function getRole() {
    // 1️⃣ Prefer ?role= from URL (persist for future)
    const qp = new URLSearchParams(location.search).get("role");
    if (qp) {
      const norm = normalizeRole(qp);
      try {
        localStorage.setItem(ROLE_KEY, norm);
      } catch {}
      return norm;
    }

    // 2️⃣ Try eskala_user JSON (if set by backend or login)
    try {
      const u = JSON.parse(localStorage.getItem("eskala_user") || "{}");
      if (u && u.role) return normalizeRole(u.role);
    } catch {}

    // 3️⃣ Fallback to stored role
    try {
      const stored = localStorage.getItem(ROLE_KEY);
      if (stored) return normalizeRole(stored);
    } catch {}

    return "";
  }

  function roleParamForDashboard(role) {
    role = String(role || "").toUpperCase();
    if (role === "PARTNER") return "Partner";
    if (role === "STAFF" || role === "ADMIN") return "Staff";
    return "Partner";
  }

  /* ---------- Redirect helper (used after login/signup) ---------- */
  function routeAfterLogin(type) {
    const t = String(type || "")
      .trim()
      .toLowerCase();

    // Map all possible synonyms clearly
    const roleParam =
      t === "staff" || t === "admin"
        ? "Staff"
        : t === "partner" || t === "partners" || t === "bank_partner"
        ? "Partner"
        : "Partner"; // default fallback

    const norm = roleParam.toUpperCase();
    try {
      localStorage.setItem("eskala_role", norm);
    } catch {}

    // Redirect to dashboard with ?role=Staff or ?role=Partner
    window.location.href = `/web/Dashboard.html
      roleParam
    )}`;
  }

  // Expose globally so login/signup can call it
  window.routeAfterLogin = routeAfterLogin;

  /* ---------- Language (same behavior as dashboard) ---------- */
  function setLangButtonLabel(lang) {
    const btn = document.querySelector('[data-menu="lang"]');
    if (btn) btn.innerHTML = (lang === "es" ? "Español" : "English") + " ▾";
  }

  function applyLanguage(lang) {
    try {
      localStorage.setItem(LANG_KEY, lang);
    } catch {}
    setLangButtonLabel(lang);
    if (typeof window.setLanguage === "function") {
      try {
        window.setLanguage(lang);
      } catch {}
    }
  }

  /* ---------- Dropdown menus (dashboard pattern) ---------- */
  function initMenus(navRoot) {
    const q = (sel, el = navRoot) => el.querySelector(sel);
    const qa = (sel, el = navRoot) => Array.from(el.querySelectorAll(sel));

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

    // Wire dropdown buttons
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

    // Outside click & ESC to close
    document.addEventListener("click", (e) => {
      if (!navRoot.contains(e.target)) closeAll();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeAll();
    });

    // Language boot + items
    const savedLang = (() => {
      try {
        return localStorage.getItem(LANG_KEY) || "en";
      } catch {
        return "en";
      }
    })();

    setLangButtonLabel(savedLang);
    if (typeof window.setLanguage === "function") {
      try {
        window.setLanguage(savedLang);
      } catch {}
    }

    const langBtn = q('[data-menu="lang"]');
    const langMenu = langBtn ? getMenu(langBtn) : null;

    if (langMenu) {
      langMenu.addEventListener("click", (e) => {
        const item = e.target.closest("[data-lang]");
        if (!item) return;
        e.preventDefault();
        applyLanguage(item.getAttribute("data-lang") || "en");
        closeAll();
      });
    }

    // Allow pages to broadcast language change events
    document.addEventListener("eskala:language", (evt) => {
      const lang = (evt.detail && evt.detail.lang) || "en";
      applyLanguage(lang);
    });
  }

  /* ---------- Home routing (brand + back button) ---------- */
  function setHomeHref() {
    const role = getRole();
    const pretty = roleParamForDashboard(role);
    const href = pretty
      ? `${DEFAULT_HOME}`
      : DEFAULT_HOME;

    const home = document.getElementById("esk-form-home");
    const brand = document.getElementById("esk-form-brand");
    if (home) home.setAttribute("href", href);
    if (brand) brand.setAttribute("href", href);
  }

  /* ---------- Completion progress (required fields only) ---------- */
  function updateCompletionBar() {
    const form = document.querySelector("form");
    const bar = document.getElementById("esk-form-progress-bar");
    if (!form || !bar) return;

    const req = Array.from(
      form.querySelectorAll("input, select, textarea")
    ).filter((el) => el.hasAttribute("required"));

    const total = req.length;
    let filled = 0;

    req.forEach((el) => {
      const t = (el.type || "").toLowerCase();
      let ok = false;
      if (t === "checkbox" || t === "radio") {
        const grp = form.querySelectorAll(
          `input[type="${t}"][name="${el.name}"]`
        );
        ok = Array.from(grp).some((n) => n.checked);
      } else if (t === "file") {
        ok = el.files && el.files.length > 0;
      } else {
        ok = el.value.trim() !== "";
      }
      if (ok) filled++;
    });

    const pct = total > 0 ? Math.round((filled / total) * 100) : 0;
    bar.style.width = pct + "%";
  }

  function watchFormProgress() {
    const form = document.querySelector("form");
    if (!form) return;
    updateCompletionBar();
    ["input", "change"].forEach((ev) =>
      form.addEventListener(ev, updateCompletionBar, true)
    );
  }

  /* ---------- Keep progress bar aligned with navbar ---------- */
  function updateNavOffsets() {
    const nav = document.querySelector(".esk-nav");
    if (!nav) return;
    const h = Math.ceil(nav.getBoundingClientRect().height);
    document.documentElement.style.setProperty("--esk-nav-h", h + "px");
    document.body.style.paddingTop = `calc(${h}px + 8px)`;
  }

  /* ---------- Boot ---------- */
  function boot() {
    setHomeHref();
    const nav = document.body.querySelector(".esk-nav");
    if (nav) initMenus(nav);
    watchFormProgress();
    updateNavOffsets();

    window.addEventListener("resize", updateNavOffsets, { passive: true });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(updateNavOffsets).catch(() => {});
    }
    setTimeout(updateNavOffsets, 0);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
