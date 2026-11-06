/**
 * PolyShift - Application Orchestrator & View Router
 */

class App {
  constructor() {
    this.currentView = 'landing';
    this.init();
  }

  async init() {
    this._bindNavigation();
    this._bindKeyboardShortcuts();
    this._bindModals();
    this.loadStats();

    // Initialize Monaco
    await window.editorManager.init();

    // Check if initial hash is set
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(`view-${hash}`)) {
      this.switchView(hash);
    } else {
      this.switchView('landing');
    }
  }

  _bindNavigation() {
    document.querySelectorAll('[data-view-target]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const target = e.currentTarget.dataset.viewTarget;
        this.switchView(target);
      });
    });
  }

  switchView(viewName) {
    const targetPane = document.getElementById(`view-${viewName}`);
    if (!targetPane) return;

    this.currentView = viewName;
    window.location.hash = viewName;

    // Toggle active pane
    document.querySelectorAll('.view-pane').forEach(p => p.classList.remove('active'));
    targetPane.classList.add('active');

    // Toggle sidebar active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.dataset.viewTarget === viewName) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Trigger sub-controllers if entering their views
    if (viewName === 'comparison') {
      window.comparatorController.updateComparison();
    } else if (viewName === 'history') {
      window.historyController.loadHistory();
    } else if (viewName === 'translator') {
      setTimeout(() => window.editorManager.layout(), 50);
    }
  }

  _bindKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey;

      // Ctrl/Cmd + Enter -> Translate
      if (isCmdOrCtrl && e.key === 'Enter') {
        e.preventDefault();
        if (this.currentView === 'translator') {
          window.translatorController.executeTranslation();
        } else {
          this.switchView('translator');
          setTimeout(() => window.translatorController.executeTranslation(), 100);
        }
      }

      // Ctrl/Cmd + Shift + S -> Swap languages
      if (isCmdOrCtrl && e.shiftKey && (e.key === 'S' || e.key === 's')) {
        e.preventDefault();
        window.translatorController.swapLanguages();
      }

      // Ctrl/Cmd + B -> Toggle Intelligence Sidebar
      if (isCmdOrCtrl && (e.key === 'b' || e.key === 'B')) {
        e.preventDefault();
        const sidebar = document.querySelector('.intelligence-sidebar');
        if (sidebar) {
          sidebar.classList.toggle('collapsed');
          window.editorManager.layout();
        }
      }

      // Escape -> Close active modal
      if (e.key === 'Escape') {
        this.closeAllModals();
      }
    });
  }

  _bindModals() {
    // Shortcuts Modal
    const shortcutsBtn = document.getElementById('btn-open-shortcuts');
    const shortcutsModal = document.getElementById('modal-shortcuts');
    if (shortcutsBtn && shortcutsModal) {
      shortcutsBtn.addEventListener('click', () => shortcutsModal.classList.add('active'));
    }

    // Settings Modal
    const settingsBtn = document.getElementById('btn-open-settings');
    const settingsModal = document.getElementById('modal-settings');
    if (settingsBtn && settingsModal) {
      settingsBtn.addEventListener('click', () => settingsModal.classList.add('active'));
    }

    // Modal Close buttons
    document.querySelectorAll('.btn-close-modal, .modal-overlay').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target === el) {
          this.closeAllModals();
        }
      });
    });
  }

  closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
  }

  async loadStats() {
    try {
      const stats = await window.api.getStats();
      const countEl = document.getElementById('stats-total-translations');
      const rateEl = document.getElementById('stats-success-rate');
      if (countEl) countEl.textContent = stats.total_translations || '12';
      if (rateEl) rateEl.textContent = `${stats.success_rate_percent}%`;
    } catch (err) {
      console.warn('Failed to fetch platform stats:', err);
    }
  }
}

// Global Toast System
window.showToast = function(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: '💡'
  };

  toast.innerHTML = `
    <span>${icons[type] || '💡'}</span>
    <div style="flex:1;">${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 250);
  }, 3500);
};

window.switchView = function(viewName) {
  if (window.appInstance) {
    window.appInstance.switchView(viewName);
  }
};

window.addEventListener('DOMContentLoaded', () => {
  window.appInstance = new App();
});

