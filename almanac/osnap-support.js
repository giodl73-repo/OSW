'use strict';

(() => {
  const byId = id => document.getElementById(id);
  const make = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  const kinds = {adcp: 'ADCP profiles', point: 'Point velocity', hydro: 'Hydrography'};
  let records = [], first, last;

  async function checkedJson(url, expected) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Source metadata unavailable (${response.status}).`);
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength !== expected.bytes) throw new Error('Source metadata size differs from the reviewed receipt.');
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)),
      value => value.toString(16).padStart(2, '0')).join('');
    if (digest !== expected.sha256) throw new Error('Source metadata checksum differs from the reviewed receipt.');
    return JSON.parse(new TextDecoder().decode(bytes));
  }

  function definition(list, label, value) {
    list.append(make('dt', label), make('dd', value));
  }

  function instrument(row) {
    const detail = make('details');
    const summary = make('summary');
    const top = make('span', undefined, 'support-row');
    top.append(make('strong', row.mooring), make('span', kinds[row.kind], 'support-role'));
    const track = make('span', undefined, 'support-bar-track');
    track.setAttribute('aria-hidden', 'true');
    const bar = make('span', undefined, 'support-bar');
    const total = last - first;
    bar.style.marginLeft = `${100 * (row.start - first) / total}%`;
    bar.style.width = `${100 * (row.end - row.start) / total}%`;
    track.append(bar);
    const tracks = make('span', undefined, 'support-tracks');tracks.append(track);
    if (row.audit.velocity_availability) {
      const months = make('span', undefined, 'support-month-track');months.setAttribute('aria-hidden', 'true');
      for (const month of row.audit.monthly) {
        const value = month.velocity_availability;
        if (!value || !value.total_cells || !value.paired_available_cells) continue;
        const start = Math.max(first, Date.parse(`${month.month}-01T00:00:00Z`));
        const date = new Date(`${month.month}-01T00:00:00Z`);
        const end = Math.min(last, Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 1));
        if (end <= start) continue;
        const segment = make('span', undefined, 'support-month');
        segment.style.left = `${100 * (start - first) / total}%`;
        segment.style.width = `${100 * (end - start) / total}%`;
        segment.style.opacity = String(.25 + .75 * value.paired_available_cells / value.total_cells);
        months.append(segment);
      }
      tracks.append(months);
    }
    top.append(tracks);summary.append(top);
    const period = make('span', undefined, 'support-period');
    const start = make('time', row.startText.slice(0, 10));start.dateTime = row.startText;
    const end = make('time', row.endText.slice(0, 10));end.dateTime = row.endText;
    period.append(start, document.createTextNode(' to '), end,
      document.createTextNode(' · declared in header'));
    summary.append(period);detail.append(summary);
    const availability = row.audit.velocity_availability;
    summary.append(make('span', availability
      ? `${(100 * availability.paired_available_cells / availability.total_cells).toFixed(1)}% paired velocity cells available · not physical QC approval`
      : 'Hydrography · no velocity pair in this file', 'support-availability'));
    const body = make('div', undefined, 'support-instrument-body');
    body.append(make('h3', row.name));
    const list = make('dl');
    definition(list, 'Original member', row.member);
    definition(list, 'Time rows', `${row.audit.time.available_rows.toLocaleString()} available timestamps · ${row.timeRows.toLocaleString()} declared rows`);
    definition(list, 'Declared cadence', row.attributes.time_coverage_resolution || 'Not declared');
    definition(list, 'Depth support', row.kind === 'adcp'
      ? 'Supplied time-varying bin depth; a common physical analysis layer has not been selected.'
      : 'Nominal depth label; pressure variation must be checked separately.');
    definition(list, 'Source summary', row.attributes.summary || 'Not declared');
    if (row.kind !== 'hydro') definition(list, 'Velocity', 'UCUR / VCUR · east / north · meter/second');
    definition(list, 'Actual time span', `${row.audit.time.first_utc} to ${row.audit.time.last_utc}`);
    definition(list, 'Time ordering', row.audit.time.all_rows_available_and_strictly_increasing
      ? 'All time rows available and strictly increasing; no duplicate timestamps.' : 'Inspect the source-support audit for anomalies.');
    if (availability) definition(list, 'Velocity availability', `${availability.paired_available_cells.toLocaleString()} / ${availability.total_cells.toLocaleString()} paired cells; ${availability.profiles_with_all_bins_paired.toLocaleString()} profiles have all bins paired. Unmasked finite pairs do not establish physical validity.`);
    if (row.audit.supplied_depth.time_varying) definition(list, 'Supplied bin-depth extrema', `${row.audit.supplied_depth.min.toFixed(1)} to ${row.audit.supplied_depth.max.toFixed(1)} m across supplied depth cells. These include negative depths; physical acceptance is not established.`);
    const pressure = row.audit.pressure_proxy_decibar;
    definition(list, 'Pressure proxy', pressure.available_cells
      ? `${pressure.min.toFixed(1)} to ${pressure.max.toFixed(1)} decibar; not converted to instrument depth.`
      : 'No available pressure cells.');
    definition(list, 'Member SHA-256', row.sha256);
    body.append(list);
    const table = make('table', undefined, 'support-months');
    table.append(make('caption', 'Monthly sample availability. Counts describe instrument cells, not current area or width.'));
    const head = make('thead'), header = make('tr');
    for (const label of ['Month (UTC)', 'Timestamp rows', 'Paired velocity cells / all cells']) {
      const cell = make('th', label);cell.scope = 'col';header.append(cell);
    }
    head.append(header);table.append(head);
    const tbody = make('tbody');
    for (const month of row.audit.monthly) {
      const tr = make('tr'), label = make('th', month.month);label.scope = 'row';
      const value = month.velocity_availability;
      tr.append(label, make('td', month.timestamp_rows.toLocaleString()), make('td', value
        ? `${value.paired_available_cells.toLocaleString()} / ${value.total_cells.toLocaleString()}` : 'No velocity variables'));
      tbody.append(tr);
    }
    table.append(tbody);body.append(table);detail.append(body);
    return detail;
  }

  function render() {
    const selected = byId('support-mooring').value;
    const kind = byId('support-kind').value;
    const search = byId('support-search').value.trim().toLowerCase();
    const visible = records.filter(row => (selected === 'all' || row.mooring === selected)
      && (kind === 'all' || row.kind === kind)
      && (!search || `${row.member} ${row.name} ${kinds[row.kind]}`.toLowerCase().includes(search)));
    byId('support-instruments').replaceChildren(...visible.map(instrument));
    byId('support-count').textContent = `${visible.length} of ${records.length} instrument records shown. Expand a row for dates, depth context, and source identity.`;
    byId('support-empty').hidden = visible.length !== 0;
    for (const button of byId('support-moorings').querySelectorAll('button')) {
      button.setAttribute('aria-pressed', String(button.dataset.mooring === selected));
    }
  }

  async function load() {
    const response = await fetch('../research/osnap-wg-2016-2018-source-header-execution-review-v1.json');
    if (!response.ok) throw new Error('Header execution review is unavailable.');
    const review = await response.json();
    if (review.schema !== 'osw.osnap-source-header-execution-review.v1'
        || review.source_run_conclusion !== 'success' || review.instrument_count !== 78) {
      throw new Error('The source execution receipt is not the reviewed 78-instrument inventory.');
    }
    // Fixed local source path: never follow a URL supplied by a source record.
    const data = await checkedJson('../research/osnap-wg-2016-2018-source-headers-v1.json', review.header_report);
    if (data.status !== 'PASS_SOURCE_HEADERS_ONLY' || data.instrument_headers.length !== 78
        || data.working_dataset_admitted !== false || data.observation_variable_arrays_materialized !== false) {
      throw new Error('The source report does not match its header-only scope.');
    }
    const supportResponse = await fetch('../research/osnap-wg-2016-2018-sample-support-execution-review-v1.json');
    if (!supportResponse.ok) throw new Error('Sample-support execution review is unavailable.');
    const supportReview = await supportResponse.json();
    if (supportReview.schema !== 'osw.osnap-sample-support-execution-review.v1'
        || supportReview.run_conclusion !== 'success' || supportReview.instrument_count !== 78) {
      throw new Error('The sample-support execution receipt is not verified.');
    }
    const support = await checkedJson('../research/osnap-wg-2016-2018-sample-support-v1.json', supportReview.support_report);
    if (support.status !== 'PASS_SAMPLE_SUPPORT_AUDIT_ONLY' || support.instrument_count !== 78
        || support.instruments.length !== 78 || support.working_dataset_admitted !== false
        || support.custody.sha256 !== data.custody.sha256 || support.physical_measurements_derived !== 0) {
      throw new Error('Sample-support scope or original custody differs.');
    }
    const samples = new Map(support.instruments.map(row => [row.member, row]));
    if (samples.size !== 78) throw new Error('Sample-support member identities are duplicated.');
    const members = new Set();
    records = data.instrument_headers.map(row => {
      const attributes = row.header.attributes;
      const variables = row.header.variables;
      const mooring = row.member.split('/')[0];
      const start = Date.parse(attributes.time_coverage_start);
      const end = Date.parse(attributes.time_coverage_end);
      if (members.has(row.member) || !/^LS[1-8]$/.test(mooring)
          || !Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
        throw new Error('An instrument identity or declared date interval is invalid.');
      }
      members.add(row.member);
      const audit = samples.get(row.member);
      if (!audit || audit.sha256 !== row.sha256) throw new Error('Sample support does not match the original instrument.');
      return {member: row.member, mooring, attributes, sha256: row.sha256, audit,
        name: attributes.id || row.member.split('/').pop(),
        kind: variables.UCUR ? (variables.BINDEPTH ? 'adcp' : 'point') : 'hydro',
        timeRows: row.header.dimensions.TIME.length,
        start, end, startText: attributes.time_coverage_start, endText: attributes.time_coverage_end};
    }).sort((a, b) => a.mooring.localeCompare(b.mooring) || a.kind.localeCompare(b.kind) || a.member.localeCompare(b.member));
    first = Math.min(...records.map(row => row.start));last = Math.max(...records.map(row => row.end));
    byId('support-start').textContent = new Date(first).toISOString().slice(0, 10);
    byId('support-end').textContent = new Date(last).toISOString().slice(0, 10);
    for (let index = 1; index <= 8; index++) {
      const mooring = `LS${index}`;
      const subset = records.filter(row => row.mooring === mooring);
      const velocity = subset.filter(row => row.kind !== 'hydro').length;
      const option = make('option', mooring);option.value = mooring;byId('support-mooring').append(option);
      const button = make('button');button.type = 'button';button.dataset.mooring = mooring;
      button.setAttribute('aria-pressed', 'false');
      button.append(make('strong', mooring), make('span', `${subset.length} files`), make('span', `${velocity} velocity`));
      button.addEventListener('click', () => {
        byId('support-mooring').value = byId('support-mooring').value === mooring ? 'all' : mooring;
        render();
      });
      byId('support-moorings').append(button);
    }
    byId('custody-stage').textContent = 'Verified · original checksum retained';
    byId('headers-stage').textContent = 'Verified · 78 instrument headers';
    byId('samples-stage').textContent = 'Audited · 78 instrument records';
    byId('support-status').textContent = '78 audited records: 8 ADCPs, 29 point velocity meters, and 41 hydrography instruments. Paired availability is checked; current dimensions remain unmeasured here.';
    byId('support-findings').textContent = 'All 78 time arrays are complete and strictly increasing. Across the eight ADCP records, 48.4%–73.1% of time-by-bin cells have both velocity components available. Point meters range from 99.1% to 100%. These fractions describe unmasked finite samples, not physical quality or current coverage.';
    render();
  }

  for (const id of ['support-mooring', 'support-kind']) byId(id).addEventListener('change', render);
  byId('support-search').addEventListener('input', render);
  load().catch(error => {
    byId('support-status').textContent = `Could not display checked coverage: ${error.message} Use the source evidence links below.`;
    byId('custody-stage').textContent = 'Not verified in this view';
    byId('headers-stage').textContent = 'Not verified in this view';
    byId('samples-stage').textContent = 'Not verified in this view';
  });
})();
