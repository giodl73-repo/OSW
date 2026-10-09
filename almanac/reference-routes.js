(() => {
  const initialAddress=location.href;
  let userInteracted=false;
  for(const type of ['pointerdown','keydown'])document.addEventListener(type,()=>{userInteracted=true;},{once:true,capture:true});
  const revealInitialCard=()=>{if(!userInteracted&&location.href===initialAddress)revealLinkedCard();};
  const node = (tag, text, parent) => { const el = document.createElement(tag); if (text != null) el.textContent = text; if (parent) parent.append(el); return el; };
  const number = value => Number(value).toLocaleString("en-US");
  const link = (text, href, parent, external = false) => { const el = node("a", text, parent); el.href = href; if (external) { el.target = "_blank"; el.rel = "noopener noreferrer"; } return el; };
  const objectHref = id => `object.html?id=${encodeURIComponent(id)}`;
  window.oswAtlasSourcesReady = new Promise((resolve,reject)=>{
    const worker=new Worker('query-worker.js?v=atlas-cartography-9');
    const timer=setTimeout(()=>finish(Error('Atlas data request timed out')),90000);
    const finish=(error,result)=>{clearTimeout(timer);worker.terminate();if(error){byId('route-atlas-status').textContent=`Atlas unavailable: ${error.message}`;reject(error);}else resolve(result);};
    worker.onerror=()=>finish(Error('Rust atlas data worker failed'));
    worker.onmessage=async event=>{const {id,result}=event.data;
      if(!result.ok){finish(Error(result.error));return;}
      if(id===1){worker.postMessage({id:2,action:'atlas'});return;}
      try {
        window.oswCartography=await window.createOswCartography(result.engine_binary);
        delete result.engine_binary;
        window.oswAtlasSnapshot=result;
        byId('route-status').dataset.engine=result.engine;
        const docs=Object.fromEntries(Object.entries(result.sources_json).map(([path,raw])=>[path,JSON.parse(raw)]));
        finish(null,docs);
      } catch(error){finish(error);}
    };
    worker.postMessage({id:1,action:'load'});
  });
  async function load(path) {
    const docs=await window.oswAtlasSourcesReady,key=path.replace(/^\.\.\//,'');
    if(!Object.hasOwn(docs,key))throw Error(`Atlas source unavailable: ${key}`);
    return docs[key];
  }
  const byId = id => document.getElementById(id);
  function revealLinkedCard() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = byId(id);
    if (!target || !target.matches('.route-card, .inventory-addition-card, #route-atlas')) return;
    if (id === 'route-atlas') {
      if (window.restoreReferenceRouteAtlas) window.restoreReferenceRouteAtlas();
      else if (!new URL(location.href).searchParams.has('atlas-feature')) window.returnToReferenceRouteAtlas?.();
      target.tabIndex = -1;
    }
    target.focus({ preventScroll: true });
    target.scrollIntoView({ block: 'start', behavior: 'instant' });
  }
  window.addEventListener('hashchange', revealLinkedCard);
  document.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor) return;
    let target;
    try { target = byId(decodeURIComponent(anchor.hash.slice(1))); } catch (_) { return; }
    if (!target?.matches('.route-card, .inventory-addition-card, #route-atlas')) return;
    event.preventDefault();
    if (target.id === 'route-atlas') window.returnToReferenceRouteAtlas?.();
    if (location.hash !== anchor.hash) history.pushState(null, '', anchor.hash);
    revealLinkedCard();
  });
  function renderProposedWidths(row, card) {
    if (!row.width_scope_audit) return;
    const records=row.width_evidence;node('h4','Source-supported branch widths',card);
    if(!records.length) {
      node('p','System width remains unknown. Branch widths cannot be added.',card);
      for(const id of row.component_proposed_ids)link('Inspect '+id.replaceAll('-',' '),`#inventory-addition-${id}`,node('p',null,card));
      return;
    }
    const figure=node('figure',null,card);figure.style.margin='0';const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
    svg.classList.add('proposed-width-chart');svg.dataset.owner=row.proposed_id;
    const h=records.length*90+42;svg.setAttribute('viewBox',`0 0 500 ${h}`);svg.setAttribute('role','img');
    svg.setAttribute('aria-label',row.name+': '+records.map(r=>r.width_range_km?`${r.source_publication_year} reported branch span ${r.width_range_km.join(' to ')} kilometres, no midpoint`:`${r.source_publication_year} ADT surface scale about ${r.approximate_width_km} kilometres, no numeric uncertainty supplied`).join('; ')+'. Different methods; not a width trend, annual range or confidence interval.');
    svg.style.cssText='width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';figure.append(svg);
    const add=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;svg.append(n);};
    const x=v=>50+390*v/75;
    records.forEach((r,i)=>{
      const y=70+i*90;
      add('text',{x:20,y:y-45,'font-size':26,fill:'#102f3b'},`${r.source_publication_year} · ${r.width_range_km?'reported branch span':'ADT surface scale'}`);
      if(r.width_range_km){
        const [low,high]=r.width_range_km;
        add('line',{x1:x(low),x2:x(high),y1:y,y2:y,stroke:'#176b82','stroke-width':5});
        for(const v of [low,high]){add('line',{x1:x(v),x2:x(v),y1:y-6,y2:y+6,stroke:'#176b82','stroke-width':2});add('text',{x:x(v),y:y-15,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);}
      }else{add('circle',{cx:x(r.approximate_width_km),cy:y,r:5,fill:'#176b82'});add('text',{x:x(r.approximate_width_km),y:y-15,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`About ${r.approximate_width_km} km`);}
    });
    const y=records.length*90+8;add('line',{x1:50,x2:440,y1:y,y2:y,stroke:'#526c77'});
    for(const v of [0,25,50,75])add('text',{x:x(v),y:y+25,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);
    node('figcaption','Different methods and smoothing: this comparison establishes no width trend, annual range or confidence interval. Range records have no selected midpoint; the approximate scalar has no numerical uncertainty supplied.',figure);
    node('p','ADT means absolute dynamic topography; the surface scale comes from altimetry-derived geostrophic flow. All records are local branch evidence for proposed identities, not whole-current dimensions.',card);
    for(const r of records){
      const detail=node('details',null,card);detail.id='proposed-width-'+r.id;
      node('summary',r.width_range_km?`${r.width_range_km.join('–')} km reported branch span`:`About ${r.approximate_width_km} km surface scale`,detail);
      node('p',`${r.geographic_scope} ${r.layer} ${r.boundary_rule}`,detail);
      node('p',`${r.temporal_interpretation} ${r.source_access}`,detail);
      link(r.source_citation,r.source_url,node('p',null,detail),true);
    }
    const url=new URL('query.html',location.href);url.searchParams.set('source-q',JSON.stringify({document:row.width_scope_audit.file,pointer:'/measurements',filters:[{field:'record.proposed_current_id',op:'eq',value:row.proposed_id}],limit:10}));
    link('Query these branch-width records',url.href,node('p',null,card));
    if(row.proposed_id==='norwegian-atlantic-front')node('p','The 2010 study discusses a broader time-mean frontal flow but gives no new numeric width. Its mean width remains unknown.',card);
  }
  let catalog;
  load("../research/ocean-current-inventory-expansion-candidates.json").then(value => {
    for (const row of value.entries) {
      const card = node("section", null, byId("inventory-addition-cards")); card.id = `inventory-addition-${row.proposed_id}`; card.className = "inventory-addition-card"; card.tabIndex = -1;
      node("h3", row.name, card);
      const navigation = node("p", null, card);
      link("Link to this proposed current", `#${card.id}`, navigation);
      navigation.append(document.createTextNode(" · "));
      link("Back to current atlas", "#route-atlas", navigation);
      node("p", `Proposed classification: ${row.proposed_kind}. ${row.identity_scope}`, card);
      node("p", "Inventory addition pending review; no whole-current length or rank admitted.", card);
      for (const evidence of row.evidence) {
        link(evidence.citation, evidence.url, node("p", null, card), true);
        node("p", `${evidence.locator} ${evidence.supports}`, card);
        if (evidence.source_access) node("p", `Source access: ${evidence.source_access}`, card);
      }
      renderProposedWidths(row,card);
      const list = node("ul", null, card); for (const gate of row.remaining_gates) node("li", gate, list);
    }
    byId("inventory-addition-status").textContent = `${value.entries.length} proposed inventory additions beyond the current 100-name ledger. Coverage is incomplete.`;
    requestAnimationFrame(revealInitialCard);
  }).catch(error => { byId("inventory-addition-status").textContent = `Inventory additions unavailable: ${error.message}`; });
  const widthInventoryReady = load("../research/ocean-current-width-inventory.json").then(value => {
    for (const row of value.measurements) {
      const tr = node("tr", null, byId("width-rows")); tr.id = `width-${row.id}`;
      link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.approximate_width_km == null ? `${row.width_range_km.map(number).join("–")} km ${row.phase_kind === "mean_offshore_extent_range" ? "offshore extent of mean surface flow; not full width or annual extrema" : row.phase_kind === "seasonal_mean_width_range" ? "author-reported seasonal mean span; not annual extrema" : row.phase_kind === "campaign_hydrographic_core" ? "reported local salinity-core span; not annual extrema" : "reported typical regional range"}` : `About ${number(row.approximate_width_km)} km${row.phase_kind === "survey_layer_median_threshold_width" ? ` ±${number(row.reported_total_error_km)} km reported total error; layer median` : ""}${row.phase_kind === "climatological_core_distribution" ? ` median across longitudes (${row.width_range_km.map(number).join("–")} km spatial range; not seasonal extrema)` : row.phase_kind === "survey_profile_composite" ? " fitted profile scale (not full width)" : row.phase_kind === "dated_band_section" ? " described subsurface band span (not full width)" : row.phase_kind === "month_dated_section" ? (row.angular_span_conversion?.source_reported_latitude_limits_degrees ? " described meridional band span (not fixed-depth full width)" : " reported section span (converted from latitude degrees)") : row.phase_kind === "ensemble_profile_band" ? " reported offshore flow-band span" : row.phase_kind === "ensemble_angular_summary" ? ` (source ${row.ensemble_angular_context.source_reported_latitude_span_degrees}° latitude; shared general summary)` : ""}`, tr);
      node("td", row.time_convention, tr);
      const scope = node("td", row.geographic_scope, tr);
      node("p", row.layer, scope); node("p", row.boundary_rule, scope);
      node("p", `${row.measurement_type.replaceAll("_", " ")}; not a uniform whole-current width.`, scope);
      node("p", `Metric: ${row.width_metric.replaceAll("_", " ")}. ${row.section_orientation}`, scope);
      if (row.source_quality_note) node("p", row.source_quality_note, scope);
      const source = node("td", null, tr); link(row.source_citation, row.source_url, source, true); node("p", row.source_locator, source);
    }
    for (const summary of value.seasonal_summaries) {
      const card = node("section", null, byId("width-seasonal-summaries")); card.id = `width-seasonal-${summary.current_id}`;
      const current = value.current_decisions.find(row => row.current_id === summary.current_id);
      node("h3", `${current.name}: ${summary.reported_seasonal_value_span_km.map(number).join("–")} km reported seasonal span`, card);
      node("p", summary.interpretation, card);
    }
    for (const row of value.current_decisions) {
      const tr = node("tr", null, byId("width-decision-rows")); tr.id = `width-decision-${row.current_id}`;
      link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.width_decision.replaceAll("_", " "), tr);
      const action = node("td", row.next_action, tr);
      const derived=value.derived_width_series_candidates?.find(candidate=>candidate.current_id===row.current_id);
      if(derived)link("Inspect derived section-width candidate",derived.visual_url||"../"+derived.file,node("p",null,action));
      const span=value.section_span_diagnostics?.find(diagnostic=>diagnostic.current_id===row.current_id);
      if(span){node("p",span.scope_note,action);link("Map dated component spans",span.visual_url,node("p",null,action));}
      const review = value.review_assessments?.find(review => review.current_id === row.current_id);
      if (review) {
        node("p", review.reason, action);
        for (const evidence of review.evidence) {
          link(evidence.citation, evidence.url, node("p", null, action), true);
          node("p", `${evidence.locator} ${evidence.supports}`, action);
        }
      }
    }
    const counts = value.counts;
    byId("width-status").textContent = `${counts.measurements} scoped width records for ${counts.currents_with_scoped_width_evidence} of ${counts.currents} currents; ${counts.currents_with_existing_mentions_pending_review} have existing mentions pending source review; ${counts.currents_with_derived_width_candidates_pending_review} have derived section-width series pending scientific review; ${counts.currents_with_sources_reviewed_no_numeric_width} reviewed without a comparable numeric current width; ${counts.currents_with_section_span_diagnostics_width_unresolved} have component-span diagnostics with width unresolved; ${counts.currents_not_assessed} not yet assessed. No annual whole-current widths admitted.`;
    return value;
  }).catch(error => { byId("width-status").textContent = `Width evidence unavailable: ${error.message}`; return null; });
  const seasonalRoutesReady = load("../research/ocean-current-seasonal-route-frames.json").catch(() => ({frames:[]}));
  function renderQueue() {
    const query = byId("route-query").value.trim().toLocaleLowerCase();
    const coverage = byId("route-coverage").value;
    const strategy = byId("route-strategy").value;
    const rows = catalog.remaining_current_decisions.filter(row => (!query || `${row.name} ${row.current_id} ${row.ledger_kind} ${row.route_strategy_label} ${row.existing_scope}`.toLocaleLowerCase().includes(query)) && (coverage === "all" || (coverage === "candidate" ? row.candidate_ids.length : !row.candidate_ids.length)) && (strategy === "all" || row.route_strategy_id === strategy));
    const body = byId("route-queue-rows"); body.replaceChildren();
    for (const row of rows) {
      const tr = node("tr", null, body); tr.id = `decision-${row.current_id}`; link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.existing_length_evidence_status.replaceAll("_", " "), tr);
      const planning = node("td", null, tr);
      node("strong", row.route_strategy_label, planning);
      node("p", `Ledger kind: ${row.ledger_kind}`, planning);
      node("p", row.next_action, planning);
      if (row.candidate_ids.length) node("p", `Scope work: ${row.strategy_next_action}`, planning);
      if (row.component_inventory_status === 'no_component_records_in_current_ledger') node("p", "Basin-member records have not yet been added to this inventory. This does not mean the flows are absent.", planning);
      if (row.known_component_currents.length) {
        const details = node("details", null, planning); node("summary", "Known component records (coverage may be incomplete)", details);
        for (const component of row.known_component_currents) link(component.name, objectHref(`current:${component.current_id}`), node("p", null, details));
      }
      const decision = node("td", null, tr);
      if (!row.candidate_ids.length) node("span", "Route not constructed", decision);
      else for (const id of row.candidate_ids) { const p = node("p", null, decision); const candidate = catalog.candidates.find(item => item.id === id); link(`Inspect ${candidate.route_extent_kind}`, `#${id}`, p); }
      const scope = node("td", row.existing_scope || "Scope unresolved", tr);
      if (row.name_source_url) { scope.append(document.createTextNode(" · ")); link("Naming source", row.name_source_url, scope, true); }
    }
    byId("queue-count").textContent = `${rows.length} of ${catalog.remaining_current_decisions.length} remaining currents`;
  }
  load("../research/ocean-current-reference-path-candidates.json").then(async value => {
    catalog = value;
    for (const strategy of catalog.planning_taxonomy.strategies) {
      const option = node("option", `${strategy.label} (${strategy.current_count})`, byId("route-strategy")); option.value = strategy.id;
      const tr = node("tr", null, byId("strategy-rows")); node("th", strategy.label, tr).scope = "row";
      node("td", `${strategy.current_count} records · ${strategy.unbuilt_count} awaiting routes`, tr);
      node("td", strategy.description, tr);
    }
    const [reports, seasonalRoutes] = await Promise.all([Promise.all(catalog.candidates.map(row => load(`../${row.candidate_file}`))), seasonalRoutesReady]);
    const body = byId("reference-route-rows");
    for (const id of catalog.reference_route_length_order) {
      const row = catalog.candidates.find(item => item.id === id);
      const tr = node("tr", null, body); tr.id = `comparison-${id}`; link(row.name, `#${id}`, node("td", null, tr));
      node("td", `≈ ${number(row.approximate_reference_path_km)} km`, tr);
      node("td", `${row.scenario_range_km.map(number).join("–")} km`, tr);
      const sensitivity = node("td", null, tr), bounds = row.ordering_sensitivity.envelope_position_bounds;
      node("span", bounds[0] === bounds[1] ? `Position ${bounds[0]} within retained envelopes` : `Positions ${bounds[0]}–${bounds[1]} within retained envelopes`, sensitivity);
      if (row.ordering_sensitivity.overlapping_candidate_ids.length) {
        const details = node("details", null, sensitivity);
        node("summary", "Overlapping route envelopes", details);
        for (const otherId of row.ordering_sensitivity.overlapping_candidate_ids) {
          const other = catalog.candidates.find(item => item.id === otherId);
          link(other.name, `#${otherId}`, node("p", null, details));
        }
      }
      node("td", row.scope, tr);
    }
    for (let index = 0; index < catalog.candidates.length; index++) {
      const row = catalog.candidates[index], report = reports[index];
      const card = node("section", null, byId("route-cards")); card.id = row.id; card.className = "route-card";
      card.tabIndex = -1;
      node("h3", `${row.name} · ${row.route_extent_kind}`, card);
      link("Link to this route card", `#${row.id}`, node("p", null, card));
      const back = link("Back to global current map ↑", '#route-atlas', node("p", null, card));

      node("p", `≈ ${number(row.approximate_reference_path_km)} km · ${row.scenario_count} scenarios · ${row.scenario_range_km.map(number).join("–")} km scenario envelope`, card);
      node("p", row.scope, card);
      if (report.parent_current_id) {
        const relation = node("p", report.parent_scope_note + " ", card);
        const parent = catalog.candidates.find(item => item.current_id === report.parent_current_id);
        link("Inspect parent current route", parent ? `#${parent.id}` : objectHref(`current:${report.parent_current_id}`), relation);
      }
      if (row.comparison_group === "osw_studied_reach_routes") node("p", "Studied reach only. Excluded from reference-route ordering above.", card).className = "warning";
      const image = node("img", null, card); image.className = "route-map"; image.src = `../${row.figure}`; image.alt = `${row.name}: schematic editorial route with labeled endpoints. Approximate length and scenario limits are provided in the surrounding text.`;
      // Reserve map height so earlier image loads cannot move the linked card.
      image.width = 800;
      image.height = Math.round(800 * report.map_view_box[3] / report.map_view_box[2]);
      link("Open route map at full size", `../${row.figure}`, node("p", null, card));
      node("p", report.coordinate_selection, card);
      node("p", `Layer: ${report.layer} Time convention: ${report.time_convention}`, card);
      node("p", report.scenario_rule, card);
      const source = node("p", "Source: ", card); link(report.source_citation, report.source_url, source, true);
      node("p", `Source locator: ${row.source_locator}`, card);
      if (report.source_anchor_observations?.length) {
        node("p", "Source frontal crossings · sampled separately; not current-axis endpoints", card);
        const anchors = node("ul", null, card);
        for (const anchor of report.source_anchor_observations) {
          const [lon,lat] = anchor.longitude_latitude;
          node("li", `${Math.abs(lon)}° ${lon < 0 ? "W" : "E"}, ${Math.abs(lat)}° ${lat < 0 ? "S" : "N"} · ${anchor.observed_period.start} to ${anchor.observed_period.end} (month precision) · observed front crossing, not velocity core`, anchors);
        }
      }
      for (const support of report.supporting_sources || []) {
        const citation = node("p", "Supporting source: ", card); link(support.citation, support.url, citation, true);
        node("p", `${support.locator} ${support.role || ""}`, card);
      }
      const geography = node("p", "Editorial route crosses atlas regions: ", card);
      const excludedStates=new Set((report.state_semantic_exclusions||[]).map(item=>item.state_code));
      for (const state of row.nominal_atlas_state_crossings.filter(code=>!excludedStates.has(code))) { link(state, objectHref(`state:${state}`), geography); geography.append(document.createTextNode(" ")); }
      if(report.state_scope_note)node('p',report.state_scope_note,card);
      const tile = report.nasa_movie_context.find(item => item.tile_id === report.recommended_nasa_tile_id);
      if (tile) link(`Open complete-route NASA crop ${tile.tile_id} (geographic context)`, tile.url, card, true);
      const details = node("details", null, card); node("summary", "Method and remaining review", details);
      node("p", report.method, details); node("p", report.map_land_check, details);
      const list = node("ul", null, details); for (const gate of row.remaining_gates) node("li", gate, list);
      const phase = seasonalRoutes.frames.find(frame => frame.route_candidate_file === row.candidate_file);
      link("Widths and seasonal evidence", `seasons.html?current=${encodeURIComponent(row.current_id)}${phase ? `&phase=${encodeURIComponent(phase.id)}` : ""}`, node("p", null, card));
      if(row.current_id==='atlantic-equatorial-undercurrent')window.renderAtlanticEucSectionProperties(card,await load('../research/atlantic-euc-layer-island-scope-audit.json'));
      link("Download coordinates, all scenarios and joins (JSON)", `../${row.candidate_file}`, card);
    }
    const counts = catalog.counts;
    byId("route-status").textContent = `${counts.route_candidates} route candidates for ${counts.currents_with_route_candidates} of ${counts.currents_without_published_ranked_estimate} currents; ${counts.currents_without_route_candidates} currents await routes. Scientific review pending.`;
    byId("route-query").addEventListener("input", renderQueue); byId("route-coverage").addEventListener("change", renderQueue); byId("route-strategy").addEventListener("change", renderQueue); renderQueue();
    requestAnimationFrame(revealInitialCard);
    window.initReferenceRouteAtlas?.(catalog, reports, await widthInventoryReady, seasonalRoutes);
  }).catch(error => { byId("route-status").textContent = `Route inventory unavailable: ${error.message}`; });
})();
