// profit_form.client.js - Handle form submission and calculations with exchange rates

const API_BASE = "";

// ---- helpers for user-specific autosave ----
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

async function initProfitAutosave() {
  const userKey = await getCurrentUserKey();
  const storageKey = `autosave_profit-form:${userKey}`; // form + user

  new FormAutosave("profit-form", {
    storageKey, // ✅ per-user drafts
    excludeFields: [],
    onRestore: () => console.log("Profit form draft restored for", userKey),
  });
}

(() => {
  const form = document.getElementById("profit-form");
  const submitButton = document.getElementById("submit-button");

  // Get form fields
  const profitField = document.getElementById("profit-l");
  const expectedPctField = document.getElementById("expected-pct");
  const companyValueField = document.getElementById("company-value");
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
        `${API_BASE}/api/equity/formulas/for-form/profit`,
        {
          credentials: "include",
        }
      );
      const result = await response.json();

      if (response.ok && result.ok) {
        activeFormulas = result.formulas;
        console.log("✅ Formulas loaded:", activeFormulas);

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
      profit_l: parseFloat(profitField?.value) || 0,
      expected_profit_pct: parseFloat(expectedPctField?.value) || 0,
      company_value_l: 0,
      investment_l: 0,
      exchange_rate: parseFloat(fxField?.value) || 0,
    };

    // Company Value (L)
    if (activeFormulas.company_value_l) {
      const companyValue = evaluateFormula(
        activeFormulas.company_value_l.expression,
        values
      );
      if (companyValue !== null && companyValue > 0) {
        companyValueField.value = companyValue.toFixed(2);
        values.company_value_l = companyValue;
      } else {
        companyValueField.value = "";
      }
    }

    // Investment (L)
    if (activeFormulas.investment_l) {
      const investmentL = evaluateFormula(
        activeFormulas.investment_l.expression,
        values
      );
      if (investmentL !== null && investmentL > 0) {
        invLField.value = investmentL.toFixed(2);
        values.investment_l = investmentL;
      } else {
        invLField.value = "";
      }
    }

    // Investment (USD)
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
  if (profitField) profitField.addEventListener("input", calculateFields);
  if (expectedPctField)
    expectedPctField.addEventListener("input", calculateFields);
  if (fxField) fxField.addEventListener("input", calculateFields);

  // ============================================
  // FORM SUBMISSION
  // ============================================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = {
        bank_id: document.getElementById("bank-id")?.value?.trim() || null,
        partner_name:
          document.getElementById("partner-name")?.value?.trim() || "",
        year: parseInt(document.getElementById("year")?.value) || null,
        technician:
          document.getElementById("technician")?.value?.trim() || null,
        comments:
          document.getElementById("comments")?.value?.trim() || null,
        profit_l: parseFloat(document.getElementById("profit-l")?.value) || null,
        expected_profit_pct:
          parseFloat(document.getElementById("expected-pct")?.value) || null,
        company_value_l:
          parseFloat(document.getElementById("company-value")?.value) || null,
        investment_l:
          parseFloat(document.getElementById("inv-l")?.value) || null,
        investment_usd:
          parseFloat(document.getElementById("inv-usd")?.value) || null,
        exchange_rate:
          parseFloat(document.getElementById("fx")?.value) || null,
        proposal_state: document.getElementById("proposal")?.value || null,
        transaction_type:
          document.getElementById("transaction")?.value || null,
        business_category:
          document.getElementById("bizcat")?.value?.trim() || null,
        company_type:
          document.getElementById("company-type")?.value?.trim() || null,
        community:
          document.getElementById("community")?.value?.trim() || null,
        municipality:
          document.getElementById("municipality")?.value?.trim() || null,
        state: document.getElementById("state")?.value?.trim() || null,
        january_l: parseFloat(document.getElementById("january")?.value) || 0,
        february_l: parseFloat(document.getElementById("february")?.value) || 0,
        march_l: parseFloat(document.getElementById("march")?.value) || 0,
        april_l: parseFloat(document.getElementById("april")?.value) || 0,
        may_l: parseFloat(document.getElementById("may")?.value) || 0,
        june_l: parseFloat(document.getElementById("june")?.value) || 0,
        july_l: parseFloat(document.getElementById("july")?.value) || 0,
        august_l: parseFloat(document.getElementById("august")?.value) || 0,
        september_l:
          parseFloat(document.getElementById("september")?.value) || 0,
        october_l: parseFloat(document.getElementById("october")?.value) || 0,
        november_l:
          parseFloat(document.getElementById("november")?.value) || 0,
        december_l:
          parseFloat(document.getElementById("december")?.value) || 0,
        start_date: new Date().toISOString().split("T")[0],
      };

      if (!formData.partner_name) {
        alert(
          window.currentLang === "es"
            ? "Por favor ingrese el nombre del socio"
            : "Please enter partner name"
        );
        return;
      }

      console.log("Submitting form data:", formData);

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
          `${API_BASE}/api/equity/profit/entry`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify(formData),
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

          companyValueField.value = "";
          invLField.value = "";
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
                ? "Guardar Detalles del Prospecto"
                : "Save Prospect Details";
          }
        }
      }
    });
  }

  // INITIALIZE
  loadFormulas();
  loadExchangeRate();
  initProfitAutosave(); // ✅ per-user autosave
})();
