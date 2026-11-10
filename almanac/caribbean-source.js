'use strict';
(() => {
  const member = document.getElementById('member');
  const filter = document.getElementById('field-filter');
  const status = document.getElementById('inventory-status');
  const body = document.getElementById('fields');
  let inventory;
  const number = value => value === null ? '—' : Number(value).toLocaleString('en-US', {maximumSignificantDigits: 10});
  function rows(group) {
    return [...Object.entries(group.variables).map(([name, value]) => ({name: `${group.path === '/' ? '' : group.path}/ ${name}`, ...value})),
      ...Object.values(group.groups).flatMap(rows)];
  }
  function render() {
    const all = rows(inventory.members[member.value]);
    const visible = all.filter(row => row.name.toLowerCase().includes(filter.value.toLowerCase().trim()));
    body.replaceChildren();
    for (const row of visible) {
      const tr = document.createElement('tr');
      for (const text of [row.name, number(row.value_count), number(row.decoded_masked_count), `${number(row.raw_minimum)} to ${number(row.raw_maximum)}`]) {
        const td = document.createElement('td'); td.textContent = text; tr.append(td);
      }
      body.append(tr);
    }
    status.textContent = `${visible.length} of ${all.length} fields · ${member.value}`;
  }
  fetch('../research/caribbean-ru29-source-inventory-v2.json').then(response => {
    if (!response.ok) throw new Error('Source inventory unavailable');
    return response.json();
  }).then(data => {
    if (data.schema !== 'osw.caribbean-ru29.source-inventory.v2') throw new Error('Unsupported source inventory');
    inventory = data;
    for (const name of Object.keys(data.members)) {
      const option = document.createElement('option'); option.value = name; option.textContent = name; member.append(option);
    }
    member.value = 'adcp-transect-1.nc';
    member.addEventListener('change', render); filter.addEventListener('input', render); render();
  }).catch(error => {status.textContent = error.message;});

  const reader = document.getElementById('cell-reader');
  const occupation = document.getElementById('cell-occupation');
  const latitude = document.getElementById('cell-latitude');
  const depth = document.getElementById('cell-depth');
  const result = document.getElementById('cell-result');
  let sections, loading = false;
  function cell() {
    const record = sections.occupations[Number(occupation.value)];
    const fields = record.source_group.variables;
    const z = Number(depth.value), a = Number(latitude.value);
    function velocity(name, positive, negative) {
      const value = fields[name].raw_values[z][a];
      if (fields[name].decoded_mask[z][a] || typeof value !== 'number' || !Number.isFinite(value)) return 'missing';
      return `${Math.abs(value).toPrecision(7)} m/s ${value === 0 ? '(zero)' : value > 0 ? positive : negative}`;
    }
    result.textContent = `Occupation ${Number(occupation.value)+1}, ${fields.latitude.raw_values[a].toFixed(6)}°N, ${fields.depth.raw_values[z]} m: E–W ${velocity('u_grid', 'eastward', 'westward')}; N–S ${velocity('v_grid', 'northward', 'southward')}.`;
  }
  function coordinates() {
    const fields = sections.occupations[Number(occupation.value)].source_group.variables;
    for (const [control, values, suffix] of [[latitude, fields.latitude.raw_values, '°N'], [depth, fields.depth.raw_values, ' m']]) {
      control.replaceChildren();
      values.forEach((value, index) => {
        const option = document.createElement('option'); option.value = index; option.textContent = `${Number(value.toFixed(6))}${suffix}`; control.append(option);
      });
    }
    cell();
  }
  reader.addEventListener('toggle', () => {
    if (!reader.open || sections || loading) return;
    loading = true; result.textContent = 'Loading section values…';
    fetch('../research/caribbean-ru29-source-page-v1.json').then(response => {
      if (!response.ok) throw new Error('Section values unavailable');
      return response.json();
    }).then(data => {
      if (data.schema !== 'osw.caribbean-ru29.source-page.v1') throw new Error('Unsupported section values');
      sections = data; coordinates();
      occupation.addEventListener('change', coordinates);
      latitude.addEventListener('change', cell); depth.addEventListener('change', cell);
    }).catch(error => {result.textContent = error.message;}).finally(() => {loading = false;});
  });
})();
