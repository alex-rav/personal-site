(async () => {
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  if (!id) return;

  const lang = localStorage.getItem('lang') || 'ru';
  const data = await fetch(`content/${lang}.json`).then(r => r.json());
  const project = data.projects.find(p => p.id === id);
  if (!project) return;

  document.getElementById('project-title').textContent = project.title;
  document.getElementById('project-details').textContent = project.details;
  document.getElementById('project-stack').textContent = project.stack;
})();