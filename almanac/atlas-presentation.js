"use strict";
// Presentation changes preserve the atlas selection, evidence and shared framing.
(() => {
  const button = document.getElementById('atlas-presentation-toggle');
  const indexButton = document.getElementById('atlas-index-toggle');
  const directory = document.getElementById('atlas-directory');
  function apply(enabled, persist = true) {
    document.body.classList.toggle('atlas-presentation', enabled);
    button.setAttribute('aria-pressed', String(enabled));
    button.textContent = enabled ? 'Full almanac' : 'Map-first view';
    indexButton.hidden = !enabled;
    directory.hidden = enabled;
    indexButton.setAttribute('aria-expanded', 'false');
    indexButton.textContent = 'Browse all 240 entries';
    if (persist) {
      const url = new URL(location.href);
      if (enabled) url.searchParams.set('atlas-layout', 'map');
      else url.searchParams.delete('atlas-layout');
      history.replaceState(null, '', url);
      const share = document.querySelector('[data-atlas-share]');
      if (share) share.href = url.href;
    }
  }
  button.addEventListener('click', () => {
    apply(!document.body.classList.contains('atlas-presentation'));
    document.getElementById('route-atlas-title').scrollIntoView({block:'start'});
  });
  indexButton.addEventListener('click', () => {
    directory.hidden = !directory.hidden;
    indexButton.setAttribute('aria-expanded', String(!directory.hidden));
    indexButton.textContent = directory.hidden ? 'Browse all 240 entries' : 'Hide inventory';
    if (!directory.hidden) directory.querySelector('input').focus();
  });
  document.addEventListener('click', event => {
    if (!document.body.classList.contains('atlas-presentation')) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(link.getAttribute('href').slice(1));
    if (target && !document.getElementById('route-atlas').contains(target)) apply(false);
  }, true);
  apply(new URL(location.href).searchParams.get('atlas-layout') === 'map', false);
})();
