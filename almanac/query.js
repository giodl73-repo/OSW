"use strict";
(() => {
  const $=id=>document.getElementById(id),worker=new Worker('query-worker.js?v=3');
  const pending=new Map();let sequence=0,metadata,lastQuery=null,lastResult=null,busy=false,detailSequence=0;
  let playbackTimer=null,playing=false,playbackGeneration=0;
  function stopPlayback(){playing=false;playbackGeneration++;clearTimeout(playbackTimer);$('query-map-play').textContent='Play recorded days';$('query-map-play').setAttribute('aria-pressed','false');}
  async function playDay(index,generation){
    const days=metadata.geometry_observation_dates||[];
    if(!playing||generation!==playbackGeneration||index>=days.length){if(generation===playbackGeneration)stopPlayback();return;}
    if(busy){playbackTimer=setTimeout(()=>playDay(index,generation),100);return;}
    const query=JSON.parse(JSON.stringify(lastQuery));query.offset=0;query.geometry_time={from:days[index],to:days[index],include_undated:query.geometry_time?.include_undated||false};
    await run(query,true);
    if(!lastResult){stopPlayback();return;}
    if(playing&&generation===playbackGeneration)playbackTimer=setTimeout(()=>playDay(index+1,generation),1000);
  }
  const names={objects:'Currents and eddies',widths:'Scoped width records',reference_routes:'Editorial reference routes',measurements:'Published measurement records',states:'OSW states',state_links:'Recorded state links',sources:'Sources',claims:'Claims',relations:'Relations',entities:'All ledger entities',geometries:'Stored geometries',series:'Time-series indexes',diagnostics:'Diagnostic documents',working_records:'Proposed working records'};
  names.geometry_frames='Dated diagnostic geometry frames';
  const order=Object.keys(names);
  const ns='http://www.w3.org/2000/svg';let mapView=[0,0,360,180],mapDrag=null,mapMoved=false;
  function mapSet(view){const w=Math.min(360,Math.max(4,view[2]));mapView=[Math.max(0,Math.min(360-w,view[0])),Math.max(0,Math.min(180-w/2,view[1])),w,w/2];$('query-map').setAttribute('viewBox',mapView.join(' '));$('query-map-ground').setAttribute('href',w<100?'../figures/ocean-motion-closeup-ground.svg':'../figures/ocean-motion-dashboard-ground.svg');}
  function mapZoom(factor,x=mapView[0]+mapView[2]/2,y=mapView[1]+mapView[3]/2){const w=Math.min(360,Math.max(4,mapView[2]*factor));mapSet([x-(x-mapView[0])*w/mapView[2],y-(y-mapView[1])*w/mapView[2],w,w/2]);}
  function fitMatches(){if(!$('query-map-features').childElementCount)return;const box=$('query-map-features').getBBox(),width=Math.max(20,box.width*1.5,box.height*3);mapSet([box.x+box.width/2-width/2,box.y+box.height/2-width/4,width,width/2]);}
  $('query-map-fit').addEventListener('click',fitMatches);
  function renderMap(scene){
    $('query-map-section').hidden=!scene;$('query-map-features').replaceChildren();$('query-map-state').replaceChildren();if(!scene)return;
    $('query-map-hover').textContent='Hover or focus a mark for its name; select it to inspect its record.';
    $('query-map-time').textContent=scene.geometry_time?`Observation window ${scene.geometry_time.from} through ${scene.geometry_time.to}. ${scene.features.filter(f=>f.undated_context).length} undated marks shown as context. Exact recorded days; gaps are not interpolated.`:'All recorded dates shown together. Undated routes and locators do not describe a particular day.';
    $('query-map-day').value=scene.geometry_time?.from===scene.geometry_time?.to?scene.geometry_time?.from||'':'';
    for(const feature of scene.state_features||[]){const node=document.createElementNS(ns,'path');node.setAttribute('d',feature.primitive.d);node.setAttribute('fill-rule','evenodd');$('query-map-state').append(node);}
    $('query-map-count').textContent=`${scene.mapped_objects} of ${scene.matching_objects} matching records have map marks · ${scene.features.length} marks · all matches, across every result page.`;
    if(scene.unmapped_objects||scene.omitted_features.length)$('query-map-count').textContent+=` ${scene.unmapped_objects} records without rendered geography; ${scene.omitted_features.length} unsupported features retained in downloaded JSON.`;
    if(scene.selected_state_code)$('query-map-count').textContent+=` State ${scene.selected_state_code} outlined; matching geometry is bright, other object geometry is faint context.`;
    for(const feature of scene.features){
      const p=feature.primitive,node=document.createElementNS(ns,p.kind==='point'?'circle':'path');
      if(p.kind==='point'){node.setAttribute('cx',p.x);node.setAttribute('cy',p.y);node.setAttribute('r','1.25');}else node.setAttribute('d',p.d);
      node.setAttribute('class','query-map-mark '+p.kind+' '+feature.role+(feature.matches_selected_state===false?' context-only':'')+(feature.undated_context?' undated-context':''));node.setAttribute('fill-rule','evenodd');
      node.dataset.entity=feature.entity_id;node.dataset.role=feature.role;node.setAttribute('tabindex','0');node.setAttribute('role','button');
      const name=feature.label+' · '+feature.role.replaceAll('_',' ')+(feature.observation_date?' · '+feature.observation_date:'')+(feature.undated_context?' · undated context':'')+(feature.matches_selected_state===true?' · matches selected state':feature.matches_selected_state===false?' · context only':'');node.setAttribute('aria-label',name);
      const title=document.createElementNS(ns,'title');title.textContent=name;node.append(title);
      const announce=()=>{$('query-map-hover').textContent=name+(feature.note?' — '+feature.note:'');};node.addEventListener('pointerenter',announce);node.addEventListener('focus',announce);
      const select=()=>{for(const other of $('query-map-features').children)other.classList.toggle('selected',other.dataset.entity===feature.entity_id);const box=node.getBBox();const width=Math.max(20,box.width*1.5,box.height*3);mapSet([box.x+box.width/2-width/2,box.y+box.height/2-width/4,width,width/2]);inspect('objects',feature.entity_id);};
      node.addEventListener('click',()=>{if(!mapMoved)select();});node.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});$('query-map-features').append(node);
    }
  }
  $('query-map-in').addEventListener('click',()=>mapZoom(.7));$('query-map-out').addEventListener('click',()=>mapZoom(1/.7));$('query-map-world').addEventListener('click',()=>mapSet([0,0,360,180]));
  $('query-map-day').addEventListener('change',()=>{if(!lastQuery||busy||!$('query-map-day').value)return;const query=JSON.parse(JSON.stringify(lastQuery));query.offset=0;query.geometry_time={from:$('query-map-day').value,to:$('query-map-day').value,include_undated:$('query-time-context').checked};showBuilder(query);run(query);});
  $('query-map-play').addEventListener('click',()=>{if(playing){stopPlayback();return;}if(!lastQuery||busy)return;playing=true;const generation=++playbackGeneration;$('query-map-play').textContent='Pause recorded days';$('query-map-play').setAttribute('aria-pressed','true');const days=metadata.geometry_observation_dates||[],selected=days.indexOf($('query-map-day').value);playDay(selected>=0?selected:0,generation);});
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
  const fieldNames={label:'Name',name:'Name',published_length_km:'Published ranked length (km)',approximate_width_km:'Scoped width value (km)',approximate_reference_path_km:'Reference route estimate (km)','capabilities.scoped_width':'Width record count','capabilities.reference_route':'Route record count','capabilities.time_samples':'Time record count'};
  sortFields.geometry_frames=['date','label','source_algorithm'];
  function rpc(action,value){const id=++sequence;return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});worker.postMessage({id,action,value});});}
  worker.onmessage=event=>{const item=pending.get(event.data.id);if(item){pending.delete(event.data.id);item.resolve(event.data.result);}};
  worker.onerror=()=>{for(const item of pending.values())item.reject(Error('Query worker failed'));pending.clear();failure('Rust query worker failed. Reload to retry.');};
  function element(tag,text,parent){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(parent)parent.append(node);return node;}
  function link(text,href,parent){try{const url=new URL(href,location.href);if(!['http:','https:'].includes(url.protocol))return;const a=element('a',text,parent);a.href=url.href;return a;}catch(_){return;}}
  function option(parent,text,value){const node=element('option',text,parent);node.value=value;}
  function failure(message){$('query-status').className='error';$('query-status').textContent=message;}
  function rejectResult(message){failure(message);renderMap(null);$('query-detail').hidden=true;detailSequence++;$('query-share').hidden=true;$('query-export').disabled=true;$('query-previous').disabled=true;$('query-next').disabled=true;lastQuery=null;lastResult=null;window.oswLastQueryResult=null;$('query-rows').replaceChildren();$('query-page').textContent='';}
  function label(row){return row.label||row.name||row.title||row.entity_label||row.id;}
  function value(row){
    if(row.status==='proposed'&&row.proposed_data)return 'proposed working record';
    if(row.approximate_width_km!==undefined)return `${row.approximate_width_km===null?(row.width_range_km?.join('–')||'unknown'):'≈ '+row.approximate_width_km} km · ${row.phase_label||row.phase_kind}`;
    if(row.approximate_reference_path_km!==undefined)return `≈ ${row.approximate_reference_path_km} km · reference route`;
    if(row.value!==undefined)return `${row.value===null?'unknown':typeof row.value==='object'?JSON.stringify(row.value):row.value} ${row.unit||''}`;
    if(row.published_length_km!==undefined&&row.published_length_km!==null)return `${row.published_length_km.toLocaleString()} km · published estimate`;
    return (row.type||row.kind||row.quantity||row.predicate||row.role||row.geometry_role||'record').replaceAll('_',' ');
  }
  function scope(row){return row.summary||row.scope||row.geographic_scope||row.note||row.limitations||(row.state_code?`${row.state_code} · ${row.state_name} · ${row.label}`:row.basin)||row.source_locator||row.source_citation||'';}
  function updateFields(){
    const collection=$('query-collection').value,objects=collection==='objects';
    $('query-type').disabled=!objects;$('query-state').disabled=!objects;$('query-state-mode').disabled=!objects;$('query-evidence').disabled=!objects;
    for(const id of ['query-time-from','query-time-to','query-time-context'])$(id).disabled=!objects;
    $('query-sort').replaceChildren();option($('query-sort'),'Stable record ID','');
    for(const field of sortFields[collection]||[])option($('query-sort'),fieldNames[field]||field.replaceAll('_',' '),field);
    if(sortFields[collection]?.includes('label'))$('query-sort').value='label';
  }
  function builder(){
    const collection=$('query-collection').value,query={collection,limit:50,offset:0};
    if($('query-text').value.trim())query.text=$('query-text').value.trim();
    if(collection==='objects'){if($('query-type').value)query.record_type=$('query-type').value;if($('query-state-mode').value!=='recorded')query.spatial={state_code:$('query-state').value,predicate:$('query-state-mode').value};else if($('query-state').value)query.state_code=$('query-state').value;if($('query-evidence').value)query.evidence=$('query-evidence').value;}
    if($('query-sort').value)query.sort={field:$('query-sort').value,direction:$('query-direction').value};
    if(collection==='objects'&&($('query-time-from').value||$('query-time-to').value))query.geometry_time={from:$('query-time-from').value,to:$('query-time-to').value,include_undated:$('query-time-context').checked};
    return query;
  }
  function showBuilder(query){
    $('query-collection').value=query.collection||'objects';updateFields();$('query-text').value=query.text||'';
    $('query-type').value=query.record_type||'';$('query-state').value=query.spatial?.state_code||query.state_code||'';$('query-state-mode').value=query.spatial?.predicate||'recorded';$('query-evidence').value=query.evidence||'';
    $('query-sort').value=query.sort?.field||'';$('query-direction').value=query.sort?.direction||'asc';
    $('query-time-from').value=query.geometry_time?.from||'';$('query-time-to').value=query.geometry_time?.to||'';$('query-time-context').checked=query.geometry_time?.include_undated||false;
  }
  function setBusy(value){busy=value;$('query-run').disabled=value;$('query-run-json').disabled=value;for(const b of document.querySelectorAll('[data-preset]'))b.disabled=value;}
  async function run(query,fromPlayback=false){
    if(!fromPlayback)stopPlayback();
    if(busy)return;setBusy(true);$('query-status').className='';$('query-status').textContent='Running query…';
    try{
      const result=await rpc('query',query);if(!result.ok)throw Error(result.error);
      lastQuery=JSON.parse(JSON.stringify(query));lastResult=result;window.oswLastQueryResult=result;
      showBuilder(query);
      $('query-json').value=JSON.stringify(query,null,2);
      const url=new URL(location.href);url.searchParams.set('q',JSON.stringify(query));history.replaceState(null,'',url);
      $('query-share').hidden=false;$('query-share').href=url.href;$('query-export').disabled=false;
      $('query-status').textContent=`${result.total.toLocaleString()} matching ${names[result.collection]?.toLowerCase()||result.collection}. Query executed in Rust / WebAssembly.`;
      $('query-caption').textContent=names[result.collection]+' · '+result.total.toLocaleString()+' matches';
      renderMap(result.map_scene);
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
  function describe(parent,row){
    element('h3',label(row),parent);element('p',value(row),parent);
    const dl=element('dl',undefined,parent);
    if(row.timeline_file){element('p',row.sampling_note,parent);for(const [key,title] of [['date','Observation day'],['method','Diagnostic method'],['stop_reason','Stop reason'],['reaches_downstream_gate','Reaches downstream gate'],['diagnostic_length_km','Diagnostic trace distance (km; not current length)'],['width_km','Current width (km)'],['positional_uncertainty_km','Positional uncertainty (km)'],['source_algorithm','Source processing algorithm'],['source_product_status','Source product status']]){if(row[key]!==undefined){element('dt',title,dl);element('dd',row[key]===null?'unresolved':String(row[key]),dl);}}element('p',row.attribution,parent);}
    for(const [key,title] of [['id','Record ID'],['scope','Scope'],['geographic_scope','Region'],['layer','Layer'],['time_convention','Time'],['boundary_rule','Boundary definition'],['range_interpretation','Range meaning'],['source_locator','Source location'],['source_quality_note','Source quality'],['kind','Relation kind'],['observation_date','Observation date'],['status','Status'],['width_rank_eligible','Width ranking eligible'],['rank_eligible','Published ranking eligible']]){
      if(row[key]!==undefined){element('dt',title,dl);element('dd',row[key]===null?'unresolved':String(row[key]),dl);}
    }
    const links=element('div',undefined,parent);links.className='record-links';
    if(row.target){const source=element('button','Inspect source reference',links);source.type='button';source.addEventListener('click',()=>inspect(row.target.collection,row.target.id));}
    if(row.timeline_file&&row.entity_id&&row.date)link('Map this observation day','query.html?q='+encodeURIComponent(JSON.stringify({collection:'objects',filters:[{field:'id',op:'eq',value:row.entity_id}],geometry_time:{from:row.date,to:row.date},limit:50})),links);
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
      const spatial=lastResult?.map_scene?.spatial_relations?.[id];
      if(spatial?.length){const details=element('details',undefined,panel);details.open=true;element('summary','Computed state relations ('+spatial.length+')',details);element('p',lastResult.spatial_scope,details);element('pre',JSON.stringify(spatial,null,2),details);}
      const groups=[['width_ids','widths','Scoped width records'],['measurement_ids','measurements','Published measurements'],['route_ids','reference_routes','Editorial routes'],['source_ids','sources','Linked sources'],['frame_ids','geometry_frames','Dated diagnostic frames']];
      if(record.source_id)groups.push(['single_source','sources','Source']);
      for(const [key,target,title] of groups){
        const ids=key==='single_source'?[record.source_id]:record[key];if(!ids?.length)continue;
        const details=element('details',undefined,panel);element('summary',`${title} (${ids.length})`,details);if(key==='width_ids'||key==='measurement_ids')details.open=true;
        for(const id of ids){const item=await rpc('record',{collection:target,id});if(generation!==detailSequence)return;if(!item.ok)throw Error(item.error);const article=element('article',undefined,details);describe(article,item.record);}
      }
      const raw=element('details',undefined,panel);element('summary','Complete record JSON',raw);element('pre',JSON.stringify(record,null,2),raw);
      window.oswWorkspace.editor(panel,collection,record);
      panel.scrollIntoView({block:'start'});panel.focus({preventScroll:true});
    }catch(error){if(generation===detailSequence){panel.replaceChildren();element('p',error.message,panel);}}
  }
  const presets={width:{collection:'objects',record_type:'named_current',evidence:'scoped_width',sort:{field:'label',direction:'asc'},limit:50},
    lengths:{collection:'objects',record_type:'named_current',evidence:'reported_length',sort:{field:'published_length_km',direction:'desc'},limit:50},
    'missing-routes':{collection:'objects',record_type:'named_current',filters:[{field:'capabilities.reference_route',op:'eq',value:0}],sort:{field:'label',direction:'asc'},limit:50},
    'eddy-geometry':{collection:'objects',record_type:'named_eddy',evidence:'geometry',sort:{field:'label',direction:'asc'},limit:50},
    kuro:{collection:'objects',record_type:'named_current',state_code:'KURO',sort:{field:'label',direction:'asc'},limit:50},
    'spatial-nadr':{collection:'objects',spatial:{state_code:'NADR',predicate:'intersects'},sort:{field:'label',direction:'asc'},limit:50},
    'gulf-dated':{collection:'objects',filters:[{field:'id',op:'eq',value:'current:gulf-stream-system'}],geometry_time:{from:'2025-01-15',to:'2025-01-15'},limit:50}};
  $('query-form').addEventListener('submit',event=>{event.preventDefault();run(builder());});$('query-collection').addEventListener('change',updateFields);
  $('query-run-json').addEventListener('click',()=>{try{const query=JSON.parse($('query-json').value);showBuilder(query);run(query);}catch(error){rejectResult('Invalid JSON query: '+error.message);}});
  for(const button of document.querySelectorAll('[data-preset]'))button.addEventListener('click',async()=>{const query=presets[button.dataset.preset];showBuilder(query);await run(query);if(button.dataset.preset==='gulf-dated'&&lastResult)fitMatches();});
  $('query-previous').addEventListener('click',()=>run({...lastQuery,offset:Math.max(0,(lastQuery.offset||0)-(lastQuery.limit||100))}));
  $('query-next').addEventListener('click',()=>run({...lastQuery,offset:(lastQuery.offset||0)+(lastQuery.limit||100)}));
  $('query-export').addEventListener('click',()=>{if(!lastResult)return;const blob=new Blob([JSON.stringify({query:lastQuery,bundle_sha256:metadata.bundle_sha256,result:lastResult},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob);const a=element('a');a.href=url;a.download='osw-query-result.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  (async()=>{
    try{
      metadata=await rpc('load');if(!metadata.ok)throw Error(metadata.error);
      for(const day of metadata.geometry_observation_dates||[])option($('query-map-day'),day,day);
      const counts=Object.fromEntries(metadata.collections.map(c=>[c.name,c.count]));
      $('query-inventory').textContent=`${metadata.object_type_counts.named_current} currents · ${metadata.object_type_counts.named_eddy + metadata.object_type_counts.operational_eddy_detection} eddy records · ${counts.states} OSW states · ${counts.claims.toLocaleString()} claims · ${counts.widths} scoped width records`;
      for(const name of order)if(counts[name]!==undefined)option($('query-collection'),`${names[name]} (${counts[name].toLocaleString()})`,name);
      await window.oswWorkspace.initialize(metadata,rpc,(workspace,query)=>{
        const option=$('query-collection').querySelector('option[value="working_records"]');if(option)option.textContent=names.working_records+' ('+workspace.record_count+')';
        if(query){const q={collection:'working_records',limit:50};showBuilder(q);run(q);}
      });
      const states=await rpc('query',{collection:'states',sort:{field:'label',direction:'asc'},limit:100});if(!states.ok)throw Error(states.error);
      for(const state of states.rows)option($('query-state'),state.code+' · '+state.label,state.code);
      $('query-controls').disabled=false;$('query-run-json').disabled=false;for(const button of document.querySelectorAll('[data-preset]'))button.disabled=false;
      $('query-engine-info').textContent=`${metadata.engine} · ${metadata.collections.length} collections · browser worker · snapshot ${metadata.bundle_sha256.slice(0,12)}.`;
      $('query-manifest').textContent=JSON.stringify(metadata.manifest,null,2);
      let query={collection:'objects',record_type:'named_current',sort:{field:'label',direction:'asc'},limit:50,offset:0};
      const shared=new URL(location.href).searchParams.get('q');if(shared){if(shared.length>20000)throw Error('Shared query is too large');query=JSON.parse(shared);}
      showBuilder(query);await run(query);
    }catch(error){failure('Query store unavailable: '+error.message);$('query-inventory').textContent='The query store could not be loaded.';}
  })();
})();
