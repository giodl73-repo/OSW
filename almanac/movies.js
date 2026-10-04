(() => {
  const packageRoot = 'release/v0.1.0-rights-screened-preview/';
  const byId = id => document.getElementById(id);
  const link = (label, href, external = false) => {
    const a = document.createElement('a');
    a.textContent = label;
    a.href = href;
    if (external) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  };
  const textCell = (row, value) => {
    const cell = row.insertCell();
    cell.textContent = value;
    return cell;
  };
  async function load(name) {
    const response = await fetch(`${packageRoot}${name}.json`);
    if (!response.ok) throw new Error(`Could not load ${name}: HTTP ${response.status}`);
    return response.json();
  }
  Promise.all(['tiles', 'tile_state_relations', 'media', 'entities'].map(load)).then(([tiles, overlaps, media, entities]) => {
    const entityById = new Map(entities.map(item => [item.id, item]));
    const states = entities.filter(item => item.type === 'osw_state').sort((a, b) => a.label.localeCompare(b.label));
    const overlapsByTile = new Map(tiles.map(tile => [tile.tile_id, []]));
    const mediaByTile = new Map(tiles.map(tile => [tile.tile_id, []]));
    overlaps.forEach(item => overlapsByTile.get(item.tile_id)?.push(item));
    media.forEach(item => { if (item.tile_id && mediaByTile.has(item.tile_id)) mediaByTile.get(item.tile_id).push(item); });
    states.forEach(state => {
      const option = document.createElement('option');
      option.value = state.id;
      option.textContent = state.label;
      byId('movie-state').append(option);
    });
    function render() {
      const query = byId('movie-query').value.trim().toLocaleLowerCase();
      const zoom = byId('movie-zoom').value;
      const state = byId('movie-state').value;
      const body = byId('movie-rows');
      body.replaceChildren();
      const visible = tiles.filter(tile => {
        const related = mediaByTile.get(tile.tile_id);
        return (zoom === 'all' || String(tile.zoom) === zoom)
          && (state === 'all' || overlapsByTile.get(tile.tile_id).some(item => item.state_id === state))
          && (!query || tile.tile_id.toLocaleLowerCase().includes(query)
            || related.some(item => entityById.get(item.entity_id)?.label.toLocaleLowerCase().includes(query)));
      });
      visible.forEach(tile => {
        const row = body.insertRow();
        row.id = `movie-${tile.tile_id}`;
        textCell(row, `${tile.tile_id} · level ${tile.zoom}`);
        row.insertCell().append(link('Watch at NASA', tile.url, true));
        const stateCell = row.insertCell();
        const stateList = overlapsByTile.get(tile.tile_id).sort((a, b) => b.display_coverage_fraction - a.display_coverage_fraction);
        const stateDetails = document.createElement('details');
        const stateSummary = document.createElement('summary');
        stateSummary.textContent = `${stateList.length} display overlaps`;
        stateDetails.append(stateSummary);
        const stateLinks = document.createElement('ul');
        stateList.forEach(item => {
          const stateEntity = entityById.get(item.state_id);
          const li = document.createElement('li');
          li.append(link(stateEntity?.label || item.state_id, `object.html?id=${encodeURIComponent(item.state_id)}`));
          li.append(` · ${(100 * item.display_coverage_fraction).toFixed(1)}% of state's display area`);
          stateLinks.append(li);
        });
        stateDetails.append(stateLinks);
        stateCell.append(stateDetails);
        const objectCell = row.insertCell();
        const objectIds = [...new Set(mediaByTile.get(tile.tile_id).map(item => item.entity_id))];
        if (!objectIds.length) { objectCell.textContent = 'No linked motion record'; return; }
        const objectDetails = document.createElement('details');
        const objectSummary = document.createElement('summary');
        objectSummary.textContent = `${objectIds.length} geographic links`;
        objectDetails.append(objectSummary);
        const objectLinks = document.createElement('ul');
        objectIds.sort((a, b) => (entityById.get(a)?.label || a).localeCompare(entityById.get(b)?.label || b));
        objectIds.forEach(id => {
          const li = document.createElement('li');
          li.append(link(entityById.get(id)?.label || id, `object.html?id=${encodeURIComponent(id)}`));
          objectLinks.append(li);
        });
        objectDetails.append(objectLinks);
        objectCell.append(objectDetails);
      });
      byId('movie-count').textContent = `${visible.length} of ${tiles.length} crops`;
    }
    ['movie-query', 'movie-zoom', 'movie-state'].forEach(id => byId(id).addEventListener(id === 'movie-query' ? 'input' : 'change', render));
    render();
  }).catch(error => { byId('movie-error').textContent = error.message; byId('movie-error').hidden = false; byId('movie-count').textContent = 'Unavailable'; });
})();
