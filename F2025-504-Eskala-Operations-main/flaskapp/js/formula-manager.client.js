
// formula-manager.client.js - Manage calculation formulas with Formula Builder
(() => {
  // FIX CORS - Use current hostname for API calls
  const API_BASE = "";

  const formulasLoading = document.getElementById('formulas-loading');
  const formulasNoData = document.getElementById('formulas-no-data');
  const formulasTable = document.getElementById('formulas-table');
  const formulasTbody = document.getElementById('formulas-tbody');
  
  const historyLoading = document.getElementById('history-loading');
  const historyNoData = document.getElementById('history-no-data');
  const historyTable = document.getElementById('history-table');
  const historyTbody = document.getElementById('history-tbody');
  
  const editModal = document.getElementById('edit-modal');
  const editForm = document.getElementById('edit-formula-form');

  let allFormulas = [];
  let formulaComponents = [];

  // Variable descriptions - What each SQL field name means in plain English
  const VARIABLE_DESCRIPTIONS = {
    'profit_l': 'The actual profit amount earned by the company, measured in Honduran Lempiras (L)',
    'expected_profit_pct': 'The expected profit percentage - how much profit the company should make as a percentage',
    'company_value_l': 'The total estimated worth of the company in Honduran Lempiras (L)',
    'investment_l': 'The amount of money invested in the company, shown in Honduran Lempiras (L)',
    'exchange_rate': 'The conversion rate from Honduran Lempiras (L) to US Dollars ($)'
  };

  // Formula field descriptions for the edit modal - Clear, non-technical explanations
  const FORMULA_DESCRIPTIONS = {
    'investment_usd': 'Automatically converts the investment amount from Honduran Lempiras (L) to US Dollars ($) so you can see the value in a common currency. This makes it easier to compare investments and report to international partners.',
    'company_value_l': 'Calculates how much a partner company is worth in Honduran Lempiras based on their reported profits and expected growth rate. This valuation helps Eskala determine fair equity stakes and make informed investment decisions.',
    'investment_l': 'The total amount of money being invested into the partner company, shown in Honduran Lempiras (L). This is the base currency amount that gets converted to USD for international reporting.',
    'exchange_rate': 'The current exchange rate used to convert between Honduran Lempiras and US Dollars. This rate updates periodically to reflect the real market exchange rate, ensuring accurate financial calculations.',
    'equity_percentage': 'Shows what percentage of a company Eskala owns based on the investment amount compared to the total company value. For example, if Eskala invests $10,000 in a company worth $100,000, Eskala owns 10% of that company.',
    'company_value_usd': 'The company valuation converted to US Dollars, making it easier to compare different companies and report to stakeholders.',
    'profit_l': 'The actual profit earned by the partner company in Honduran Lempiras during a specific period.',
    'expected_profit_pct': 'The percentage of profit the company is expected to generate relative to their revenue or investment.',
    'matching_amount': 'Calculates how much money Eskala will contribute to match the partner\'s investment.',
    'total_investment': 'Shows the combined total of what the partner invested plus what Eskala matched.',
    'shares_owned': 'The number of ownership shares Eskala holds in the partner company.',
    'share_value': 'How much each individual share of the company is worth in dollars.'
  };

  const AVAILABLE_VARIABLES = [
    'profit_l',
    'expected_profit_pct',
    'company_value_l',
    'investment_l',
    'exchange_rate'
  ];

  const AVAILABLE_OPERATORS = ['+', '-', '*', '/', '(', ')'];

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  }

  // ============================================
  // GENERATE VARIABLE DESCRIPTION FROM FORMULA
  // ============================================
  function generateVariableDescription(expression) {
    // Extract all variables from the expression
    const variables = [];
    const tokens = expression.match(/([a-z_]+)/gi) || [];
    
    tokens.forEach(token => {
      if (AVAILABLE_VARIABLES.includes(token) && !variables.includes(token)) {
        variables.push(token);
      }
    });

    // Build description
    if (variables.length === 0) {
      return 'No variables used in this formula';
    }

    const descriptions = variables.map(v => {
      const desc = VARIABLE_DESCRIPTIONS[v] || v;
      return `<strong>${v}</strong> = ${desc}`;
    });

    return descriptions.join('<br>');
  }

  // ============================================
  // FORMULA PARSER
  // ============================================
  function parseFormula(expression) {
    const components = [];
    const tokens = expression.match(/([a-z_]+|\d+\.?\d*|[+\-*/()])/gi) || [];
    
    tokens.forEach(token => {
      if (AVAILABLE_VARIABLES.includes(token)) {
        components.push({ type: 'variable', value: token });
      } else if (AVAILABLE_OPERATORS.includes(token)) {
        components.push({ type: 'operator', value: token });
      } else if (!isNaN(parseFloat(token))) {
        components.push({ type: 'number', value: token });
      }
    });
    
    return components;
  }

  // ============================================
  // FORMULA BUILDER UI
  // ============================================
  function buildFormulaEditor(expression) {
    formulaComponents = parseFormula(expression);
    renderFormulaBuilder();
    updateFormulaPreview();
  }

  function renderFormulaBuilder() {
    const container = document.getElementById('formula-builder-container');
    container.innerHTML = '';

    formulaComponents.forEach((component, index) => {
      const componentDiv = document.createElement('div');
      componentDiv.className = 'formula-component';

      if (component.type === 'variable') {
        // Display variable as read-only (no dropdown to change it)
        const variableLabel = document.createElement('span');
        variableLabel.className = 'formula-variable-label';
        variableLabel.textContent = component.value;
        componentDiv.appendChild(variableLabel);
      } else if (component.type === 'operator') {
        const select = document.createElement('select');
        select.className = 'formula-select formula-select-operator';
        AVAILABLE_OPERATORS.forEach(op => {
          const option = document.createElement('option');
          option.value = op;
          option.textContent = op;
          option.selected = op === component.value;
          select.appendChild(option);
        });
        select.addEventListener('change', (e) => {
          formulaComponents[index].value = e.target.value;
          updateFormulaPreview();
        });
        componentDiv.appendChild(select);
      } else if (component.type === 'number') {
        const input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.className = 'formula-input';
        input.value = component.value;
        input.addEventListener('input', (e) => {
          formulaComponents[index].value = e.target.value;
          updateFormulaPreview();
        });
        componentDiv.appendChild(input);
      }

      container.appendChild(componentDiv);
    });
  }

  function updateFormulaPreview() {
    const preview = document.getElementById('formula-preview');
    const expression = formulaComponents.map(c => c.value).join(' ');
    preview.textContent = expression || '(empty formula)';
    
    // Update hidden field for form submission
    document.getElementById('edit-formula-expression').value = expression;
  }

  // ============================================
  // LOAD ACTIVE FORMULAS
  // ============================================
  async function loadFormulas() {
    try {
      formulasLoading.style.display = 'block';
      formulasNoData.style.display = 'none';
      formulasTable.style.display = 'none';

      const resp = await fetch(`${API_BASE}/api/equity/formulas`, {
        credentials: 'include'
      });
      const json = await resp.json();

      formulasLoading.style.display = 'none';

      if (!resp.ok || !json.ok) {
        formulasNoData.textContent = 'Error loading formulas';
        formulasNoData.style.display = 'block';
        return;
      }

      allFormulas = json.formulas || [];
      
      // 🔍 DEBUG - Check field names
      console.log('📊 All Formula Field Names:');
      allFormulas.forEach(f => {
        console.log(`  - field_name: "${f.field_name}", field_label: "${f.field_label}"`);
      });
      
      if (allFormulas.length === 0) {
        formulasNoData.textContent = 'No formulas found';
        formulasNoData.style.display = 'block';
        return;
      }

      // Populate table
      formulasTbody.innerHTML = '';
      allFormulas.forEach(formula => {
        const row = document.createElement('tr');
        
        const fieldName = escapeHtml(formula.field_name || '-');
        const fieldLabel = escapeHtml(formula.field_label || '-');
        const expression = escapeHtml(formula.expression || '-');
        
        // Generate description based on variables in the formula
        const description = generateVariableDescription(formula.expression);
        
        const formType = escapeHtml(formula.form_type || '-').toUpperCase();
        const lastUpdated = formatDate(formula.effective_from);
        const version = formula.version || 1;
        
        row.innerHTML = `
          <td>${fieldName}</td>
          <td><strong>${fieldLabel}</strong></td>
          <td><code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${expression}</code></td>
          <td style="font-size: 13px; line-height: 1.6;">${description}</td>
          <td><span style="background: #10B981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">${formType} v${version}</span></td>
          <td>${lastUpdated}</td>
          <td>
            <button class="action-btn edit-btn" data-key="${formula.formula_key}">
              Edit
            </button>
            <button class="action-btn" style="background: #3B82F6; color: white;" data-key="${formula.formula_key}">
              History
            </button>
          </td>
        `;
        formulasTbody.appendChild(row);
      });

      // Attach event listeners
      document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const key = btn.getAttribute('data-key');
          editFormula(key);
        });
      });

      document.querySelectorAll('[data-key]').forEach(btn => {
        if (btn.textContent.includes('History')) {
          btn.addEventListener('click', () => {
            const key = btn.getAttribute('data-key');
            viewHistory(key);
          });
        }
      });

      formulasTable.style.display = 'table';

    } catch (err) {
      console.error('Error loading formulas:', err);
      formulasLoading.style.display = 'none';
      formulasNoData.textContent = 'Network error loading formulas';
      formulasNoData.style.display = 'block';
    }
  }

  // ============================================
  // LOAD FORMULA HISTORY
  // ============================================
  async function loadHistory() {
    try {
      historyLoading.style.display = 'block';
      historyNoData.style.display = 'none';
      historyTable.style.display = 'none';

      const resp = await fetch(`${API_BASE}/api/equity/formulas/all-history`, {
        credentials: 'include'
      });
      const json = await resp.json();

      historyLoading.style.display = 'none';

      if (!resp.ok || !json.ok) {
        historyNoData.textContent = 'Error loading history';
        historyNoData.style.display = 'block';
        return;
      }

      const history = json.history || [];
      
      if (history.length === 0) {
        historyNoData.textContent = 'No formula changes yet';
        historyNoData.style.display = 'block';
        return;
      }

      // Populate history table
      historyTbody.innerHTML = '';
      history.forEach(item => {
        const row = document.createElement('tr');
        
        const fieldLabel = escapeHtml(item.field_label || item.field_name || '-');
        const oldExpr = escapeHtml(item.old_expression || '-');
        const newExpr = escapeHtml(item.new_expression || '-');
        const changedAt = formatDate(item.changed_at);
        const changedBy = escapeHtml(item.changed_by || 'System');
        const reason = escapeHtml(item.change_reason || item.reason || 'No reason provided');
        const versions = `v${item.old_version || '?'} → v${item.new_version || '?'}`;
        
        row.innerHTML = `
          <td><strong>${fieldLabel}</strong><br><small style="color: #6b7280;">${versions}</small></td>
          <td><code style="background: #FEF3C7; padding: 4px 8px; border-radius: 4px; font-size: 11px;">${oldExpr}</code></td>
          <td><code style="background: #D1FAE5; padding: 4px 8px; border-radius: 4px; font-size: 11px;">${newExpr}</code></td>
          <td>${changedBy}</td>
          <td>${changedAt}</td>
          <td>${reason}</td>
        `;
        historyTbody.appendChild(row);
      });

      historyTable.style.display = 'table';

    } catch (err) {
      console.error('Error loading history:', err);
      historyLoading.style.display = 'none';
      historyNoData.textContent = 'Network error loading history';
      historyNoData.style.display = 'block';
    }
  }

  // ============================================
  // EDIT FORMULA
  // ============================================
  function editFormula(formulaKey) {
    const formula = allFormulas.find(f => f.formula_key === formulaKey);
    
    if (!formula) {
      alert('Formula not found');
      return;
    }

    // Populate edit form
    document.getElementById('edit-formula-id').value = formula.formula_id;
    document.getElementById('edit-field-name').value = formulaKey;
    document.getElementById('edit-field-label').value = formula.field_label;
    document.getElementById('edit-formula-expression').value = formula.expression;
    
    // Get description
    let description = FORMULA_DESCRIPTIONS[formula.field_name];
    
    if (!description) {
      // If no specific description, just show what variables mean
      description = generateVariableDescription(formula.expression).replace(/<br>/g, '\n').replace(/<\/?strong>/g, '');
    }
    
    document.getElementById('edit-description').value = description;
    document.getElementById('edit-reason').value = '';

    // Build formula editor
    buildFormulaEditor(formula.expression);

    // Show modal
    editModal.classList.add('active');
  }

  // ============================================
  // VIEW SPECIFIC FORMULA HISTORY
  // ============================================
  async function viewHistory(formulaKey) {
    try {
      const resp = await fetch(`${API_BASE}/api/equity/formulas/history/${formulaKey}`, {
        credentials: 'include'
      });
      const json = await resp.json();

      if (!resp.ok || !json.ok) {
        alert('Error loading formula history');
        return;
      }

      const history = json.history || [];
      
      if (history.length === 0) {
        alert('No history found for this formula');
        return;
      }

      let message = `History for ${formulaKey}:\n\n`;
      history.forEach(item => {
        const date = formatDate(item.effective_from);
        const changedBy = item.changed_by || 'System';
        const reason = item.description || 'No reason provided';
        
        message += `Version ${item.version} (${date}):\n`;
        message += `Expression: ${item.expression}\n`;
        message += `Changed by: ${changedBy}\n`;
        message += `Reason: ${reason}\n`;
        message += '\n';
      });

      alert(message);

    } catch (err) {
      console.error('Error loading history:', err);
      alert('Network error loading history');
    }
  }

  // ============================================
  // SAVE FORMULA UPDATE
  // ============================================
  if (editForm) {
    editForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formulaKey = document.getElementById('edit-field-name').value;
      const expression = document.getElementById('edit-formula-expression').value.trim();
      const data = {
        expression: expression,
        description: document.getElementById('edit-description').value.trim(),
        reason: document.getElementById('edit-reason').value.trim()
      };

      if (!data.expression) {
        alert('Formula expression is required');
        return;
      }

      if (!data.reason) {
        alert('Reason for change is required');
        return;
      }

      try {
        const url = `${API_BASE}/api/equity/formulas/update/${formulaKey}`;
        const resp = await fetch(url, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(data)
        });
        const json = await resp.json();

        if (!resp.ok || !json.ok) {
          alert(`Update failed: ${json.error || 'Unknown error'}`);
        } else {
          alert(`Formula updated successfully!\nVersion ${json.old_version} → ${json.new_version}`);
          closeEditModal();
          loadFormulas();
          loadHistory();
        }
      } catch (err) {
        console.error('Error updating formula:', err);
        alert('Network error');
      }
    });
  }

  // ============================================
  // MODAL CONTROLS
  // ============================================
  function closeEditModal() {
    editModal.classList.remove('active');
    editForm.reset();
    formulaComponents = [];
  }

  const closeModalBtn = document.getElementById('close-modal');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeEditModal);
  }

  const cancelBtn = document.getElementById('cancel-edit');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeEditModal();
    });
  }

  if (editModal) {
    editModal.addEventListener('click', (e) => {
      if (e.target === editModal) {
        closeEditModal();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && editModal.classList.contains('active')) {
      closeEditModal();
    }
  });

  // ============================================
  // INITIALIZE
  // ============================================
  loadFormulas();
  loadHistory();

})();