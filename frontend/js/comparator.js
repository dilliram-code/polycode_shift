/**
 * PolyShift - Code Comparison View Controller
 */

class ComparatorController {
  constructor() {
    this.init();
  }

  init() {
    const refreshBtn = document.getElementById('btn-refresh-comparison');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.updateComparison());
    }
  }

  async updateComparison() {
    const srcCode = window.editorManager.getSourceCode();
    const tgtCode = window.editorManager.getTargetCode();
    const srcLang = document.getElementById('source-lang-select').value;
    const tgtLang = document.getElementById('target-lang-select').value;

    const cleanSrcLang = srcLang === 'auto' ? 'python' : srcLang;

    // Initialize Monaco Diff Editor
    window.editorManager.setupDiffEditor(
      'monaco-diff-container',
      srcCode,
      tgtCode,
      cleanSrcLang,
      tgtLang
    );

    // Call comparison API for metrics
    try {
      const res = await window.api.compare(srcCode, tgtCode, cleanSrcLang, tgtLang);
      this.renderMetrics(res);
    } catch (err) {
      console.warn('Comparison metrics computation error:', err);
    }
  }

  renderMetrics(data) {
    const simEl = document.getElementById('diff-similarity-ratio');
    const addedEl = document.getElementById('diff-lines-added');
    const removedEl = document.getElementById('diff-lines-removed');
    const mappingsContainer = document.getElementById('diff-construct-mappings');

    if (simEl) simEl.textContent = `${Math.round(data.similarity_ratio * 100)}%`;
    if (addedEl) addedEl.textContent = `+${data.added_lines}`;
    if (removedEl) removedEl.textContent = `-${data.removed_lines}`;

    if (mappingsContainer) {
      mappingsContainer.innerHTML = '';
      if (data.construct_mappings && data.construct_mappings.length > 0) {
        data.construct_mappings.forEach(m => {
          const item = document.createElement('div');
          item.className = 'glass-card';
          item.style.padding = '10px 14px';
          item.style.marginBottom = '8px';
          item.innerHTML = `
            <div style="font-size:12px;font-family:var(--font-mono);margin-bottom:4px;">
              <span style="color:var(--color-coral-500);">${m.source_construct}</span>
              &nbsp;→&nbsp;
              <span style="color:var(--color-emerald-500);">${m.target_construct}</span>
            </div>
            <div style="font-size:12px;color:var(--text-muted);">${m.description}</div>
          `;
          mappingsContainer.appendChild(item);
        });
      } else {
        mappingsContainer.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">Construct alignment verified.</div>';
      }
    }
  }
}

window.comparatorController = new ComparatorController();

