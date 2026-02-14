const THEME_KEY = 'theme';
const THEME_LINK_ID = 'theme-style';

function applyTheme(theme) {
  const link = document.getElementById(THEME_LINK_ID);
  if (!link) return;

  // cache-busting, иначе Firefox делает вид что ничего не менялось
  link.href = `css/${theme}.css?v=${Date.now()}`;
}

function toggleTheme() {
  const current = localStorage.getItem(THEME_KEY) || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';

  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
}

// инициализация при загрузке страницы
(function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(saved);
})();
