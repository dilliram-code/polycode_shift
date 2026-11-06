/**
 * PolyShift - Translation History Controller
 */

class HistoryController {
  constructor() {
    this.init();
  }

  init() {
    this.loadHistory();

    const searchInput = document.getElementById('history-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.loadHistory(e.target.value));
    }

    const exportJsonBtn = document.getElementById('btn-export-history-json');
    if (exportJsonBtn) {
      exportJsonBtn.addEventListener('click', () => {
        window.open('/api/v1/history/export?format=json', '_blank');
      });
    }

    const exportCsvBtn = document.getElementById('btn-export-history-csv');
    if (exportCsvBtn) {
      exportCsvBtn.addEventListener('click', () => {
        window.open('/api/v1/history/export?format=csv', '_blank');
      });
    }
  }

  async loadHistory(searchKeyword = null) {
    const listContainer = document.getElementById('history-items-container');
    if (!listContainer) return;

    try {
      const items = await window.api.getHistory(searchKeyword);
      if (items.length === 0) {
        listContainer.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);">No translation history recorded yet.</div>';
        return;
      }

      listContainer.innerHTML = '';
      items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'glass-card';
        row.style.padding = '16px';
        row.style.marginBottom = '12px';
        row.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="badge badge-${item.source_language}">${item.source_language.toUpperCase()}</span>
              <span style="color:var(--text-muted);">→</span>
              <span class="badge badge-${item.target_language}">${item.target_language.toUpperCase()}</span>
              <strong style="font-size:14px;color:var(--text-primary);margin-left:6px;">${item.title || 'Translation'}</strong>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="badge badge-${item.translation_status.includes('success') ? 'success' : 'warning'}">${item.translation_status.toUpperCase()}</span>
              <button class="btn-icon btn-bookmark ${item.is_bookmarked ? 'bookmarked' : ''}" title="Bookmark">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="${item.is_bookmarked ? 'var(--color-amber-500)' : 'none'}" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </button>
              <button class="btn btn-secondary btn-restore" style="height:28px;padding:0 10px;font-size:12px;">Restore</button>
              <button class="btn-icon btn-delete" title="Delete" style="color:var(--color-status-error);">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>
          </div>
          <div style="font-size:12px;color:var(--text-muted);font-family:var(--font-mono);background:var(--bg-surface-translucent);padding:8px;border-radius:var(--radius-sm);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            ${item.source_code.split('\n')[0] || ''}
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:6px;">
            ${new Date(item.created_at).toLocaleString()} • Confidence: ${Math.round(item.confidence_score * 100)}%
          </div>
        `;

        // Restore event
        row.querySelector('.btn-restore').addEventListener('click', () => {
          window.editorManager.setSourceCode(item.source_code);
          window.editorManager.setTargetCode(item.target_code);
          const srcSelect = document.getElementById('source-lang-select');
          const tgtSelect = document.getElementById('target-lang-select');
          if (srcSelect) srcSelect.value = item.source_language;
          if (tgtSelect) tgtSelect.value = item.target_language;
          window.editorManager.setSourceLanguage(item.source_language);
          window.editorManager.setTargetLanguage(item.target_language);
          window.translatorController.updateLanguageBadges();
          window.showToast('Translation restored into workspace!', 'success');
          window.switchView('translator');
        });

        // Bookmark toggle
        row.querySelector('.btn-bookmark').addEventListener('click', async () => {
          await window.api.toggleBookmark(item.id);
          this.loadHistory();
        });

        // Delete event
        row.querySelector('.btn-delete').addEventListener('click', async () => {
          await window.api.deleteHistory(item.id);
          window.showToast('Item deleted from history.', 'info');
          this.loadHistory();
        });

        listContainer.appendChild(row);
      });
    } catch (err) {
      console.error('History load error:', err);
    }
  }
}

window.historyController = new HistoryController();
