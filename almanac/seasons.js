(() => {
  const byId = id => document.getElementById(id);
  let inventory, catalog, seasonalRoutes, directionAudit, timer = null, phases = [];
  function validDirectionAudit(data) {
    if (data?.schema !== "osw.current-seasonal-direction-scope-audit.v1" || data.current_id !== "new-guinea-coastal-current" || !Array.isArray(data.phases) || data.phases.length !== 3) return false;
    const expected = [[11,12,1,2,3,4],[5,6,7,8,9,10],null];
    return data.phases.every((p,i) => p.current_id === data.current_id && p.flow_direction === ["southeastward","northwestward","southeastward NGCC absent; northwestward undercurrent shoals"][i] && p.geometry_role === "local_direction_symbol_not_current_axis" && JSON.stringify(p.site_lon_lat) === "[141.4,-1.7]" && JSON.stringify(p.calendar_months) === JSON.stringify(expected[i]) && p.playback_eligible === (i < 2) && p.phase_kind === (i < 2 ? "seasonal_direction_composite" : "event_exception") && ["length_km","width_km","route_coordinates","annual_length_range_km","annual_width_range_km"].every(key => p[key] === null));
  }
  function stop() { if (timer !== null) clearInterval(timer); timer = null; byId("season-play").textContent = "Play seasonal states"; }
  const phaseId = phase => phase?.frame?.id || phase?.width?.id || phase?.direction?.id;
  function renderPhase() {
    const phase = phases[Number(byId("season-phase").value)];
    const row = phase?.width;
    const barMaximum = Math.max(50, Math.ceil(Math.max(...phases.filter(p => p.width?.approximate_width_km != null).map(p => p.width.approximate_width_km), 0) / 50) * 50);
    const frame = phase?.frame;
    const direction = phase?.direction;
    const current=byId("season-current").value;
    const address=new URL(location.href);address.searchParams.set("current",current);
    if(phaseId(phase))address.searchParams.set("phase",phaseId(phase));else address.searchParams.delete("phase");
    history.replaceState(null,"",address);
    byId("season-share").href=address.href;
    const atlas=new URL("reference-routes.html",location.href);atlas.searchParams.set("atlas-feature","current:"+current);atlas.hash="route-atlas";
    const frameRoute=phase?.frame && catalog.candidates.find(row=>row.candidate_file===phase.frame.route_candidate_file);
    if(frameRoute)atlas.searchParams.set("atlas-route",frameRoute.id);
    if(current==='leeuwin'&&row?.calendar_months?.length===1){atlas.searchParams.set('atlas-width-month',String(row.calendar_months[0]));atlas.searchParams.set('atlas-layout','map');}
    if(current==='kuroshio'&&row?.stream_mean_context?.season){atlas.searchParams.set('atlas-width-season',row.stream_mean_context.season);atlas.searchParams.set('atlas-layout','map');}
    byId("season-atlas").href=atlas.href;
    renderDirection(direction);
    byId("season-title").textContent = frame || row?.phase_kind === "seasonal_summary" ? "Seasonal state" : row?.phase_kind === "survey_threshold_section" ? "Survey section observation" : row?.phase_kind === "month_dated_section" ? "Historical section observation" : row?.phase_kind === "ensemble_profile_band" ? "Composite profile observation" : "Recorded evidence";
    const route = frame ? catalog.candidates.find(row => row.candidate_file === frame.route_candidate_file) : catalog.candidates.find(row => row.current_id === byId("season-current").value);
    renderMap(route, frame);
    const sectionLocator=byId("season-section-locator"); sectionLocator.replaceChildren(); sectionLocator.hidden=true;
    if(window.currentSectionLocator?.coordinates(row)) {window.currentSectionLocator.render(sectionLocator,row); sectionLocator.hidden=false;}
    const widthText = row?.approximate_width_km == null ? row?.width_range_km ? `${row.width_range_km.join("–")} km reported typical regional range` : "width unknown" : `about ${row.approximate_width_km} km${row.phase_kind === "survey_profile_composite" ? " fitted profile scale (not full width)" : row.phase_kind === "month_dated_section" ? " reported section span (converted from latitude degrees)" : row.phase_kind === "ensemble_profile_band" ? " reported offshore flow-band span" : ""}`;
    byId("season-value").textContent = row ? `${row.name}: ${widthText}${row.width_metric_label ? ` · ${row.width_metric_label}` : ""} · ${row.time_convention}` : "Seasonal width not available in this pilot.";
    if(row?.phase_kind==='ensemble_angular_summary') {
      byId('season-title').textContent='General jet width summary';
      byId('season-value').textContent=`${row.name}: source reports ${row.ensemble_angular_context.source_reported_latitude_span_degrees}° latitude, approximately ${row.approximate_width_km} km · shared study summary`;
    }
    if(row?.phase_kind==='regional_scalar_summary')byId('season-title').textContent='Regional width summary';
    if(row?.phase_kind==='campaign_hydrographic_core') {
      byId('season-title').textContent='Local salinity-core observation';
      byId('season-value').textContent=`${row.name}: ${row.width_range_km?row.width_range_km.join('–'):'about '+row.approximate_width_km} km local water-mass core · ${row.phase_label} · ${row.time_convention}`;
    }
    byId("season-bar").parentElement.hidden = row?.approximate_width_km == null || row?.mean_section_context?.section_axis_kind==='oblique' || (["survey_profile_composite","dated_band_section","climatological_core_distribution","campaign_hydrographic_core","ensemble_angular_summary","regional_scalar_summary","monthly_climatological_fit","stream_mean_threshold_summary","eulerian_mean_section_span","width_time_series_statistics"].includes(row?.phase_kind));
    byId("season-bar").style.width = row ? `${Math.min(100, row.approximate_width_km / barMaximum * 100)}%` : "0%";
    byId("season-definition").textContent = row ? `${row.geographic_scope} ${row.layer} ${row.boundary_rule} ${byId("season-bar").parentElement.hidden ? row.range_interpretation : `Bar scale: 0–${barMaximum} km.`}` : "This current needs scoped seasonal observations; unknown does not mean zero width.";
    if (frame) {
      byId("season-value").textContent = `${frame.phase_label}: ${frame.flow_direction} · editorial seasonal route${row ? ` · regional width context: about ${row.approximate_width_km} km` : ""}`;
      byId("season-definition").textContent = `${frame.time_convention} ${frame.layer} ${row ? `${row.geographic_scope} ${row.boundary_rule} ${frame.width_scope_note} Bar scale: 0–${barMaximum} km.` : "Width: unknown."} No occupied footprint inferred.`;
    }
    byId("season-length").textContent = frame && route ? `Approximate scoped route length: ${route.approximate_reference_path_km.toLocaleString("en-US")} km; ${route.scenario_range_km.map(v => v.toLocaleString("en-US")).join("–")} km editorial sensitivity envelope. Different phase scopes cannot supply annual extrema.` : "Seasonal length: unknown for this recorded phase. No annual minimum/maximum or uncertainty margin inferred.";
    if(row?.phase_kind==='campaign_hydrographic_core')byId('season-definition').textContent=`${row.geographic_scope}. ${row.layer} Boundary: ${row.boundary_rule}. This is a water-mass core metric, not a paired velocity envelope. Bar omitted; section locations and occupations cannot supply an annual cycle.`;
    if(row?.phase_kind==='ensemble_angular_summary')byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} Equator used only for unit conversion, not an observed location. Shared source claim, not independent jet measurements. Core displacement and PV-front scale are separate metrics. Bar omitted; annual variation unresolved.`;
    if(row?.phase_kind==='regional_scalar_summary')byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} No edge locator or full-width bar inferred from this regional scalar. Annual variation unresolved.`;
    if(row?.phase_kind==='width_time_series_statistics') {
      const statistics=row.width_statistics_context.reported_statistics;
      byId('season-title').textContent='Local surface jet width statistics';
      byId('season-value').textContent=`${row.name}: ${statistics.mean_km} km mean · ${row.width_range_km.join('–')} km observed range · ${row.phase_label}`;
      byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} ${row.range_interpretation} Seasonal pattern: peak in August/September; minimum in late winter. The atlas card links to a separate monthly graph-reading chart; geographic boundaries remain unresolved, so map playback is omitted.`;
    }
    if(row?.phase_kind==='eulerian_mean_section_span'){byId('season-title').textContent='Eulerian mean section span';byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} No boundary coordinates or instantaneous moving-boundary series extracted; bar and seasonal playback omitted.`;}
    if(row?.phase_kind==='stream_mean_threshold_summary') {
      byId('season-title').textContent='Regional surface stream-mean width';
      byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} Mean of weekly diagnosed cross-stream spans, not width of a seasonal mean velocity field. Regional averages can hide opposite local seasonal changes. No seasonal map edges, full-current width or physical annual range inferred.`;
    }
    if(row?.phase_kind==='monthly_climatological_fit') {
      byId('season-title').textContent='Monthly climatological fitted width';
      byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} Mean of per-cycle fitted widths, not width of the monthly mean velocity field. This inspector preserves the two prose-reported values. The atlas card separately provides all twelve graph readings with reading allowances; no edge locator or full-current width inferred.`;
    }
    if (row?.phase_kind === "month_dated_section" && row.angular_span_conversion?.source_reported_latitude_limits_degrees) {
      byId("season-title").textContent="Month-dated current band";
      byId("season-value").textContent=`${row.name}: about ${row.approximate_width_km} km described meridional band span · ${row.observed_month}`;
      byId("season-definition").textContent=`${row.time_convention} ${row.geographic_scope} ${row.layer} ${row.boundary_rule} Computational midpoint is not an observed current center. Full-width bar omitted.`;
      byId("season-bar").parentElement.hidden=true;
    }
    if (row?.phase_kind === "seasonal_mean_width_range") {
      byId("season-title").textContent = "Seasonal mean undercurrent width";
      byId("season-value").textContent = `${row.name}: ${row.width_range_km.join("–")} km author-reported seasonal mean span`;
      byId("season-definition").textContent = `${row.time_convention} ${row.geographic_scope} ${row.layer} ${row.boundary_rule} Width of a seasonal mean section, not the mean of instantaneous widths. ${row.range_interpretation}`;
    }
    if (row?.phase_kind === "survey_profile_composite") byId("season-definition").textContent += " Fitted center-to-e-folding scale; full-width bar omitted. Composite depth and exact sampling dates unresolved.";
    if (row?.phase_kind === "survey_threshold_section") byId("season-definition").textContent += " This local section uses a relative velocity threshold. Campaign months provide sampling context; exact section dates and a fixed depth layer remain unresolved. The bar does not show an annual or whole-current width.";
    if (row?.phase_kind === "dated_band_section") {
      byId("season-title").textContent = "Dated subsurface band";
      byId("season-value").textContent = `${row.name}: about ${row.approximate_width_km} km described meridional band span`;
      byId("season-definition").textContent = `${row.geographic_scope} ${row.layer} ${row.boundary_rule} Full-width bar omitted; no route buffer or annual range inferred.`;
    }
    if (row?.source_quality_note) byId("season-definition").textContent += ` ${row.source_quality_note}`;
    if (row?.phase_kind === "climatological_core_distribution") {
      byId("season-title").textContent = "Climatological core · spatial variation";
      byId("season-value").textContent = `${row.name}: ${row.approximate_width_km} km median across longitudes · ${row.width_range_km.join("–")} km spatial range`;
      byId("season-definition").textContent = `${row.time_convention} ${row.geographic_scope} ${row.layer} ${row.boundary_rule} Median and range describe longitude-to-longitude variation of a three-dimensional threshold core. They are not fixed-depth full widths, seasonal extrema or confidence limits. Full-width bar omitted.`;
    }
    if (row?.phase_kind === "mean_velocity_section") {
      byId("season-title").textContent = "Mean velocity section";
      if(row.mean_section_context?.section_axis_kind==='oblique') {
        byId('season-title').textContent='Mean oblique section';
        byId('season-bar').parentElement.hidden=true;
        byId('season-definition').textContent+=` ${row.mean_section_context.section_id} / ${row.mean_section_context.source_flow_label}, source rotation ${row.mean_section_context.rotation_angle_degrees}°. Width of the mean rotated velocity field, not mean instantaneous widths. Unextracted section geometry cannot supply an edge locator or route buffer. These sections are not seasonal phases.`;
      } else byId("season-definition").textContent += " Width of the averaged velocity field, not an average of instantaneous widths. These section locations do not form a seasonal sequence; the route beside them has its own summer scope.";
    }
    const source = byId("season-source"); source.replaceChildren();
    const evidence = direction || row || route;
    if (evidence) { const a = document.createElement("a"); a.href = evidence.source_url; a.textContent = direction ? `Local direction source: ${direction.source_locator}` : row ? row.source_citation : `${frame ? "Seasonal route" : "Static reference route"} source: ${evidence.source_locator}`; a.target = "_blank"; a.rel = "noopener noreferrer"; source.append(a); }
    if (direction) {
      byId("season-title").textContent = direction.phase_kind === "event_exception" ? "Observed El Niño exception" : "Local seasonal direction composite";
      byId("season-value").textContent = `${direction.phase_label}: ${direction.flow_direction}`;
      byId("season-definition").textContent = `${directionAudit.scope} ${directionAudit.sampling_note} ${direction.layer}`;
      byId("season-length").textContent = "Seasonal length and width: unknown. Direction symbols have no measured length or width.";
      byId("season-map-note").textContent = "Mooring location on coarse OSW display geography; coastline detail is insufficient to place the coastal boundary precisely. Arrow indicates local direction only; it is not a route, occupied footprint or a connection to another current.";
      byId("season-nasa").replaceChildren();
      const a = document.createElement("a"); a.href = `../research/new-guinea-coastal-current-seasonal-direction-scope-audit.json`; a.textContent = "Inspect seasonal direction evidence and limits"; byId("season-nasa").append(a);
    }
  }
  function renderDirection(row) {
    const panel = byId("season-direction"); panel.hidden = !row;
    if (!row) return;
    const [lon,lat] = row.site_lon_lat;
    const x = 60+(lon+180)/360*1480, y = 90+(90-lat)/180*740;
    byId("season-direction-map").setAttribute("viewBox", `${x-15} ${y-10} 30 20`);
    byId("season-direction-site").setAttribute("cx",x); byId("season-direction-site").setAttribute("cy",y);
    const arrow = byId("season-direction-arrow"); arrow.hidden = row.phase_kind === "event_exception";
    arrow.setAttribute("visibility", row.phase_kind === "event_exception" ? "hidden" : "visible");
    arrow.setAttribute("transform", `translate(${x} ${y}) rotate(${row.flow_direction === "northwestward" ? 225 : 45})`);
    byId("season-direction-description").textContent = `${lon}° E, ${Math.abs(lat)}° S · ${row.flow_direction}. Symbol size is illustrative; no speed, current extent or measured dimensions encoded.`;
    const months = byId("season-direction-months"); months.replaceChildren();
    for (const month of row.calendar_months || []) { const span = document.createElement("span"); span.textContent = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][month-1]; months.append(span); }
  }
  function renderCurrent(requestedPhase = null) {
    stop(); const id = byId("season-current").value;
    const frames = seasonalRoutes.frames.filter(row => row.current_id === id);
    const linkedWidths = new Set(frames.flatMap(row => row.width_measurement_ids));
    phases = inventory.measurements.filter(row => row.current_id === id && !linkedWidths.has(row.id)).map(row => ({width:row, label:row.phase_label || row.time_convention.split(" ")[0]}));
    phases.push(...frames.map(row => ({frame:row, width:inventory.measurements.find(width => row.width_measurement_ids.includes(width.id)), label:row.phase_label})));
    if (id === directionAudit.current_id) phases.push(...directionAudit.phases.map(row => ({direction:row,label:row.phase_label})));
    const select = byId("season-phase"); select.replaceChildren();
    for (const [i, row] of phases.entries()) { const option = document.createElement("option"); option.value = i; option.textContent = row.label; select.append(option); }
    const requestedIndex = phases.findIndex(phase => phaseId(phase) === requestedPhase);
    if(requestedIndex >= 0)select.value=String(requestedIndex);
    const summary = inventory.seasonal_summaries.find(row => row.current_id === id);
    const restriction = inventory.comparability_notes?.find(row => row.current_id === id);
    const comparableWidths = summary && phases.every(p => p.width && summary.measurement_ids.includes(p.width.id));
    const routePhases = phases.length > 1 && phases.every(p => p.frame);
    select.disabled = !phases.length;
    byId("season-play").disabled = phases.length < 2 || Boolean(restriction) || !(comparableWidths || routePhases || phases.filter(p => p.direction?.playback_eligible).length > 1);
    byId("season-range").textContent = summary ? `${summary.reported_seasonal_value_span_km.join("–")} km: ${summary.interpretation}` : "Annual width range and measurement uncertainty: not available. A single dated section does not establish a seasonal cycle.";
    const comparison = seasonalRoutes.comparability.find(row => row.current_id === id);
    if (comparison) byId("season-range").textContent = comparison.reason;
    if (restriction) byId("season-range").textContent = restriction.reason;
    if (id === directionAudit.current_id) byId("season-range").textContent = directionAudit.interpretation;
    renderPhase();
  }
  function renderMap(route, frame) {
    const map = byId("season-map"); map.hidden = !route;
    if (route) { map.src = `../${route.figure}`; map.alt = frame ? `${frame.phase_label}: ${frame.flow_direction} editorial route for ${route.name}; not observed seasonal footprint` : `Static editorial reference route for ${route.name}; seasonal geometry unresolved`; }
    else map.removeAttribute("src");
    byId("season-map-note").textContent = route ? `${frame ? "Selected editorial seasonal component" : "Static route context"}: approximately ${route.approximate_reference_path_km.toLocaleString("en-US")} km. ${route.scope}` : "Reference route not yet constructed. Seasonal path geometry is also unresolved.";
    const nasa = byId("season-nasa"); nasa.replaceChildren();
    if (route) { const a = document.createElement("a"); a.href = `reference-routes.html#${route.id}`; a.textContent = "Inspect route assumptions and NASA geographic context"; nasa.append(a); }
  }
  Promise.all([fetch("../research/ocean-current-width-inventory.json").then(r => { if (!r.ok) throw Error("Width evidence unavailable"); return r.json(); }), fetch("../research/ocean-current-reference-path-candidates.json").then(r => { if (!r.ok) throw Error("Route context unavailable"); return r.json(); }), fetch("../research/ocean-current-seasonal-route-frames.json").then(r => { if (!r.ok) throw Error("Seasonal route evidence unavailable"); return r.json(); }), fetch("../research/new-guinea-coastal-current-seasonal-direction-scope-audit.json").then(r => { if (!r.ok) throw Error("Local direction evidence unavailable"); return r.json(); })]).then(([widths, routes, routeFrames, directions]) => {
    inventory = widths; catalog = routes; seasonalRoutes = routeFrames; directionAudit = directions;
    if (!validDirectionAudit(directions)) throw Error("Invalid local direction evidence");
    for (const row of inventory.current_decisions) { const option = document.createElement("option"); option.value = row.current_id; option.textContent = row.name; byId("season-current").append(option); }
    const requestedCurrent = new URLSearchParams(window.location.search).get("current");
    byId("season-current").value = inventory.current_decisions.some(row => row.current_id === requestedCurrent) ? requestedCurrent : "northern-mediterranean";
    byId("season-current").addEventListener("change", () => renderCurrent());
    byId("season-phase").addEventListener("change", () => { stop(); renderPhase(); });
    byId("season-play").addEventListener("click", () => { if (timer !== null) { stop(); return; } byId("season-play").textContent = "Pause"; timer = setInterval(() => { const eligible = phases.map((p,i) => p.direction && !p.direction.playback_eligible ? null : i).filter(i => i !== null); const current = eligible.indexOf(Number(byId("season-phase").value)); byId("season-phase").value = eligible[(current + 1) % eligible.length]; renderPhase(); }, 2200); });
    document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
    byId("season-loading").textContent = "100 currents indexed; Northern Current width states, Somali components and Sri Lanka Monsoon Current editorial seasonal routes can play. Azores sections, Mediterranean Undercurrent observations and the historical Davidson winter summary can be inspected. New Guinea local direction composites can play, with El Niño exceptions selectable separately. Scientific review pending.";
    renderCurrent(new URL(location.href).searchParams.get("phase"));
  }).catch(error => { byId("season-loading").textContent = error.message; });
})();
