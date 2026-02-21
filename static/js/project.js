(async () => {
  const pathParts = location.pathname.split('/').filter(Boolean);
  const id = pathParts[pathParts.length - 1];
  if (!id) return;

  const lang = localStorage.getItem('lang') || 'ru';
  const data = await fetch(`/static/content/${lang}.json`).then(r => r.json());
  const project = data.projects.find(p => p.id === id);
  if (!project) return;

  document.getElementById('project-title').textContent = project.title;
  document.getElementById('project-details').textContent = project.details;
  document.getElementById('project-stack').textContent = project.stack;
})();
