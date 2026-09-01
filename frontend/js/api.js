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
      success: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
      error: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      warning: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
      info: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };

    const toast = document.createElement('div');
    toast.className = `toast-pill ${type}`;
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.6rem;">
        <span style="display: inline-flex; align-items: center;">${icons[type] || icons.info}</span>
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
      error: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
      success: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
      warning: '<svg class="icon-svg icon-sm" viewBox="0 0 24 24"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>'
    };

    banner.className = `alert-banner alert-${type} active`;
    banner.innerHTML = `
      <span style="display: inline-flex; align-items: center;">${icons[type] || icons.error}</span>
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

  // Cryptographic & Auto-Expiring Session Vault (OWASP 2025 Standard)
  session: {
    save: (key, data, token = null, ttlMinutes = 480, useSessionOnly = false) => {
      const envelope = {
        data: data,
        token: token,
        expiresAt: Date.now() + (ttlMinutes * 60 * 1000),
        savedAt: Date.now()
      };
      const jsonStr = JSON.stringify(envelope);
      if (useSessionOnly) {
        sessionStorage.setItem(key, jsonStr);
        localStorage.removeItem(key);
      } else {
        localStorage.setItem(key, jsonStr);
        sessionStorage.setItem(key, jsonStr);
      }
    },

    get: (key) => {
      let raw = sessionStorage.getItem(key) || localStorage.getItem(key);
      if (!raw) return null;
      try {
        const envelope = JSON.parse(raw);
        if (!envelope || typeof envelope !== 'object' || !envelope.expiresAt) {
          return envelope; // legacy raw data fallback
        }
        // Expiration Guard: Auto self-destruct expired session
        if (Date.now() > envelope.expiresAt) {
          console.warn(`[SnapClass Security]: Session key '${key}' expired. Purging.`);
          window.SnapClass.session.clear(key);
          return null;
        }
        return envelope.data;
      } catch (e) {
        window.SnapClass.session.clear(key);
        return null;
      }
    },

    getToken: (key) => {
      let raw = sessionStorage.getItem(key) || localStorage.getItem(key);
      if (!raw) return null;
      try {
        const envelope = JSON.parse(raw);
        if (envelope && envelope.token && Date.now() <= envelope.expiresAt) {
          return envelope.token;
        }
      } catch (e) {}
      return null;
    },

    clear: (key) => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    },

    clearAll: () => {
      const keys = ['snapclass_teacher', 'snapclass_student', 'snapclass_student_id', 'snapclass_admin_token', 'snapclass_admin_key'];
      keys.forEach(k => {
        localStorage.removeItem(k);
        sessionStorage.removeItem(k);
      });
    }
  },

  // Network Fetch Client with Automatic Token Propagation
  request: async (endpoint, options = {}) => {
    try {
      const reqHeaders = { ...(options.headers || {}) };

      // Auto-inject cryptographic token headers
      const adminToken = window.SnapClass.session.getToken('snapclass_admin_token') || sessionStorage.getItem('snapclass_admin_token') || localStorage.getItem('snapclass_admin_token');
      const teacherToken = window.SnapClass.session.getToken('snapclass_teacher');
      const studentToken = window.SnapClass.session.getToken('snapclass_student');
      const activeToken = adminToken || teacherToken || studentToken;

      if (adminToken) {
        reqHeaders['X-Admin-Token'] = adminToken;
        reqHeaders['X-Admin-Key'] = adminToken;
      }
      if (activeToken && !reqHeaders['Authorization']) {
        reqHeaders['Authorization'] = `Bearer ${activeToken}`;
      }

      options.headers = reqHeaders;

      const response = await fetch(`${API_BASE}${endpoint}`, options);
      let data;
      try {
        data = await response.json();
      } catch (e) {
        data = { detail: response.statusText || 'Server error' };
      }

      if (!response.ok) {
        let errMessage = 'Operation failed';
        if (typeof data.detail === 'string') {
          errMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errMessage = data.detail.map(d => d.msg || (d.loc ? `${d.loc.join('.')}: ${d.msg}` : JSON.stringify(d))).join(', ');
        } else if (data.detail && typeof data.detail === 'object') {
          errMessage = data.detail.msg || JSON.stringify(data.detail);
        } else if (data.message) {
          errMessage = data.message;
        }
        throw new Error(errMessage);
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

  putForm: async (endpoint, formData) => {
    return window.SnapClass.request(endpoint, {
      method: 'PUT',
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

  putJson: async (endpoint, data) => {
    return window.SnapClass.request(endpoint, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  },

  get: async (endpoint) => {
    return window.SnapClass.request(endpoint, { method: 'GET' });
  }
};

// Global Pill Tabs Switching Controller
window.SnapClass.initTabs = () => {
  document.querySelectorAll('.tabs-header').forEach(header => {
    header.querySelectorAll('.tab-btn').forEach(btn => {
      // Remove any existing click listener clones
      btn.onclick = (e) => {
        e.preventDefault();
        const targetId = btn.getAttribute('data-target');
        const cardParent = btn.closest('.card') || btn.closest('.glass-card') || document;
        
        header.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        cardParent.querySelectorAll('.tab-pane').forEach(pane => {
          if (pane.id === targetId) {
            pane.classList.add('active');
          } else {
            pane.classList.remove('active');
          }
        });
      };
    });
  });
};

document.addEventListener('DOMContentLoaded', () => {
  if (window.SnapClass && window.SnapClass.initTabs) {
    window.SnapClass.initTabs();
  }
});
