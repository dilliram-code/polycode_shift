/**
 * PolyShift - Example Library View Controller
 */

class ExamplesController {
  constructor() {
    this.allExamples = [];
    this.selectedExample = null;
    this.previewLanguage = 'python';
    this.init();
  }

  async init() {
    this.loadExamples();

    // Language Preview Tabs
    const langTabs = document.querySelectorAll('.example-lang-tab');
    langTabs.forEach(tab => {
      tab.addEventListener('click', (e) => {
        langTabs.forEach(t => t.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.previewLanguage = e.currentTarget.dataset.lang;
        this.updatePreview();
      });
    });

    // Load into Workspace button
    const loadBtn = document.getElementById('btn-load-example-workspace');
    if (loadBtn) {
      loadBtn.addEventListener('click', () => {
        if (this.selectedExample) {
          const codeKey = `${this.previewLanguage}_code`;
          const code = this.selectedExample[codeKey];
          window.editorManager.setSourceCode(code);
          const srcSelect = document.getElementById('source-lang-select');
          if (srcSelect) {
            srcSelect.value = this.previewLanguage;
            window.editorManager.setSourceLanguage(this.previewLanguage);
            window.translatorController.updateLanguageBadges();
          }
          window.showToast(`Loaded "${this.selectedExample.title}" into Workspace!`, 'success');
          window.switchView('translator');
        }
      });
    }

    // Search filter
    const searchInput = document.getElementById('example-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.filterExamples(e.target.value));
    }
  }

  async loadExamples() {
    try {
      this.allExamples = await window.api.getExamples();
      this.renderExampleList(this.allExamples);
      if (this.allExamples.length > 0) {
        this.selectExample(this.allExamples[0]);
      }
    } catch (err) {
      console.error('Failed to load examples:', err);
    }
  }

  renderExampleList(examples) {
    const listContainer = document.getElementById('examples-list-container');
    if (!listContainer) return;

    listContainer.innerHTML = '';
    examples.forEach(ex => {
      const card = document.createElement('div');
      card.className = `glass-card example-card ${this.selectedExample && this.selectedExample.id === ex.id ? 'active' : ''}`;
      card.style.padding = '12px 14px';
      card.style.cursor = 'pointer';
      card.style.marginBottom = '8px';
      card.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
          <strong style="font-size:13px;color:var(--text-primary);">${ex.title}</strong>
          <span class="badge badge-info" style="font-size:10px;">${ex.difficulty}</span>
        </div>
        <div style="font-size:11px;color:var(--text-muted);">${ex.category}</div>
      `;
      card.addEventListener('click', () => {
        document.querySelectorAll('.example-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');
        this.selectExample(ex);
      });
      listContainer.appendChild(card);
    });
  }

  filterExamples(keyword) {
    const q = keyword.toLowerCase().trim();
    if (!q) {
      this.renderExampleList(this.allExamples);
      return;
    }
    const filtered = this.allExamples.filter(e => 
      e.title.toLowerCase().includes(q) || 
      e.category.toLowerCase().includes(q) ||
      (e.description && e.description.toLowerCase().includes(q))
    );
    this.renderExampleList(filtered);
  }

  selectExample(ex) {
    this.selectedExample = ex;
    const titleEl = document.getElementById('selected-example-title');
    const descEl = document.getElementById('selected-example-desc');
    const catEl = document.getElementById('selected-example-category');

    if (titleEl) titleEl.textContent = ex.title;
    if (descEl) descEl.textContent = ex.description;
    if (catEl) catEl.textContent = ex.category;

    this.updatePreview();
  }

  updatePreview() {
    if (!this.selectedExample) return;
    const codeContainer = document.getElementById('example-code-preview');
    if (codeContainer) {
      const codeKey = `${this.previewLanguage}_code`;
      codeContainer.textContent = this.selectedExample[codeKey] || '// Code unavailable';
    }
  }
}

window.examplesController = new ExamplesController();

