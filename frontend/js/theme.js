/**
 * PolyShift - Theme Management Subsystem
 * Handles dark/light theme switching, persistence, and Monaco Editor synchronization.
 */

class ThemeManager {
  constructor() {
    this.theme = localStorage.getItem('polyshift_theme') || 'dark';
    this.init();
  }

  init() {
    this.applyTheme(this.theme);
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => this.toggleTheme());
    }
  }

  applyTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('polyshift_theme', theme);

    // Update icon if present
    const icon = document.getElementById('theme-toggle-icon');
    if (icon) {
      icon.innerHTML = theme === 'dark' 
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
    }

    // Synchronize Monaco Editor theme if Monaco is ready
    if (window.monaco && window.monaco.editor) {
      window.monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
    }

    window.dispatchEvent(new CustomEvent('polyshift:themechange', { detail: { theme } }));
  }

  toggleTheme() {
    const nextTheme = this.theme === 'dark' ? 'light' : 'dark';
    this.applyTheme(nextTheme);
  }

  getMonacoTheme() {
    return this.theme === 'dark' ? 'vs-dark' : 'vs';
  }
}

window.themeManager = new ThemeManager();
