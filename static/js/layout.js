async function loadContent() {
  const lang = localStorage.getItem('lang') || 'ru';

  const response = await fetch(`/static/content/${lang}.json?v=1`);
  const data = await response.json();

  document.querySelectorAll('[data-key]').forEach(el => {
    const key = el.dataset.key;
    if (data[key]) el.textContent = data[key];
  });
  
  renderList('skills_backend', data.skills_backend);
  renderList('skills_frontend', data.skills_frontend);
  renderList('skills_infrastructure', data.skills_infrastructure);
  renderList('skills_industrial', data.skills_industrial);
  renderList('about_highlights', data.about_highlights);
 
  function renderList(id, items) {
    const container = document.getElementById(id);
    if (!container || !items) return;

    container.innerHTML = '';
    items.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      container.appendChild(li);
    });
  }

  const projects = document.getElementById('projects');
  if (projects && data.projects) {
    projects.innerHTML = '';
    data.projects.forEach(p => {
      projects.innerHTML += `
        <a class="card" href="project.html?id=${p.id}">
          <h3>${p.title}</h3>
          <p>${p.desc}</p>
          <small>${p.stack}</small>
        </a>`;
    });
  }
}

function setActiveNav() {
  const currentPath = window.location.pathname.replace(/\/$/, '');

  document.querySelectorAll('nav a').forEach(link => {
    const linkPath = new URL(link.href).pathname.replace(/\/$/, '');

    if (linkPath === currentPath) {
      link.classList.add('active');
    }
  });
}

document.addEventListener('DOMContentLoaded', setActiveNav);


window.toggleLang = () => {
  const current = localStorage.getItem('lang') || 'ru';
  const next = current === 'ru' ? 'en' : 'ru';
  localStorage.setItem('lang', next);
  location.reload();
};

function updateLangLabel() {
  const lang = localStorage.getItem('lang') || 'ru';
  const label = document.getElementById('lang-label');
  if (label) label.textContent = lang.toUpperCase();
}

updateLangLabel();
loadContent();
setActiveNav();
