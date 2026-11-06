/**
 * PolyShift - Translator Workspace Controller
 * Orchestrates bidirectional translation, intelligence metrics, terminal execution, and editor actions.
 */

class TranslatorController {
  constructor() {
    this.sourceLangSelect = document.getElementById('source-lang-select');
    this.targetLangSelect = document.getElementById('target-lang-select');
    this.translateBtn = document.getElementById('translate-btn');
    this.swapBtn = document.getElementById('swap-languages-btn');
    this.isTranslating = false;

    this.init();
  }

  init() {
    if (this.sourceLangSelect) {
      this.sourceLangSelect.addEventListener('change', (e) => this.onSourceLangChange(e.target.value));
    }
    if (this.targetLangSelect) {
      this.targetLangSelect.addEventListener('change', (e) => this.onTargetLangChange(e.target.value));
    }
    if (this.translateBtn) {
      this.translateBtn.addEventListener('click', () => this.executeTranslation());
    }
    if (this.swapBtn) {
      this.swapBtn.addEventListener('click', () => this.swapLanguages());
    }

    this._bindToolbarButtons();
    this._bindTerminalControls();
  }

  onSourceLangChange(lang) {
    if (lang !== 'auto') {
      window.editorManager.setSourceLanguage(lang);
    }
    this.updateLanguageBadges();
  }

  onTargetLangChange(lang) {
    window.editorManager.setTargetLanguage(lang);
    this.updateLanguageBadges();
  }

  updateLanguageBadges() {
    const srcBadge = document.getElementById('source-lang-badge');
    const tgtBadge = document.getElementById('target-lang-badge');
    if (srcBadge) srcBadge.textContent = this.sourceLangSelect.value.toUpperCase();
    if (tgtBadge) tgtBadge.textContent = this.targetLangSelect.value.toUpperCase();
  }

  swapLanguages() {
    if (!this.sourceLangSelect || !this.targetLangSelect) return;

    let srcVal = this.sourceLangSelect.value;
    const tgtVal = this.targetLangSelect.value;

    if (srcVal === 'auto') {
      srcVal = 'python';
    }

    // Trigger rotate animation
    this.swapBtn.classList.add('swap-animating');
    setTimeout(() => this.swapBtn.classList.remove('swap-animating'), 400);

    // Swap values
    this.sourceLangSelect.value = tgtVal;
    this.targetLangSelect.value = srcVal;

    // Swap code in editors
    const srcCode = window.editorManager.getSourceCode();
    const tgtCode = window.editorManager.getTargetCode();

    if (tgtCode && !tgtCode.startsWith('// Click')) {
      window.editorManager.setSourceCode(tgtCode);
      window.editorManager.setTargetCode(srcCode);
    }

    window.editorManager.setSourceLanguage(tgtVal);
    window.editorManager.setTargetLanguage(srcVal);
    this.updateLanguageBadges();

    window.showToast('Languages swapped successfully.', 'info');
  }

  async executeTranslation() {
    if (this.isTranslating) return;

    const sourceCode = window.editorManager.getSourceCode();
    if (!sourceCode.trim()) {
      window.showToast('Please enter source code to translate.', 'warning');
      return;
    }

    const sourceLang = this.sourceLangSelect.value;
    const targetLang = this.targetLangSelect.value;

    this.setTranslatingState(true);

    try {
      const res = await window.api.translate(sourceCode, sourceLang, targetLang);
      if (res.success) {
        window.editorManager.setTargetCode(res.translated_code);
        this.renderIntelligence(res);
        window.showToast(`Translated to ${res.target_language.toUpperCase()} successfully!`, 'success');
      } else {
        window.showToast(res.warnings[0] || 'Translation failed', 'error');
      }
    } catch (err) {
      window.showToast(err.message || 'Translation error occurred', 'error');
    } finally {
      this.setTranslatingState(false);
    }
  }

  setTranslatingState(loading) {
    this.isTranslating = loading;
    if (!this.translateBtn) return;

    if (loading) {
      this.translateBtn.disabled = true;
      this.translateBtn.innerHTML = `
        <svg class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10"/></svg>
        <span>Translating...</span>
      `;
    } else {
      this.translateBtn.disabled = false;
      this.translateBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        <span>Translate Code</span>
      `;
    }
  }

  renderIntelligence(data) {
    // Confidence & Status
    const statusPill = document.getElementById('intel-status-pill');
    const confVal = document.getElementById('intel-confidence-val');
    const confBar = document.getElementById('intel-confidence-bar');

    if (statusPill) {
      statusPill.textContent = data.status.toUpperCase();
      statusPill.className = `badge badge-${data.status === 'success' ? 'success' : 'warning'}`;
    }
    if (confVal) {
      confVal.textContent = `${Math.round(data.confidence * 100)}%`;
    }
    if (confBar) {
      confBar.style.width = `${Math.round(data.confidence * 100)}%`;
    }

    // AST Counts
    const fnCount = document.getElementById('intel-functions');
    const clsCount = document.getElementById('intel-classes');
    const stmtCount = document.getElementById('intel-statements');

    if (fnCount) fnCount.textContent = data.ast_summary.functions_count || 0;
    if (clsCount) clsCount.textContent = data.ast_summary.classes_count || 0;
    if (stmtCount) stmtCount.textContent = data.ast_summary.statements_count || 0;

    // Semantic Differences
    const semList = document.getElementById('intel-semantics-list');
    if (semList) {
      semList.innerHTML = '';
      if (data.semantic_differences && data.semantic_differences.length > 0) {
        data.semantic_differences.forEach(item => {
          const div = document.createElement('div');
          div.className = 'notice-item notice-info';
          div.innerHTML = `<span>ℹ️</span><div>${item}</div>`;
          semList.appendChild(div);
        });
      } else {
        semList.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">Direct syntax correspondence achieved.</div>';
      }
    }

    // Warnings and Caveats
    const warnList = document.getElementById('intel-warnings-list');
    if (warnList) {
      warnList.innerHTML = '';
      const allNotices = [...(data.warnings || []), ...(data.approximation_notices || [])];
      if (allNotices.length > 0) {
        allNotices.forEach(w => {
          const div = document.createElement('div');
          div.className = 'notice-item notice-warning';
          div.innerHTML = `<span>⚠️</span><div>${w}</div>`;
          warnList.appendChild(div);
        });
      } else {
        warnList.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">No semantic conflicts or approximation caveats detected.</div>';
      }
    }
  }

  _bindToolbarButtons() {
    // Copy Target
    const copyBtn = document.getElementById('btn-copy-target');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const code = window.editorManager.getTargetCode();
        if (code) {
          navigator.clipboard.writeText(code);
          window.showToast('Translated code copied to clipboard!', 'success');
        }
      });
    }

    // Download Target
    const dlBtn = document.getElementById('btn-download-target');
    if (dlBtn) {
      dlBtn.addEventListener('click', () => {
        const code = window.editorManager.getTargetCode();
        const lang = this.targetLangSelect.value;
        const extMap = { python: 'py', cpp: 'cpp', javascript: 'js', rust: 'rs' };
        const ext = extMap[lang] || 'txt';

        const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `translated_code.${ext}`;
        a.click();
        window.showToast(`Downloaded as translated_code.${ext}`, 'info');
      });
    }

    // Upload Source
    const uploadInput = document.getElementById('file-upload-input');
    const uploadBtn = document.getElementById('btn-upload-source');
    if (uploadBtn && uploadInput) {
      uploadBtn.addEventListener('click', () => uploadInput.click());
      uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (evt) => {
            window.editorManager.setSourceCode(evt.target.result);
            window.showToast(`Loaded ${file.name} into editor.`, 'success');
          };
          reader.readAsText(file);
        }
      });
    }

    // Clear Source
    const clearBtn = document.getElementById('btn-clear-source');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        window.editorManager.setSourceCode('');
        window.showToast('Source editor cleared.', 'info');
      });
    }

    // Layout Toggle (Side-by-side vs Stacked)
    const layoutBtn = document.getElementById('btn-toggle-layout');
    const panesContainer = document.querySelector('.editor-panes-container');
    if (layoutBtn && panesContainer) {
      layoutBtn.addEventListener('click', () => {
        panesContainer.classList.toggle('layout-stacked');
        window.editorManager.layout();
        const isStacked = panesContainer.classList.contains('layout-stacked');
        window.showToast(`Layout switched to ${isStacked ? 'stacked' : 'side-by-side'}.`, 'info');
      });
    }

    // Toggle Intelligence Sidebar
    const intelToggle = document.getElementById('btn-toggle-intel');
    const intelSidebar = document.querySelector('.intelligence-sidebar');
    if (intelToggle && intelSidebar) {
      intelToggle.addEventListener('click', () => {
        intelSidebar.classList.toggle('collapsed');
        window.editorManager.layout();
      });
    }
  }

  _bindTerminalControls() {
    // Run Target Code in Sandboxed Subprocess
    const runBtn = document.getElementById('btn-run-code');
    const termBody = document.getElementById('terminal-output-body');
    const termToggle = document.getElementById('terminal-toggle-btn');
    const bottomPanel = document.querySelector('.bottom-terminal-panel');

    if (termToggle && bottomPanel) {
      termToggle.addEventListener('click', () => {
        bottomPanel.classList.toggle('collapsed');
        window.editorManager.layout();
      });
    }

    if (runBtn && termBody) {
      runBtn.addEventListener('click', async () => {
        const code = window.editorManager.getTargetCode();
        const lang = this.targetLangSelect.value;

        if (!code.trim() || code.startsWith('// Click')) {
          window.showToast('Translate code first or provide valid code to run.', 'warning');
          return;
        }

        bottomPanel.classList.remove('collapsed');
        termBody.innerHTML = '<span style="color:var(--text-muted);">Executing in isolated sandbox environment...</span>';

        try {
          const res = await window.api.execute(code, lang);
          let outputHtml = '';

          if (res.stdout) {
            outputHtml += `<div style="color:var(--text-primary);">${this._escapeHtml(res.stdout)}</div>`;
          }
          if (res.stderr) {
            outputHtml += `<div style="color:var(--color-status-error);">${this._escapeHtml(res.stderr)}</div>`;
          }
          if (!res.stdout && !res.stderr) {
            outputHtml += `<div style="color:var(--text-muted);">Process completed with no output.</div>`;
          }

          outputHtml += `\n<div style="color:var(--text-muted);border-top:1px solid var(--border-subtle);padding-top:6px;margin-top:6px;">Status: <span class="badge badge-${res.success ? 'success' : 'error'}">${res.validation_status}</span> | Exit Code: ${res.exit_code} | Time: ${res.execution_time_ms} ms</div>`;

          termBody.innerHTML = outputHtml;
        } catch (err) {
          termBody.innerHTML = `<span style="color:var(--color-status-error);">Execution Error: ${this._escapeHtml(err.message)}</span>`;
        }
      });
    }

    // Validate Syntax Button
    const valBtn = document.getElementById('btn-validate-code');
    if (valBtn && termBody) {
      valBtn.addEventListener('click', async () => {
        const code = window.editorManager.getTargetCode();
        const lang = this.targetLangSelect.value;
        bottomPanel.classList.remove('collapsed');
        termBody.innerHTML = '<span style="color:var(--text-muted);">Running multi-stage syntax and compiler checks...</span>';

        try {
          const res = await window.api.validate(code, lang);
          let html = `<div style="margin-bottom:6px;">Validation Status: <span class="badge badge-${res.valid ? 'success' : 'warning'}">${res.valid ? 'SYNTAX VALID' : 'ERRORS DETECTED'}</span></div>`;
          html += `<div>Host Compiler/Runtime: <span style="color:${res.compiler_available ? 'var(--color-status-success)' : 'var(--color-status-warning)'};">${res.compiler_info}</span></div>`;

          if (res.errors && res.errors.length > 0) {
            html += `<div style="color:var(--color-status-error);margin-top:8px;"><strong>Diagnostic Messages:</strong>\n${this._escapeHtml(res.errors.join('\n'))}</div>`;
          }

          termBody.innerHTML = html;
        } catch (err) {
          termBody.innerHTML = `<span style="color:var(--color-status-error);">Validation Error: ${this._escapeHtml(err.message)}</span>`;
        }
      });
    }
  }

  _escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

window.translatorController = new TranslatorController();

