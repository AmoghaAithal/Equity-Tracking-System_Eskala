/**
 * Form Autosave Utility
 */
class FormAutosave {
  constructor(formId, options = {}) {
    this.form = document.getElementById(formId);
    if (!this.form) {
      console.warn("Form with id '" + formId + "' not found");
      return;
    }
    this.storageKey = options.storageKey || ("autosave_" + formId);
    this.debounceTime = options.debounceTime || 500;
    this.excludeFields = options.excludeFields || [];
    this.onRestore = options.onRestore || null;
    this.onClear = options.onClear || null;
    this.debounceTimer = null;
    this.init();
  }
  
  init() {
    this.restoreDraft();
    const inputs = this.form.querySelectorAll('input:not([type="file"]), select, textarea');
    inputs.forEach(input => {
      if (!this.excludeFields.includes(input.name) && !this.excludeFields.includes(input.id)) {
        input.addEventListener('input', () => this.debouncedSave());
        input.addEventListener('change', () => this.debouncedSave());
      }
    });
    this.addClearDraftButton();
  }
  
  debouncedSave() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => this.saveDraft(), this.debounceTime);
  }
  
  saveDraft() {
    const data = {};
    const inputs = this.form.querySelectorAll('input:not([type="file"]), select, textarea');
    inputs.forEach(input => {
      const key = input.name || input.id;
      if (key && !this.excludeFields.includes(key)) {
        if (input.type === 'checkbox') {
          data[key] = input.checked;
        } else if (input.type === 'radio') {
          if (input.checked) data[key] = input.value;
        } else {
          data[key] = input.value;
        }
      }
    });
    if (Object.keys(data).length > 0) {
      localStorage.setItem(this.storageKey, JSON.stringify({
        data: data,
        timestamp: new Date().toISOString()
      }));
      this.showDraftIndicator();
    }
  }
  
  restoreDraft() {
    const saved = localStorage.getItem(this.storageKey);
    if (!saved) return;
    try {
      const parsed = JSON.parse(saved);
      const data = parsed.data;
      const timestamp = parsed.timestamp;
      const draftAge = Date.now() - new Date(timestamp).getTime();
      const maxAge = 7 * 24 * 60 * 60 * 1000;
      if (draftAge > maxAge) {
        this.clearDraft();
        return;
      }
      Object.entries(data).forEach(([key, value]) => {
        const input = this.form.querySelector("[name='" + key + "'], #" + key);
        if (input) {
          if (input.type === 'file') return;
          if (input.type === 'checkbox') {
            input.checked = value === 'on' || value === 'true' || value === true;
          } else if (input.type === 'radio') {
            if (input.value === value) input.checked = true;
          } else {
            input.value = value;
          }
        }
      });
      this.showDraftRestoredMessage(timestamp);
      if (this.onRestore) this.onRestore(data, timestamp);
    } catch (e) {
      console.error('Error restoring draft:', e);
      this.clearDraft();
    }
  }
  
  clearDraft() {
    localStorage.removeItem(this.storageKey);
    this.hideDraftIndicator();
    if (this.onClear) this.onClear();
  }
  
  showDraftIndicator() {
    let indicator = document.getElementById('draft-indicator');
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'draft-indicator';
      indicator.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#10b981;color:white;padding:8px 16px;border-radius:8px;font-size:13px;box-shadow:0 4px 6px rgba(0,0,0,0.1);z-index:1000;opacity:0;transition:opacity 0.3s';
      indicator.textContent = '✓ Draft saved';
      document.body.appendChild(indicator);
    }
    indicator.style.opacity = '1';
    setTimeout(() => { indicator.style.opacity = '0'; }, 2000);
  }
  
  hideDraftIndicator() {
    const indicator = document.getElementById('draft-indicator');
    if (indicator) indicator.remove();
  }
  
  showDraftRestoredMessage(timestamp) {
    const date = new Date(timestamp);
    const timeAgo = this.getTimeAgo(date);
    const message = document.createElement('div');
    message.style.cssText = 'background:#3b82f6;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 4px rgba(0,0,0,0.1)';
    message.innerHTML = '<span>📝 Draft restored from ' + timeAgo + '</span><button id="dismiss-draft-message" style="background:transparent;border:1px solid white;color:white;padding:4px 12px;border-radius:4px;cursor:pointer;font-size:12px">Dismiss</button>';
    this.form.insertBefore(message, this.form.firstChild);
    document.getElementById('dismiss-draft-message').addEventListener('click', () => message.remove());
    setTimeout(() => message.remove(), 10000);
  }
  
  addClearDraftButton() {
    if (document.getElementById('clear-draft-btn')) return;
    const button = document.createElement('button');
    button.id = 'clear-draft-btn';
    button.type = 'button';
    button.textContent = '🗑️ Clear Draft';
    button.style.cssText = 'background:#ef4444;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-size:14px;margin-left:8px';
    button.addEventListener('click', () => {
      if (confirm('Clear saved draft? This cannot be undone.')) {
        this.clearDraft();
        this.form.reset();
        alert('Draft cleared!');
      }
    });
    const submitBtn = this.form.querySelector('button[type="submit"]');
    if (submitBtn && submitBtn.parentElement) {
      submitBtn.parentElement.appendChild(button);
    }
  }
  
  getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
    return Math.floor(seconds / 86400) + ' days ago';
  }
  
  clearOnSuccess() {
    this.clearDraft();
  }
}

window.FormAutosave = FormAutosave;
