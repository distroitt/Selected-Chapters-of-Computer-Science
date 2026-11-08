'use strict';
window.PetCare = {
  read(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch (_) { return fallback; }
  },
  save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch (_) { return false; }
  },
  node(tag, text, attrs = {}) {
    const element = document.createElement(tag);
    if (text !== null && text !== undefined) element.textContent = text;
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    return element;
  },
  pagination(container, page, count, onChange) {
    container.replaceChildren();
    if (!count) return;
    const button = (label, target, disabled = false) => {
      const item = this.node('button', label, {type: 'button'});
      item.disabled = disabled;
      if (target === page && /^\d+$/.test(label)) item.setAttribute('aria-current', 'page');
      item.addEventListener('click', () => onChange(target));
      container.append(item);
    };
    button('Назад', page - 1, page === 1);
    for (let i = 1; i <= count; i++) button(String(i), i);
    button('Далее', page + 1, page === count);
  },
  async request(url, options = {}) {
    const response = await fetch(url, {credentials: 'same-origin', signal: AbortSignal.timeout(15000), ...options});
    const json = (response.headers.get('content-type') || '').includes('application/json');
    const data = json ? await response.json() : {};
    if (!response.ok) {
      const error = new Error(data.error || (response.status === 403
        ? 'Нет доступа. Войдите снова и обновите страницу.' : 'Операция не выполнена. Повторите попытку.'));
      error.fields = data.errors;
      throw error;
    }
    return data;
  },
};
