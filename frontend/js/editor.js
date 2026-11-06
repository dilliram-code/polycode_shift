/**
 * PolyShift - Monaco Editor Subsystem
 * Initializes and orchestrates Monaco instances for source, target, and diff viewing.
 */

class EditorManager {
  constructor() {
    this.sourceEditor = null;
    this.targetEditor = null;
    this.diffEditor = null;
    this.isReady = false;
    this._initCallbacks = [];
  }

  init() {
    return new Promise((resolve) => {
      if (window.monaco) {
        this._setupEditors();
        resolve();
        return;
      }

      if (window.require) {
        window.require.config({
          paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }
        });

        window.require(['vs/editor/editor.main'], () => {
          this._setupEditors();
          resolve();
        });
      } else {
        console.warn('Monaco require loader not found, will retry on window load.');
        window.addEventListener('load', () => this.init().then(resolve));
      }
    });
  }

  _setupEditors() {
    const theme = window.themeManager ? window.themeManager.getMonacoTheme() : 'vs-dark';

    // Source Editor
    const srcContainer = document.getElementById('source-editor-container');
    if (srcContainer) {
      this.sourceEditor = window.monaco.editor.create(srcContainer, {
        value: `def calculate_fibonacci(n: int) -> int:\n    """Calculates n-th Fibonacci number."""\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)\n\nprint(calculate_fibonacci(10))`,
        language: 'python',
        theme: theme,
        automaticLayout: true,
        fontSize: 13,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace",
        lineHeight: 20,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        roundedSelection: true,
        padding: { top: 12, bottom: 12 }
      });

      this.sourceEditor.onDidChangeCursorPosition((e) => {
        this._updateStatusBar('source', e.position);
      });
      this.sourceEditor.onDidChangeModelContent(() => {
        this._updateStatusBar('source', this.sourceEditor.getPosition());
      });
      this._updateStatusBar('source', { lineNumber: 1, column: 1 });
    }

    // Target Editor
    const tgtContainer = document.getElementById('target-editor-container');
    if (tgtContainer) {
      this.targetEditor = window.monaco.editor.create(tgtContainer, {
        value: `// Click 'Translate Code' to generate target translation`,
        language: 'cpp',
        theme: theme,
        automaticLayout: true,
        fontSize: 13,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace",
        lineHeight: 20,
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        roundedSelection: true,
        padding: { top: 12, bottom: 12 }
      });

      this.targetEditor.onDidChangeCursorPosition((e) => {
        this._updateStatusBar('target', e.position);
      });
      this.targetEditor.onDidChangeModelContent(() => {
        this._updateStatusBar('target', this.targetEditor.getPosition());
      });
      this._updateStatusBar('target', { lineNumber: 1, column: 1 });
    }

    this.isReady = true;
    window.addEventListener('resize', () => this.layout());

    // Listen to theme changes
    window.addEventListener('polyshift:themechange', (e) => {
      const monacoTheme = e.detail.theme === 'dark' ? 'vs-dark' : 'vs';
      window.monaco.editor.setTheme(monacoTheme);
    });

    this._initCallbacks.forEach(cb => cb());
  }

  onReady(callback) {
    if (this.isReady) {
      callback();
    } else {
      this._initCallbacks.push(callback);
    }
  }

  _mapMonacoLanguage(lang) {
    const l = (lang || '').toLowerCase();
    if (l === 'cpp' || l === 'c++') return 'cpp';
    if (l === 'javascript' || l === 'js') return 'javascript';
    if (l === 'python') return 'python';
    if (l === 'rust') return 'rust';
    return 'plaintext';
  }

  setSourceLanguage(lang) {
    if (!this.sourceEditor) return;
    const model = this.sourceEditor.getModel();
    if (model) {
      window.monaco.editor.setModelLanguage(model, this._mapMonacoLanguage(lang));
    }
  }

  setTargetLanguage(lang) {
    if (!this.targetEditor) return;
    const model = this.targetEditor.getModel();
    if (model) {
      window.monaco.editor.setModelLanguage(model, this._mapMonacoLanguage(lang));
    }
  }

  getSourceCode() {
    return this.sourceEditor ? this.sourceEditor.getValue() : '';
  }

  setSourceCode(code) {
    if (this.sourceEditor) {
      this.sourceEditor.setValue(code);
    }
  }

  getTargetCode() {
    return this.targetEditor ? this.targetEditor.getValue() : '';
  }

  setTargetCode(code) {
    if (this.targetEditor) {
      this.targetEditor.setValue(code);
    }
  }

  layout() {
    if (this.sourceEditor) this.sourceEditor.layout();
    if (this.targetEditor) this.targetEditor.layout();
    if (this.diffEditor) this.diffEditor.layout();
  }

  _updateStatusBar(type, pos) {
    const editor = type === 'source' ? this.sourceEditor : this.targetEditor;
    if (!editor) return;

    const model = editor.getModel();
    if (!model) return;

    const lineCount = model.getLineCount();
    const charCount = model.getValueLength();

    const lineColEl = document.getElementById(`${type}-line-col`);
    const charCountEl = document.getElementById(`${type}-char-count`);

    if (lineColEl) {
      lineColEl.textContent = `Ln ${pos.lineNumber}, Col ${pos.column}`;
    }
    if (charCountEl) {
      charCountEl.textContent = `${charCount} chars (${lineCount} lines)`;
    }
  }

  // Setup Diff Editor for Comparison View
  setupDiffEditor(containerId, originalCode, modifiedCode, origLang, modLang) {
    if (!window.monaco) return;
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    const theme = window.themeManager ? window.themeManager.getMonacoTheme() : 'vs-dark';

    this.diffEditor = window.monaco.editor.createDiffEditor(container, {
      theme: theme,
      automaticLayout: true,
      fontSize: 13,
      fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace",
      readOnly: true
    });

    const origModel = window.monaco.editor.createModel(originalCode, this._mapMonacoLanguage(origLang));
    const modModel = window.monaco.editor.createModel(modifiedCode, this._mapMonacoLanguage(modLang));

    this.diffEditor.setModel({
      original: origModel,
      modified: modModel
    });
  }
}

window.editorManager = new EditorManager();
