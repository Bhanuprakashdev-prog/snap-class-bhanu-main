const API_BASE = '/api';

window.SnapClassAPI = {
    showToast: (message, type = 'success') => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Remove after animation (3 seconds total)
        setTimeout(() => {
            if(container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 3000);
    },

    request: async (endpoint, options = {}) => {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, options);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || data.message || 'API Error');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            window.SnapClassAPI.showToast(error.message, 'error');
            throw error;
        }
    },
    
    postForm: async (endpoint, formData) => {
        return window.SnapClassAPI.request(endpoint, {
            method: 'POST',
            body: formData
        });
    },

    postJson: async (endpoint, data) => {
        return window.SnapClassAPI.request(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    },
    
    get: async (endpoint) => {
        return window.SnapClassAPI.request(endpoint, {
            method: 'GET'
        });
    }
};

// Utilities for UI
window.Tabs = {
    init: () => {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active from all tabs in this group
                const group = tab.parentElement;
                group.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                
                // Add active to clicked tab
                tab.classList.add('active');
                
                // Hide all panes
                const targetId = tab.dataset.target;
                const panesContainer = tab.closest('.container').querySelector('.tab-panes') || document;
                
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    if (pane.id === targetId) {
                        pane.classList.add('active');
                    } else {
                        pane.classList.remove('active');
                    }
                });
            });
        });
    }
};

// Auto init
document.addEventListener('DOMContentLoaded', () => {
    window.Tabs.init();
});
