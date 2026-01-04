
// profit_form.client.js - Handle form submission and calculations
(() => {
  const API_BASE = "";//

  const form = document.getElementById('profit-form');
  const submitButton = document.getElementById('submit-button');

  // Get form fields
  const profitField = document.getElementById('profit-l');
  const expectedPctField = document.getElementById('expected-pct');
  const companyValueField = document.getElementById('company-value');
  const invLField = document.getElementById('inv-l');
  const invUsdField = document.getElementById('inv-usd');
  const fxField = document.getElementById('fx');

  // Auto-calculate company value when profit or expected % changes
  function calculateCompanyValue() {
    const profit = parseFloat(profitField.value) || 0;
    const expectedPct = parseFloat(expectedPctField.value) || 0;

    if (profit > 0 && expectedPct > 0) {
      const companyValue = profit / (expectedPct / 100);
      companyValueField.value = companyValue.toFixed(2);
      calculateInvestments(companyValue);
    } else {
      companyValueField.value = '';
      invLField.value = '';
      invUsdField.value = '';
    }
  }

  // Calculate investment amounts
  function calculateInvestments(companyValue) {
    const expectedPct = parseFloat(expectedPctField.value) || 0;
    const fx = parseFloat(fxField.value) || 0;

    if (companyValue > 0 && expectedPct > 0) {
      const investmentL = companyValue * (expectedPct / 100);
      invLField.value = investmentL.toFixed(2);

      if (fx > 0) {
        const investmentUsd = investmentL / fx;
        invUsdField.value = investmentUsd.toFixed(2);
      }
    }
  }

  // Recalculate USD when exchange rate changes
  function recalculateUsd() {
    const investmentL = parseFloat(invLField.value) || 0;
    const fx = parseFloat(fxField.value) || 0;

    if (investmentL > 0 && fx > 0) {
      const investmentUsd = investmentL / fx;
      invUsdField.value = investmentUsd.toFixed(2);
    }
  }

  // Attach event listeners
  if (profitField) profitField.addEventListener('input', calculateCompanyValue);
  if (expectedPctField) expectedPctField.addEventListener('input', calculateCompanyValue);
  if (fxField) fxField.addEventListener('input', recalculateUsd);

  // Form submission
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = {
        bank_id: document.getElementById('bank-id')?.value?.trim() || null,
        partner_name: document.getElementById('partner-name')?.value?.trim() || '',
        year: parseInt(document.getElementById('year')?.value) || null,
        technician: document.getElementById('technician')?.value?.trim() || null,
        comments: document.getElementById('comments')?.value?.trim() || null,
        profit_l: parseFloat(document.getElementById('profit-l')?.value) || null,
        expected_profit_pct: parseFloat(document.getElementById('expected-pct')?.value) || null,
        company_value_l: parseFloat(document.getElementById('company-value')?.value) || null,
        investment_l: parseFloat(document.getElementById('inv-l')?.value) || null,
        investment_usd: parseFloat(document.getElementById('inv-usd')?.value) || null,
        exchange_rate: parseFloat(document.getElementById('fx')?.value) || null,
        proposal_state: document.getElementById('proposal')?.value || null,
        transaction_type: document.getElementById('transaction')?.value || null,
        business_category: document.getElementById('bizcat')?.value?.trim() || null,
        company_type: document.getElementById('company-type')?.value?.trim() || null,
        community: document.getElementById('community')?.value?.trim() || null,
        municipality: document.getElementById('municipality')?.value?.trim() || null,
        state: document.getElementById('state')?.value?.trim() || null,
        // Monthly distributions
        january_l: parseFloat(document.getElementById('january')?.value) || 0,
        february_l: parseFloat(document.getElementById('february')?.value) || 0,
        march_l: parseFloat(document.getElementById('march')?.value) || 0,
        april_l: parseFloat(document.getElementById('april')?.value) || 0,
        may_l: parseFloat(document.getElementById('may')?.value) || 0,
        june_l: parseFloat(document.getElementById('june')?.value) || 0,
        july_l: parseFloat(document.getElementById('july')?.value) || 0,
        august_l: parseFloat(document.getElementById('august')?.value) || 0,
        september_l: parseFloat(document.getElementById('september')?.value) || 0,
        october_l: parseFloat(document.getElementById('october')?.value) || 0,
        november_l: parseFloat(document.getElementById('november')?.value) || 0,
        december_l: parseFloat(document.getElementById('december')?.value) || 0,
        start_date: new Date().toISOString().split('T')[0]
      };

      // Validation
      if (!formData.partner_name) {
        alert(window.currentLang === 'es' 
          ? 'Por favor ingrese el nombre del socio' 
          : 'Please enter partner name');
        return;
      }

      console.log('Submitting form data:', formData);

      // Disable button
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = window.currentLang === 'es' ? 'Guardando...' : 'Saving...';
      }

      try {
        const response = await fetch(`${API_BASE}/api/equity/profit/entry`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok && result.ok) {
          alert(window.currentLang === 'es' 
            ? '¡Entrada guardada exitosamente!' 
            : 'Entry saved successfully!');
          form.reset();
          // Reset monthly fields to 0
          const monthFields = ['january', 'february', 'march', 'april', 'may', 'june', 
                               'july', 'august', 'september', 'october', 'november', 'december'];
          monthFields.forEach(month => {
            const field = document.getElementById(month);
            if (field) field.value = '0';
          });
        } else {
          alert(window.currentLang === 'es' 
            ? `Error: ${result.error || 'Error desconocido'}` 
            : `Error: ${result.error || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('Submission error:', error);
        alert(window.currentLang === 'es' 
          ? 'Error de red. Por favor intente de nuevo.' 
          : 'Network error. Please try again.');
      } finally {
        // Re-enable button
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.querySelector('span').textContent = window.currentLang === 'es' 
            ? 'Guardar Detalles del Prospecto' 
            : 'Save Prospect Details';
        }
      }
    });
  }
})();
// Initialize autosave
const profitFormAutosave = new FormAutosave('profit-form', {
  excludeFields: [], // Add field names to exclude if needed
  onRestore: () => console.log('Profit form draft restored'),
  onClear: () => console.log('Profit form draft cleared')
});

// Clear draft on successful submission
// Add this to your existing submit handler
document.getElementById('profit-form')?.addEventListener('submit', async (e) => {
  // After successful submission in your existing code, add:
  // profitFormAutosave.clearOnSuccess();
});
