/**
 * PolyShift - Code Explanation View Controller
 */

class ExplainerController {
  constructor() {
    this.level = 'intermediate';
    this.init();
  }

  init() {
    const explainBtn = document.getElementById('btn-run-explain');
    const levelBtns = document.querySelectorAll('.explain-level-btn');

    levelBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        levelBtns.forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.level = e.currentTarget.dataset.level;
        this.runExplanation();
      });
    });

    if (explainBtn) {
      explainBtn.addEventListener('click', () => this.runExplanation());
    }
  }

  async runExplanation() {
    const code = window.editorManager.getSourceCode();
    const lang = document.getElementById('source-lang-select').value;
    const cleanLang = lang === 'auto' ? 'python' : lang;

    if (!code.trim()) {
      window.showToast('No code available to explain.', 'warning');
      return;
    }

    const container = document.getElementById('explainer-results-container');
    if (container) {
      container.innerHTML = '<div style="padding:20px;color:var(--text-muted);">Generating semantic explanation...</div>';
    }

    try {
      const data = await window.api.explain(code, cleanLang, this.level);
      this.render(data);
    } catch (err) {
      if (container) {
        container.innerHTML = `<div style="padding:20px;color:var(--color-status-error);">Explanation Error: ${err.message}</div>`;
      }
    }
  }

  render(data) {
    const container = document.getElementById('explainer-results-container');
    if (!container) return;

    let stepsHtml = '';
    data.algorithmic_steps.forEach((s) => {
      stepsHtml += `
        <div class="glass-card" style="padding:14px;margin-bottom:10px;">
          <div style="font-weight:600;font-size:14px;color:var(--accent-primary);margin-bottom:4px;">${s.step}</div>
          <div style="font-size:13px;color:var(--text-secondary);">${s.detail}</div>
        </div>
      `;
    });

    let idiomsHtml = '';
    data.language_idioms.forEach(item => {
      idiomsHtml += `<li style="margin-bottom:6px;font-size:13px;color:var(--text-secondary);">${item}</li>`;
    });

    container.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:18px;">
        <div class="glass-panel" style="padding:18px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <h3 style="font-size:16px;font-weight:700;">Executive Summary</h3>
            <span class="badge badge-primary">${data.level.toUpperCase()} LEVEL</span>
          </div>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;">${data.executive_summary}</p>
          <div style="display:flex;gap:16px;margin-top:14px;border-top:1px solid var(--border-subtle);padding-top:12px;">
            <div><span style="font-size:11px;color:var(--text-muted);display:block;">TIME COMPLEXITY</span><strong style="font-family:var(--font-mono);color:var(--color-cyan-400);">${data.time_complexity}</strong></div>
            <div><span style="font-size:11px;color:var(--text-muted);display:block;">SPACE COMPLEXITY</span><strong style="font-family:var(--font-mono);color:var(--color-violet-400);">${data.space_complexity}</strong></div>
          </div>
        </div>

        <div>
          <h4 style="font-size:14px;font-weight:700;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);">Algorithmic Execution Path</h4>
          ${stepsHtml}
        </div>

        <div class="glass-card" style="padding:16px;">
          <h4 style="font-size:14px;font-weight:700;margin-bottom:8px;color:var(--text-primary);">Language Idioms & Characteristics</h4>
          <ul style="padding-left:20px;">
            ${idiomsHtml}
          </ul>
        </div>
      </div>
    `;
  }
}

window.explainerController = new ExplainerController();

