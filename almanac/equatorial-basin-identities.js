(() => {
  'use strict';
  const add = (tag, text, parent) => {
    const el = document.createElement(tag);
    if (text != null) el.textContent = text;
    parent.append(el);
    return el;
  };
  const link = (text, href, parent) => {
    const el = add('a', text, parent);
    el.href = href;
    return el;
  };
  window.renderEquatorialBasinIdentities = (parent, scene, inspect) => {
    if (scene?.kind !== 'equatorial_basin_identity_context') return null;
    const section = add('section', null, parent);
    section.className = 'equatorial-basin-identity-context';
    section.style.cssText = 'min-width:0;overflow-wrap:anywhere';
    add('h3', scene.title, section);
    add('p', scene.scope, section);
    const list = add('ul', null, section);
    list.style.cssText = 'list-style:none;padding:0;display:grid;gap:.5rem';
    for (const member of scene.members) {
      const item = add('li', null, list);
      item.dataset.entityId = member.entity_id;
      item.style.cssText = 'border:1px solid #758b93;border-radius:.3rem;padding:.6rem';
      const name = link(member.label, member.object_url, item);
      name.style.cssText = 'display:inline-block;min-height:44px;align-content:center';
      if (scene.selected_entity_id === member.entity_id) name.setAttribute('aria-current', 'page');
      const family = add('p', 'Member of: ', item);
      family.style.margin = '.25rem 0';
      link(member.family_label, member.family_url, family);
      if (inspect) {
        const button = add('button', 'Inspect membership record', item);
        button.type = 'button';
        button.addEventListener('click', () => inspect('current_basin_memberships', member.membership_record.id));
      }
    }
    add('p', scene.dimension_status, section);
    const query = {collection:'current_basin_memberships', limit:100};
    link('Query all basin memberships', 'query.html?q=' + encodeURIComponent(JSON.stringify(query)), add('p', null, section));
    link('Read the naming source', scene.source_url, add('p', null, section));
    link('View the full family diagram', '../' + scene.figure, add('p', null, section));
    return section;
  };
})();
