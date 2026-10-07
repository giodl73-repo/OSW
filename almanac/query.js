"use strict";
(() => {
  const $=id=>document.getElementById(id),worker=new Worker('query-worker.js?v=3');
  const pending=new Map();let sequence=0,metadata,lastQuery=null,lastResult=null,busy=false,detailSequence=0;
  let playbackTimer=null,playing=false,playbackGeneration=0;
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  function stopPlayback(){playing=false;playbackGeneration++;clearTimeout(playbackTimer);$('query-map-play').textContent='Play recorded days';$('query-map-play').setAttribute('aria-pressed','false');$('query-map-play-months').textContent='Play source months';$('query-map-play-months').setAttribute('aria-pressed','false');$('query-map-play-samples').textContent='Play recorded section days';$('query-map-play-samples').setAttribute('aria-pressed','false');}
  async function playSectionDay(base,days,index,generation){
    if(!playing||generation!==playbackGeneration||index>=days.length){if(generation===playbackGeneration)stopPlayback();return;}
    if(busy){playbackTimer=setTimeout(()=>playSectionDay(base,days,index,generation),100);return;}
    const query=JSON.parse(JSON.stringify(base));query.offset=0;
    query.filters.push({field:'observation_date',op:'eq',value:days[index]});
    await run(query,true);if(!lastResult){stopPlayback();return;}
    if(playing&&generation===playbackGeneration)playbackTimer=setTimeout(()=>playSectionDay(base,days,index+1,generation),1000);
  }
  async function startSectionPlayback(){
    if(playing){stopPlayback();return;}
    if(!lastQuery||busy||reducedMotion.matches||lastQuery.collection!=='width_samples')return;
    playing=true;const generation=++playbackGeneration;
    $('query-map-play-samples').textContent='Pause recorded section days';$('query-map-play-samples').setAttribute('aria-pressed','true');
    const base=JSON.parse(JSON.stringify(lastQuery)),selected=sampleFilters(base.filters).represented['query-sample-day'];
    // Replace only the day represented by the visible control. Retain every
    // duplicate, unsupported predicate, year, month, method and source filter.
    base.filters=(base.filters||[]).filter(f=>f!==selected);base.offset=0;
    try{
      const inventory=await rpc('query',{...base,limit:1});
      if(!playing||generation!==playbackGeneration)return;
      if(!inventory.ok)throw Error(inventory.error);
      const scene=inventory.map_scene,days=scene?.recorded_days||[],bounds=scene?.display_bounds;
      if(!days.length){stopPlayback();return;}
      if(bounds){const width=Math.max(4,(bounds[2]-bounds[0])*1.5,(bounds[3]-bounds[1])*3);mapSet([(bounds[0]+bounds[2]-width)/2,(bounds[1]+bounds[3])/2-width/4,width,width/2]);}
      const index=selected?days.indexOf(selected.value):0;
      await playSectionDay(base,days,index>=0?index:0,generation);
    }catch(error){if(generation===playbackGeneration){stopPlayback();failure('Section playback failed: '+error.message);}}
  }
  async function playMonth(month,generation){
    if(!playing||generation!==playbackGeneration||month>12){if(generation===playbackGeneration)stopPlayback();return;}
    if(busy){playbackTimer=setTimeout(()=>playMonth(month,generation),100);return;}
    const query=JSON.parse(JSON.stringify(lastQuery));delete query.geometry_time;query.offset=0;query.seasonal={month};
    await run(query,true);if(!lastResult){stopPlayback();return;}
    if(playing&&generation===playbackGeneration)playbackTimer=setTimeout(()=>playMonth(month+1,generation),1000);
  }
  async function playDay(index,generation){
    const days=metadata.geometry_observation_dates||[];
    if(!playing||generation!==playbackGeneration||index>=days.length){if(generation===playbackGeneration)stopPlayback();return;}
    if(busy){playbackTimer=setTimeout(()=>playDay(index,generation),100);return;}
    const query=JSON.parse(JSON.stringify(lastQuery));delete query.seasonal;query.offset=0;query.geometry_time={from:days[index],to:days[index],include_undated:query.geometry_time?.include_undated||false};
    await run(query,true);
    if(!lastResult){stopPlayback();return;}
    if(playing&&generation===playbackGeneration)playbackTimer=setTimeout(()=>playDay(index+1,generation),1000);
  }
  const names={objects:'Currents and eddies',widths:'Scoped width records',reference_routes:'Editorial reference routes',measurements:'Published measurement records',states:'OSW states',state_links:'Recorded state links',sources:'Sources',claims:'Claims',relations:'Relations',entities:'All ledger entities',geometries:'Stored geometries',series:'Time-series indexes',diagnostics:'Diagnostic documents',working_records:'Proposed working records',flow_networks:'Flow networks',flow_network_nodes:'Network nodes',flow_network_edges:'Network connections',passage_samples:'Passage transport samples'};
  names.taxonomy_links='Declared identity memberships';
  names.geometry_frames='Dated diagnostic geometry frames';
  names.seasonal_routes='Source-defined seasonal routes';
  names.width_samples='Scoped width samples';
  names.route_decisions='Remaining current-length decisions';
  names.model_frames='Hourly model section frames';
  names.model_samples='Model section field samples';
  const widthFamilies={leeuwin_monthly_fitted_plot:'Monthly fitted-width plot readings at Leeuwin track a101',kuroshio_seasonal_profile_plot:'Seasonal axis-normal threshold-profile plot readings',necc_monthly_connected_component:'Monthly-mean positive-zonal connected-component diagnostics'};
  widthFamilies.loop_dated_half_peak_section='Recorded-day Yucatan gate half-peak northward-component spans';
  widthFamilies.gulf_stream_dated_half_peak_section='Recorded-day half-peak eastward-component section spans at 70 W';
  const order=Object.keys(names);
  const ns='http://www.w3.org/2000/svg';let mapView=[0,0,360,180],mapDrag=null,mapMoved=false;
  function mapSet(view){const w=Math.min(360,Math.max(4,view[2]));mapView=[Math.max(0,Math.min(360-w,view[0])),Math.max(0,Math.min(180-w/2,view[1])),w,w/2];$('query-map').setAttribute('viewBox',mapView.join(' '));for(const point of $('query-map-features').querySelectorAll('circle'))point.setAttribute('r',w/288);$('query-map-ground').setAttribute('href',w<100?'../figures/ocean-motion-closeup-ground.svg':'../figures/ocean-motion-dashboard-ground.svg');const longitude=x=>Math.abs(x-180).toFixed(1)+'° '+(x<180?'W':'E'),latitude=y=>Math.abs(90-y).toFixed(1)+'° '+(y<=90?'N':'S');$('query-map-position').textContent='Display window: '+longitude(mapView[0])+' to '+longitude(mapView[0]+w)+' · '+latitude(mapView[1]+w/2)+' to '+latitude(mapView[1])+' · equirectangular, display only.';}
  function mapZoom(factor,x=mapView[0]+mapView[2]/2,y=mapView[1]+mapView[3]/2){const w=Math.min(360,Math.max(4,mapView[2]*factor));mapSet([x-(x-mapView[0])*w/mapView[2],y-(y-mapView[1])*w/mapView[2],w,w/2]);}
  function fitMatches(){if(!$('query-map-features').childElementCount)return;const box=$('query-map-features').getBBox(),width=Math.max(['width_samples','model_frames','model_samples'].includes(lastQuery?.collection)?4:20,box.width*1.5,box.height*3);mapSet([box.x+box.width/2-width/2,box.y+box.height/2-width/4,width,width/2]);}
  $('query-map-fit').addEventListener('click',fitMatches);
  function renderMap(scene){
    $('query-map-section').hidden=!scene;$('query-map-features').replaceChildren();$('query-map-state').replaceChildren();if(!scene)return;
    const samples=scene.inspection_collection==='width_samples',models=['model_frames','model_samples'].includes(scene.inspection_collection),temporalObjects=lastQuery?.collection==='objects';
    $('query-map-play-samples').hidden=!samples;
    $('query-map-play-samples').disabled=!samples;
    $('query-map-sample-playback-note').hidden=!samples;
    $('query-map-playback-note').hidden=!temporalObjects;
    $('query-map-day').closest('label').hidden=!temporalObjects;
    for(const id of ['query-map-day','query-map-play','query-map-play-months']){$(id).disabled=!temporalObjects;if(id!=='query-map-day')$(id).hidden=!temporalObjects;}
    $('query-map-legend').textContent=samples?'Orange dashed: nominal local section spans. Individual recorded days may overlap. Use the sample day/year controls and table to inspect each record.':'Teal: editorial routes · orange dashed: dated diagnostic lines · purple: polygons · hollow: locators · amber dashed: shared gateways. Names appear on hover or focus.';
    if(models)$('query-map-legend').textContent='Blue dashed lines: fixed model section support. Blue circles: sampling sites; gray dashed circles: missing fields. Dates may overlap; use date/month filters and the table to inspect individual records. No current boundary or state containment.';
    $('query-map-hover').textContent='Hover or focus a mark for its name; select it to inspect its record.';
    $('query-map-time').textContent=scene.geometry_time?`Observation window ${scene.geometry_time.from} through ${scene.geometry_time.to}. ${scene.features.filter(f=>f.undated_context).length} undated marks shown as context. Exact recorded days; gaps are not interpolated.`:'All recorded dates shown together. Undated routes and locators do not describe a particular day.';
    if(scene.seasonal)$('query-map-time').textContent=(scene.seasonal.month?`Source phases covering month ${scene.seasonal.month}. `:`Selected source phase: ${metadata.seasonal_phases.find(p=>p.id===scene.seasonal.phase_id)?.label||scene.seasonal.phase_id}. `)+scene.seasonal.scope;
    if(scene.inspection_collection==='passage_samples'||models)$('query-map-time').textContent=scene.scope;
    if(samples)$('query-map-time').textContent=(scene.recorded_days?.length===1?'Recorded section day: '+scene.recorded_days[0]+' · '+[...new Set(scene.features.map(f=>f.source_algorithm).filter(Boolean))].join(', ')+'. ':'')+scene.scope;
    $('query-map-day').value=scene.geometry_time?.from===scene.geometry_time?.to?scene.geometry_time?.from||'':'';
    for(const feature of scene.state_features||[]){const node=document.createElementNS(ns,'path');node.setAttribute('d',feature.primitive.d);node.setAttribute('fill-rule','evenodd');$('query-map-state').append(node);}
    $('query-map-count').textContent=`${scene.mapped_objects} of ${scene.matching_objects} matching records have map marks · ${scene.features.length} marks · all matches, across every result page.`;
    if(scene.unmapped_objects||scene.omitted_features.length)$('query-map-count').textContent+=` ${scene.unmapped_objects} records without rendered geography; ${scene.omitted_features.length} unsupported features retained in downloaded JSON.`;
    if(scene.selected_state_code)$('query-map-count').textContent+=` State ${scene.selected_state_code} outlined; matching geometry is bright, other object geometry is faint context.`;
    for(const feature of scene.features){
      const p=feature.primitive,node=document.createElementNS(ns,p.kind==='point'?'circle':'path');
      if(p.kind==='point'){node.setAttribute('cx',p.x);node.setAttribute('cy',p.y);node.setAttribute('r',mapView[2]/288);}else node.setAttribute('d',p.d);
      node.setAttribute('class','query-map-mark '+p.kind+' '+feature.role+(feature.field_values_available===false?' model-fields-missing':'')+(feature.matches_selected_state===false?' context-only':'')+(feature.undated_context?' undated-context':''));node.setAttribute('fill-rule','evenodd');
      node.dataset.entity=feature.entity_id;node.dataset.role=feature.role;if(feature.phase_id)node.dataset.phase=feature.phase_id;node.setAttribute('tabindex','0');node.setAttribute('role','button');
      const name=feature.label+' · '+feature.role.replaceAll('_',' ')+(feature.observation_date?' · '+feature.observation_date:'')+(feature.sample_time_utc?' · '+feature.sample_time_utc:'')+(feature.undated_context?' · undated context':'')+(feature.matches_selected_state===true?' · matches selected state':feature.matches_selected_state===false?' · context only':'');node.setAttribute('aria-label',name);
      if(feature.phase_id)node.setAttribute('aria-label',name+' · '+feature.phase_label+' · '+feature.flow_direction);
      const title=document.createElementNS(ns,'title');title.textContent=node.getAttribute('aria-label');node.append(title);
      const announce=()=>{$('query-map-hover').textContent=node.getAttribute('aria-label')+(feature.note?' — '+feature.note:'');};node.addEventListener('pointerenter',announce);node.addEventListener('focus',announce);
      const select=()=>{for(const other of $('query-map-features').children)other.classList.toggle('selected',other.dataset.entity===feature.entity_id);const box=node.getBBox();const width=Math.max(samples?4:20,box.width*1.5,box.height*3);mapSet([box.x+box.width/2-width/2,box.y+box.height/2-width/4,width,width/2]);inspect(feature.inspection_collection||scene.inspection_collection||'objects',feature.entity_id);};
      node.addEventListener('click',()=>{if(!mapMoved)select();});node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});$('query-map-features').append(node);
    }
    if(samples&&!playing)fitMatches();
    if(reducedMotion.matches)for(const id of ['query-map-play','query-map-play-months','query-map-play-samples'])$(id).disabled=true;
  }
  $('query-map-in').addEventListener('click',()=>mapZoom(.7));$('query-map-out').addEventListener('click',()=>mapZoom(1/.7));$('query-map-world').addEventListener('click',()=>mapSet([0,0,360,180]));
  $('query-map-day').addEventListener('change',()=>{if(!lastQuery||busy||!$('query-map-day').value)return;const query=JSON.parse(JSON.stringify(lastQuery));delete query.seasonal;query.offset=0;query.geometry_time={from:$('query-map-day').value,to:$('query-map-day').value,include_undated:$('query-time-context').checked};showBuilder(query);run(query);});
  $('query-map-play').addEventListener('click',()=>{if(playing){stopPlayback();return;}if(!lastQuery||busy||reducedMotion.matches)return;playing=true;const generation=++playbackGeneration;$('query-map-play').textContent='Pause recorded days';$('query-map-play').setAttribute('aria-pressed','true');const days=metadata.geometry_observation_dates||[],selected=days.indexOf($('query-map-day').value);playDay(selected>=0?selected:0,generation);});
  $('query-map-play-months').addEventListener('click',()=>{if(playing){stopPlayback();return;}if(!lastQuery||busy||reducedMotion.matches)return;playing=true;const generation=++playbackGeneration;$('query-map-play-months').textContent='Pause source months';$('query-map-play-months').setAttribute('aria-pressed','true');playMonth(lastQuery.seasonal?.month||1,generation);});
  $('query-map-play-samples').addEventListener('click',startSectionPlayback);
  reducedMotion.addEventListener('change',()=>{stopPlayback();renderMap(lastResult?.map_scene);});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopPlayback();});
  $('query-map-export').addEventListener('click',async()=>{
    if(!lastQuery||!lastResult?.map_scene)return;
    const button=$('query-map-export');button.disabled=true;
    try{const result=await rpc('query_svg',lastQuery);if(!result.ok)throw Error(result.error);
      const url=URL.createObjectURL(new Blob([result.svg],{type:'image/svg+xml'})),a=element('a');a.href=url;a.download='osw-query-map.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }catch(error){failure('Map export failed: '+error.message);}finally{button.disabled=false;}
  });
  $('query-map').addEventListener('wheel',event=>{event.preventDefault();const r=$('query-map').getBoundingClientRect();mapZoom(event.deltaY<0?.85:1/.85,mapView[0]+(event.clientX-r.left)/r.width*mapView[2],mapView[1]+(event.clientY-r.top)/r.height*mapView[3]);},{passive:false});
  $('query-map').addEventListener('pointerdown',e=>{mapMoved=false;mapDrag={id:e.pointerId,x:e.clientX,y:e.clientY,view:[...mapView]};if(e.target===$('query-map'))$('query-map').setPointerCapture(e.pointerId);});
  $('query-map').addEventListener('pointermove',e=>{if(!mapDrag||mapDrag.id!==e.pointerId)return;const dx=e.clientX-mapDrag.x,dy=e.clientY-mapDrag.y;if(Math.abs(dx)+Math.abs(dy)>5)mapMoved=true;if(mapMoved){const r=$('query-map').getBoundingClientRect();mapSet([mapDrag.view[0]-dx/r.width*mapDrag.view[2],mapDrag.view[1]-dy/r.height*mapDrag.view[3],mapDrag.view[2],mapDrag.view[3]]);}});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])$('query-map').addEventListener(event,()=>{mapDrag=null;});
  const sortFields={objects:['label','published_length_km','capabilities.scoped_width','capabilities.reference_route','capabilities.time_samples'],widths:['name','current_id','approximate_width_km','phase_label'],reference_routes:['name','approximate_reference_path_km'],measurements:['entity_id','value','quantity'],states:['label','code'],state_links:['entity_label','state_code','kind'],sources:['label','title'],claims:['id','predicate','review_status'],relations:['id','predicate','subject_id'],entities:['label','type'],geometries:['id','entity_id'],series:['entity_id','frames'],diagnostics:['id']};
  sortFields.model_frames=['date','sample_count','available_sample_count'];
  sortFields.model_samples=['date','sample_index','distance_from_section_start_km','salinity','u_eastward','v_northward'];
  const fieldNames={label:'Name',name:'Name',published_length_km:'Published ranked length (km)',approximate_width_km:'Scoped width value (km)',approximate_reference_path_km:'Reference route estimate (km)','capabilities.scoped_width':'Width record count','capabilities.reference_route':'Route record count','capabilities.time_samples':'Time record count'};
  Object.assign(fieldNames,{date:'Source date',sample_count:'Sampling sites',available_sample_count:'Sites with all fields',sample_index:'Section sample index',distance_from_section_start_km:'Distance from section start (km)',salinity:'Salinity (dimensionless)',u_eastward:'Eastward component (m/s)',v_northward:'Northward component (m/s)'});
  sortFields.geometry_frames=['date','label','source_algorithm'];
  sortFields.seasonal_routes=['label','phase_label','flow_direction'];
  sortFields.width_samples=['label','current_id','sample_family','month','year','observation_date','source_algorithm','longitude_degrees_east','value_km'];
  sortFields.route_decisions=['label','strategy_label','construction_status','candidate_count'];
  Object.assign(fieldNames,{strategy_label:'Construction strategy',construction_status:'Route construction status',candidate_count:'Editorial route count'});
  Object.assign(fieldNames,{value_km:'Scoped sample value (km)',month:'Source month',year:'Source year',sample_family:'Sample family',longitude_degrees_east:'Section longitude'});
  function rpc(action,value){const id=++sequence;return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});worker.postMessage({id,action,value});});}
  worker.onmessage=event=>{const item=pending.get(event.data.id);if(item){pending.delete(event.data.id);item.resolve(event.data.result);}};
  worker.onerror=()=>{for(const item of pending.values())item.reject(Error('Query worker failed'));pending.clear();failure('Rust query worker failed. Reload to retry.');};
  function element(tag,text,parent){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(parent)parent.append(node);return node;}
  function link(text,href,parent){try{const url=new URL(href,location.href);if(!['http:','https:'].includes(url.protocol))return;const a=element('a',text,parent);a.href=url.href;return a;}catch(_){return;}}
  function option(parent,text,value){const node=element('option',text,parent);node.value=value;}
  function failure(message){$('query-status').className='error';$('query-status').textContent=message;}
  function rejectResult(message){failure(message);renderMap(null);window.oswCharts.render(null,inspect);$('query-detail').hidden=true;detailSequence++;$('query-share').hidden=true;$('query-export').disabled=true;$('query-previous').disabled=true;$('query-next').disabled=true;lastQuery=null;lastResult=null;window.oswLastQueryResult=null;$('query-rows').replaceChildren();$('query-page').textContent='';}
  function label(row){if(row.id?.startsWith('taxonomy-link:'))return row.child_label+' → '+row.parent_label;return row.label||row.name||row.title||row.entity_label||row.id;}
  function value(row){
    const model=window.oswModelSectionCard?.value(row);if(model!==null&&model!==undefined)return model;
    if(row.document?.schema==='osw.flow-network.v1')return `${row.document.nodes.length} nodes · ${row.document.edges.length} connections · length unresolved`;
    if(row.quantity==='section_volume_transport')return `${row.value} Sv · 2004–2006 exit mean`;
    if(row.document?.schema==='osw.loop-section-spans.v1')return row.document.frames.length+' recorded-day local section spans · '+(row.document.product_key==='noaa'?'NOAA':'DUACS');
    if(row.document&&row.current_id==='loop'&&row.document.approximate_diagnostic_path_km!==undefined)return (row.document.approximate_diagnostic_path_km===null?'Unresolved':`≈ ${row.document.approximate_diagnostic_path_km.toLocaleString()} km`)+' · unranked dated diagnostic';
    if(row.source_decision)return row.candidate_count+' editorial route'+(row.candidate_count===1?'':'s')+' · '+row.strategy_label;
    if(row.status==='proposed'&&row.proposed_data)return 'proposed working record';
    if(row.sample_family)return (row.value_km===null?'Unresolved':`≈ ${row.value_km.toLocaleString('en',{maximumFractionDigits:1})} km`)+(row.plot_reading_interval_km?` · plot reading ${row.plot_reading_interval_km.join('–')} km`:row.diagnostic_sensitivity_interval_km?` · threshold sensitivity ${row.diagnostic_sensitivity_interval_km.join('–')} km`:' · measurement uncertainty unresolved');
    if(row.approximate_width_km!==undefined)return `${row.approximate_width_km===null?(row.width_range_km?.join('–')||'unknown'):'≈ '+row.approximate_width_km} km · ${row.phase_label||row.phase_kind}`;
    if(row.approximate_reference_path_km!==undefined)return `≈ ${row.approximate_reference_path_km} km · reference route`;
    if(row.value!==undefined)return `${row.value===null?'unknown':typeof row.value==='object'?JSON.stringify(row.value):row.value} ${row.unit||''}`;
    if(row.published_length_km!==undefined&&row.published_length_km!==null)return `${row.published_length_km.toLocaleString()} km · published estimate`;
    return (row.type||row.kind||row.quantity||row.predicate||row.role||row.geometry_role||'record').replaceAll('_',' ');
  }
  function scope(row){const model=window.oswModelSectionCard?.scope(row);if(model)return model;return row.summary||row.scope||row.geographic_scope||row.note||row.limitations||(row.state_code?`${row.state_code} · ${row.state_name} · ${row.label}`:row.basin)||row.source_locator||row.source_citation||'';}
  function sampleFilters(filters){
    const represented={},extra=[],controls={current_id:'query-sample-current',sample_family:'query-sample-family',month:'query-sample-month',year:'query-sample-year',observation_date:'query-sample-day',value_km:'query-sample-availability'};
    for(const filter of filters||[]){
      const id=controls[filter.field],expected=filter.field==='value_km'?'exists':'eq';
      const typeOk=filter.field==='value_km'?typeof filter.value==='boolean':['month','year'].includes(filter.field)?typeof filter.value==='number'&&Number.isInteger(filter.value):typeof filter.value==='string';
      const value=String(filter.value),canShow=id&&typeOk&&value!==''&&filter.op===expected&&[...$(id).options].some(o=>o.value===value);
      if(canShow&&!represented[id])represented[id]=filter;else extra.push(filter);
    }
    return {represented,extra};
  }
  function decisionFilters(filters){
    const represented={},extra=[],controls={entity_id:'query-decision-current',strategy_id:'query-decision-strategy',construction_status:'query-decision-status'};
    for(const filter of filters||[]){
      const id=controls[filter.field],canShow=id&&filter.op==='eq'&&typeof filter.value==='string'&&filter.value!==''&&[...$(id).options].some(o=>o.value===filter.value);
      if(canShow&&!represented[id])represented[id]=filter;else extra.push(filter);
    }
    return {represented,extra};
  }
  function identityFilters(filters){
    let represented=null;const extra=[];
    for(const filter of filters||[]){if(!represented&&filter.field==='identity_level'&&filter.op==='eq'&&typeof filter.value==='string'&&[...$('query-identity-level').options].some(o=>o.value===filter.value&&o.value))represented=filter;else extra.push(filter);}
    return {represented,extra};
  }
  function updateFields(){
    const collection=$('query-collection').value,objects=collection==='objects',passages=collection==='passage_samples';
    for(const id of ['query-identity-level','query-taxonomy-root','query-taxonomy-relation','query-taxonomy-include']){$(id).disabled=!objects;$(id).closest('label').hidden=!objects;}
    $('query-type').disabled=!objects;$('query-state').disabled=!(objects||passages);$('query-state-mode').disabled=!(objects||passages);$('query-evidence').disabled=!objects;
    for(const option of $('query-state-mode').options)option.disabled=passages&&option.value!=='locator';
    if(passages)$('query-state-mode').value='locator';
    for(const id of ['query-time-from','query-time-to','query-time-context','query-season-month','query-season-phase'])$(id).disabled=!objects;
    for(const id of ['query-sample-current','query-sample-family','query-sample-month','query-sample-year','query-sample-day','query-sample-availability']){$(id).disabled=collection!=='width_samples';$(id).closest('label').hidden=collection!=='width_samples';}
    for(const id of ['query-decision-current','query-decision-strategy','query-decision-status']){$(id).disabled=collection!=='route_decisions';$(id).closest('label').hidden=collection!=='route_decisions';}
    $('query-sort').replaceChildren();option($('query-sort'),'Stable record ID','');
    for(const field of sortFields[collection]||[])option($('query-sort'),fieldNames[field]||field.replaceAll('_',' '),field);
    if(sortFields[collection]?.includes('label'))$('query-sort').value='label';
  }
  function builder(){
    const collection=$('query-collection').value,query={collection,limit:50,offset:0};
    if($('query-text').value.trim())query.text=$('query-text').value.trim();
    if(collection==='objects'){if($('query-type').value)query.record_type=$('query-type').value;if($('query-state-mode').value!=='recorded')query.spatial={state_code:$('query-state').value,predicate:$('query-state-mode').value};else if($('query-state').value)query.state_code=$('query-state').value;if($('query-evidence').value)query.evidence=$('query-evidence').value;}
    if(collection==='objects'){
      query.filters=lastQuery?.collection==='objects'?identityFilters(lastQuery.filters).extra:[];
      if($('query-identity-level').value)query.filters.push({field:'identity_level',op:'eq',value:$('query-identity-level').value});
      if($('query-taxonomy-root').value)query.taxonomy={root_id:$('query-taxonomy-root').value,relation:$('query-taxonomy-relation').value,include_root:$('query-taxonomy-include').checked};
    }
    if(collection==='passage_samples'){if(lastQuery?.collection===collection&&lastQuery.filters)query.filters=lastQuery.filters;if($('query-state').value)query.spatial={state_code:$('query-state').value,predicate:'locator'};}
    if($('query-sort').value)query.sort={field:$('query-sort').value,direction:$('query-direction').value};
    if(collection==='objects'&&($('query-time-from').value||$('query-time-to').value))query.geometry_time={from:$('query-time-from').value,to:$('query-time-to').value,include_undated:$('query-time-context').checked};
    if(collection==='objects'&&$('query-season-phase').value)query.seasonal={phase_id:$('query-season-phase').value};
    else if(collection==='objects'&&$('query-season-month').value)query.seasonal={month:Number($('query-season-month').value)};
    if(collection==='width_samples'){
      query.filters=lastQuery?.collection==='width_samples'?sampleFilters(lastQuery.filters).extra:[];
      for(const [id,field] of [['query-sample-current','current_id'],['query-sample-family','sample_family'],['query-sample-month','month'],['query-sample-year','year'],['query-sample-day','observation_date']])if($(id).value)query.filters.push({field,op:'eq',value:['month','year'].includes(field)?Number($(id).value):$(id).value});
      if($('query-sample-availability').value)query.filters.push({field:'value_km',op:'exists',value:$('query-sample-availability').value==='true'});
    }
    if(collection==='route_decisions'){
      query.filters=lastQuery?.collection==='route_decisions'?decisionFilters(lastQuery.filters).extra:[];
      for(const [id,field] of [['query-decision-current','entity_id'],['query-decision-strategy','strategy_id'],['query-decision-status','construction_status']])if($(id).value)query.filters.push({field,op:'eq',value:$(id).value});
    }
    if(collection==='flow_networks'&&lastQuery?.collection==='flow_networks'&&lastQuery.network_path){query.network_path=lastQuery.network_path;query.filters=lastQuery.filters||[];}
    return query;
  }
  function showBuilder(query){
    $('query-collection').value=query.collection||'objects';updateFields();$('query-text').value=query.text||'';
    $('query-type').value=query.record_type||'';$('query-state').value=query.spatial?.state_code||query.state_code||'';$('query-state-mode').value=query.spatial?.predicate||(query.collection==='passage_samples'?'locator':'recorded');$('query-evidence').value=query.evidence||'';
    $('query-identity-level').value=identityFilters(query.filters).represented?.value||'';$('query-taxonomy-root').value=query.taxonomy?.root_id||'';$('query-taxonomy-relation').value=query.taxonomy?.relation||'descendants';$('query-taxonomy-include').checked=query.taxonomy?.include_root||false;
    $('query-sort').value=query.sort?.field||'';$('query-direction').value=query.sort?.direction||'asc';
    $('query-time-from').value=query.geometry_time?.from||'';$('query-time-to').value=query.geometry_time?.to||'';$('query-time-context').checked=query.geometry_time?.include_undated||false;
    $('query-season-month').value=query.seasonal?.month||'';$('query-season-phase').value=query.seasonal?.phase_id||'';
    const sample=sampleFilters(query.filters);
    for(const id of ['query-sample-current','query-sample-family','query-sample-month','query-sample-year','query-sample-day','query-sample-availability'])$(id).value=sample.represented[id]?String(sample.represented[id].value):'';
    $('query-sample-extra').hidden=query.collection!=='width_samples'||!sample.extra.length;
    const decisions=decisionFilters(query.filters);
    for(const id of ['query-decision-current','query-decision-strategy','query-decision-status'])$(id).value=decisions.represented[id]?decisions.represented[id].value:'';
    $('query-decision-extra').hidden=query.collection!=='route_decisions'||!decisions.extra.length;
  }
  function setBusy(value){busy=value;$('query-run').disabled=value;$('query-run-json').disabled=value;for(const b of document.querySelectorAll('[data-preset]'))b.disabled=value||!metadata.collections.some(c=>c.name===presets[b.dataset.preset]?.collection);}
  async function run(query,fromPlayback=false){
    if(!fromPlayback)stopPlayback();
    if(busy)return;setBusy(true);$('query-status').className='';$('query-status').textContent='Running query…';
    try{
      const result=await rpc('query',query);if(!result.ok)throw Error(result.error);
      lastQuery=JSON.parse(JSON.stringify(query));lastResult=result;window.oswLastQueryResult=result;
      showBuilder(query);
      $('query-json').value=JSON.stringify(query,null,2);
      const url=new URL(location.href);url.searchParams.delete('inspect');url.searchParams.set('q',JSON.stringify(query));history.replaceState(null,'',url);
      $('query-share').hidden=false;$('query-share').href=url.href;$('query-export').disabled=false;
      $('query-status').textContent=`${result.total.toLocaleString()} matching ${names[result.collection]?.toLowerCase()||result.collection}. Query executed in Rust / WebAssembly.`;
      if(result.taxonomy_scope)element('p',result.taxonomy_scope,$('query-status'));
      if(result.network_paths){const details=element('details',undefined,$('query-status'));element('summary',`${result.network_paths.paths.length} conceptual connections · no metric length`,details);element('p',result.network_paths.scope,details);const list=element('ol',undefined,details);for(const path of result.network_paths.paths)element('li',path.map(id=>result.network_paths.node_labels[id]||id).join(' → '),list);if(result.network_paths.truncated||result.network_paths.hop_limit_reached)element('p','Search limits were reached; these results may be incomplete.',details);}
      $('query-caption').textContent=names[result.collection]+' · '+result.total.toLocaleString()+' matches';
      renderMap(result.map_scene);
      window.oswCharts.render(result.chart_scene,inspect);
      $('query-rows').replaceChildren();
      for(const row of result.rows){
        const tr=element('tr',undefined,$('query-rows')),name=element('td',undefined,tr),button=element('button',label(row),name);button.type='button';button.addEventListener('click',()=>inspect(result.collection,row.id));
        element('small',row.id,name);element('td',value(row),tr);const evidence=element('td',undefined,tr);element('span',scope(row),evidence).className='scope';
        if(row.width_metric)element('small',row.width_metric.replaceAll('_',' '),evidence);
        if(row.comparison_group)element('small',row.comparison_group.replaceAll('_',' '),evidence);
        if(row.state_codes?.length)element('small','State links: '+row.state_codes.join(', '),evidence);
        if(row.spatial_matches?.length)element('small','Computed: '+row.spatial_matches.map(r=>r.role.replaceAll('_',' ')+(r.boundary_touch_only?' (boundary contact)':'')+(r.semantic_exclusion?' (source-excluded)':'')).join('; '),evidence);
      }
      const start=result.total?Math.min(result.offset+1,result.total):0,end=Math.min(result.offset+result.rows.length,result.total);
      $('query-page').textContent=`${start}–${end} of ${result.total.toLocaleString()}`;$('query-previous').disabled=result.offset===0;$('query-next').disabled=end>=result.total;
      $('query-detail').hidden=true;detailSequence++;
    }catch(error){rejectResult(error.message);}
    finally{setBusy(false);}
  }
  function drawFlowNetwork(parent,row){
    const doc=row.document,section=element('section',undefined,parent);section.className='flow-network';
    element('h3','Passage connections',section);element('p',doc.scope,section);
    element('p','Schematic positions and arrow lengths have no geographic scale. Arrows describe selected pathways across different layers; reversals and unrepresented passages remain possible.',section);
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 960 440');svg.setAttribute('role','group');svg.setAttribute('aria-label','Indonesian Throughflow conceptual passage network');svg.style.width='100%';svg.style.maxHeight='500px';section.append(svg);
    const lookup=new Map(doc.nodes.map(n=>[n.id,n]));const defs=document.createElementNS(ns,'defs'),arrow=document.createElementNS(ns,'marker'),head=document.createElementNS(ns,'path');const arrowId='network-arrow-'+detailSequence;arrow.setAttribute('id',arrowId);arrow.setAttribute('viewBox','0 0 10 10');arrow.setAttribute('refX','9');arrow.setAttribute('refY','5');arrow.setAttribute('markerWidth','5');arrow.setAttribute('markerHeight','5');arrow.setAttribute('orient','auto');head.setAttribute('d','M 0 0 L 10 5 L 0 10 z');head.setAttribute('fill','#c6d5d5');arrow.append(head);defs.append(arrow);svg.append(defs);
    for(const edge of doc.edges){const a=lookup.get(edge.from_id).schematic_xy,b=lookup.get(edge.to_id).schematic_xy,path=document.createElementNS(ns,'path');path.setAttribute('d',`M ${a[0]} ${a[1]} H ${(a[0]+b[0])/2} V ${b[1]} H ${b[0]}`);path.setAttribute('fill','none');path.setAttribute('stroke',edge.connection_kind.includes('eastern')?'#bda4ef':'#7cceca');path.setAttribute('stroke-width','4');path.setAttribute('marker-end',`url(#${arrowId})`);const title=document.createElementNS(ns,'title');title.textContent=lookup.get(edge.from_id).label+' → '+lookup.get(edge.to_id).label;path.append(title);svg.append(path);}
    const selected=element('p','Hover or focus a node for its name; select it to inspect the source record.',section);selected.setAttribute('aria-live','polite');
    for(const node of doc.nodes){const g=document.createElementNS(ns,'g');g.setAttribute('role','button');g.setAttribute('tabindex','0');g.setAttribute('aria-label',node.label+' · '+node.node_kind.replaceAll('_',' ')+' · inspect');g.style.cursor='pointer';const marker=document.createElementNS(ns,node.node_kind.includes('gateway')?'rect':'circle');const [x,y]=node.schematic_xy;if(marker.tagName==='rect'){marker.setAttribute('x',x-12);marker.setAttribute('y',y-12);marker.setAttribute('width','24');marker.setAttribute('height','24');}else{marker.setAttribute('cx',x);marker.setAttribute('cy',y);marker.setAttribute('r','12');}marker.setAttribute('fill','#123f4c');marker.setAttribute('stroke','#f4d88a');marker.setAttribute('stroke-width','3');g.append(marker);const title=document.createElementNS(ns,'title');title.textContent=node.label;g.append(title);g.addEventListener('pointerenter',()=>selected.textContent=node.label+' · '+node.node_kind.replaceAll('_',' '));g.addEventListener('focus',()=>selected.textContent=node.label+' · '+node.node_kind.replaceAll('_',' '));g.addEventListener('click',()=>inspect('flow_network_nodes',node.id));g.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();inspect('flow_network_nodes',node.id);}});svg.append(g);}
    element('p','Squares: passage gateways. Circles: basins. Violet: eastern contribution; teal: western/interior/exit connections. Names appear on hover or focus. The node records and source provide equivalent text access.',section);
    const paths={collection:'flow_networks',filters:[{field:'id',op:'eq',value:row.id}],network_path:{network_id:row.id,from_id:'flow-node:itf:pacific',to_id:'flow-node:itf:indian',max_hops:8}};
    link('Query Pacific-to-Indian connections','query.html?q='+encodeURIComponent(JSON.stringify(paths)),section);
    const nodes=element('details',undefined,section);element('summary','All twelve named nodes',nodes);const list=element('ul',undefined,nodes);for(const node of doc.nodes){const item=element('li',undefined,list),button=element('button',node.label,item);button.type='button';button.addEventListener('click',()=>inspect('flow_network_nodes',node.id));}
    link('Query measured exit passages','query.html?q='+encodeURIComponent(JSON.stringify({collection:'passage_samples',filters:[{field:'network_id',op:'eq',value:row.id}]})),section);
  }
  async function openIdentityCard(id){
    if(busy)return;
    if(lastQuery?.collection!=='objects'||!lastResult?.rows.some(row=>row.id===id)){
      const query={collection:'objects',filters:[{field:'id',op:'eq',value:id}],limit:1};showBuilder(query);await run(query);
      if(lastResult?.collection!=='objects'||!lastResult.rows.some(row=>row.id===id))return;
    }
    await inspect('objects',id);
  }
  function describe(parent,row){
    if(window.oswModelSectionCard?.render(parent,row,inspect))return;
    if(row.id?.startsWith('taxonomy-link:')){
      element('h3',label(row),parent);element('p',row.scope,parent);
      element('p','This assignment is recorded in the editorial ledger. The naming reference does not independently establish the parent relationship.',parent);
      const links=element('div',undefined,parent);links.className='record-links';
      for(const [id,text] of [[row.child_id,row.child_label],[row.parent_id,row.parent_label]]){const button=element('button',text,links);button.type='button';button.addEventListener('click',()=>openIdentityCard(id));}
      link('Naming reference (context only)',row.naming_source_url,links);return;
    }

    if(row.document?.schema==='osw.flow-network.v1')drawFlowNetwork(parent,row);
    if(row.quantity==='section_volume_transport'){element('p',`${row.value} Sv (negative toward the Indian Ocean), mean for 2004–2006; depth ${row.depth_range_m.join('–')} m.`,parent);element('p',`Calculation-choice interval: ${row.calculation_choice_interval_Sv.join(' to ')} Sv, from gap/extrapolation choices; not seasonal extrema or a confidence interval. Integration width: ${row.transport_integration_width_km} km; this is not a physical current width.`,parent);}
    if(row.moorings){const details=element('details',undefined,parent);element('summary',`Published mooring sites (${row.moorings.length})`,details);for(const site of row.moorings)element('p',`${site.label}: ${site.coordinates_lon_lat.join(', ')} (lon, lat); ${site.deployment_start} to ${site.deployment_end}; first-deployment location, not a current edge.`,details);}
    if(row.network_id&&row.document?.schema!=='osw.flow-network.v1')link('Back to passage network','query.html?q='+encodeURIComponent(JSON.stringify({collection:'flow_networks',filters:[{field:'id',op:'eq',value:row.network_id}]})),parent);
    element('h3',label(row),parent);element('p',value(row),parent);
    if(row.source_decision){
      element('p','Editorial worklist for names without a published ranked length. Existing candidates remain pending scientific review; no new length is assigned by this decision.',parent);
      element('h4','Next evidence needed',parent);element('p',row.next_action,parent);
      element('p','Construction status: '+row.construction_status.replaceAll('_',' ')+'.',parent);
      element('p','Strategy: '+row.strategy_label+'. '+row.source_decision.strategy_next_action,parent);
      for(const review of row.scope_reviews){
        const details=element('details',undefined,parent);element('summary',review.note.label,details);
        element('p',review.note.summary,details);element('p',review.document.source_access||'See the audit for inspected access and source support.',details);
        const reviewLinks=element('div',undefined,details);reviewLinks.className='record-links';
        link('Evidence source',review.note.source_url,reviewLinks);link('Source scope audit','../'+review.note.audit_file,reviewLinks);
        if(/^almanac\/[a-z0-9-]+\.html$/.test(review.document.diagnostic_page||''))link('View mapped experiment','../'+review.document.diagnostic_page,reviewLinks);
        const raw=element('details',undefined,details);element('summary','Complete scope audit',raw);element('pre',JSON.stringify(review.document,null,2),raw);
      }
    }
    const dl=element('dl',undefined,parent);
    if(row.document?.schema==='osw.loop-section-spans.v1')element('p',row.document.scope_note+' No annual range or representative whole-current width admitted.',parent);
    if(row.document&&row.current_id==='loop'&&row.document.approximate_diagnostic_path_km!==undefined){
      element('p','Dated diagnostic path: approximately '+(row.document.approximate_diagnostic_path_km?.toLocaleString()||'unresolved')+' km. Unranked; no whole-current dimension or annual range admitted.',parent);
      element('p',row.document.interpretation,parent);
      if(row.document.comparison)element('p','DUACS contour versus NOAA integration: '+row.document.comparison.signed_difference_duacs_minus_noaa_km+' km before display rounding. '+row.document.comparison.scope,parent);
    }
    if(row.sample_family){
      element('p','Scoped source sample. Plot-reading intervals are extraction allowances, not confidence intervals or measurement uncertainty. These samples are not whole-current widths or annual extrema.',parent);
      element('p','Parent diagnostic status: '+row.source_context.status.replaceAll('_',' ')+'.',parent);
      for(const [key,title] of [['sample_family','Method family'],['metric','Width metric'],['month','Source month'],['year','Source year'],['phase_label','Source phase'],['longitude_degrees_east','Section longitude (degrees east)'],['latitude_degrees_north','Section latitude (degrees north)'],['measurement_uncertainty_interval_km','Measurement uncertainty interval']]){element('dt',title,dl);element('dd',row[key]===null?'unresolved':key==='sample_family'?widthFamilies[row[key]]:String(row[key]).replaceAll('_',' '),dl);}
      for(const key of ['layer','source_locator','source_quality_note','averaging_order'])if(row.source_context[key])element('p',row.source_context[key],parent);
      if(row.source_context.velocity_threshold_m_s!==undefined)element('p','Velocity threshold: '+row.source_context.velocity_threshold_m_s+' m/s.',parent);
      if(row.source_context.source_period_labels)element('p','Historical period labels differ in the source: '+Object.values(row.source_context.source_period_labels).join('; ')+'. Combined averaging period unresolved.',parent);
      if(row.source_context.study_period_years)element('p','Study-period years: '+row.source_context.study_period_years.join('–')+'.',parent);
      if(row.observation_date){
        element('p','Observation day: '+row.observation_date+' · Source processing: '+row.source_algorithm+'. Individual-day section diagnostic; not a monthly mean or the width of a mapped streamline.',parent);
        const brackets=row.sampling_bracket_interval_km?[Math.floor(row.sampling_bracket_interval_km[0]/10)*10,Math.ceil(row.sampling_bracket_interval_km[1]/10)*10].join('–'):'unresolved';
        element('p','Finite 40–60% boundary-threshold sensitivity: '+(row.diagnostic_sensitivity_interval_km?.join('–')||'unresolved')+' km. Grid-bracket separation (display rounded outward to 10 km): '+brackets+' km. Original brackets remain in the source record. These ranges are neither confidence intervals nor measurement uncertainty.',parent);
        element('p','Resolution review flag: '+(row.resolution_review_required===null?'unresolved':row.resolution_review_required?'yes':'no')+'. Scientific boundary validation remains pending.',parent);
      }
      if(row.source_phase?.calendar_months===null)element('p','Calendar months for this source season are unresolved.',parent);
    }
    if(row.timeline_file){element('p',row.sampling_note,parent);for(const [key,title] of [['date','Observation day'],['method','Diagnostic method'],['stop_reason','Stop reason'],['reaches_downstream_gate','Reaches downstream gate'],['diagnostic_length_km','Diagnostic trace distance (km; not current length)'],['width_km','Current width (km)'],['positional_uncertainty_km','Positional uncertainty (km)'],['source_algorithm','Source processing algorithm'],['source_product_status','Source product status']]){if(row[key]!==undefined){element('dt',title,dl);element('dd',row[key]===null?'unresolved':String(row[key]),dl);}}element('p',row.attribution,parent);}
    for(const [key,title] of [['id','Record ID'],['scope','Scope'],['geographic_scope','Region'],['layer','Layer'],['time_convention','Time'],['boundary_rule','Boundary definition'],['range_interpretation','Range meaning'],['source_locator','Source location'],['source_quality_note','Source quality'],['kind','Relation kind'],['observation_date','Observation date'],['status','Status'],['width_rank_eligible','Width ranking eligible'],['rank_eligible','Published ranking eligible']]){
      if(row[key]!==undefined){element('dt',title,dl);element('dd',row[key]===null?'unresolved':key==='status'?String(row[key]).replaceAll('_',' '):String(row[key]),dl);}
    }
    const links=element('div',undefined,parent);links.className='record-links';
    if(/^almanac\/[a-z0-9-]+\.html$/.test(row.diagnostic_page||''))link('View mapped experiment','../'+row.diagnostic_page+(row.observation_date?'?date='+encodeURIComponent(row.observation_date):''),links);
    if(['gulf_stream_dated_half_peak_section','loop_dated_half_peak_section'].includes(row.sample_family)&&row.status==='paired_boundaries'&&row.value_km!==null)link('Map this local section span','query.html?q='+encodeURIComponent(JSON.stringify({collection:'width_samples',filters:[{field:'id',op:'eq',value:row.id}],limit:50}))+'#query-map-section',links);
    if(row.width_sample_ids?.length)link('Query scoped width samples','query.html?q='+encodeURIComponent(JSON.stringify({collection:'width_samples',filters:[{field:'current_id',op:'eq',value:row.id.replace(/^current:/,'')}],sort:{field:'label'},limit:100})),links);
    if(row.route_decision_ids?.length)link('Query remaining length decision','query.html?q='+encodeURIComponent(JSON.stringify({collection:'route_decisions',filters:[{field:'entity_id',op:'eq',value:row.id}],limit:50})),links);
    if(row.diagnostic_id){const source=element('button','Inspect parent diagnostic',links);source.type='button';source.addEventListener('click',()=>inspect('diagnostics',row.diagnostic_id));}
    if(row.source_context?.source_inventory_file)link('Source inventory and receipts','../'+row.source_context.source_inventory_file,links);
    if(row.source_context?.protocol_file)link('Sample measurement protocol','../'+row.source_context.protocol_file,links);
    if(row.source_catalog_file)link('Audited route catalog and receipt','../'+row.source_catalog_file,links);
    if(row.target){const source=element('button','Inspect source reference',links);source.type='button';source.addEventListener('click',()=>inspect(row.target.collection,row.target.id));}
    if(row.timeline_file&&row.entity_id&&row.date)link('Map this observation day','query.html?q='+encodeURIComponent(JSON.stringify({collection:'objects',filters:[{field:'id',op:'eq',value:row.entity_id}],geometry_time:{from:row.date,to:row.date},limit:50})),links);
    if(row.seasonal_inventory_file)link('Map this source phase','query.html?q='+encodeURIComponent(JSON.stringify({collection:'objects',seasonal:{phase_id:row.id},limit:50})),links);
    if(row.comparability)element('p',row.comparability.reason,parent);
    if(row.seasonal_inventory_file)element('p','Source month convention: '+(row.calendar_months?.join(', ')||'unresolved')+'. Flow: '+row.flow_direction+'.',parent);
    const entity=row.id.startsWith('current:')||row.id.startsWith('eddy:')||row.id.startsWith('operational-eddy:')?row.id:row.entity_id||row.subject_id||(row.current_id?'current:'+row.current_id:null);
    if(entity && (/^(current:|eddy:|operational-eddy:)/.test(entity)||row.type==='operational_eddy_detection')){link('Open atlas card',`reference-routes.html?atlas-layout=map&atlas-feature=${encodeURIComponent(entity)}#route-atlas`,links);link('Object record','object.html?id='+encodeURIComponent(entity),links);}
    if(row.source_url)link('Published source',row.source_url,links);else if(row.url)link('Source',row.url,links);
    if(row.current_id&&row.phase_kind)link('Inspect width',`seasons.html?current=${encodeURIComponent(row.current_id)}&phase=${encodeURIComponent(row.id)}`,links);
    if(row.type==='named_current'&&row.state_codes?.length)element('p','Recorded state links: '+row.state_codes.join(', ')+'. Relation kinds are available in the state-links collection.',parent);
  }
  async function inspect(collection,id){
    const generation=++detailSequence,panel=$('query-detail');panel.hidden=false;panel.replaceChildren();element('p','Loading record and linked evidence…',panel);
    try{
      const result=await rpc('record',{collection,id});if(!result.ok)throw Error(result.error);if(generation!==detailSequence)return;
      panel.replaceChildren();const close=element('button','Close record',panel);close.type='button';close.addEventListener('click',()=>{panel.hidden=true;detailSequence++;});describe(panel,result.record);
      const record=result.record;
      if(collection==='width_samples')window.oswCharts.selectSample(id);
      if(result.taxonomy_context){
        const context=result.taxonomy_context,details=element('details',undefined,panel);details.open=true;
        element('summary',`Declared identity memberships (${context.parents.length} parents, ${context.children.length} children)`,details);
        element('p',context.scope,details);
        const definition=metadata.taxonomy?.identity_levels[result.record.identity_level];if(definition)element('p',result.record.identity_level.replaceAll('_',' ')+': '+definition,details);
        if(!context.parents.length&&!context.children.length)element('p','No parent or child assignment is recorded. This does not establish isolation or a complete physical taxonomy.',details);
        for(const [direction,edges] of [['parents',context.parents],['children',context.children]]){
          if(edges.length)element('h4',direction==='parents'?'Parent families or systems':'Declared members or components',details);
          for(const edge of edges){
          const id=direction==='parents'?edge.parent_id:edge.child_id,text=direction==='parents'?edge.parent_label:edge.child_label,item=element('p',undefined,details);
          const button=element('button',text,item);button.type='button';button.addEventListener('click',()=>openIdentityCard(id));
          element('span',' · '+edge.predicate.replaceAll('_',' ')+' · editorial assignment',item);
        }
        }
        const actions=element('div',undefined,details);actions.className='record-links';
        for(const [relation,text] of [['descendants','Query all declared descendants'],['ancestors','Query all declared ancestors']]){const button=element('button',text,actions);button.type='button';button.addEventListener('click',async()=>{const q={collection:'objects',taxonomy:{root_id:result.record.id,relation,include_root:false},sort:{field:'label'},limit:100};showBuilder(q);await run(q);if(lastResult)fitMatches();});}
      }

      const spatial=lastResult?.map_scene?.spatial_relations?.[id];
      if(spatial?.length){const details=element('details',undefined,panel);details.open=true;element('summary','Computed state relations ('+spatial.length+')',details);element('p',lastResult.spatial_scope,details);element('pre',JSON.stringify(spatial,null,2),details);}
      const groups=[['width_ids','widths','Scoped width records'],['measurement_ids','measurements','Published measurements'],['route_ids','reference_routes','Editorial routes'],['source_ids','sources','Linked sources'],['frame_ids','geometry_frames','Dated diagnostic frames']];
      groups.push(['seasonal_route_ids','seasonal_routes','Source-defined seasonal routes']);
      groups.push(['route_decision_ids','route_decisions','Length construction decision']);
      groups.push(['diagnostic_ids','diagnostics','Unranked method diagnostics']);
      groups.push(['flow_network_ids','flow_networks','Source-described flow networks']);
      groups.push(['passage_sample_ids','passage_samples','Observed passage transport']);
      groups.push(['model_frame_ids','model_frames','Hourly model sections (context only)']);
      if(record.source_id)groups.push(['single_source','sources','Source']);
      for(const [key,target,title] of groups){
        const ids=key==='single_source'?[record.source_id]:record[key];if(!ids?.length)continue;
        const details=element('details',undefined,panel);element('summary',`${title} (${ids.length})`,details);if(key==='width_ids'||key==='measurement_ids'||key==='route_decision_ids'||(key==='seasonal_route_ids'&&lastQuery?.seasonal))details.open=true;
        for(const id of ids){const item=await rpc('record',{collection:target,id});if(generation!==detailSequence)return;if(!item.ok)throw Error(item.error);const article=element('article',undefined,details);describe(article,item.record);}
      }
      const raw=element('details',undefined,panel);element('summary','Complete record JSON',raw);element('pre',JSON.stringify(record,null,2),raw);
      window.oswWorkspace.editor(panel,collection,record);
      if(collection===lastQuery?.collection&&lastResult?.rows.some(r=>r.id===id)){const url=new URL($('query-share').href);url.searchParams.set('inspect',id);$('query-share').href=url.href;history.replaceState(null,'',url);}
      panel.scrollIntoView({block:'start'});panel.focus({preventScroll:true});
    }catch(error){if(generation===detailSequence){panel.replaceChildren();element('p',error.message,panel);}}
  }
  const presets={'norkyst-frames':{collection:'model_frames',sort:{field:'date'},limit:50},'norkyst-january':{collection:'model_samples',filters:[{field:'month',op:'eq',value:1}],sort:{field:'sample_index'},limit:100},'countercurrent-family':{collection:'objects',taxonomy:{root_id:'current:equatorial-countercurrent',relation:'descendants',include_root:false},sort:{field:'label'},limit:100},width:{collection:'objects',record_type:'named_current',evidence:'scoped_width',sort:{field:'label',direction:'asc'},limit:50},
    'itf-moorings-sund':{collection:'passage_samples',spatial:{state_code:'SUND',predicate:'locator'},limit:50},
    'loop-section-samples':{collection:'width_samples',filters:[{field:'sample_family',op:'eq',value:'loop_dated_half_peak_section'}],sort:{field:'observation_date'},limit:50},
    'length-decisions':{collection:'route_decisions',sort:{field:'strategy_label'},limit:100},
    'unbuilt-decisions':{collection:'route_decisions',filters:[{field:'construction_status',op:'eq',value:'reference_path_not_constructed'}],sort:{field:'strategy_label'},limit:100},
    lengths:{collection:'objects',record_type:'named_current',evidence:'reported_length',sort:{field:'published_length_km',direction:'desc'},limit:50},
    'missing-routes':{collection:'objects',record_type:'named_current',filters:[{field:'capabilities.reference_route',op:'eq',value:0}],sort:{field:'label',direction:'asc'},limit:50},
    'eddy-geometry':{collection:'objects',record_type:'named_eddy',evidence:'geometry',sort:{field:'label',direction:'asc'},limit:50},
    kuro:{collection:'objects',record_type:'named_current',state_code:'KURO',sort:{field:'label',direction:'asc'},limit:50},
    'spatial-nadr':{collection:'objects',spatial:{state_code:'NADR',predicate:'intersects'},sort:{field:'label',direction:'asc'},limit:50},
    'gulf-dated':{collection:'objects',filters:[{field:'id',op:'eq',value:'current:gulf-stream-system'}],geometry_time:{from:'2025-01-15',to:'2025-01-15'},limit:50},
    'seasonal-january':{collection:'objects',seasonal:{month:1},limit:50},
    'leeuwin-samples':{collection:'width_samples',filters:[{field:'current_id',op:'eq',value:'leeuwin'}],sort:{field:'month'},limit:50},
    'kuroshio-samples':{collection:'width_samples',filters:[{field:'current_id',op:'eq',value:'kuroshio'}],sort:{field:'label'},limit:100},
    'necc-samples':{collection:'width_samples',filters:[{field:'current_id',op:'eq',value:'pacific-north-equatorial-countercurrent'}],sort:{field:'month'},limit:50},
    'gulf-width-samples':{collection:'width_samples',filters:[{field:'sample_family',op:'eq',value:'gulf_stream_dated_half_peak_section'}],sort:{field:'observation_date'},limit:50}};
  $('query-form').addEventListener('submit',event=>{event.preventDefault();run(builder());});$('query-collection').addEventListener('change',updateFields);
  for(const [chosen,other] of [['query-season-month','query-season-phase'],['query-season-phase','query-season-month']])$(chosen).addEventListener('change',()=>{if(!$(chosen).value)return;$(other).value='';$('query-time-from').value='';$('query-time-to').value='';$('query-time-context').checked=false;});
  for(const id of ['query-time-from','query-time-to'])$(id).addEventListener('change',()=>{if($(id).value){$('query-season-month').value='';$('query-season-phase').value='';}});
  $('query-run-json').addEventListener('click',()=>{try{const query=JSON.parse($('query-json').value);showBuilder(query);run(query);}catch(error){rejectResult('Invalid JSON query: '+error.message);}});
  for(const button of document.querySelectorAll('[data-preset]'))button.addEventListener('click',async()=>{const query=presets[button.dataset.preset];showBuilder(query);await run(query);if(['gulf-dated','itf-moorings-sund','norkyst-frames','norkyst-january'].includes(button.dataset.preset)&&lastResult)fitMatches();});
  $('query-previous').addEventListener('click',()=>run({...lastQuery,offset:Math.max(0,(lastQuery.offset||0)-(lastQuery.limit||100))}));
  $('query-next').addEventListener('click',()=>run({...lastQuery,offset:(lastQuery.offset||0)+(lastQuery.limit||100)}));
  $('query-export').addEventListener('click',()=>{if(!lastResult)return;const blob=new Blob([JSON.stringify({query:lastQuery,bundle_sha256:metadata.bundle_sha256,result:lastResult},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob);const a=element('a');a.href=url;a.download='osw-query-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  (async()=>{
    try{
      metadata=await rpc('load');if(!metadata.ok)throw Error(metadata.error);
      for(const day of metadata.geometry_observation_dates||[])option($('query-map-day'),day,day);
      for(let month=1;month<=12;month++)option($('query-season-month'),new Intl.DateTimeFormat('en',{month:'long',timeZone:'UTC'}).format(new Date(Date.UTC(2000,month-1,1))),String(month));
      for(const phase of metadata.seasonal_phases||[])option($('query-season-phase'),phase.label+(phase.calendar_months?'':' (months unresolved)'),phase.id);
      for(const current of metadata.width_sample_currents||[])option($('query-sample-current'),current.label,current.current_id);
      for(const year of metadata.width_sample_years||[])option($('query-sample-year'),String(year),String(year));
      for(const day of metadata.width_sample_days||[])option($('query-sample-day'),day,day);
      for(const current of metadata.route_decision_currents||[])option($('query-decision-current'),current.label,current.entity_id);
      for(const [id,label] of Object.entries(metadata.route_decision_strategies||{}))option($('query-decision-strategy'),label,id);
      for(const [value,label] of Object.entries(widthFamilies))option($('query-sample-family'),label,value);
      for(let month=1;month<=12;month++)option($('query-sample-month'),new Intl.DateTimeFormat('en',{month:'long',timeZone:'UTC'}).format(new Date(Date.UTC(2000,month-1,1))),String(month));
      const counts=Object.fromEntries(metadata.collections.map(c=>[c.name,c.count]));
      $('query-inventory').textContent=`${metadata.object_type_counts.named_current} currents · ${metadata.object_type_counts.named_eddy + metadata.object_type_counts.operational_eddy_detection} eddy records · ${counts.states} OSW states · ${counts.claims.toLocaleString()} claims · ${counts.widths} scoped width records · ${counts.width_samples} scoped width samples`;
      const collectionOrder=[...order,...metadata.collections.map(row=>row.name).filter(name=>!order.includes(name))];
      for(const name of collectionOrder)if(counts[name]!==undefined)option($('query-collection'),`${names[name]||name.replaceAll('_',' ')} (${counts[name].toLocaleString()})`,name);
      await window.oswWorkspace.initialize(metadata,rpc,(workspace,query)=>{
        const option=$('query-collection').querySelector('option[value="working_records"]');if(option)option.textContent=names.working_records+' ('+workspace.record_count+')';
        if(query){const q={collection:'working_records',limit:50};showBuilder(q);run(q);}
      });
      const states=await rpc('query',{collection:'states',sort:{field:'label',direction:'asc'},limit:100});if(!states.ok)throw Error(states.error);
      for(const state of states.rows)option($('query-state'),state.code+' · '+state.label,state.code);
      for(const [key,definition] of Object.entries(metadata.taxonomy?.identity_levels||{})){option($('query-identity-level'),key.replaceAll('_',' '),key);$('query-identity-level').lastElementChild.title=definition;}
      for(const node of metadata.taxonomy?.nodes||[])option($('query-taxonomy-root'),node.label+' · '+node.identity_level.replaceAll('_',' '),node.id);
      $('query-controls').disabled=false;$('query-run-json').disabled=false;for(const button of document.querySelectorAll('[data-preset]'))button.disabled=!metadata.collections.some(c=>c.name===presets[button.dataset.preset]?.collection);
      $('query-engine-info').textContent=`${metadata.engine} · ${metadata.collections.length} collections · browser worker · snapshot ${metadata.bundle_sha256.slice(0,12)}.`;
      $('query-manifest').textContent=JSON.stringify(metadata.manifest,null,2);
      let query={collection:'objects',record_type:'named_current',sort:{field:'label',direction:'asc'},limit:50,offset:0};
      const shared=new URL(location.href).searchParams.get('q');if(shared){if(shared.length>20000)throw Error('Shared query is too large');query=JSON.parse(shared);}
      const selected=new URL(location.href).searchParams.get('inspect');
      showBuilder(query);await run(query);if((query.seasonal?.phase_id||['model_frames','model_samples'].includes(query.collection))&&lastResult)fitMatches();
      if(selected&&lastResult){if(lastResult.rows.some(r=>r.id===selected)){fitMatches();await inspect(lastResult.collection,selected);}else failure('Selected record is not in this result page. Choose a record from the results.');}
    }catch(error){failure('Query store unavailable: '+error.message);$('query-inventory').textContent='The query store could not be loaded.';}
  })();
})();
