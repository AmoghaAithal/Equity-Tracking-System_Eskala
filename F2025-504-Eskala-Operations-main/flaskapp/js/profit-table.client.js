
// profit-table_client.js - WITH ALL-OR-NOTHING BULK CSV UPLOAD, AUDIT TRACKING, YELLOW HIGHLIGHTING
(() => {
  const API_BASE = "";

  const tableLoading = document.getElementById('table-loading');
  const tableNoData = document.getElementById('table-no-data');
  const entriesTable = document.getElementById('entries-table');
  const entriesTbody = document.getElementById('entries-tbody');
  const editModal = document.getElementById('edit-modal');
  const editForm = document.getElementById('edit-form');
  const searchInput = document.getElementById('search-input');
  const downloadCsvBtn = document.getElementById('download-csv-btn');
  const refreshBtn = document.getElementById('refresh-btn');
  
  // Bulk upload elements
  const downloadTemplateBtn = document.getElementById('download-template-btn');
  const uploadCsvInput = document.getElementById('upload-csv-input');
  const uploadCsvLabel = document.getElementById('upload-csv-label');
  const uploadProgress = document.getElementById('upload-progress');
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');
  const uploadResult = document.getElementById('upload-result');

  // Store entries globally for edit access and filtering
  let allEntries = [];
  let filteredEntries = [];

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatCurrency(value) {
    if (!value || value === '-') return '-';
    const num = parseFloat(value);
    return isNaN(num) ? '-' : num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
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
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return dateStr;
    }
  }

  function isRecentlyEdited(updatedAt) {
    if (!updatedAt) return false;
    const now = new Date();
    const updated = new Date(updatedAt);
    const hoursDiff = (now - updated) / (1000 * 60 * 60);
    return hoursDiff <= 24;
  }

  // ============================================
  // POPULATE FILTER DROPDOWNS
  // ============================================
  function populateFilters() {
    // Get unique years
    const years = [...new Set(allEntries.map(e => e.year).filter(Boolean))].sort((a, b) => b - a);
    const yearFilter = document.getElementById('year-filter');
    if (yearFilter) {
      yearFilter.innerHTML = '<option value="">All Years</option>' + 
        years.map(year => `<option value="${year}">${year}</option>`).join('');
    }

    // Get unique proposal states
    const proposals = [...new Set(allEntries.map(e => e.proposal_state).filter(Boolean))];
    const proposalFilter = document.getElementById('proposal-filter');
    if (proposalFilter) {
      proposalFilter.innerHTML = '<option value="">All Proposals</option>' +
        proposals.map(p => `<option value="${p}">${p}</option>`).join('');
    }

    // Get unique transaction types
    const transactions = [...new Set(allEntries.map(e => e.transaction_type).filter(Boolean))];
    const transactionFilter = document.getElementById('transaction-filter');
    if (transactionFilter) {
      transactionFilter.innerHTML = '<option value="">All Transactions</option>' +
        transactions.map(t => `<option value="${t}">${t}</option>`).join('');
    }
  }

  // ============================================
  // UPDATE STATISTICS (FOR FILTERED ENTRIES)
  // ============================================
  function updateStats(entries) {
    const totalEntries = entries.length;
    const totalInvestmentL = entries.reduce((sum, e) => sum + (parseFloat(e.investment_l) || 0), 0);
    const totalInvestmentUSD = entries.reduce((sum, e) => sum + (parseFloat(e.investment_usd) || 0), 0);
    const avgProfit = entries.length > 0 
      ? entries.reduce((sum, e) => sum + (parseFloat(e.expected_profit_pct) || 0), 0) / entries.length 
      : 0;

    document.getElementById('stat-total-entries').textContent = totalEntries.toLocaleString();
    document.getElementById('stat-investment-l').textContent = 
      'L ' + totalInvestmentL.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('stat-investment-usd').textContent = 
      '$ ' + totalInvestmentUSD.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('stat-avg-profit').textContent = avgProfit.toFixed(1) + '%';
  }

  // ============================================
  // SEARCH AND FILTER FUNCTIONALITY
  // ============================================
  function filterEntries() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const yearFilter = document.getElementById('year-filter')?.value || '';
    const proposalFilter = document.getElementById('proposal-filter')?.value || '';
    const transactionFilter = document.getElementById('transaction-filter')?.value || '';
    
    filteredEntries = allEntries.filter(entry => {
      // Text search across multiple fields
      const matchesSearch = 
        (entry.partner_name || '').toLowerCase().includes(searchTerm) ||
        (entry.bank_id || '').toLowerCase().includes(searchTerm) ||
        (entry.comments || '').toLowerCase().includes(searchTerm) ||
        (entry.technician || '').toLowerCase().includes(searchTerm) ||
        (entry.created_by || '').toLowerCase().includes(searchTerm) ||
        (entry.updated_by || '').toLowerCase().includes(searchTerm);
      
      // Filter by year
      const matchesYear = !yearFilter || entry.year?.toString() === yearFilter;
      
      // Filter by proposal state
      const matchesProposal = !proposalFilter || entry.proposal_state === proposalFilter;
      
      // Filter by transaction type
      const matchesTransaction = !transactionFilter || entry.transaction_type === transactionFilter;
      
      return matchesSearch && matchesYear && matchesProposal && matchesTransaction;
    });

    renderTable(filteredEntries);
    updateStats(filteredEntries);
  }

  // ============================================
  // RENDER TABLE
  // ============================================
  function renderTable(entries) {
    entriesTbody.innerHTML = '';
    
    entries.forEach(entry => {
      const row = document.createElement('tr');
      
      // Mark recently edited rows (within 24 hours)
      const recentlyEdited = isRecentlyEdited(entry.updated_at);
      if (recentlyEdited) {
        row.setAttribute('data-recently-edited', 'true');
      }
      
      row.innerHTML = `
        <td>${escapeHtml(entry.partner_name || '-')}</td>
        <td>${escapeHtml(entry.bank_id || '-')}</td>
        <td>${escapeHtml(entry.year || '-')}</td>
        <td>${escapeHtml(entry.technician || '-')}</td>
        <td>${formatCurrency(entry.profit_l)}</td>
        <td>${entry.expected_profit_pct ? entry.expected_profit_pct + '%' : '-'}</td>
        <td>${formatCurrency(entry.company_value_l)}</td>
        <td>${formatCurrency(entry.investment_l)}</td>
        <td>${formatCurrency(entry.investment_usd)}</td>
        <td>${formatCurrency(entry.exchange_rate)}</td>
        <td>${escapeHtml(entry.proposal_state || '-')}</td>
        <td>${escapeHtml(entry.transaction_type || '-')}</td>
        <td>${escapeHtml(entry.business_category || '-')}</td>
        <td>${escapeHtml(entry.company_type || '-')}</td>
        <td>${escapeHtml(entry.community || '-')}</td>
        <td>${escapeHtml(entry.municipality || '-')}</td>
        <td>${escapeHtml(entry.state || '-')}</td>
        <td>${formatCurrency(entry.january_l)}</td>
        <td>${formatCurrency(entry.february_l)}</td>
        <td>${formatCurrency(entry.march_l)}</td>
        <td>${formatCurrency(entry.april_l)}</td>
        <td>${formatCurrency(entry.may_l)}</td>
        <td>${formatCurrency(entry.june_l)}</td>
        <td>${formatCurrency(entry.july_l)}</td>
        <td>${formatCurrency(entry.august_l)}</td>
        <td>${formatCurrency(entry.september_l)}</td>
        <td>${formatCurrency(entry.october_l)}</td>
        <td>${formatCurrency(entry.november_l)}</td>
        <td>${formatCurrency(entry.december_l)}</td>
        <td>${escapeHtml((entry.comments || '').substring(0, 50) + ((entry.comments || '').length > 50 ? '...' : ''))}</td>
        <td>
          ${escapeHtml(entry.updated_by || entry.created_by || '-')}
          <small>${formatDateTime(entry.updated_at || entry.created_at)}</small>
        </td>
        <td>
          <div class="action-buttons">
            <button class="btn-edit" onclick="editEntry(${entry.investment_id})">✏️ Edit</button>
            <button class="btn-delete" onclick="deleteEntry(${entry.investment_id})">🗑️ Delete</button>
          </div>
        </td>
      `;
      
      entriesTbody.appendChild(row);
    });
    
    entriesTable.style.display = entries.length > 0 ? 'table' : 'none';
    tableNoData.style.display = entries.length > 0 ? 'none' : 'block';
  }

  // ============================================
  // LOAD ENTRIES
  // ============================================
  async function loadEntries(highlightId = null) {
    try {
      tableLoading.style.display = 'block';
      tableNoData.style.display = 'none';
      entriesTable.style.display = 'none';

      const resp = await fetch(`${API_BASE}/api/equity/profit/entries`, {
        credentials: 'include'
      });
      const json = await resp.json();

      tableLoading.style.display = 'none';

      if (!resp.ok || !json.ok) {
        tableNoData.textContent = 'Error loading entries';
        tableNoData.style.display = 'block';
        return;
      }

      allEntries = json.entries || [];
      filteredEntries = [...allEntries];
      
      if (allEntries.length === 0) {
        tableNoData.textContent = window.currentLang === 'es' ? 'No se encontraron entradas' : 'No entries found';
        tableNoData.style.display = 'block';
        return;
      }

      populateFilters();
      renderTable(filteredEntries);
      updateStats(filteredEntries);
      entriesTable.style.display = 'table';

      // If highlighting specific ID, scroll to it
      if (highlightId) {
        setTimeout(() => {
          const row = document.querySelector(`tr[data-investment-id="${highlightId}"]`);
          if (row) {
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 100);
      }

    } catch (err) {
      console.error('Error loading entries:', err);
      tableLoading.style.display = 'none';
      tableNoData.textContent = 'Network error loading entries';
      tableNoData.style.display = 'block';
    }
  }

  // ============================================
  // EVENT LISTENERS FOR SEARCH AND FILTERS
  // ============================================
  if (searchInput) {
    searchInput.addEventListener('input', filterEntries);
  }

  ['year-filter', 'proposal-filter', 'transaction-filter'].forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener('change', filterEntries);
    }
  });

  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => loadEntries());
  }

  // ============================================
  // DOWNLOAD CSV FUNCTIONALITY
  // ============================================
  function downloadCSV() {
    const headers = [
      'Partner Name', 'Bank ID', 'Year', 'Technician', 'Profit (L)', 'Expected %',
      'Company Value (L)', 'Investment (L)', 'Investment ($)', 'Exchange Rate',
      'Proposal State', 'Transaction Type',
      'Jan (L)', 'Feb (L)', 'Mar (L)', 'Apr (L)', 'May (L)', 'Jun (L)',
      'Jul (L)', 'Aug (L)', 'Sep (L)', 'Oct (L)', 'Nov (L)', 'Dec (L)',
      'Business Category', 'Company Type',
      'Community', 'Municipality', 'State', 'Comments', 'Last Edited By', 'Last Edited'
    ];

    const rows = filteredEntries.map(entry => [
      entry.partner_name || '',
      entry.bank_id || '',
      entry.year || '',
      entry.technician || '',
      entry.profit_l || '',
      entry.expected_profit_pct || '',
      entry.company_value_l || '',
      entry.investment_l || '',
      entry.investment_usd || '',
      entry.exchange_rate || '',
      entry.proposal_state || '',
      entry.transaction_type || '',
      entry.january_l || 0,
      entry.february_l || 0,
      entry.march_l || 0,
      entry.april_l || 0,
      entry.may_l || 0,
      entry.june_l || 0,
      entry.july_l || 0,
      entry.august_l || 0,
      entry.september_l || 0,
      entry.october_l || 0,
      entry.november_l || 0,
      entry.december_l || 0,
      entry.business_category || '',
      entry.company_type || '',
      entry.community || '',
      entry.municipality || '',
      entry.state || '',
      entry.comments || '',
      entry.updated_by || entry.created_by || '',
      formatDateTime(entry.updated_at || entry.created_at)
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `profit_entries_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  }

  if (downloadCsvBtn) {
    downloadCsvBtn.addEventListener('click', downloadCSV);
  }

  // ============================================
  // BULK CSV UPLOAD - TEMPLATE DOWNLOAD
  // ============================================
  function downloadTemplate() {
    const headers = [
      'partner_name',           // Required
      'expected_profit_pct',    // Required
      'year',
      'bank_id',
      'technician',
      'profit_l',
      'company_value_l',
      'investment_l',
      'investment_usd',
      'exchange_rate',
      'proposal_state',
      'transaction_type',
      'january_l',
      'february_l',
      'march_l',
      'april_l',
      'may_l',
      'june_l',
      'july_l',
      'august_l',
      'september_l',
      'october_l',
      'november_l',
      'december_l',
      'business_category',
      'company_type',
      'community',
      'municipality',
      'state',
      'comments',
      'start_date'
    ];

    // Create example row with guidance
    const exampleRow = [
      'Example Partner Inc.',   // partner_name (REQUIRED)
      '15.5',                    // expected_profit_pct (REQUIRED - between 0 and 100)
      '2024',                    // year (optional - YYYY format)
      'BANK001',                 // bank_id (optional)
      'John Smith',              // technician (optional)
      '50000',                   // profit_l (optional - positive number in Lempiras)
      '250000',                  // company_value_l (optional - positive number)
      '75000',                   // investment_l (optional - positive number in Lempiras)
      '3000',                    // investment_usd (optional - positive number in USD)
      '25.0',                    // exchange_rate (optional - positive number)
      'Approved',                // proposal_state (optional)
      'New Investment',          // transaction_type (optional)
      '1000',                    // january_l (optional - defaults to 0)
      '1000',                    // february_l
      '1000',                    // march_l
      '1000',                    // april_l
      '1000',                    // may_l
      '1000',                    // june_l
      '1000',                    // july_l
      '1000',                    // august_l
      '1000',                    // september_l
      '1000',                    // october_l
      '1000',                    // november_l
      '1000',                    // december_l
      'Agriculture',             // business_category (optional)
      'SME',                     // company_type (optional)
      'Santa Rosa',              // community (optional)
      'Tegucigalpa',             // municipality (optional)
      'Francisco Morazán',       // state (optional)
      'Initial investment',      // comments (optional)
      '2024-01-15'               // start_date (optional - YYYY-MM-DD format)
    ];

    // Create CSV content
    let csvContent = headers.join(',') + '\n';
    csvContent += exampleRow.map(val => `"${val}"`).join(',') + '\n';
    
    // Add a few empty rows for users to fill in
    csvContent += '\n\n';  // User can add their data here

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'profit_entries_template.csv';
    link.click();
    
    console.log('📥 Template downloaded with format guidance');
  }

  if (downloadTemplateBtn) {
    downloadTemplateBtn.addEventListener('click', downloadTemplate);
  }

  // ============================================
  // BULK CSV UPLOAD - SHOW RESULT
  // ============================================
  function showUploadResult(success, title, details = '') {
    uploadResult.classList.add('active');
    uploadResult.style.background = success 
      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
      : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    
    const icon = success ? '✓' : '✗';
    
    uploadResult.innerHTML = `
      <div style="display: flex; gap: 16px; align-items: start;">
        <div style="font-size: 32px; font-weight: bold; flex-shrink: 0;">${icon}</div>
        <div style="flex: 1;">
          <div style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">${title}</div>
          ${details ? `<div style="font-size: 14px; line-height: 1.6; opacity: 0.95;">${details}</div>` : ''}
        </div>
      </div>
    `;
    
    // Auto-hide success messages after 8 seconds
    if (success) {
      setTimeout(() => {
        uploadResult.classList.remove('active');
      }, 8000);
    }
  }

  // ============================================
  // BULK CSV UPLOAD - UPLOAD FUNCTION (ALL-OR-NOTHING)
  // ============================================
  async function uploadCSV(file) {
    // Show progress
    uploadProgress.classList.add('active');
    progressBar.style.width = '0%';
    progressText.textContent = 'Reading file...';
    uploadResult.classList.remove('active');

    try {
      const text = await file.text();
      progressBar.style.width = '30%';
      progressText.textContent = 'Validating CSV data...';

      // Send to backend for validation and upload
      const formData = new FormData();
      formData.append('file', file);

      progressBar.style.width = '50%';
      progressText.textContent = 'Uploading and validating records...';

      const resp = await fetch(`${API_BASE}/api/equity/profit/bulk-upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const json = await resp.json();

      progressBar.style.width = '100%';
      progressText.textContent = 'Complete!';

      setTimeout(() => {
        uploadProgress.classList.remove('active');
      }, 1000);

      // Handle successful upload (all records passed validation and were inserted)
      if (resp.ok && json.ok) {
        const uploadedCount = json.uploaded_count || 0;
        
        showUploadResult(
          true,
          `✅ Success! All ${uploadedCount} records uploaded successfully.`,
          `<em>All records have been validated and added to the database.</em>`
        );

        // Reload entries to show the new data
        loadEntries();
        
      } 
      // Handle validation failures (no records were inserted)
      else if (resp.status === 400 && json.validation_errors) {
        const validCount = json.valid_count || 0;
        const invalidCount = json.invalid_count || 0;
        const totalCount = validCount + invalidCount;
        
        // Build detailed error message
        let errorDetails = `<div style="max-height: 300px; overflow-y: auto; margin-top: 12px;">`;
        errorDetails += `<table style="width: 100%; border-collapse: collapse; font-size: 13px;">`;
        errorDetails += `<thead style="position: sticky; top: 0; background: #f3f4f6;">`;
        errorDetails += `<tr style="border-bottom: 2px solid #d1d5db;">`;
        errorDetails += `<th style="padding: 8px; text-align: left; font-weight: 600;">Row</th>`;
        errorDetails += `<th style="padding: 8px; text-align: left; font-weight: 600;">Partner Name</th>`;
        errorDetails += `<th style="padding: 8px; text-align: left; font-weight: 600;">Error</th>`;
        errorDetails += `</tr>`;
        errorDetails += `</thead>`;
        errorDetails += `<tbody>`;
        
        json.validation_errors.forEach((err, idx) => {
          const bgColor = idx % 2 === 0 ? '#ffffff' : '#f9fafb';
          errorDetails += `<tr style="background: ${bgColor}; border-bottom: 1px solid #e5e7eb;">`;
          errorDetails += `<td style="padding: 8px; vertical-align: top;">${err.row}</td>`;
          errorDetails += `<td style="padding: 8px; vertical-align: top;">${escapeHtml(err.partner_name || 'N/A')}</td>`;
          errorDetails += `<td style="padding: 8px; vertical-align: top; color: #dc2626;">${escapeHtml(err.error)}</td>`;
          errorDetails += `</tr>`;
        });
        
        errorDetails += `</tbody></table></div>`;
        errorDetails += `<div style="margin-top: 16px; padding: 12px; background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">`;
        errorDetails += `<strong>⚠️ What to do:</strong>`;
        errorDetails += `<ol style="margin: 8px 0 0 20px; padding: 0;">`;
        errorDetails += `<li>Download the template again to ensure you have the correct format</li>`;
        errorDetails += `<li>Fix the errors listed above in your CSV file</li>`;
        errorDetails += `<li>Make sure all required fields are filled in: <code>partner_name</code> and <code>expected_profit_pct</code></li>`;
        errorDetails += `<li>Verify that numeric fields contain valid numbers</li>`;
        errorDetails += `<li>Upload your corrected file</li>`;
        errorDetails += `</ol></div>`;
        
        showUploadResult(
          false,
          `❌ Validation Failed: ${invalidCount} error(s) found`,
          `<strong>No records were uploaded.</strong> Please fix all errors and try again.<br><br>` +
          `Found ${invalidCount} invalid record(s) out of ${totalCount} total.` +
          errorDetails
        );
      }
      // Handle other errors
      else {
        throw new Error(json.error || 'Upload failed');
      }

    } catch (err) {
      console.error('Upload error:', err);
      uploadProgress.classList.remove('active');
      showUploadResult(
        false,
        '❌ Upload Failed',
        `<strong>Error:</strong> ${escapeHtml(err.message)}<br><br>` +
        `<em>Make sure your CSV file follows the same format as the template. ` +
        `Check that all required fields (partner_name, expected_profit_pct) are filled in correctly.</em><br><br>` +
        `<strong>Common issues:</strong>` +
        `<ul style="margin: 8px 0 0 20px;">` +
        `<li>Missing required columns in the CSV header</li>` +
        `<li>Invalid characters in the file</li>` +
        `<li>File is not in CSV format</li>` +
        `<li>Network connection issues</li>` +
        `</ul>`
      );
    }

    // Reset file input
    uploadCsvInput.value = '';
  }

  if (uploadCsvInput) {
    uploadCsvInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        if (!file.name.endsWith('.csv')) {
          alert('Please select a CSV file');
          return;
        }
        uploadCSV(file);
      }
    });
  }

  if (uploadCsvLabel) {
  }

  // ============================================
  // EDIT ENTRY MODAL
  // ============================================
  function editEntry(id) {
    const entry = allEntries.find(e => e.investment_id === id);
    if (!entry) {
      alert('Entry not found');
      return;
    }

    document.getElementById('edit-investment-id').value = entry.investment_id;
    document.getElementById('edit-bank-id').value = entry.bank_id || '';
    document.getElementById('edit-partner-name').value = entry.partner_name || '';
    document.getElementById('edit-year').value = entry.year || '';
    document.getElementById('edit-technician').value = entry.technician || '';
    document.getElementById('edit-profit-l').value = entry.profit_l || '';
    document.getElementById('edit-expected-pct').value = entry.expected_profit_pct || '';
    document.getElementById('edit-company-value').value = entry.company_value_l || '';
    document.getElementById('edit-investment-l').value = entry.investment_l || '';
    document.getElementById('edit-investment-usd').value = entry.investment_usd || '';
    document.getElementById('edit-exchange-rate').value = entry.exchange_rate || '';
    document.getElementById('edit-proposal-state').value = entry.proposal_state || '';
    document.getElementById('edit-transaction-type').value = entry.transaction_type || '';
    document.getElementById('edit-business-category').value = entry.business_category || '';
    document.getElementById('edit-company-type').value = entry.company_type || '';
    document.getElementById('edit-community').value = entry.community || '';
    document.getElementById('edit-municipality').value = entry.municipality || '';
    document.getElementById('edit-state').value = entry.state || '';
    document.getElementById('edit-comments').value = entry.comments || '';
    
    // Monthly distributions
    document.getElementById('edit-january').value = entry.january_l || 0;
    document.getElementById('edit-february').value = entry.february_l || 0;
    document.getElementById('edit-march').value = entry.march_l || 0;
    document.getElementById('edit-april').value = entry.april_l || 0;
    document.getElementById('edit-may').value = entry.may_l || 0;
    document.getElementById('edit-june').value = entry.june_l || 0;
    document.getElementById('edit-july').value = entry.july_l || 0;
    document.getElementById('edit-august').value = entry.august_l || 0;
    document.getElementById('edit-september').value = entry.september_l || 0;
    document.getElementById('edit-october').value = entry.october_l || 0;
    document.getElementById('edit-november').value = entry.november_l || 0;
    document.getElementById('edit-december').value = entry.december_l || 0;

    editModal.classList.add('active');
  }

  // Make edit and delete functions available globally
  window.editEntry = editEntry;
  window.deleteEntry = deleteEntry;

  // ============================================
  // CLOSE MODAL
  // ============================================
  document.getElementById('close-edit-modal')?.addEventListener('click', () => {
    editModal.classList.remove('active');
  });

  document.getElementById('cancel-edit')?.addEventListener('click', () => {
    editModal.classList.remove('active');
  });

  editModal?.addEventListener('click', (e) => {
    if (e.target === editModal) {
      editModal.classList.remove('active');
    }
  });

  // ============================================
  // SUBMIT EDIT FORM
  // ============================================
  if (editForm) {
    editForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const id = parseInt(document.getElementById('edit-investment-id').value);
      const updatedData = {
        bank_id: document.getElementById('edit-bank-id').value.trim(),
        partner_name: document.getElementById('edit-partner-name').value.trim(),
        year: parseInt(document.getElementById('edit-year').value) || null,
        technician: document.getElementById('edit-technician').value.trim(),
        profit_l: parseFloat(document.getElementById('edit-profit-l').value) || null,
        expected_profit_pct: parseFloat(document.getElementById('edit-expected-pct').value) || null,
        company_value_l: parseFloat(document.getElementById('edit-company-value').value) || null,
        investment_l: parseFloat(document.getElementById('edit-investment-l').value) || null,
        investment_usd: parseFloat(document.getElementById('edit-investment-usd').value) || null,
        exchange_rate: parseFloat(document.getElementById('edit-exchange-rate').value) || null,
        proposal_state: document.getElementById('edit-proposal-state').value,
        transaction_type: document.getElementById('edit-transaction-type').value,
        business_category: document.getElementById('edit-business-category').value.trim(),
        company_type: document.getElementById('edit-company-type').value.trim(),
        community: document.getElementById('edit-community').value.trim(),
        municipality: document.getElementById('edit-municipality').value.trim(),
        state: document.getElementById('edit-state').value.trim(),
        comments: document.getElementById('edit-comments').value.trim(),
        // Monthly distributions
        january_l: parseFloat(document.getElementById('edit-january').value) || 0,
        february_l: parseFloat(document.getElementById('edit-february').value) || 0,
        march_l: parseFloat(document.getElementById('edit-march').value) || 0,
        april_l: parseFloat(document.getElementById('edit-april').value) || 0,
        may_l: parseFloat(document.getElementById('edit-may').value) || 0,
        june_l: parseFloat(document.getElementById('edit-june').value) || 0,
        july_l: parseFloat(document.getElementById('edit-july').value) || 0,
        august_l: parseFloat(document.getElementById('edit-august').value) || 0,
        september_l: parseFloat(document.getElementById('edit-september').value) || 0,
        october_l: parseFloat(document.getElementById('edit-october').value) || 0,
        november_l: parseFloat(document.getElementById('edit-november').value) || 0,
        december_l: parseFloat(document.getElementById('edit-december').value) || 0
      };

      try {
        const resp = await fetch(`${API_BASE}/api/equity/profit/entry/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(updatedData)
        });

        const json = await resp.json();

        if (resp.ok && json.ok) {
          alert(window.currentLang === 'es' 
            ? '¡Entrada actualizada exitosamente!' 
            : 'Entry updated successfully!');
          editModal.classList.remove('active');
          // Reload without scrolling - row will stay in place and be highlighted yellow
          loadEntries(id);
        } else {
          alert(window.currentLang === 'es' 
            ? `Error: ${json.error || 'Error desconocido'}` 
            : `Error: ${json.error || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('Update error:', err);
        alert(window.currentLang === 'es' 
          ? 'Error de red. Por favor intente de nuevo.' 
          : 'Network error. Please try again.');
      }
    });
  }

  // ============================================
  // DELETE ENTRY
  // ============================================
  async function deleteEntry(id) {
    const entry = allEntries.find(e => e.investment_id === id);
    if (!entry) {
      alert('Entry not found');
      return;
    }

    const confirmed = confirm(
      window.currentLang === 'es' 
        ? `¿Está seguro de que desea eliminar la entrada de "${entry.partner_name}"?` 
        : `Are you sure you want to delete entry for "${entry.partner_name}"?`
    );

    if (!confirmed) return;

    try {
      const resp = await fetch(`${API_BASE}/api/equity/profit/entry/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      const json = await resp.json();

      if (resp.ok && json.ok) {
        alert(window.currentLang === 'es' 
          ? '¡Entrada eliminada exitosamente!' 
          : 'Entry deleted successfully!');
        loadEntries();
      } else {
        alert(window.currentLang === 'es' 
          ? `Error: ${json.error || 'Error desconocido'}` 
          : `Error: ${json.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Delete error:', err);
      alert(window.currentLang === 'es' 
        ? 'Error de red. Por favor intente de nuevo.' 
        : 'Network error. Please try again.');
    }
  }

  // ============================================
  // INITIALIZE - LOAD ENTRIES ON PAGE LOAD
  // ============================================
  loadEntries();
})();