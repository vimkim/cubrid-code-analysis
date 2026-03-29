function getTheme() { return localStorage.getItem('theme'); }
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  var btn = document.querySelector('.theme-toggle');
  if (btn) btn.textContent = t === 'light' ? 'Dark mode' : 'Light mode';
}
function toggleTheme() {
  var t = getTheme() === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', t);
  applyTheme(t);
}
applyTheme(getTheme() || 'dark');
