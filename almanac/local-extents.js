"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const collection = 'current_local_extents', cases = 'current_local_extent_cases';
  const months = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const primary = [
    {field:'native_latitude_offset',op:'eq',value:0},
    {field:'normal_sample_step_km',op:'eq',value:5},
    {field:'threshold_fraction',op:'eq',value:0.5},
    {field:'quantity',op:'eq',value:'core_to_positive_normal_threshold_extent'}
  ];
  const presets = {
    primary: {collection, filters:primary},
    missing: {collection:cases, filters:[
      {field:'native_latitude_offset',op:'eq',value:0},
      {field:'normal_sample_step_km',op:'eq',value:10},
      {field:'status',op:'eq',value:'missing_supported_profile'}]},
    all: {collection}, cases: {collection:cases}
  };
  let worker = null, nextId = 0, ready = false, generation = 0;
  let query = {...presets.primary, sort:{field:'month',direction:'asc'}, limit:100, offset:0};
  let result = null;
  const pending = new Map();
  const distanceFormat = new Intl.NumberFormat('en', {maximumFractionDigits:2, useGrouping:false});
  const human = value => String(value).replaceAll('_', ' ');
  const json = value => JSON.stringify(value, null, 2);
  function message(id, text, error = false) {
    $(id).textContent = text; $(id).dataset.error = String(error);
  }
  function send(action, value) {
    return new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, {resolve,reject});
      worker.postMessage({id,action,value});
    });
  }
  function stopWorker(error) {
    ready = false; worker?.terminate(); worker = null;
    for (const request of pending.values()) request.reject(error);
    pending.clear(); $('query-controls').inert = true;
    $('result-body').inert = true;
    $('previous').disabled = $('next').disabled = true;
  }
  function syncFilters() {
    $('collection').value = query.collection;
    const fields = {month:'month',step:'normal_sample_step_km',offset:'native_latitude_offset',quantity:'quantity',fraction:'threshold_fraction'};
    for (const [id,field] of Object.entries(fields)) {
      const filter = (query.filters || []).find(item => item.field === field && item.op === 'eq');
      $(id).value = filter ? String(filter.value) : '';
    }
    const isCase = query.collection === cases;
    $('quantity').disabled = $('fraction').disabled = isCase;
  }
  function share(recordId) {
    const url = new URL(location.href);
    url.searchParams.set('q', JSON.stringify(query));
    url.searchParams.delete('record');
    if (recordId) url.searchParams.set('record', recordId);
    history.replaceState(null, '', url);
  }
  function cell(row, value) {
    const td = document.createElement('td');
    td.textContent = value == null ? 'Unresolved' : String(value);
    row.append(td); return td;
  }
  function renderRows() {
    const isCase = query.collection === cases;
    $('result-head').replaceChildren(); $('result-body').replaceChildren();
    const tr = document.createElement('tr');
    for (const name of isCase ? ['Case','Month','Step / offset','Outcome','Evidence'] : ['Case','Month','Reference / fraction','Bounds (km)','Outcome','Evidence']) {
      const th = document.createElement('th'); th.scope = 'col'; th.textContent = name; tr.append(th);
    }
    $('result-head').append(tr);
    for (const record of result.rows) {
      const row = document.createElement('tr');
      cell(row, record.source_case_id); cell(row, months[record.month]);
      if (isCase) cell(row, `${record.normal_sample_step_km} km / ${record.native_latitude_offset}`);
      else {
        cell(row, `${human(record.quantity)} / ${record.threshold_fraction}`);
        const bounds = cell(row, record.extent_bracket_km == null ? null
          : record.extent_bracket_km.map(value => distanceFormat.format(value)).join(' – '));
        if (record.extent_bracket_km != null) bounds.title = JSON.stringify(record.extent_bracket_km);
      }
      cell(row, human(record.status));
      const td = document.createElement('td'), button = document.createElement('button');
      button.type = 'button'; button.textContent = 'Inspect';
      button.setAttribute('aria-label', `Inspect ${record.id}`);
      button.addEventListener('click', () => inspect(record.id)); td.append(button); row.append(td);
      $('result-body').append(row);
    }
    const start = result.rows.length ? result.offset + 1 : 0;
    $('page-status').textContent = `${start}–${result.offset + result.rows.length} of ${result.total}`;
    $('previous').disabled = !result.offset;
    $('next').disabled = result.offset + result.rows.length >= result.total;
  }
  async function inspect(id) {
    const token = generation;
    try {
      const detail = await send('record', {collection:query.collection,id});
      if (token !== generation) return;
      if (!detail.ok) throw Error(detail.error);
      $('record-title').textContent = detail.record.source_case_id;
      $('record-summary').textContent = `${months[detail.record.month]} 2013 · ${human(detail.record.status)}. Local model evidence; physical current width remains unresolved.`;
      $('record-json').textContent = json(detail.record);
      $('case-context').hidden = !detail.case_context;
      $('case-json').textContent = detail.case_context ? json(detail.case_context) : '';
      $('case-link').replaceChildren();
      if (detail.case_context) {
        const button = document.createElement('button');button.type = 'button';button.textContent = 'Query this original source case';
        button.addEventListener('click', () => execute({collection:cases,filters:[{field:'id',op:'eq',value:detail.case_context.id}],limit:100,offset:0}));
        $('case-link').append(button);
      }
      $('record-panel').hidden = false; $('record-panel').focus(); share(id);
    } catch (error) {
      if (token === generation) { $('record-panel').hidden = true; message('query-status', error.message, true); }
    }
  }
  async function execute(request, recordId) {
    if (!ready) return;
    const token = ++generation;
    $('query-controls').inert = true; $('result-body').inert = true;
    $('previous').disabled = $('next').disabled = true;
    message('query-status', 'Querying retained evidence…');
    try {
      if (!request || typeof request !== 'object' || Array.isArray(request)) throw Error('Enter a JSON query object.');
      request = {...request,limit:request.limit ?? 100,offset:request.offset ?? 0};
      if (!Number.isInteger(request.limit) || request.limit < 1 || request.limit > 100) throw Error('Choose a page limit from 1 to 100.');
      if (new TextEncoder().encode(JSON.stringify(request)).length > 20000) throw Error('Query exceeds 20,000 bytes.');
      const response = await send('query', request);
      if (token !== generation) return;
      if (!response.ok) throw Error(response.error);
      query = request; result = response;
      $('query-json').value = json(query); syncFilters(); renderRows();
      $('record-panel').hidden = true; share();
      message('query-status', `${response.total} retained ${query.collection === cases ? 'source cases' : 'attempted extents'} match. Missing outcomes remain in the snapshot.`);
      if (recordId) await inspect(recordId);
    } catch (error) {
      if (token !== generation) return;
      result = null; $('result-head').replaceChildren(); $('result-body').replaceChildren();
      $('record-panel').hidden = true; $('page-status').textContent = '';
      message('query-status', error.message, true);
    } finally {
      if (token === generation) { $('query-controls').inert = !ready; $('result-body').inert = !ready; }
    }
  }
  function fromLocation() {
    const params = new URLSearchParams(location.search), raw = params.get('q');
    if (raw) {
      if (new TextEncoder().encode(raw).length > 20000) throw Error('Shared query exceeds 20,000 bytes.');
      query = JSON.parse(raw);
    }
    return params.get('record');
  }
  async function load() {
    stopWorker(Error('Evidence worker reloaded.')); result = null; ++generation;
    $('result-head').replaceChildren(); $('result-body').replaceChildren();
    $('record-panel').hidden = true; $('page-status').textContent = '';
    message('query-status', ''); message('engine-status', 'Loading verified evidence assets…'); $('reload').hidden = true;
    try {
      worker = new Worker('local-extents-worker.js');
      worker.onmessage = event => {
        const request = pending.get(event.data.id);
        if (request) { pending.delete(event.data.id); request.resolve(event.data.result); }
      };
      worker.onerror = () => {
        stopWorker(Error('Evidence worker failed. Retry loading.'));
        message('engine-status', 'Evidence worker failed. Retry loading.', true); $('reload').hidden = false;
      };
      const metadata = await send('load');
      if (!metadata.ok) throw Error(metadata.error);
      ready = true; $('query-controls').inert = false;
      message('engine-status', 'Ready · 72 source cases · 864 attempted extents · 278 KB engine · 2013 monthly fields at 15 m');
      $('field-list').textContent = json(metadata.collections);
      $('provenance').textContent = json(metadata.provenance);
      let recordId;
      try { recordId = fromLocation(); }
      catch (error) { message('query-status', error.message, true); $('query-json').value = json(query); return; }
      await execute(query, recordId);
    } catch (error) {
      stopWorker(error); message('engine-status', `${error.message} The chart and source documents remain available.`, true); $('reload').hidden = false;
    }
  }
  $('filters').addEventListener('submit', event => {
    event.preventDefault();
    const selected = $('collection').value, filters = [];
    const fields = {month:'month',step:'normal_sample_step_km',offset:'native_latitude_offset',quantity:'quantity',fraction:'threshold_fraction'};
    for (const [id,field] of Object.entries(fields)) {
      if ($(id).value === '' || (selected === cases && ['quantity','fraction'].includes(id))) continue;
      filters.push({field,op:'eq',value:id === 'quantity' ? $(id).value : Number($(id).value)});
    }
    execute({collection:selected,filters,sort:{field:'month',direction:'asc'},limit:100,offset:0});
  });
  $('collection').addEventListener('change', () => { $('quantity').disabled = $('fraction').disabled = $('collection').value === cases; });
  for (const button of document.querySelectorAll('[data-preset]')) button.addEventListener('click', () => execute({...presets[button.dataset.preset],sort:{field:'month',direction:'asc'},limit:100,offset:0}));
  $('run-json').addEventListener('click', () => {
    try { execute(JSON.parse($('query-json').value)); }
    catch (error) {
      result = null; $('result-head').replaceChildren(); $('result-body').replaceChildren();
      $('record-panel').hidden = true; $('page-status').textContent = '';
      $('previous').disabled = $('next').disabled = true;
      message('query-status', error.message, true);
    }
  });
  $('previous').addEventListener('click', () => execute({...query,offset:Math.max(0,result.offset-result.limit)}));
  $('next').addEventListener('click', () => execute({...query,offset:result.offset+result.limit}));
  $('reload').addEventListener('click', load);
  load();
})();
