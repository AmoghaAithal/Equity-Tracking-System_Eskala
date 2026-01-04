// matching-equity.client.js - Handle matching form submission with dynamic formulas and exchange rates

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

async function initMatchingAutosave() {
  const userKey = await getCurrentUserKey();
  const storageKey = `autosave_matching-equity:${userKey}`; // form + user

  new FormAutosave("matching-form", {
    storageKey, // ✅ per-user
    excludeFields: [],
    onRestore: () =>
      console.log("Matching equity form draft restored for", userKey),
  });
}

(() => {
  const form = document.getElementById("matching-form");
  const submitButton = document.getElementById("submit-button");

  // Get form fields
  const reportedSharesField = document.getElementById("reported-shares");
  const invLField = document.getElementById("inv-l");
  const invUsdField = document.getElementById("inv-usd");
  const fxField = document.getElementById("fx");

  // Store formulas fetched from backend
  let activeFormulas = {};

  // ============================================
  // LOAD EXCHANGE RATE FROM API
  // ============================================
  async function loadExchangeRate() {
    try {
      console.log("Loading current exchange rate...");

      const response = await fetch(`${API_BASE}/api/fx-rates/current`, {
        credentials: "include",
      });
      const result = await response.json();

      if (response.ok && result.success && result.rate) {
        const rate = parseFloat(result.rate.rate);
        console.log("✅ Exchange rate loaded:", rate);

        if (fxField) {
          fxField.value = rate.toFixed(4);
          fxField.style.backgroundColor = "#f0fdf4";
          fxField.style.fontWeight = "600";
        }

        calculateFields();
      } else {
        console.warn("⚠️ Could not load exchange rate, using default");
      }
    } catch (error) {
      console.error("❌ Error loading exchange rate:", error);
    }
  }

  // ============================================
  // LOAD FORMULAS FROM BACKEND
  // ============================================
  async function loadFormulas() {
    try {
      const response = await fetch(
        `${API_BASE}/api/equity/formulas/for-form/matching`,
        {
          credentials: "include",
        }
      );
      const result = await response.json();

      if (response.ok && result.ok) {
        activeFormulas = result.formulas;
        console.log("✅ Matching formulas loaded:", activeFormulas);

        calculateFields();
      } else {
        console.error("Failed to load formulas:", result.error);
      }
    } catch (error) {
      console.error("Error loading formulas:", error);
    }
  }

  // ============================================
  // EVALUATE FORMULA EXPRESSION
  // ============================================
  function evaluateFormula(expression, values) {
    try {
      let evalExpression = expression;
      for (const [key, value] of Object.entries(values)) {
        const regex = new RegExp(`\\b${key}\\b`, "g");
        evalExpression = evalExpression.replace(regex, value || 0);
      }

      const result = Function('"use strict"; return (' + evalExpression + ")")();

      if (isNaN(result) || !isFinite(result)) {
        return null;
      }

      return result;
    } catch (error) {
      console.error("Formula evaluation error:", error);
      return null;
    }
  }

  // ============================================
  // CALCULATE ALL AUTO-CALCULATED FIELDS
  // ============================================
  function calculateFields() {
    const values = {
      reported_shares: parseFloat(reportedSharesField?.value) || 0,
      investment_l: parseFloat(invLField?.value) || 0,
      exchange_rate: parseFloat(fxField?.value) || 0,
    };

    if (activeFormulas.investment_usd) {
      const investmentUsd = evaluateFormula(
        activeFormulas.investment_usd.expression,
        values
      );
      if (investmentUsd !== null && investmentUsd > 0) {
        invUsdField.value = investmentUsd.toFixed(2);
      } else {
        invUsdField.value = "";
      }
    }
  }

  // ============================================
  // ATTACH EVENT LISTENERS
  // ============================================
  if (reportedSharesField)
    reportedSharesField.addEventListener("input", calculateFields);
  if (invLField) invLField.addEventListener("input", calculateFields);
  if (fxField) fxField.addEventListener("input", calculateFields);

  // ============================================
  // FORM SUBMISSION
  // ============================================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData();

      const fileInput = document.getElementById("supporting-file");
      if (fileInput && fileInput.files.length > 0) {
        formData.append("supporting_file", fileInput.files[0]);
      }

      formData.append(
        "partner_name",
        document.getElementById("partner-name")?.value?.trim() || ""
      );
      formData.append("year", document.getElementById("year")?.value || "");
      formData.append(
        "technician",
        document.getElementById("technician")?.value?.trim() || ""
      );
      formData.append(
        "reported_shares",
        document.getElementById("reported-shares")?.value || ""
      );
      formData.append(
        "share_capital_multiplied",
        document.getElementById("share-capital")?.value || ""
      );
      formData.append(
        "expected_profit_pct",
        document.getElementById("expected-pct")?.value || ""
      );
      formData.append("investment_l", invLField?.value || "");
      formData.append("investment_usd", invUsdField?.value || "");
      formData.append("exchange_rate", fxField?.value || "");
      formData.append(
        "proposal_state",
        document.getElementById("proposal")?.value || ""
      );
      formData.append(
        "transaction_type",
        document.getElementById("transaction")?.value || ""
      );

      // Monthly distributions
      formData.append(
        "january_l",
        document.getElementById("january")?.value || "0"
      );
      formData.append(
        "february_l",
        document.getElementById("february")?.value || "0"
      );
      formData.append(
        "march_l",
        document.getElementById("march")?.value || "0"
      );
      formData.append(
        "april_l",
        document.getElementById("april")?.value || "0"
      );
      formData.append("may_l", document.getElementById("may")?.value || "0");
      formData.append("june_l", document.getElementById("june")?.value || "0");
      formData.append("july_l", document.getElementById("july")?.value || "0");
      formData.append(
        "august_l",
        document.getElementById("august")?.value || "0"
      );
      formData.append(
        "september_l",
        document.getElementById("september")?.value || "0"
      );
      formData.append(
        "october_l",
        document.getElementById("october")?.value || "0"
      );
      formData.append(
        "november_l",
        document.getElementById("november")?.value || "0"
      );
      formData.append(
        "december_l",
        document.getElementById("december")?.value || "0"
      );

      formData.append(
        "business_category",
        document.getElementById("bizcat")?.value?.trim() || ""
      );
      formData.append(
        "company_type",
        document.getElementById("company-type")?.value?.trim() || ""
      );
      formData.append(
        "community",
        document.getElementById("community")?.value?.trim() || ""
      );
      formData.append(
        "municipality",
        document.getElementById("municipality")?.value?.trim() || ""
      );
      formData.append(
        "state",
        document.getElementById("state")?.value?.trim() || ""
      );
      formData.append(
        "comments",
        document.getElementById("comments")?.value?.trim() || ""
      );
      formData.append("start_date", new Date().toISOString().split("T")[0]);

      const partnerName = formData.get("partner_name");
      const year = formData.get("year");
      const expectedPct = formData.get("expected_profit_pct");

      if (!partnerName) {
        alert(
          window.currentLang === "es"
            ? "Por favor ingrese el nombre del socio"
            : "Please enter partner name"
        );
        return;
      }

      if (!year) {
        alert(
          window.currentLang === "es"
            ? "Por favor ingrese el año"
            : "Please enter year"
        );
        return;
      }

      if (!expectedPct) {
        alert(
          window.currentLang === "es"
            ? "Por favor ingrese el porcentaje de ganancia esperado"
            : "Please enter expected profit percentage"
        );
        return;
      }

      console.log("Submitting matching form data...");

      if (submitButton) {
        submitButton.disabled = true;
        const btnText = submitButton.querySelector("span");
        if (btnText) {
          btnText.textContent =
            window.currentLang === "es" ? "Guardando..." : "Saving...";
        }
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/equity/matching/manual-entry`,
          {
            method: "POST",
            credentials: "include",
            body: formData,
          }
        );

        const result = await response.json();

        if (response.ok && result.ok) {
          alert(
            window.currentLang === "es"
              ? "¡Entrada guardada exitosamente!"
              : "Entry saved successfully!"
          );
          form.reset();

          const monthFields = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
          ];
          monthFields.forEach((month) => {
            const field = document.getElementById(month);
            if (field) field.value = "0";
          });

          invUsdField.value = "";

          loadExchangeRate();
        } else {
          alert(
            window.currentLang === "es"
              ? `Error: ${result.error || "Error desconocido"}`
              : `Error: ${result.error || "Unknown error"}`
          );
        }
      } catch (error) {
        console.error("Submission error:", error);
        alert(
          window.currentLang === "es"
            ? "Error de red. Por favor intente de nuevo."
            : "Network error. Please try again."
        );
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          const btnText = submitButton.querySelector("span");
          if (btnText) {
            btnText.textContent =
              window.currentLang === "es"
                ? "Guardar Detalles de Emparejamiento"
                : "Save Matching Details";
          }
        }
      }
    });
  }

  // INITIALIZE - LOAD FORMULAS AND EXCHANGE RATE
  loadFormulas();
  loadExchangeRate();

  // ✅ Initialize per-user autosave
  initMatchingAutosave();
})();
