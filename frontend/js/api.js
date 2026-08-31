/**
 * SnapClass API Client & Interactive UI Controller
 */

const API_BASE = '/api';

window.SnapClass = {
  // Multi-Toast Notification Shelf
  showToast: (message, type = 'success', duration = 3500) => {
    let shelf = document.getElementById('toast-shelf');
    if (!shelf) {
      shelf = document.createElement('div');
      shelf.id = 'toast-shelf';
      document.body.appendChild(shelf);
    }

    const icons = {
      success: '✅',
      error: '🚨',
      warning: '⚠️',
      info: '💡'
    };

    const toast = document.createElement('div');
    toast.className = `toast-pill ${type}`;
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.6rem;">
        <span style="font-size: 1.1rem;">${icons[type] || '✨'}</span>
        <span>${message}</span>
      </div>
      <button style="background:none; border:none; color:rgba(255,255,255,0.6); cursor:pointer; font-size:1.1rem; padding:0 4px;" onclick="this.parentElement.remove()">×</button>
      <div class="toast-progress" style="animation-duration: ${duration}ms;"></div>
    `;

    shelf.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }
    }, duration);
  },

  // In-Card Form Alert Banners
  showAlert: (containerId, message, type = 'error') => {
    const banner = document.getElementById(containerId);
    if (!banner) return;

    const icons = {
      error: '⚠️',
      success: '🎉',
      warning: '⚡'
    };

    banner.className = `alert-banner alert-${type} active`;
    banner.innerHTML = `
      <span>${icons[type] || 'ℹ️'}</span>
      <span style="flex: 1;">${message}</span>
      <button style="background:none; border:none; color:inherit; cursor:pointer; font-size:1.1rem;" onclick="this.parentElement.classList.remove('active')">×</button>
    `;
  },

  hideAlert: (containerId) => {
    const banner = document.getElementById(containerId);
    if (banner) banner.classList.remove('active');
  },

  // Button Loading State Helpers
  setLoading: (btnElement, isLoading, normalText = 'Submit') => {
    if (!btnElement) return;
    if (isLoading) {
      btnElement.disabled = true;
      btnElement.classList.add('btn-loading');
      btnElement.dataset.originalText = btnElement.innerHTML;
      btnElement.innerHTML = '';
    } else {
      btnElement.disabled = false;
      btnElement.classList.remove('btn-loading');
      btnElement.innerHTML = btnElement.dataset.originalText || normalText;
    }
  },

  // Form Field Real-Time Validation
  validateInput: (inputElement, validatorFn, errorMsg = 'Invalid input') => {
    if (!inputElement) return true;
    const isValid = validatorFn(inputElement.value);
    const parent = inputElement.closest('.input-group') || inputElement.parentElement;
    let errorEl = parent.querySelector('.field-error-msg');

    if (!isValid) {
      inputElement.classList.add('is-invalid');
      inputElement.classList.remove('is-valid');
      if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'field-error-msg';
        parent.appendChild(errorEl);
      }
      errorEl.textContent = errorMsg;
      errorEl.style.display = 'block';
    } else {
      inputElement.classList.remove('is-invalid');
      inputElement.classList.add('is-valid');
      if (errorEl) errorEl.style.display = 'none';
    }
    return isValid;
  },

  // Network Fetch Client
  request: async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, options);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Operation failed');
      }

      return data;
    } catch (error) {
      console.error(`[SnapClass API Error on ${endpoint}]:`, error);
      throw error;
    }
  },

  postForm: async (endpoint, formData) => {
    return window.SnapClass.request(endpoint, {
      method: 'POST',
      body: formData
    });
  },

  postJson: async (endpoint, data) => {
    return window.SnapClass.request(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },

  get: async (endpoint) => {
    return window.SnapClass.request(endpoint, { method: 'GET' });
  }
};

// Tabs Initialization
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const container = btn.closest('.glass-card') || document;
      container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const targetId = btn.dataset.target;
      container.querySelectorAll('.tab-pane').forEach(pane => {
        if (pane.id === targetId) {
          pane.classList.add('active');
        } else {
          pane.classList.remove('active');
        }
      });
    });
  });
});
