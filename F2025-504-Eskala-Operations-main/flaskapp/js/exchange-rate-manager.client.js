
/**
 * Exchange Rate Manager - Client-side JavaScript
 * Handles UI interactions and API calls for managing exchange rates
 * UPDATED: Single unified table combining rates and audit history
 */

(function() {
  'use strict';

  // API endpoints (adjust these to match your backend)
  const API_BASE = '/api';
  const ENDPOINTS = {
    getCurrentRate: `${API_BASE}/fx-rates/current`,
    getAllRates: `${API_BASE}/fx-rates/all`,
    getHistory: `${API_BASE}/fx-rates/history`,
    updateRate: `${API_BASE}/fx-rates/update`
  };

  // DOM elements
  const elements = {
    // Current rate displays
    currentRateHnlUsd: document.getElementById('current-rate-hnl-usd'),
    rateDateHnl: document.getElementById('rate-date-hnl'),
    
    // Unified table
    historyTable: document.getElementById('history-table'),
    historyTbody: document.getElementById('history-tbody'),
    historyLoading: document.getElementById('history-loading'),
    historyNoData: document.getElementById('history-no-data'),
    
    // Modal
    updateModal: document.getElementById('update-modal'),
    updateRateBtn: document.getElementById('update-rate-btn'),
    closeModalBtn: document.getElementById('close-modal'),
    cancelUpdateBtn: document.getElementById('cancel-update'),
    updateForm: document.getElementById('update-rate-form'),
    
    // Form fields
    newRateHnlUsd: document.getElementById('new-rate-hnl-usd'),
    effectiveDate: document.getElementById('effective-date'),
    updateReason: document.getElementById('update-reason')
  };

  /**
   * Initialize the page
   */
  function init() {
    // Set default effective date to now
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const localDate = new Date(now.getTime() - (offset * 60 * 1000));
    elements.effectiveDate.value = localDate.toISOString().slice(0, 16);

    // Load data
    loadCurrentRate();
    loadUnifiedHistory();

    // Event listeners
    elements.updateRateBtn.addEventListener('click', openUpdateModal);
    elements.closeModalBtn.addEventListener('click', closeUpdateModal);
    elements.cancelUpdateBtn.addEventListener('click', closeUpdateModal);
    elements.updateForm.addEventListener('submit', handleUpdateSubmit);
    
    // Close modal on outside click
    elements.updateModal.addEventListener('click', (e) => {
      if (e.target === elements.updateModal) {
        closeUpdateModal();
      }
    });
  }

  /**
   * Load current exchange rate
   */
  async function loadCurrentRate() {
    try {
      const response = await fetch(ENDPOINTS.getCurrentRate, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to load current rate');
      }
      
      const data = await response.json();
      
      if (data.success && data.rate) {
        const rate = parseFloat(data.rate.rate);
        const formattedRate = rate.toFixed(4);
        
        // Update HNL to USD display
        elements.currentRateHnlUsd.textContent = formattedRate;
        
        // Format date
        const validFrom = new Date(data.rate.valid_from);
        const formattedDate = validFrom.toLocaleDateString() + ' ' + validFrom.toLocaleTimeString();
        elements.rateDateHnl.textContent = formattedDate;
      } else {
        // Use default rate if no rate found
        console.warn('No current rate found, using default');
        elements.currentRateHnlUsd.textContent = '25.2500';
        elements.rateDateHnl.textContent = 'Not set';
      }
    } catch (error) {
      console.error('Error loading current rate:', error);
      showNotification('Error loading current exchange rate', 'error');
    }
  }

  /**
   * Load unified history (combines all rates with audit info)
   */
  async function loadUnifiedHistory() {
    try {
      elements.historyLoading.style.display = 'block';
      elements.historyNoData.style.display = 'none';
      elements.historyTable.style.display = 'none';

      // Fetch both all rates and history
      const [ratesResponse, historyResponse] = await Promise.all([
        fetch(ENDPOINTS.getAllRates, { credentials: 'include' }),
        fetch(ENDPOINTS.getHistory, { credentials: 'include' })
      ]);
      
      if (!ratesResponse.ok || !historyResponse.ok) {
        throw new Error('Failed to load data');
      }
      
      const ratesData = await ratesResponse.json();
      const historyData = await historyResponse.json();
      
      elements.historyLoading.style.display = 'none';
      
      // Combine the data
      const allRates = ratesData.rates || [];
      const history = historyData.history || [];
      
      if (allRates.length === 0 && history.length === 0) {
        elements.historyNoData.textContent = 'No exchange rate data found';
        elements.historyNoData.style.display = 'block';
        return;
      }

      // Create unified data structure
      const unifiedData = combineRatesAndHistory(allRates, history);
      
      if (unifiedData.length === 0) {
        elements.historyNoData.textContent = 'No exchange rate data found';
        elements.historyNoData.style.display = 'block';
        return;
      }

      // Render unified table
      renderUnifiedTable(unifiedData);
      elements.historyTable.style.display = 'table';

    } catch (error) {
      console.error('Error loading history:', error);
      elements.historyLoading.style.display = 'none';
      elements.historyNoData.textContent = 'Network error loading data';
      elements.historyNoData.style.display = 'block';
      showNotification('Error loading exchange rate data', 'error');
    }
  }

  /**
   * Combine rates and history data into unified structure
   */
  function combineRatesAndHistory(rates, history) {
    const unified = [];
    
    // Create a map of rate IDs to history records
    const historyMap = new Map();
    history.forEach(h => {
      const key = `${h.from_currency}-${h.to_currency}-${h.effective_date}`;
      historyMap.set(key, h);
    });

    // Process each rate
    rates.forEach(rate => {
      const key = `${rate.from_currency}-${rate.to_currency}-${rate.valid_from}`;
      const historyRecord = historyMap.get(key);
      
      unified.push({
        from_currency: rate.from_currency,
        to_currency: rate.to_currency,
        rate: rate.rate,
        valid_from: rate.valid_from,
        valid_to: rate.valid_to,
        status: !rate.valid_to ? 'current' : 'expired',
        changed_by: historyRecord ? historyRecord.changed_by : 'System',
        changed_at: historyRecord ? historyRecord.changed_at : rate.valid_from,
        reason: historyRecord ? historyRecord.reason : '—'
      });
    });

    // Sort by valid_from descending (most recent first)
    unified.sort((a, b) => new Date(b.valid_from) - new Date(a.valid_from));
    
    return unified;
  }

  /**
   * Render unified table with all information
   */
  function renderUnifiedTable(data) {
    elements.historyTbody.innerHTML = '';
    
    data.forEach(item => {
      const row = document.createElement('tr');
      
      const isCurrent = item.status === 'current';
      const validFrom = new Date(item.valid_from).toLocaleString();
      const validTo = item.valid_to ? new Date(item.valid_to).toLocaleString() : 'Current';
      const changedAt = new Date(item.changed_at).toLocaleString();
      
      row.innerHTML = `
        <td>${escapeHtml(item.from_currency)}</td>
        <td>${escapeHtml(item.to_currency)}</td>
        <td><strong>${parseFloat(item.rate).toFixed(4)}</strong></td>
        <td>${validFrom}</td>
        <td>${validTo}</td>
        <td>
          <span class="status-badge ${isCurrent ? 'status-current' : 'status-expired'}">
            ${isCurrent ? 'Current' : 'Expired'}
          </span>
        </td>
        <td>${escapeHtml(item.changed_by || 'System')}</td>
        <td>${changedAt}</td>
        <td>${escapeHtml(item.reason || '—')}</td>
        <td>
          ${isCurrent ? '<button class="action-btn edit-btn" onclick="openUpdateModal()">Update</button>' : '—'}
        </td>
      `;
      
      elements.historyTbody.appendChild(row);
    });
  }

  /**
   * Open update modal
   */
  function openUpdateModal() {
    // Pre-fill with current rate
    const currentRate = elements.currentRateHnlUsd.textContent;
    elements.newRateHnlUsd.value = currentRate;
    
    // Reset form
    elements.updateReason.value = '';
    
    // Set default effective date to now
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const localDate = new Date(now.getTime() - (offset * 60 * 1000));
    elements.effectiveDate.value = localDate.toISOString().slice(0, 16);
    
    // Show modal
    elements.updateModal.classList.add('active');
  }

  /**
   * Close update modal
   */
  function closeUpdateModal() {
    elements.updateModal.classList.remove('active');
    elements.updateForm.reset();
  }

  /**
   * Handle form submission
   */
  async function handleUpdateSubmit(e) {
    e.preventDefault();
    
    const newRate = parseFloat(elements.newRateHnlUsd.value);
    const effectiveDate = elements.effectiveDate.value;
    const reason = elements.updateReason.value.trim();
    
    // Validation
    if (!newRate || newRate <= 0) {
      showNotification('Please enter a valid exchange rate', 'error');
      return;
    }
    
    if (!effectiveDate) {
      showNotification('Please select an effective date', 'error');
      return;
    }
    
    if (!reason) {
      showNotification('Please provide a reason for this change', 'error');
      return;
    }
    
    try {
      const response = await fetch(ENDPOINTS.updateRate, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          from_currency: 'HNL',
          to_currency: 'USD',
          rate: newRate,
          effective_date: effectiveDate,
          reason: reason
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        showNotification('Exchange rate updated successfully!', 'success');
        closeUpdateModal();
        
        // Reload data
        await loadCurrentRate();
        await loadUnifiedHistory();
      } else {
        throw new Error(data.message || 'Failed to update rate');
      }
    } catch (error) {
      console.error('Error updating rate:', error);
      showNotification(error.message || 'Error updating exchange rate', 'error');
    }
  }

  /**
   * Show notification
   */
  function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      border-radius: 8px;
      color: white;
      font-weight: 600;
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    // Set color based on type
    if (type === 'success') {
      notification.style.background = '#10b981';
    } else if (type === 'error') {
      notification.style.background = '#ef4444';
    } else {
      notification.style.background = '#3b82f6';
    }
    
    notification.textContent = message;
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(400px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
      notification.style.animation = 'slideIn 0.3s ease-out reverse';
      setTimeout(() => notification.remove(), 300);
    }, 4000);
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Make openUpdateModal globally accessible for inline onclick
  window.openUpdateModal = openUpdateModal;

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();