/**
 * PolyShift - Central API Client
 * Manages all communication with the FastAPI backend.
 */

const API_BASE = '/api/v1';

class PolyShiftAPI {
  async _request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        let errDetail = 'API request failed';
        try {
          const errData = await response.json();
          errDetail = errData.detail || errData.error || errDetail;
        } catch (_) {}
        throw new Error(errDetail);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error on ${endpoint}:`, error);
      throw error;
    }
  }

  // Translation
  async translate(sourceCode, sourceLang, targetLang, useAi = false, title = null) {
    return this._request('/translate', {
      method: 'POST',
      body: JSON.stringify({
        source_code: sourceCode,
        source_language: sourceLang,
        target_language: targetLang,
        use_ai: useAi,
        title: title
      })
    });
  }

  // Analysis
  async analyze(code, language) {
    return this._request('/analyze', {
      method: 'POST',
      body: JSON.stringify({ code, language })
    });
  }

  // Explainer
  async explain(code, language, level = 'intermediate') {
    return this._request('/explain', {
      method: 'POST',
      body: JSON.stringify({ code, language, level })
    });
  }

  // Optimizer
  async optimize(code, language) {
    return this._request('/optimize', {
      method: 'POST',
      body: JSON.stringify({ code, language })
    });
  }

  // Comparison
  async compare(sourceCode, targetCode, sourceLang, targetLang) {
    return this._request('/compare', {
      method: 'POST',
      body: JSON.stringify({
        source_code: sourceCode,
        target_code: targetCode,
        source_language: sourceLang,
        target_language: targetLang
      })
    });
  }

  // Validation
  async validate(code, language) {
    return this._request('/validate', {
      method: 'POST',
      body: JSON.stringify({ code, language })
    });
  }

  // Execution
  async execute(code, language, timeout = 5) {
    return this._request('/execute', {
      method: 'POST',
      body: JSON.stringify({ code, language, timeout })
    });
  }

  // History
  async getHistory(q = null, sourceLang = null, targetLang = null, bookmarkedOnly = false) {
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    if (sourceLang) params.append('source_lang', sourceLang);
    if (targetLang) params.append('target_lang', targetLang);
    if (bookmarkedOnly) params.append('bookmarked_only', 'true');
    return this._request(`/history?${params.toString()}`);
  }

  async deleteHistory(id) {
    return this._request(`/history/${id}`, { method: 'DELETE' });
  }

  async toggleBookmark(id) {
    return this._request(`/history/${id}/bookmark`, { method: 'POST' });
  }

  // Examples
  async getExamples(category = null) {
    const endpoint = category ? `/examples?category=${encodeURIComponent(category)}` : '/examples';
    return this._request(endpoint);
  }

  async getExampleById(id) {
    return this._request(`/examples/${id}`);
  }

  // Stats and Health
  async getStats() {
    return this._request('/stats');
  }

  async getHealth() {
    return this._request('/health');
  }
}

window.api = new PolyShiftAPI();
