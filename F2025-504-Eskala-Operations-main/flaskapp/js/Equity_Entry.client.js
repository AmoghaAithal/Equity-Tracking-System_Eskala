// Equity_Entry.client.js
// Updated to work with Flask backend on port 5000
const API_BASE = "";

// --- helpers for user-specific autosave --- //
async function getCurrentUserKey() {
  try {
    const res = await fetch(`${API_BASE}/api/auth/check-session`, {
      credentials: "include",
    });
    const data = await res.json();

    if (data && data.email) return data.email.toLowerCase();
    if (data && data.username) return data.username.toLowerCase();
    if (data && data.user_id) return String(data.user_id);
  } catch (err) {
    console.warn("Could not load user for autosave key", err);
  }
  return "anonymous";
}

async function initEquityEntryAutosave() {
  const userKey = await getCurrentUserKey();
  const storageKey = `autosave_equity-entry:${userKey}`;

  new FormAutosave("equity-form", {
    storageKey,
    excludeFields: ["supporting_file"], // don’t try to autosave the file field
    onRestore: () =>
      console.log("Equity entry form draft restored for", userKey),
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("equity-form");
  if (!form) return;

  const success = document.getElementById("success-message");

  // ⬇️ this MUST match your HTML
  const fileInput = document.getElementById("supporting-file");
  const confirmBox = document.getElementById("confirm-accurate");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fd = new FormData();

    const bank_id = document.getElementById("bank-id")?.value?.trim();
    const partner_name = document.getElementById("partner-name")?.value?.trim();
    const shares = document.getElementById("shares")?.value?.trim();

    const investment_hnl =
      (document.getElementById("investment-hnl")?.value || "").replace(
        /[^0-9.]/g,
        ""
      );
    const investment_usd =
      (document.getElementById("investment-usd")?.value || "").replace(
        /[^0-9.]/g,
        ""
      );

    let payout_date =
      document.getElementById("payout-date")?.value?.trim() || "";
    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(payout_date)) {
      let [dd, mm, yyyy] = payout_date.split("/");
      payout_date = `${yyyy}-${String(mm).padStart(2, "0")}-${String(
        dd
      ).padStart(2, "0")}`;
    }

    const amount_paid =
      document.getElementById("amount-paid")?.value?.trim() || "";
    const payment_method =
      document.getElementById("payment-method")?.value?.trim() || "";
    const comments =
      document.getElementById("comments")?.value?.trim() || "";

    fd.set("bank_id", bank_id || "");
    fd.set("partner_name", partner_name || "");
    fd.set("shares", shares || "");
    fd.set("investment_hnl", investment_hnl || "");
    fd.set("investment_usd", investment_usd || "");
    fd.set("payout_date", payout_date || "");
    fd.set("amount_paid", amount_paid || "");
    fd.set("payment_method", payment_method || "");
    fd.set("comments", comments);
    fd.set("confirmed", confirmBox ? String(!!confirmBox.checked) : "true");

    // ⬇️ BACKEND FIELD NAME – adjust if your Flask route expects something else
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const f = fileInput.files[0];
      fd.set("supporting_file", f);  // matches HTML name
      fd.set("payment_proof", f);    // backwards-compat with old backend
      fd.set("attachment", f);       // if API expects "attachment"
    }

    try {
      const res = await fetch(`${API_BASE}/api/equity/entry`, {
        method: "POST",
        body: fd,
        credentials: "include",
      });

      const out = await res.json().catch(() => ({}));
      if (!res.ok || !out.ok)
        throw new Error(out.error || `HTTP ${res.status}`);

      if (success) success.style.display = "block";

      // clear this user’s draft on success
      const userKey = await getCurrentUserKey();
      localStorage.removeItem(`autosave_equity-entry:${userKey}`);

      form.reset();
      setTimeout(() => {
        if (success) success.style.display = "none";
      }, 5000);
    } catch (err) {
      console.error("Dividend entry failed:", err);
      alert(err.message || "Failed to submit dividend entry.");
    }
  });

  // per-user autosave
  initEquityEntryAutosave();
});
