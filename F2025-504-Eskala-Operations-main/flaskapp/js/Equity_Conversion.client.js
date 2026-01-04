// Equity_Conversion.client.js
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

async function initConversionAutosave() {
  const userKey = await getCurrentUserKey();
  const storageKey = `autosave_equity-conversion:${userKey}`;

  new FormAutosave("conversion-form", {
    storageKey,
    excludeFields: ["supporting_file"],
    onRestore: () =>
      console.log("Conversion form draft restored for", userKey),
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("conversion-form");
  if (!form) return;

  const successBanner = document.getElementById("conversion-success");
  const declaration = document.getElementById("confirm-accurate"); // checkbox id
  const fileInput = document.getElementById("supporting-file"); // ✅ match HTML

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fd = new FormData();

    const bank_name = document.getElementById("bank-name")?.value?.trim();
    const rtn_number = document.getElementById("rtn-number")?.value?.trim();
    const representative_name =
      document.getElementById("representative-name")?.value?.trim();
    const phone_number =
      document.getElementById("phone-number")?.value?.trim();
    const loan_id = document.getElementById("loan-id")?.value?.trim();
    const original_loan_amount =
      document
        .getElementById("original-loan-amount")
        ?.value?.replace(/[^0-9.]/g, "") || "";
    const payoutDateRaw =
      document.getElementById("loan-approval-date")?.value?.trim() || "";
    const interest_paid =
      document
        .getElementById("interest-paid")
        ?.value?.replace(/[^0-9.]/g, "") || "";
    const loan_amount_remaining =
      document
        .getElementById("loan-amount-remaining")
        ?.value?.replace(/[^0-9.]/g, "") || "";
    const repayment_frequency =
      document.getElementById("repayment-frequency")?.value?.trim() || "";
    const proposed_conversion_amount =
      document
        .getElementById("proposed-conversion-amount")
        ?.value?.replace(/[^0-9.]/g, "") || "";
    const proposed_conversion_ratio =
      document.getElementById("proposed-conversion-ratio")?.value?.trim() ||
      "";
    const proposed_equity_percentage =
      document
        .getElementById("proposed-equity-percentage")
        ?.value?.replace(/[^0-9.]/g, "") || "";
    const desired_conversion_date =
      document.getElementById("desired-conversion-date")?.value?.trim() || "";
    const comments =
      document.getElementById("comments")?.value?.trim() || "";

    let loan_approval_date = payoutDateRaw;
    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(loan_approval_date)) {
      let [dd, mm, yyyy] = loan_approval_date.split("/");
      loan_approval_date = `${yyyy}-${String(mm).padStart(2, "0")}-${String(
        dd
      ).padStart(2, "0")}`;
    }

    fd.set("bank_name", bank_name || "");
    fd.set("rtn_number", rtn_number || "");
    fd.set("representative_name", representative_name || "");
    fd.set("phone_number", phone_number || "");
    fd.set("loan_id", loan_id || "");
    fd.set("original_loan_amount", original_loan_amount || "");
    fd.set("loan_approval_date", loan_approval_date || "");
    fd.set("interest_paid", interest_paid || "");
    fd.set("loan_amount_remaining", loan_amount_remaining || "");
    fd.set("repayment_frequency", repayment_frequency || "");
    fd.set("proposed_conversion_amount", proposed_conversion_amount || "");
    fd.set("proposed_conversion_ratio", proposed_conversion_ratio || "");
    fd.set("proposed_equity_percentage", proposed_equity_percentage || "");
    fd.set("desired_conversion_date", desired_conversion_date || "");
    fd.set("comments", comments);
    fd.set("confirmed", declaration ? String(!!declaration.checked) : "true");

    // ⬇️ again, match whatever your Flask route expects
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const f = fileInput.files[0];
      fd.set("attachment", f);
      fd.set("supporting_file", f);
      fd.set("payment_proof", f);
    }

    try {
      const res = await fetch(`${API_BASE}/api/equity/conversion`, {
        method: "POST",
        body: fd,
        credentials: "include",
      });
      const out = await res.json().catch(() => ({}));
      if (!res.ok || !out.ok)
        throw new Error(out.error || `HTTP ${res.status}`);

      if (successBanner) successBanner.classList.remove("hidden");

      const userKey = await getCurrentUserKey();
      localStorage.removeItem(`autosave_equity-conversion:${userKey}`);

      form.reset();
      if (successBanner)
        setTimeout(() => successBanner.classList.add("hidden"), 5000);
    } catch (err) {
      console.error("Conversion submit failed:", err);
      alert(err.message || "Failed to submit conversion request.");
    }
  });

  initConversionAutosave();
});
