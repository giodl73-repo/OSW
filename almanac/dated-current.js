(() => {
  const byId = id => document.getElementById(id);
  let series, widths, timer = null, mapToken = 0;
  function stop() { if (timer !== null) clearInterval(timer); timer = null; byId('dated-play').textContent = 'Play observations'; }
  function render() {
    const index = Number(byId('dated-phase').value), frame = series.frames[index];
    const address=new URL(location.href);address.searchParams.set('series',byId('dated-series').value);address.searchParams.set('date',frame.date);history.replaceState(null,'',address);
    byId('dated-value').textContent = `${frame.date}: ${Math.round(frame.diagnostic_length_km).toLocaleString('en-US')} km ${frame.reaches_downstream_gate ? 'gate-reaching diagnostic' : 'truncated diagnostic'}; not a whole-current length.`;
    const map = byId('dated-map'),token=++mapToken;map.hidden = true;map.src = `../${frame.figure}`;
    byId('dated-map-status').textContent='Loading selected diagnostic map…';
    map.decode().then(()=>{if(token===mapToken){map.hidden=false;map.dataset.sampleDate=frame.date;byId('dated-map-status').textContent='';}}).catch(()=>{if(token===mapToken){stop();byId('dated-map-status').textContent='Selected diagnostic map unavailable; source calculations remain inspectable.';}});
    map.alt = `Gulf Stream surface geostrophic diagnostic on ${frame.date}, fixed seed to ${frame.reaches_downstream_gate ? '50 W gate' : 'threshold stop'}. OSW state context; no current footprint.`;
    byId('dated-stop').textContent = frame.reaches_downstream_gate ? 'Trace reaches the declared 50 W gate (dashed line).' : `Trace stopped: ${frame.stop_reason.replaceAll('_', ' ')}. The diagnostic does not measure the current endpoint or a change in whole-current length.${frame.stop_reason === 'distance_cap' ? ' The trace can circulate near its seed until the integration cap; its accumulated distance is not a downstream current extent.' : ''}`;
    const previous = series.frames[index - 1];
    const days = previous ? Math.round((Date.parse(frame.date) - Date.parse(previous.date)) / 86400000) : 0;
    const next = series.frames[index + 1];
    const nextGap = next ? Math.round((Date.parse(next.date) - Date.parse(frame.date)) / 86400000) : 0;
    byId('dated-gap').textContent = previous ? `${days} calendar day${days === 1 ? '' : 's'} since previous frame.${days > 1 ? ` ${days - 1} intervening days are unsampled here.` : ''}` : `First sampled date.${next ? ` Next available frame: ${next.date}; ${nextGap - 1} intervening days are unsampled here.` : ''}`;
    const versions = [...new Set(series.frames.map(row => row.source_algorithm))];
    byId('dated-version').textContent = `Source processing: ${frame.source_algorithm}; ${frame.source_product_status}.${versions.length > 1 ? ' Processing version changes within this sequence. Differences cannot be assigned entirely to ocean change.' : ''}`;
    const width = widths.frames.find(row => row.date === frame.date);
    byId('dated-width').textContent = width?.approximate_section_span_km != null ? `Local width candidate at 70 W: about ${width.approximate_section_span_km} km meridional half-peak eastward-velocity span. ${width.nominal.native_cell_spacings} native grid spacings.${width.nominal.resolution_review_required ? ' Fewer than four grid spacings: resolution review required.' : ' Boundary validation still required.'} Not a flow-normal or whole-current width. The section peak is selected independently of the plotted streamline.` : 'Local section width candidate: unknown (unbracketed boundaries).';
    byId('dated-width-range').textContent = width?.threshold_sensitivity_span_km ? `40/50/60% boundary-choice spans: ${width.threshold_sensitivity_span_km.join('–')} km, rounded outward to 10 km. This is threshold sensitivity, not statistical uncertainty. Positional error, representative current width and annual length/width ranges remain unknown.` : 'Boundary-choice sensitivity unavailable. Positional error and annual length/width ranges remain unknown.';
    const sampled = widths.sample_value_spans.find(row => String(row.year) === frame.date.slice(0,4));
    byId('dated-width-samples').textContent = sampled?.rounded_sample_value_span_km ? `${sampled.year} sampled section values: ${sampled.rounded_sample_value_span_km.join('–')} km across ${sampled.sample_count} daily samples. This sample span is not annual extrema or an error margin.${sampled.source_algorithms.length > 1 ? ' Processing changes within these samples; physical variability is not isolated.' : ''}` : '';
    const sensitivity = frame.diagnostic_sensitivity;
    const span = sensitivity.rounded_successful_scenario_span_km;
    byId('dated-sensitivity').textContent = `${sensitivity.gate_reaching_count} of ${sensitivity.scenarios.length} seed/step scenarios reach the 50 W gate. ${span ? `Successful diagnostic lengths span ${span.map(v => v.toLocaleString('en-US')).join('–')} km, rounded outward to 10 km.` : 'No successful gate-reaching span is available.'} This is finite scenario sensitivity, not a confidence interval, width or annual range.${!frame.reaches_downstream_gate && span ? ' The selected trace stopped early; this span describes successful alternatives only.' : ''}`;
    const rows = byId('dated-scenario-rows'); rows.replaceChildren();
    for (const scenario of sensitivity.scenarios) {
      const tr = document.createElement('tr');
      for (const value of [`${scenario.seed_latitude} N`, `${scenario.step_km} km`, `${scenario.diagnostic_length_km.toLocaleString('en-US')} km`, scenario.stop_reason.replaceAll('_', ' ')]) {
        const td = document.createElement('td'); td.textContent = value; tr.append(td);
      }
      rows.append(tr);
    }
    const list = byId('dated-state-list'); list.replaceChildren();
    for (const relation of frame.state_relations) {
      const li = document.createElement('li'), link = document.createElement('a');
      link.href = `index.html?state=${encodeURIComponent(relation.state_code)}#state-title`;
      link.textContent = `${relation.state_code}: about ${Math.round(relation.intersection_length_km).toLocaleString('en-US')} km of diagnostic line`;
      li.append(link); list.append(li);
    }
    const source = byId('dated-source'); source.replaceChildren();
    const link = document.createElement('a'); link.href = frame.source_url; link.textContent = `NOAA daily source file: ${frame.time_start} to ${frame.time_end_exclusive} (exclusive)`; source.append(link);
  }
  let loadToken = 0;
  let requestedDate = new URLSearchParams(window.location.search).get('date');
  function loadSeries() {
    stop(); const token = ++loadToken;
    const year = byId('dated-series').value;
    const path = year === '2025' ? '../research/ocean-current-dated-timeline-2025.json' : '../research/ocean-current-dated-timeline.json';
    byId('dated-play').disabled = true;
    byId('dated-phase').disabled = true;
    byId('dated-phase').replaceChildren();
    ++mapToken;byId('dated-map').hidden=true;
    for(const id of ['dated-value','dated-stop','dated-gap','dated-version','dated-width','dated-width-range','dated-width-samples','dated-sensitivity','dated-scenario-rows','dated-state-list','dated-source','dated-map-status'])byId(id).replaceChildren();
    byId('dated-status').textContent = 'Loading pinned frames…';
    return window.oswCheckedAtlasReady.then(({documents}) => {
    const value=documents[path.replace(/^\.\.\//,'')],widthSeries=documents['research/gulf-stream-section-width-series.json'];
    if(!value||!widthSeries)throw Error('Checked dated evidence unavailable');
    if (token !== loadToken) return;
    series = value;
    widths = widthSeries;
    byId('dated-phase').replaceChildren();
    byId('dated-phase').disabled = false;
    byId('dated-heading').textContent = year === '2025' ? 'Gulf Stream: twelve snapshots across 2025' : 'Gulf Stream: five sampled days';
    byId('dated-download').href = path;
    for (const [index, frame] of series.frames.entries()) { const option = document.createElement('option'); option.value = index; option.textContent = frame.date; byId('dated-phase').append(option); }
    byId('dated-method').textContent = series.method; byId('dated-layer').textContent = series.layer;
    byId('dated-limit').textContent = series.limitations; byId('dated-credit').textContent = series.attribution;
    byId('dated-status').textContent = series.sampling_note;
    if(requestedDate) { const index=series.frames.findIndex(frame=>frame.date===requestedDate);if(index>=0)byId('dated-phase').value=String(index);requestedDate=null; }
    byId('dated-play').disabled = series.frames.length < 2;
    render();
  }).catch(error => { if (token === loadToken) byId('dated-status').textContent = error.message; });
  }
  byId('dated-series').value = new URLSearchParams(window.location.search).get('series') === '2026' ? '2026' : '2025';
  byId('dated-series').addEventListener('change', loadSeries);
  byId('dated-phase').addEventListener('change', () => { stop(); render(); });
  byId('dated-play').addEventListener('click', () => { if (timer !== null) { stop(); return; } byId('dated-play').textContent = 'Pause'; timer = setInterval(() => { byId('dated-phase').value = (Number(byId('dated-phase').value) + 1) % series.frames.length; render(); }, 2200); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  loadSeries();
})();
