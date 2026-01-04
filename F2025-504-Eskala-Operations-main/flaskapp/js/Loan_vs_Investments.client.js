// Loan_vs_Investments.client.js – Complete CRUD with audit tracking, search, CSV, bulk upload, and highlighting
(() => {
  const form = document.getElementById('ivl-form');
  if (!form) return;

  // ============================================
  // FIX CORS - Use current hostname
  // ============================================
  const API_BASE = "";

  const alertBox = document.getElementById('ivl-alert');
  const tableLoading = document.getElementById('table-loading');
  const tableNoData = document.getElementById('table-no-data');
  const entriesTable = document.getElementById('entries-table');
  const entriesTbody = document.getElementById('entries-tbody');
  const editModal = document.getElementById('edit-modal');
  const editForm = document.getElementById('edit-form');
  
  const summaryLoading = document.getElementById('summary-loading');
  const summaryContent = document.getElementById('summary-content');
  const totalInvestmentEl = document.getElementById('total-investment');
  const totalLastLoanEl = document.getElementById('total-last-loan');
  const totalDifferenceEl = document.getElementById('total-difference');

  let currentEditId = null;
  let allEntries = []; // Store for search filtering

  function showBanner(kind, enMsg, esMsg) {
    if (!alertBox) return;
    const msg = (window.currentLang === 'es' ? (esMsg || enMsg) : enMsg);
    alertBox.className = 'alert ' + (kind === 'success' ? 'alert--success' : 'alert--error');
    alertBox.innerHTML = `<span class="alert__icon">${kind === 'success' ? '✅' : '⚠️'}</span> ${msg}`;
    alertBox.style.display = 'block';
    clearTimeout(showBanner._t);
    showBanner._t = setTimeout(() => { alertBox.style.display = 'none'; }, 10000);
  }

  function extractFileFromNotes(notes) {
    if (!notes) return null;
    const match = notes.match(/File:\s*(.+?)(?:\n|$)/);
    return match ? match[1].trim() : null;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatCurrency(value) {
    if (value === null || value === undefined || value === '-') return '-';
    const num = parseFloat(value);
    return isNaN(num) ? '-' : `L. ${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  }

  function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {year: 'numeric', month: 'short', day: 'numeric'});
    } catch {
      return dateStr;
    }
  }

  function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    try {
      const date = new Date(dateStr);
      const dateOptions = {year: 'numeric', month: 'short', day: 'numeric'};
      const timeOptions = {hour: '2-digit', minute: '2-digit'};
      return `${date.toLocaleDateString('en-US', dateOptions)} ${date.toLocaleTimeString('en-US', timeOptions)}`;
    } catch {
      return dateStr;
    }
  }

  function isRecentlyEdited(updatedAt) {
    if (!updatedAt) return false;
    const updatedDate = new Date(updatedAt);
    const now = new Date();
    const hoursDiff = (now - updatedDate) / (1000 * 60 * 60);
    return hoursDiff <= 24;
  }

  // ============================================
  // SEARCH FUNCTIONALITY
  // ============================================
  function filterEntries(searchTerm) {
    const filtered = allEntries.filter(entry => {
      const term = searchTerm.toLowerCase();
      return (
        (entry.partner_name || '').toLowerCase().includes(term) ||
        (entry.comments || '').toLowerCase().includes(term) ||
        (entry.created_by || '').toLowerCase().includes(term) ||
        (entry.updated_by || '').toLowerCase().includes(term)
      );
    });
    displayEntries(filtered);
  }

  // ============================================
  // CSV DOWNLOAD FUNCTIONALITY
  // ============================================
  function downloadCSV() {
    if (allEntries.length === 0) {
      showBanner('error', 'No data to download', 'No hay datos para descargar');
      return;
    }

    // CSV Headers
    const headers = [
      'Partner Name',
      'Expected Profit %',
      'Investment Amount (L.)',
      'Last Loan (L.)',
      'Difference (L.)',
      'Comments',
      'Date Entered',
      'Created By',
      'Last Edited',
      'Last Edited By'
    ];

    // CSV Rows
    const rows = allEntries.map(entry => {
      return [
        entry.partner_name || '',
        entry.expected_profit_pct || '',
        entry.investment_amount || '',
        entry.last_loan || '',
        entry.difference || '',
        (entry.comments || '').replace(/"/g, '""'), // Escape quotes
        entry.created_at || '',
        entry.created_by || '',
        entry.updated_at || '',
        entry.updated_by || ''
      ].map(val => `"${val}"`).join(',');
    });

    // Combine headers and rows
    const csv = [headers.join(','), ...rows].join('\n');

    // Create download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `ivl_entries_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showBanner('success', 'CSV downloaded successfully!', '¡CSV descargado correctamente!');
  }

  // ============================================
  // CSV TEMPLATE DOWNLOAD WITH EXAMPLE ROW
  // ============================================
  function downloadCSVTemplate() {
    // CSV Headers
    const headers = [
      'Partner Name',
      'Expected Profit %',
      'Investment Amount (L.)',
      'Last Loan (L.)',
      'Comments'
    ];

    // Example row
    const exampleRow = [
      'Example Partner LLC',
      '15.5',
      '50000.00',
      '25000.00',
      'Sample comment'
    ].map(val => `"${val}"`).join(',');

    // Combine headers and example
    const csv = [headers.join(','), exampleRow].join('\n');

    // Create download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `ivl_template_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showBanner('success', 'CSV template downloaded!', '¡Plantilla CSV descargada!');
  }

  // ============================================
  // CSV BULK UPLOAD FUNCTIONALITY - ALL OR NOTHING
  // ============================================
  async function uploadCSV(file) {
    if (!file) {
      showBanner('error', 'Please select a CSV file', 'Por favor seleccione un archivo CSV');
      return;
    }

    // Show loading state
    showBanner('success', 'Validating CSV file...', 'Validando archivo CSV...');

    const formData = new FormData();
    formData.append('csv_file', file);

    try {
      const resp = await fetch(`${API_BASE}/api/equity/ivl/bulk-upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const json = await resp.json();

      if (!resp.ok || !json.ok) {
        // Handle validation errors
        if (json.validation_errors && json.validation_errors.length > 0) {
          const errorList = json.validation_errors
            .map(err => `• Row ${err.row}: ${err.error}`)
            .join('\n');
          
          const errorMsg = window.currentLang === 'es'
            ? `❌ Errores de validación encontrados:\n\n${errorList}\n\nPor favor revise el archivo de plantilla y asegúrese de que todos los registros coincidan con la estructura requerida. Ningún registro ha sido agregado.`
            : `❌ Validation errors found:\n\n${errorList}\n\nPlease review the template file and ensure all records match the required structure. No records have been added.`;
          
          showBanner('error', errorMsg, errorMsg);
          return;
        }
        
        // Handle other errors
        const errorMsg = json.error || 'Upload failed';
        const esErrorMsg = json.error || 'Error al subir el archivo';
        showBanner('error', errorMsg, esErrorMsg);
        return;
      }

      // Success - all records passed validation and were added
      const successMsg = window.currentLang === 'es'
        ? `✅ ¡Éxito! Se agregaron ${json.entries_created} registro(s) correctamente. Todos los registros pasaron la validación.`
        : `✅ Success! ${json.entries_created} record(s) have been successfully added. All records passed validation.`;
      
      showBanner('success', successMsg, successMsg);

      // Reload entries and summary
      await loadEntries();
      await loadSummary();

    } catch (err) {
      console.error('Error uploading CSV:', err);
      const errorMsg = window.currentLang === 'es'
        ? 'Error de red al subir el archivo CSV'
        : 'Network error uploading CSV file';
      showBanner('error', errorMsg, errorMsg);
    }
  }

  // ============================================
  // LOAD ENTRIES
  // ============================================
  async function loadEntries() {
    try {
      tableLoading.style.display = 'block';
      tableNoData.style.display = 'none';
      entriesTable.style.display = 'none';

      const resp = await fetch(`${API_BASE}/api/equity/ivl/entries`, {
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json();

      if (!json.ok) {
        console.error('Failed to load entries:', json.error);
        tableLoading.style.display = 'none';
        tableNoData.style.display = 'block';
        return;
      }

      allEntries = json.entries || [];
      displayEntries(allEntries);

    } catch (err) {
      console.error('Error loading entries:', err);
      tableLoading.style.display = 'none';
      tableNoData.style.display = 'block';
    }
  }

  // ============================================
  // DISPLAY ENTRIES
  // ============================================
  function displayEntries(entries) {
    tableLoading.style.display = 'none';

    if (!entries || entries.length === 0) {
      tableNoData.style.display = 'block';
      entriesTable.style.display = 'none';
      return;
    }

    tableNoData.style.display = 'none';
    entriesTable.style.display = 'table';
    entriesTbody.innerHTML = '';

    entries.forEach(entry => {
      const tr = document.createElement('tr');
      
      // Apply highlighting for recently edited entries
      if (isRecentlyEdited(entry.updated_at)) {
        tr.style.backgroundColor = '#fef3c7';
      }

      const fileName = extractFileFromNotes(entry.notes);
      const fileLink = fileName 
        ? `<a href="/uploads/${encodeURIComponent(fileName)}" target="_blank" class="file-link">
             <span class="file-icon">📄</span>${escapeHtml(fileName)}
           </a>`
        : '-';

      const diffValue = entry.difference !== null ? parseFloat(entry.difference) : null;
      let differenceClass = '';
      if (diffValue !== null) {
        differenceClass = diffValue >= 0 ? 'difference-positive' : 'difference-negative';
      }

      tr.innerHTML = `
        <td>${escapeHtml(entry.partner_name || '-')}</td>
        <td>${entry.expected_profit_pct !== null ? entry.expected_profit_pct + '%' : '-'}</td>
        <td>${formatCurrency(entry.investment_amount)}</td>
        <td>${formatCurrency(entry.last_loan)}</td>
        <td class="${differenceClass}">${formatCurrency(entry.difference)}</td>
        <td>${escapeHtml(entry.comments || '-')}</td>
        <td>${fileLink}</td>
        <td>${formatDate(entry.created_at)}</td>
        <td>${escapeHtml(entry.created_by || '-')}</td>
        <td>${formatDateTime(entry.updated_at)}</td>
        <td>
          <button class="action-btn edit-btn" onclick="editEntry(${entry.investment_id})">Edit</button>
          <button class="action-btn delete-btn" onclick="deleteEntry(${entry.investment_id})">Delete</button>
        </td>
      `;
      entriesTbody.appendChild(tr);
    });
  }

  // ============================================
  // LOAD SUMMARY
  // ============================================
  async function loadSummary() {
    if (!summaryLoading || !summaryContent) return;

    try {
      summaryLoading.style.display = 'block';
      summaryContent.style.display = 'none';

      const resp = await fetch(`${API_BASE}/api/equity/ivl/summary`, {
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json();

      if (!json.ok) {
        console.error('Failed to load summary:', json.error);
        summaryLoading.innerHTML = '<p style="color: #e74c3c;">Failed to load summary</p>';
        return;
      }

      const summary = json.summary || {};
      
      if (totalInvestmentEl) totalInvestmentEl.textContent = formatCurrency(summary.total_investment || 0);
      if (totalLastLoanEl) totalLastLoanEl.textContent = formatCurrency(summary.total_last_loan || 0);
      if (totalDifferenceEl) totalDifferenceEl.textContent = formatCurrency(summary.total_difference || 0);

      summaryLoading.style.display = 'none';
      summaryContent.style.display = 'grid';

    } catch (err) {
      console.error('Error loading summary:', err);
      summaryLoading.innerHTML = '<p style="color: #e74c3c;">Network error</p>';
    }
  }

  // ============================================
  // SUBMIT FORM
  // ============================================
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const partner = form['partner_name'].value.trim();
    const pct = form['expected_profit_pct'].value;
    
    if (!partner) {
      showBanner('error', 'Please enter Partner Name.', 'Por favor ingrese la razón social.');
      return;
    }
    if (pct === '' || pct == null) {
      showBanner('error', 'Please enter Expected Profit Percentage.', 'Por favor ingrese el porcentaje de utilidad.');
      return;
    }

    const fd = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const prevText = submitBtn?.textContent;
    
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = window.currentLang === 'es' ? 'Guardando…' : 'Saving…';
    }

    try {
      // FIX: Changed from /api/equity/investment-loan to /api/equity/ivl/entry
      const url = `${API_BASE}/api/equity/ivl/entry`;
      const resp = await fetch(url, { 
        method: 'POST', 
        body: fd,
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json().catch(() => ({}));
      
      if (!resp.ok || !json.ok) {
        const msg = json?.error || `Request failed (${resp.status})`;
        showBanner('error', msg, `Solicitud fallida (${resp.status})`);
      } else {
        showBanner('success', 'Entry submitted successfully!', '¡Solicitud enviada correctamente!');
        form.reset();
        loadEntries();
        loadSummary();
      }
    } catch (err) {
      console.error(err);
      showBanner('error', 'Network error submitting the form.', 'Error de red al enviar el formulario.');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = prevText;
      }
    }
  });

  // ============================================
  // EDIT - OPEN MODAL
  // ============================================
  window.editEntry = async (investmentId) => {
    try {
      const resp = await fetch(`${API_BASE}/api/equity/ivl/entries`, {
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json();
      
      if (!json.ok) {
        showBanner('error', 'Failed to load entry data', 'Error al cargar los datos');
        return;
      }

      const entry = json.entries.find(e => e.investment_id === investmentId);
      if (!entry) {
        showBanner('error', 'Entry not found', 'Entrada no encontrada');
        return;
      }

      currentEditId = investmentId;
      document.getElementById('edit-investment-id').value = investmentId;
      document.getElementById('edit-partner-name').value = entry.partner_name || '';
      document.getElementById('edit-expected-profit').value = entry.expected_profit_pct || '';
      document.getElementById('edit-investment-amount').value = entry.investment_amount || '';
      document.getElementById('edit-last-loan').value = entry.last_loan || '';
      document.getElementById('edit-difference').value = entry.difference || '';
      document.getElementById('edit-comments').value = entry.comments || '';

      editModal.classList.add('active');
      
    } catch (err) {
      console.error('Error loading entry for edit:', err);
      showBanner('error', 'Network error', 'Error de red');
    }
  };

  // ============================================
  // EDIT - SAVE CHANGES
  // ============================================
  editForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const investmentId = document.getElementById('edit-investment-id').value;
    const data = {
      partner_name: document.getElementById('edit-partner-name').value.trim(),
      expected_profit_pct: document.getElementById('edit-expected-profit').value,
      investment_amount: document.getElementById('edit-investment-amount').value || null,
      last_loan: document.getElementById('edit-last-loan').value || null,
      difference: document.getElementById('edit-difference').value || null,
      comments: document.getElementById('edit-comments').value.trim()
    };

    if (!data.partner_name || !data.expected_profit_pct) {
      showBanner('error', 'Partner name and expected profit are required', 'Nombre del socio y utilidad esperada son requeridos');
      return;
    }

    try {
      const url = `${API_BASE}/api/equity/ivl/entry/${investmentId}`;
      const resp = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json();

      if (!resp.ok || !json.ok) {
        showBanner('error', json.error || 'Update failed', 'Error al actualizar');
      } else {
        showBanner('success', 'Entry updated successfully!', '¡Entrada actualizada correctamente!');
        closeEditModal();
        loadEntries();
        loadSummary();
      }
    } catch (err) {
      console.error('Error updating entry:', err);
      showBanner('error', 'Network error', 'Error de red');
    }
  });

  // ============================================
  // DELETE - REMOVE ENTRY
  // ============================================
  window.deleteEntry = async (investmentId) => {
    const confirmMsg = window.currentLang === 'es' 
      ? '¿Está seguro de que desea eliminar esta entrada?' 
      : 'Are you sure you want to delete this entry?';
    
    if (!confirm(confirmMsg)) return;

    try {
      const url = `${API_BASE}/api/equity/ivl/entry/${investmentId}`;
      const resp = await fetch(url, { 
        method: 'DELETE',
        credentials: 'include'  // Send session cookies
      });
      const json = await resp.json();

      if (!resp.ok || !json.ok) {
        showBanner('error', json.error || 'Delete failed', 'Error al eliminar');
      } else {
        showBanner('success', 'Entry deleted successfully!', '¡Entrada eliminada correctamente!');
        loadEntries();
        loadSummary();
      }
    } catch (err) {
      console.error('Error deleting entry:', err);
      showBanner('error', 'Network error', 'Error de red');
    }
  };

  // ============================================
  // MODAL CONTROLS
  // ============================================
  window.closeEditModal = () => {
    editModal.classList.remove('active');
    currentEditId = null;
    editForm.reset();
  };

  editModal.addEventListener('click', (e) => {
    if (e.target === editModal) {
      window.closeEditModal();
    }
  });

  // ============================================
  // SEARCH BAR EVENT
  // ============================================
  const searchInput = document.getElementById('ivl-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterEntries(e.target.value);
    });
  }

  // ============================================
  // CSV DOWNLOAD BUTTON
  // ============================================
  const csvBtn = document.getElementById('download-csv-btn');
  if (csvBtn) {
    csvBtn.addEventListener('click', downloadCSV);
  }

  // ============================================
  // CSV TEMPLATE DOWNLOAD BUTTON
  // ============================================
  const csvTemplateBtn = document.getElementById('download-csv-template-btn');
  if (csvTemplateBtn) {
    csvTemplateBtn.addEventListener('click', downloadCSVTemplate);
  }

  // ============================================
  // CSV BULK UPLOAD EVENT
  // ============================================
  const csvUploadInput = document.getElementById('csv-upload-input');
  const csvUploadBtn = document.getElementById('csv-upload-btn');
  
  if (csvUploadBtn && csvUploadInput) {
    csvUploadBtn.addEventListener('click', () => {
      csvUploadInput.click();
    });
    
    csvUploadInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        uploadCSV(file);
        // Reset input so same file can be uploaded again
        csvUploadInput.value = '';
      }
    });
  }

  // Make functions globally available
  window.filterEntries = filterEntries;
  window.downloadCSV = downloadCSV;
  window.downloadCSVTemplate = downloadCSVTemplate;

  // ============================================
  // INITIALIZE
  // ============================================
  loadEntries();
  loadSummary();
})();

// Initialize autosave
const ivlFormAutosave = new FormAutosave('ivl-form', {
  excludeFields: [],
  onRestore: () => console.log('Investment vs Loan form draft restored')
});