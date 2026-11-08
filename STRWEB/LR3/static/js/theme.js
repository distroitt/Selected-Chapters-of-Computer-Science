// Выполняется до отрисовки body, чтобы сохранённая тема не мигала.
try {
  document.documentElement.dataset.theme = localStorage.getItem('petcare.theme') === 'dark' ? 'dark' : 'light';
} catch (_) {
  document.documentElement.dataset.theme = 'light';
}
