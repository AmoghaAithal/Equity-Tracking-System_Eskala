
// web/js/signup.client.js
// Front-end handler for signup.html (works for Staff + Partner/Community Rep)

(function () {
  // Small helpers using your existing api.js
  const $ = (sel) => document.querySelector(sel);
  const text = (el, msg) => { if (el) el.textContent = msg; };

  // ---- role detection -------------------------------------------------------
  function resolveRoleFromQuery() {
    const params = new URLSearchParams(location.search);
    const raw = (params.get("role") || "").toLowerCase();
    // map UI query to backend enum
    if (raw === "staff") return { ui: "Eskala Staff", api: "STAFF" };
    return { ui: "Bank Partner", api: "COMMUNITY_REP" }; // default Partner
  }

  // ---- username helper ------------------------------------------------------
  function makeUsername(email) {
    // email local-part, keep alnum/._-, lowercased, max 30 chars
    const local = (email.split("@")[0] || "").toLowerCase();
    const cleaned = local.replace(/[^a-z0-9._-]/g, "");
    return cleaned.slice(0, 30) || "user" + Date.now();
  }

  // ---- form validation ------------------------------------------------------
  function validateForm({ roleApi, emailEl, pw1El, pw2El, rtnEl }) {
    const email = (emailEl.value || "").trim().toLowerCase();
    const pw1 = pw1El.value || "";
    const pw2 = pw2El.value || "";

    if (!email || !/.+@.+\..+/.test(email)) {
      throw new Error("Please enter a valid email.");
    }
    if (pw1.length < 8) {
      throw new Error("Password must be at least 8 characters.");
    }
    if (pw1 !== pw2) {
      throw new Error("Passwords do not match.");
    }
    if (roleApi === "COMMUNITY_REP") {
      const rtn = (rtnEl?.value || "").trim();
      if (!rtn) throw new Error("Please enter the partner RTN number.");
      if (!/^\d{5,}$/.test(rtn)) throw new Error("RTN must be numeric.");
    }
  }

  // ---- build backend payload -----------------------------------------------
  function buildPayload(roleApi, els) {
    const email = (els.email.value || "").trim().toLowerCase();
    const username = makeUsername(email); // Auto-generate from email

    const profile = {
      first_name: (els.first_name.value || "").trim() || null,
      last_name:  (els.last_name.value  || "").trim() || null,
      title:      (els.title.value      || "").trim() || null,
      bank_name:  roleApi === "COMMUNITY_REP" ? (els.bank_name?.value || "").trim() || null : null,
      rtn_number: roleApi === "COMMUNITY_REP" ? (els.rtn_number?.value || "").trim() || null : null,
    };

    return {
      email,
      username,
      password: els.password.value,
      account_type: roleApi, // "STAFF" | "COMMUNITY_REP"
      profile
    };
  }

  // ---- UI wiring ------------------------------------------------------------
  function init() {
    const role = resolveRoleFromQuery();
    const statusEl = $("#status");
    const roleBadge = $("#role-badge");
    if (roleBadge) text(roleBadge, role.ui);

    // Grab all inputs
    const els = {
      email:      $("#email"),
      password:   $("#password"),
      password2:  $("#password2"),
      first_name: $("#first_name"),
      last_name:  $("#last_name"),
      title:      $("#title"),
      // partner-only (may be absent for staff view)
      bank_name:  $("#bank_name"),
      rtn_number: $("#rtn_number"),
      submitBtn:  $("#create-btn"),
      form:       $("#signup-form")
    };

    // prevent native submit reload just in case
    els.form?.addEventListener("submit", (e) => e.preventDefault());

    // partner-only section visibility (if your HTML has #partner-fields)
    const partnerFields = $("#partner-fields");
    if (partnerFields) {
      partnerFields.style.display = role.api === "COMMUNITY_REP" ? "grid" : "none";
    }

    els.submitBtn?.addEventListener("click", async (e) => {
      e.preventDefault();
      try {
        text(statusEl, "Creating account…");
        validateForm({
          roleApi: role.api,
          emailEl: els.email,
          pw1El: els.password,
          pw2El: els.password2,
          rtnEl: els.rtn_number
        });

        const payload = buildPayload(role.api, els);
        const res = await api.postJSON("/api/auth/signup", payload);

        if (!res || res.ok !== true) {
          throw new Error(res?.error || "Sign-up failed.");
        }

        text(statusEl, "Account created! Redirecting…");
        // Send to the correct login page
        const next = role.api === "STAFF" ? "/staff-login.html" : "/partner-login.html";
        setTimeout(() => (window.location.href = next), 600);
      } catch (err) {
        console.error(err);
        text(statusEl, err.message || "There was a problem creating your account.");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();