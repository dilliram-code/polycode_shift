/**
 * PolyShift - Code Optimizer Controller
 */

class OptimizerController {
  constructor() {
    this.latestOptimizedCode = '';
    this.init();
  }

  init() {
    const runBtn = document.getElementById('btn-run-optimizer');
    if (runBtn) {
      runBtn.addEventListener('click', () => this.runOptimization());
    }

    const applyBtn = document.getElementById('btn-apply-optimized');
    if (applyBtn) {
      applyBtn.addEventListener('click', () => {
        if (this.latestOptimizedCode) {
          window.editorManager.setSourceCode(this.latestOptimizedCode);
          window.showToast('Optimized code applied to Source Editor!', 'success');
          window.switchView('translator');
        }
      });
    }
  }

  async runOptimization() {
    const code = window.editorManager.getSourceCode();
    const lang = document.getElementById('source-lang-select').value;
    const cleanLang = lang === 'auto' ? 'python' : lang;

    if (!code.trim()) {
      window.showToast('No code available to optimize.', 'warning');
      return;
    }

    const listContainer = document.getElementById('optimizations-list');
    const previewContainer = document.getElementById('optimized-code-preview');
    if (listContainer) listContainer.innerHTML = '<div style="color:var(--text-muted);">Analyzing code for performance gains...</div>';

    try {
      const data = await window.api.optimize(code, cleanLang);
      this.latestOptimizedCode = data.suggested_code;
      this.render(data);
    } catch (err) {
      if (listContainer) {
        listContainer.innerHTML = `<div style="color:var(--color-status-error);">Optimization Analysis Error: ${err.message}</div>`;
      }
    }
  }

  render(data) {
    const listContainer = document.getElementById('optimizations-list');
    const previewContainer = document.getElementById('optimized-code-preview');
    const countBadge = document.getElementById('optimizations-count-badge');

    if (countBadge) {
      countBadge.textContent = `${data.optimizations_count} FOUND`;
    }

    if (listContainer) {
      listContainer.innerHTML = '';
      data.optimizations.forEach(opt => {
        const div = document.createElement('div');
        div.className = 'glass-card';
        div.style.padding = '14px';
        div.style.marginBottom = '12px';
        div.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <strong style="color:var(--text-primary);font-size:14px;">${opt.type}</strong>
            <span class="badge badge-warning">${opt.impact}</span>
          </div>
          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;">${opt.description}</p>
          <div style="font-size:12px;color:var(--text-muted);"><strong>Trade-off:</strong> ${opt.tradeoff}</div>
        `;
        listContainer.appendChild(div);
      });
    }

    if (previewContainer) {
      previewContainer.textContent = data.suggested_code;
    }

    const applyBtn = document.getElementById('btn-apply-optimized');
    if (applyBtn) {
      applyBtn.disabled = false;
    }
  }
}

window.optimizerController = new OptimizerController();

