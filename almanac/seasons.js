(() => {
  const byId = id => document.getElementById(id);
  let inventory, catalog, seasonalRoutes, directionAudit, timer = null, phases = [], playbackIndices = [];
  function loadSeasonSources() {
    return new Promise((resolve,reject)=>{
      const worker=new Worker('query-worker.js?v=seasons-6');
      const timer=setTimeout(()=>finish(Error('Seasonal data request timed out')),90000);
      const finish=(error,result)=>{clearTimeout(timer);worker.terminate();if(error)reject(error);else resolve(result);};
      worker.onerror=()=>finish(Error('Rust seasonal data worker failed'));
      worker.onmessage=event=>{const {id,result}=event.data;
        if(!result.ok){finish(Error(result.error));return;}
        if(id===1){worker.postMessage({id:2,action:'seasons'});return;}
        try {
          window.oswSeasonSnapshot=result;
          byId('season-loading').dataset.engine=result.engine;
          finish(null,['widths','routes','frames','directions'].map(key=>JSON.parse(result.sources_json[key])));
        } catch(error){finish(error);}
      };
      worker.postMessage({id:1,action:'load'});
    });
  }
  function stop() { if (timer !== null) clearInterval(timer); timer = null; byId("season-play").textContent = "Play seasonal states"; }
  const phaseId = phase => phase?.frame?.id || phase?.width?.id || phase?.direction?.id;
  function renderAdcpComparison(container, selected) {
    container.hidden=false;
    const rows=inventory.measurements.filter(r=>r.current_id===selected.current_id&&r.phase_kind==='survey_layer_median_threshold_width');
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox','0 0 500 230');svg.setAttribute('role','img');
    svg.setAttribute('aria-label',rows.map(r=>`${r.phase_label}: ${r.approximate_width_km} kilometres, source total error plus or minus ${r.reported_total_error_km} kilometres`).join('; ')+'. Layer medians of four local crossings, not seasonal ranges or confidence intervals.');
    svg.style.cssText='width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
    const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
    const maximum=100,x=v=>80+380*v/maximum;
    rows.forEach((r,i)=>{
      const y=42+i*44,v=r.approximate_width_km,e=r.reported_total_error_km,color=r.id===selected.id?'#176b82':'#526c77';
      add('text',{x:16,y:y+7,fill:'#102f3b','font-size':22},r.adcp_threshold_context.crossing_id.toUpperCase());
      add('text',{x:460,y:y-12,'text-anchor':'end',fill:'#102f3b','font-size':22},`${v} ±${e} km`);
      add('line',{x1:x(v-e),x2:x(v+e),y1:y,y2:y,stroke:color,'stroke-width':3});
      for(const n of [v-e,v+e])add('line',{x1:x(n),x2:x(n),y1:y-6,y2:y+6,stroke:color,'stroke-width':2});
      add('circle',{cx:x(v),cy:y,r:5,fill:color});
    });
    add('line',{x1:80,x2:460,y1:204,y2:204,stroke:'#526c77'});
    for(const v of [0,50,100])add('text',{x:x(v),y:225,'text-anchor':'middle',fill:'#102f3b','font-size':22},`${v} km`);
    container.append(svg);
    const caption=document.createElement('figcaption');caption.textContent='ADCP means acoustic Doppler current profiler. A, B1, B2 and C are four 1997 cruise crossings; exact crossing dates remain unresolved. Points show the reported layer-median widths; whiskers show source total error estimates. Projection error is included already. No confidence level or seasonal range inferred.';container.append(caption);
  }
  function renderRegionalRange(row) {
    const container=byId('regional-width-range');container.replaceChildren();container.hidden=true;
    if(row?.source_scope_context){container.hidden=false;window.renderAbstractRegionalWidth(container,row);return;}
    if(row?.phase_kind==='survey_layer_median_threshold_width'){renderAdcpComparison(container,row);return;}
    if(!['regional_summary','mean_offshore_extent_range'].includes(row?.phase_kind)||!row.width_range_km)return;
    const offshore=row.phase_kind==='mean_offshore_extent_range';
    container.hidden=false;
    const [low,high]=row.width_range_km, maximum=Math.ceil(high/50)*50+(offshore?50:0);
    const ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox','0 0 500 110');svg.setAttribute('role','img');
    svg.setAttribute('aria-label',`${row.name}: ${offshore?'mean surface offshore extent':'reported regional width range'} ${low} to ${high} kilometres. Not annual extrema or a confidence interval.`);
    svg.style.cssText='width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
    const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
    const x=v=>40+420*v/maximum;
    add('line',{x1:40,x2:460,y1:80,y2:80,stroke:'#47616b'});
    add('line',{x1:x(low),x2:x(high),y1:45,y2:45,stroke:'#176b82','stroke-width':5});
    for(const v of [low,high]){add('line',{x1:x(v),x2:x(v),y1:35,y2:55,stroke:'#176b82','stroke-width':2});add('text',{x:x(v),y:25,'text-anchor':offshore?(v===low?'end':'start'):'middle',fill:'#102f3b','font-size':22},`${v} km`);}
    for(const v of [0,maximum])add('text',{x:x(v),y:101,'text-anchor':'middle',fill:'#102f3b','font-size':22},`${v} km`);
    container.append(svg);
    const caption=document.createElement('figcaption');caption.textContent=`${offshore?'Mean surface offshore extent':'Reported regional span'}: ${low}–${high} km. No midpoint selected. ${offshore?'This is a one-sided prose extent of averaged flow, not a paired-boundary full width. ':''}This is not an annual range, confidence interval or mapped current envelope.`;container.append(caption);
  }
  function renderPhase() {
    const phase = phases[Number(byId("season-phase").value)];
    const row = phase?.width;
    renderRegionalRange(row);
    const barMaximum = Math.max(50, Math.ceil(Math.max(...phases.filter(p => p.width?.approximate_width_km != null).map(p => p.width.approximate_width_km), 0) / 50) * 50);
    const frame = phase?.frame;
    const direction = phase?.direction;
    const current=byId("season-current").value;
    window.renderAtlanticCruiseWidths(byId('cruise-span-panel'), current, inventory);
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
    if(row?.phase_kind==='synoptic_stream_tube_section'){sectionLocator.hidden=false;window.renderStreamTubeWidths(sectionLocator,inventory.measurements.filter(r=>r.current_id===row.current_id));}
    if(window.currentSectionLocator?.coordinates(row)) {window.currentSectionLocator.render(sectionLocator,row); sectionLocator.hidden=false;}
    const widthText = row?.approximate_width_km == null ? row?.width_range_km ? `${row.width_range_km.join("–")} km reported typical regional range` : "width unknown" : `about ${row.approximate_width_km} km${row.phase_kind === "survey_profile_composite" ? " fitted profile scale (not full width)" : row.phase_kind === "month_dated_section" ? " reported section span (converted from latitude degrees)" : row.phase_kind === "ensemble_profile_band" ? " reported offshore flow-band span" : ""}`;
    byId("season-value").textContent = row ? `${row.name}: ${widthText}${row.width_metric_label ? ` · ${row.width_metric_label}` : ""} · ${row.time_convention}` : "Seasonal width not available in this pilot.";
    if(row?.phase_kind==='ensemble_angular_summary') {
      byId('season-title').textContent='General jet width summary';
      byId('season-value').textContent=`${row.name}: source reports ${row.ensemble_angular_context.source_reported_latitude_span_degrees}° latitude, approximately ${row.approximate_width_km} km · shared study summary`;
    }
    if(row?.phase_kind==='inverse_hydrographic_section_span')byId('season-title').textContent='Hydrographic cruise-section span';
    if(row?.phase_kind==='regional_scalar_summary')byId('season-title').textContent='Regional width summary';
    if(row?.phase_kind==='survey_layer_median_threshold_width') {
      byId('season-title').textContent='ADCP crossing width · layer median';
      byId('season-value').textContent=`${row.name}: ${row.approximate_width_km} ±${row.reported_total_error_km} km · source total error · ${row.phase_label} · 1997 cruise`;
    }
    if(row?.phase_kind==='synoptic_stream_tube_section')byId('season-title').textContent='Synoptic stream-tube section width';
    if(row?.phase_kind==='regional_summary')byId('season-title').textContent='Regional width range';
    if(row?.phase_kind==='mean_offshore_extent_range') {
      byId('season-title').textContent='Mean surface offshore extent';
      byId('season-value').textContent=`${row.name}: ${row.width_range_km.join('–')} km reported offshore extent · not full width`;
    }
    if(row?.phase_kind==='campaign_hydrographic_core') {
      byId('season-title').textContent='Local salinity-core observation';
      byId('season-value').textContent=`${row.name}: ${row.width_range_km?row.width_range_km.join('–'):'about '+row.approximate_width_km} km local water-mass core · ${row.phase_label} · ${row.time_convention}`;
    }
    byId("season-bar").parentElement.hidden = row?.approximate_width_km == null || row?.mean_section_context?.section_axis_kind==='oblique' || (["synoptic_stream_tube_section","survey_layer_median_threshold_width","inverse_hydrographic_section_span","survey_profile_composite","dated_band_section","climatological_core_distribution","campaign_hydrographic_core","ensemble_angular_summary","regional_scalar_summary","monthly_climatological_fit","stream_mean_threshold_summary","eulerian_mean_section_span","width_time_series_statistics"].includes(row?.phase_kind));
    byId("season-bar").style.width = row ? `${Math.min(100, row.approximate_width_km / barMaximum * 100)}%` : "0%";
    byId("season-definition").textContent = row ? `${row.geographic_scope} ${row.layer} ${row.boundary_rule} ${byId("season-bar").parentElement.hidden ? row.range_interpretation : `Bar scale: 0–${barMaximum} km.`}` : "This current needs scoped seasonal observations; unknown does not mean zero width.";
    if (frame) {
      byId("season-value").textContent = `${frame.phase_label}: ${frame.flow_direction} · editorial seasonal route${row ? ` · regional width context: about ${row.approximate_width_km} km` : ""}`;
      byId("season-definition").textContent = `${frame.time_convention} ${frame.layer} ${row ? `${row.geographic_scope} ${row.boundary_rule} ${frame.width_scope_note} Bar scale: 0–${barMaximum} km.` : "Width: unknown."} No occupied footprint inferred.`;
    }
    byId("season-length").textContent = frame && route ? `Approximate scoped route length: ${route.approximate_reference_path_km.toLocaleString("en-US")} km; ${route.scenario_range_km.map(v => v.toLocaleString("en-US")).join("–")} km editorial sensitivity envelope. Different phase scopes cannot supply annual extrema.` : "Seasonal length: unknown for this recorded phase. No annual minimum/maximum or uncertainty margin inferred.";
    if(row?.phase_kind==='campaign_hydrographic_core')byId('season-definition').textContent=`${row.geographic_scope}. ${row.layer} Boundary: ${row.boundary_rule}. This is a water-mass core metric, not a paired velocity envelope. Bar omitted; section locations and occupations cannot supply an annual cycle.`;
    if(row?.phase_kind==='ensemble_angular_summary')byId('season-definition').textContent=`${row.geographic_scope} ${row.layer} ${row.boundary_rule} Equator used only for unit conversion, not an observed location. Shared source claim, not independent jet measurements. Core displacement and PV-front scale are separate metrics. Bar omitted; annual variation unresolved.`;
    if(row?.phase_kind==='mean_offshore_extent_range')byId('season-definition').textContent+=` ${row.time_convention} ${row.mean_offshore_context.source_date_discrepancy} No edge locator or route buffer inferred; annual variation unresolved.`;
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
    const plan=window.oswSeasonSnapshot.phase_plans[id];
    if(!plan)throw Error('No checked seasonal phase plan for this current');
    const widths=new Map(inventory.measurements.map(row=>[row.id,row])),frames=new Map(seasonalRoutes.frames.map(row=>[row.id,row])),directions=new Map(directionAudit.phases.map(row=>[row.id,row]));
    phases=plan.phases.map(row=>({width:widths.get(row.width_id),frame:frames.get(row.frame_id),direction:directions.get(row.direction_id),label:row.label}));
    playbackIndices=plan.eligible_indices;
    window.oswSeasonPlan=plan;
    const select = byId("season-phase"); select.replaceChildren();
    for (const [i, row] of phases.entries()) { const option = document.createElement("option"); option.value = i; option.textContent = row.label; select.append(option); }
    const requestedIndex = phases.findIndex(phase => phaseId(phase) === requestedPhase);
    if(requestedIndex >= 0)select.value=String(requestedIndex);
    select.disabled = !phases.length;
    byId("season-play").disabled = !plan.can_play;
    byId("season-range").textContent = plan.range_note;
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
  loadSeasonSources().then(([widths, routes, routeFrames, directions]) => {
    inventory = widths; catalog = routes; seasonalRoutes = routeFrames; directionAudit = directions;
    for (const row of inventory.current_decisions) { const option = document.createElement("option"); option.value = row.current_id; option.textContent = row.name; byId("season-current").append(option); }
    const requestedCurrent = new URLSearchParams(window.location.search).get("current");
    byId("season-current").value = inventory.current_decisions.some(row => row.current_id === requestedCurrent) ? requestedCurrent : "northern-mediterranean";
    byId("season-current").addEventListener("change", () => renderCurrent());
    byId("season-phase").addEventListener("change", () => { stop(); renderPhase(); });
    byId("season-play").addEventListener("click", () => { if (timer !== null) { stop(); return; } byId("season-play").textContent = "Pause"; timer = setInterval(() => { const eligible = playbackIndices; const current = eligible.indexOf(Number(byId("season-phase").value)); byId("season-phase").value = eligible[(current + 1) % eligible.length]; renderPhase(); }, 2200); });
    document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
    byId("season-loading").textContent = "100 currents indexed; Northern Current width states, Somali components and Sri Lanka Monsoon Current editorial seasonal routes can play. Azores sections, Mediterranean Undercurrent observations and the historical Davidson winter summary can be inspected. New Guinea local direction composites can play, with El Niño exceptions selectable separately. Scientific review pending.";
    renderCurrent(new URL(location.href).searchParams.get("phase"));
  }).catch(error => { byId("season-loading").textContent = error.message; });
})();
