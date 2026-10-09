"use strict";
window.initReferenceRouteAtlas = async function(catalog, reports, widthInventory, seasonalRoutes) {
  const byId=id=>document.getElementById(id), svg=byId('route-atlas-map'), layer=byId('route-atlas-features');
  const world=[60,90,1480,740], minimumViewWidth=8, ns='http://www.w3.org/2000/svg';
  let view=[...world], drag=null, dragged=false, sectionGround=false, inventorySummary='Loading atlas inventory…', timelineCleanup=()=>{}, refreshDirectory=()=>{}, refreshStateMap=()=>{};
  let restoredView=null,restoringSelection=false;
  const project=point=>window.oswCartography({op:'project',coordinates:point}).point;
  function make(tag,attrs,parent=layer) {
    const el=document.createElementNS(ns,tag);
    for(const [key,value] of Object.entries(attrs))el.setAttribute(key,value);
    parent.append(el);return el;
  }
  function encodedView() {
    const width=Number(view[2].toFixed(6));
    return [Number(view[0].toFixed(6)),Number(view[1].toFixed(6)),width,width/2].join(',');
  }
  function saveView() {
    const url=new URL(location.href);url.searchParams.set('atlas-view',encodedView());url.hash='route-atlas';
    history.replaceState(null,'',url);
    const anchor=byId('route-atlas-preview').querySelector('[data-atlas-share]');if(anchor)anchor.href=url.href;
  }
  function readView(value) {
    if(!value)return null;
    const parts=value.split(',');if(parts.length!==4||parts.some(part=>!part.trim()))return null;
    const box=parts.map(Number);if(box.some(part=>!Number.isFinite(part)))return null;
    const [x,y,width,height]=box;
    return width>=minimumViewWidth&&width<=1480&&Math.abs(height-width/2)<=.000001&&x>=60&&y>=90&&x+width<=1540.000001&&y+height<=830.000001?box:null;
  }
  function setView(box,persist=false) {
    const width=Math.max(minimumViewWidth,Math.min(1480,box[2])),height=width/2;
    view=[Math.max(60,Math.min(1540-width,box[0])),Math.max(90,Math.min(830-height,box[1])),width,height];
    svg.setAttribute('viewBox',view.join(' '));
    svg.querySelector(':scope > image').setAttribute('href',`../figures/ocean-motion-${sectionGround&&width<160?'closeup':'dashboard'}-ground.svg`);
    for(const circle of layer.querySelectorAll('circle'))circle.setAttribute('r',width/1480*8);
    for(const text of layer.querySelectorAll('text'))text.setAttribute('font-size',width/1480*18);
    byId('route-atlas-in').disabled=width<=minimumViewWidth;byId('route-atlas-out').disabled=width>=1480;
    if(persist||byId('route-atlas-preview').querySelector('[data-atlas-share]'))saveView();
  }
  function zoom(factor,px=.5,py=.5) {
    const width=Math.max(minimumViewWidth,Math.min(1480,view[2]*factor));
    restoredView=null;setView([view[0]+(view[2]-width)*px,view[1]+(view[3]-width/2)*py,width,width/2],true);
  }
  function fit(coordinates) {
    if(restoredView){setView(restoredView);return;}
    if(!coordinates.length)return;
    const box=window.oswCartography({op:'fit',coordinates}).view_box;if(box)setView(box);
  }
  function clearSelection() {
    if(!restoringSelection)restoredView=null;
    sectionGround=false;
    timelineCleanup();timelineCleanup=()=>{};
    layer.querySelectorAll('.selected,.route-atlas-related').forEach(el=>el.classList.remove('selected','route-atlas-related'));
    byId('route-atlas-select').value='';byId('route-atlas-eddy-select').value='';
    byId('route-atlas-preview').hidden=true;
    byId('route-atlas-preview').replaceChildren();
    byId('route-atlas-workspace').classList.remove('has-card');
    refreshDirectory();
  }
  function preview(title) {
    const panel=byId('route-atlas-preview');panel.hidden=false;
    byId('route-atlas-workspace').classList.add('has-card');
    const heading=document.createElement('h3');heading.textContent=title;panel.append(heading);
    return panel;
  }
  function paragraph(parent,text) { const p=document.createElement('p');p.textContent=text;parent.append(p);return p; }
  function previewLink(parent,text,href) { const a=document.createElement('a');a.textContent=text;a.href=href;paragraph(parent,'').append(a); }
  function selectionAddress(id) {
    const url=new URL(location.href);url.searchParams.delete('atlas-feature');url.searchParams.delete('atlas-route');url.searchParams.delete('atlas-geometry');url.searchParams.delete('atlas-date');url.searchParams.delete('atlas-series');url.searchParams.delete('atlas-section');url.searchParams.delete('atlas-view');url.searchParams.delete('atlas-width-month');url.searchParams.delete('atlas-width-season');
    if(id)url.searchParams.set('atlas-feature',id);
    return url;
  }
  function shareSelection(panel,id,routeId,geometryId,sectionId) {
    const url=selectionAddress(id);url.hash='route-atlas';
    if(routeId)url.searchParams.set('atlas-route',routeId);
    if(geometryId)url.searchParams.set('atlas-geometry',geometryId);
    if(sectionId)url.searchParams.set('atlas-section',sectionId);
    const widthMonth=panel.querySelector('.atlas-width-month:not([disabled])')?.value;
    if(id==='current:leeuwin'&&/^(?:[1-9]|1[0-2])$/.test(widthMonth||''))url.searchParams.set('atlas-width-month',widthMonth);
    const widthSeason=panel.querySelector('.atlas-width-season:not([disabled])')?.value;
    if(id==='current:kuroshio'&&['winter','spring','summer','autumn'].includes(widthSeason))url.searchParams.set('atlas-width-season',widthSeason);
    url.searchParams.set('atlas-view',encodedView());
    history.replaceState(null,'',url);
    let anchor=panel.querySelector('[data-atlas-share]');
    if(!anchor){anchor=document.createElement('a');anchor.dataset.atlasShare='true';anchor.textContent='Link to this atlas view';paragraph(panel,'').append(anchor);}
    anchor.href=url.href;refreshDirectory();
  }
  function reset(clearAddress=true) {
    if(clearAddress!==false)history.replaceState(null,'',selectionAddress(null));
    clearSelection();byId('route-atlas-card-link').hidden=true;setView(world);
    byId('route-atlas-status').textContent=inventorySummary;
  }
  window.returnToReferenceRouteAtlas=reset;
  function interactive(el,label,activate) {
    el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',label);
    make('title',{},el).textContent=label;
    el.addEventListener('click',()=>{if(!dragged)activate();});
    el.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});
  }
  function pointMarker(point,label,cls,parent) {
    const [x,y]=project(point),mark=make('g',{transform:`translate(${x} ${y})`,class:cls},parent);
    make('circle',{r:8,'vector-effect':'non-scaling-stroke'},mark);
    make('text',{x:12,y:-12,'font-size':18},mark).textContent=label;
    return mark;
  }
  function pathData(coordinates,close=false) {
    return window.oswCartography({op:'path',coordinates,closed:close}).d;
  }
  try {
    const sources=await window.oswAtlasSourcesReady;
    const stateJoin=sources['research/ocean-current-reference-route-state-join.json']||null;
    const snapshot=sources['research/ocean-motion-dashboard.json'],currents=snapshot.entries.filter(r=>r.type==='named_current');
    const eddies=snapshot.entries.filter(r=>r.type==='named_eddy'||r.type==='operational_eddy_detection');
    inventorySummary=`${currents.length} named currents · ${catalog.counts.currents_with_route_candidates} with reference-route cards · ${eddies.filter(r=>r.type==='named_eddy').length} named eddies · ${eddies.filter(r=>r.type==='operational_eddy_detection').length} dated detections. Select a current, eddy or path.`;
    if(snapshot.schema!=='osw.motion-dashboard.v1'||snapshot.fingerprint_version!==2||new Set(snapshot.entries.map(r=>r.id)).size!==snapshot.entries.length||snapshot.entries.some(r=>typeof r.id!=='string'||typeof r.fingerprint!=='string'||!r.section_fingerprints||!Array.isArray(r.map_features)))throw Error('Invalid atlas inventory snapshot');
    const seenKey='osw-motion-dashboard-seen-v2';
    const sectionLabels={identity:'Identity',sources:'Sources',claims:'Claims / reviews',measurements:'Measurements',routes_geometry:'Routes / geometry',media:'Media links',time_evidence:'Time evidence'};
    let baseline;
    function readBaseline() {
      try{baseline=JSON.parse(localStorage.getItem(seenKey));}catch(_){baseline=null;}
      if(!baseline||typeof baseline!=='object'||Array.isArray(baseline))baseline=null;
    }
    function markSeen() {
      baseline=Object.fromEntries(snapshot.entries.map(r=>[r.id,{fingerprint:r.fingerprint,sections:r.section_fingerprints}]));
      try{localStorage.setItem(seenKey,JSON.stringify(baseline));}catch(_){/* Keep a session baseline if storage is unavailable. */}
    }
    const changed=row=>Boolean(baseline&&baseline[row.id]?.fingerprint!==row.fingerprint);
    function changeDescription(row) {
      if(!changed(row))return '';
      const prior=baseline[row.id];
      if(!prior)return 'New inventory record since your saved baseline.';
      const groups=Object.entries(sectionLabels).filter(([key])=>prior.sections?.[key]!==row.section_fingerprints?.[key]).map(([,label])=>label);
      return `Updated since your saved baseline: ${groups.length?groups.join(', '):'record metadata'}.`;
    }
    readBaseline();if(!baseline)markSeen();
    function renderUpdates() {
      const rows=[...currents,...eddies],byId=new Map(rows.map(row=>[row.id,row]));
      for(const mark of layer.querySelectorAll('[data-current-id],[data-eddy-ids]')) {
        const members=mark.dataset.currentId?[byId.get(mark.dataset.currentId)]:JSON.parse(mark.dataset.eddyIds).map(id=>byId.get(id));
        const updates=members.filter(row=>row&&changed(row));
        mark.classList.toggle('updated',updates.length>0);
        const label=mark.dataset.atlasLabel||(members.length===1?members[0].label:`${members.length} names · regional gateway`);
        const note=updates.length?members.length===1?changeDescription(updates[0]):`${updates.length} updated records at this shared regional gateway.`:'';
        mark.setAttribute('aria-label',`${label}${note?' · '+note:''}`);
        const title=mark.querySelector('title');if(title)title.textContent=mark.getAttribute('aria-label');
      }
      const updates=rows.filter(changed);
      byIdElement('route-atlas-update-summary').textContent=`${updates.length} updated records since your saved baseline · amber outlines mark changes. These indicate inventory edits, not live ocean activity.`;
      for(const paths of reportsById.values())for(const {row,report} of paths) {
        const card=byIdElement(row.id),current=byId.get('current:'+report.current_id);
        if(!card||!current)continue;
        let note=card.querySelector('.route-atlas-update-note');
        if(changed(current)) {
          if(!note){note=document.createElement('p');note.className='route-atlas-update-note';card.querySelector('h3')?.after(note);}
          note.textContent=changeDescription(current);
        } else note?.remove();
      }
      byIdElement('route-atlas-seen').disabled=!updates.length;
      refreshDirectory();
    }
    const byIdElement=id=>document.getElementById(id);
    const reportsById=new Map();
    reports.forEach((report,i)=>{if(!reportsById.has(report.current_id))reportsById.set(report.current_id,[]);reportsById.get(report.current_id).push({report,row:catalog.candidates[i]});});
    const componentDecisions=catalog.remaining_current_decisions.filter(row=>row.known_component_currents?.length);
    function currentAtlasLink(parent,current) {
      const anchor=document.createElement('a');anchor.textContent=current.label;
      const url=selectionAddress(current.id);url.hash='route-atlas';anchor.href=url;
      anchor.dataset.atlasCurrent=current.id;parent.append(anchor);
      anchor.addEventListener('click',event=>{
        if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
        event.preventDefault();chooseCurrent(current);
      });
    }
    const routeLayer=make('g',{}),datedLayer=make('g',{id:'route-atlas-dated-lines'}),eddyLayer=make('g',{id:'route-atlas-eddies'}),stationLayer=make('g',{});
    const sectionLayer=make('g',{id:'route-atlas-section-locators'});
    const sectionRecords=(widthInventory?.measurements||[]).filter(row=>window.currentSectionLocator?.coordinates(row));
    const datedRoles={dated_partial_geostrophic_streamline:'Partial geostrophic diagnostic',dated_analyzed_surface_front:'Analyzed surface front'};
    const datedFeatures=current=>current.map_features.filter(f=>f.geometry.type==='LineString'&&datedRoles[f.role]&&f.geometry_id&&f.observation_date);
    const datedLabel=f=>`${f.observation_date} · ${datedRoles[f.role]}${f.front_side?' · '+f.front_side.replaceAll('_',' '):''}`;
    function chooseCurrent(current,geometryId) {
      const requestedRoute=new URL(location.href).searchParams.get('atlas-route');
      const requestedGeometry=geometryId||new URL(location.href).searchParams.get('atlas-geometry');
      const requestedDate=new URL(location.href).searchParams.get('atlas-date'),requestedSeries=new URL(location.href).searchParams.get('atlas-series');
      const requestedSection=new URL(location.href).searchParams.get('atlas-section');
      const requestedWidthMonth=new URL(location.href).searchParams.get('atlas-width-month');
      const requestedWidthSeason=new URL(location.href).searchParams.get('atlas-width-season');
      clearSelection();byId('route-atlas-select').value=current.id;
      layer.querySelectorAll('[data-current-id]').forEach(el=>el.classList.toggle('selected',el.dataset.currentId===current.id));
      const paths=reportsById.get(current.id.replace(/^current:/,''))||[];
      const observedSeries=current.series.find(row=>row.evidence_role==='observed_sections_with_unadmitted_one_sided_span');
      const monthlySeries=current.series.find(row=>row.evidence_role==='monthly_mean_section_width_candidate');
      sectionGround=Boolean(monthlySeries)||!paths.length&&(sectionRecords.some(row=>'current:'+row.current_id===current.id)||Boolean(observedSeries));
      const point=current.map_features.find(f=>f.geometry.type==='Point')?.geometry.coordinates;
      fit(paths.length?paths[0].report.coordinates_lon_lat:point?[point]:[]);
      const link=byId('route-atlas-card-link');link.hidden=false;link.href=paths.length?'#'+paths[0].row.id:current.object_url;
      link.textContent=paths.length?'Open current map card ↓':'Open current record — route pending';
      byId('route-atlas-status').textContent=paths.length
        ? `${current.label} · ${paths.length} reference-route card${paths.length===1?'':'s'} available beside the map.${paths.length>1?' Choose a component in the card.':''}`
        : `${current.label} · no reference-route card yet. Showing its name locator; ${current.capabilities.reported_length?'a source-reported length is available in its record.':'length and route remain unresolved.'}`;
      if(changed(current))byId('route-atlas-status').textContent+=' '+changeDescription(current);
      const panel=preview(current.label);
      const dated=datedFeatures(current);
      let showDated;
      const classification=document.createElement('details');classification.className='route-atlas-classification';panel.append(classification);
      const classificationTitle=document.createElement('summary');classificationTitle.textContent='Inventory classification';classification.append(classificationTitle);
      const facets=document.createElement('dl');facets.className='route-atlas-identity-facets';classification.append(facets);
      for(const [label,value] of [['Inventory level',current.identity_level],['Inventory description',current.source_kind],['Setting',current.setting],['Time behavior',current.time_behavior]]) {
        const term=document.createElement('dt'),definition=document.createElement('dd');term.textContent=label;definition.textContent=(value||'unresolved').replaceAll('_',' ');facets.append(term,definition);
      }
      paragraph(classification,'These are existing editorial inventory classifications; a name or category does not establish a measured route, observed footprint or scientific approval.');
      shareSelection(panel,current.id,null,null,observedSeries||monthlySeries?requestedSection:null);
      previewLink(panel,"Widths and seasonal evidence →",current.season_url);
      window.renderAtlasWidthEvidence(panel,current,widthInventory);
      if(current.id==='current:leeuwin'&&window.initAtlasMonthlyWidth)timelineCleanup=window.initAtlasMonthlyWidth(panel,current,requestedWidthMonth);
      if(current.id==='current:kuroshio'&&window.initAtlasSeasonalWidthProfile)timelineCleanup=window.initAtlasSeasonalWidthProfile(panel,current,requestedWidthSeason);
      if(observedSeries&&window.initAtlasObservedSections)timelineCleanup=window.initAtlasObservedSections(panel,current,{svg,layer,fit,make,ns,project,shareSelection,requestedSection,fitBounds:box=>setView(restoredView||box),refreshUpdates:renderUpdates,wasDragged:()=>dragged});
      if(monthlySeries&&window.initAtlasMonthlySection)timelineCleanup=window.initAtlasMonthlySection(panel,current,{svg,layer,fit,make,ns,project,shareSelection,requestedSection,fitBounds:box=>setView(restoredView||box),refreshUpdates:renderUpdates,wasDragged:()=>dragged});
      if(!dated.length && current.id!=='current:gulf-stream-system')for(const series of current.series)previewLink(panel,series.label+' →',series.url);
      if(dated.length) {
        const section=document.createElement('section');section.className='route-atlas-dated-preview';panel.append(section);
        const heading=document.createElement('h4');heading.textContent='Saved dated surface evidence';section.append(heading);
        paragraph(section,'Each view retains its own date and method. Fronts and diagnostic streamlines are different features; these snapshots do not establish a whole-current axis, width or annual extent.');
        const tabs=document.createElement('div');tabs.className='route-atlas-controls';section.append(tabs);
        const content=document.createElement('div');content.className='route-atlas-dated-content';section.append(content);
        showDated=feature=>{
          panel.dispatchEvent(new Event('atlas-saved-view'));content.hidden=false;
          content.replaceChildren();fit(feature.geometry.coordinates);
          shareSelection(panel,current.id,null,feature.geometry_id);
          tabs.querySelectorAll('button').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.geometryId===feature.geometry_id)));
          datedLayer.querySelectorAll('[data-current-id]').forEach(line=>line.classList.toggle('selected',line.dataset.currentId===current.id&&line.dataset.geometryId===feature.geometry_id));
          paragraph(content,datedLabel(feature));
          const image=document.createElementNS(ns,'svg');image.classList.add('route-atlas-dated-map');image.setAttribute('viewBox',view.join(' '));image.setAttribute('role','img');image.setAttribute('aria-label',`${current.label}: ${datedLabel(feature)}. Saved surface evidence, not whole-current geometry.`);content.append(image);
          make('image',{href:'../figures/ocean-motion-dashboard-ground.svg',x:60,y:90,width:1480,height:740,opacity:.45},image);
          make('path',{d:pathData(feature.geometry.coordinates),class:'route-atlas-dated-line '+feature.role,'vector-effect':'non-scaling-stroke'},image);
          paragraph(content,feature.note);
          if(feature.source_url)previewLink(content,'Dated source',feature.source_url);
          if(feature.receipt_file)previewLink(content,'Geometry evidence receipt','../'+feature.receipt_file);
          for(const series of current.series)previewLink(content,series.label+' →',series.url);
          byId('route-atlas-status').textContent+=` Selected saved view: ${datedLabel(feature)}.`;
        };
        for(const feature of dated) {
          const button=document.createElement('button');button.type='button';button.dataset.geometryId=feature.geometry_id;button.textContent=`${feature.observation_date} · ${feature.front_side?feature.front_side.replace('_wall','')+' front':'diagnostic'}`;button.setAttribute('aria-label',datedLabel(feature));
          button.addEventListener('click',()=>{byId('route-atlas-status').textContent=`${current.label} · saved dated surface evidence, not a continuous family or system route.`;showDated(feature);});tabs.append(button);
        }
      }
      if(paths.length) {
        const tabs=document.createElement('div');tabs.className='route-atlas-controls';tabs.hidden=paths.length<2;if(paths.length>1)panel.append(tabs);
        const content=document.createElement('div');panel.append(content);
        function showPath(path,index) {
          const {row,report}=path;content.replaceChildren();
          shareSelection(panel,current.id,row.id);
          tabs.querySelectorAll('button').forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));
          fit(report.coordinates_lon_lat);link.href='#'+row.id;
          paragraph(content,`≈ ${Number(row.approximate_reference_path_km).toLocaleString('en-US')} km · ${row.scenario_range_km.map(v=>Number(v).toLocaleString('en-US')).join('–')} km scenario envelope`);
          if(report.route_topology==='closed_circuit')paragraph(content,`Closed ${report.circuit_direction} circuit; arbitrary anchor, no current origin or termination. Not a parcel travel path or continuous annual flow.`);
          const image=byId(row.id)?.querySelector('.route-map')?.cloneNode(true);if(image)content.append(image);
          paragraph(content,row.scope);
          const phase=seasonalRoutes?.frames.find(frame=>frame.route_candidate_file===row.candidate_file);
          if(phase)previewLink(content,'Open this recorded seasonal phase →',`${current.season_url}&phase=${encodeURIComponent(phase.id)}`);
          if(report.source_season_convention) {
            const convention=report.source_season_convention,months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            const labels=Object.entries(convention.months_by_label).map(([label,values])=>`${label}: ${values.map(month=>months[month-1]).join(', ')}`).join('; ');
            const note=paragraph(content,`${convention.label_basis} source sampling labels · ${labels}. These are source observation labels, not seasonal route geometry or annual length/width ranges.`);
            note.className='route-atlas-source-seasons';
          }
          if(report.parent_current_id) {
            paragraph(content,report.parent_scope_note);
            const parent=catalog.candidates.find(item=>item.current_id===report.parent_current_id);
            previewLink(content,'Inspect parent current route ↓',parent?'#'+parent.id:`object.html?id=${encodeURIComponent('current:'+report.parent_current_id)}`);
          }
          paragraph(content,`Layer: ${report.layer} Time: ${report.time_convention}`);
          paragraph(content,'Editorial reference route; scenario limits are selected assumptions, not measured seasonal variation.');
          if(row.comparison_group==='osw_studied_reach_routes')paragraph(content,'Studied reach only; this is not a whole-current length.');
          const states=document.createElement('section');states.className='route-atlas-state-links';content.append(states);
          const heading=document.createElement('h4');heading.textContent='OSW states intersected by this reference route';states.append(heading);
          if(report.state_scope_note)paragraph(states,report.state_scope_note);
          if(stateJoin) {
            const crossings=Object.entries(stateJoin.states).flatMap(([code,state])=>(state.route_candidates||[]).filter(item=>item.candidate_id===row.id).map(item=>({...item,code,name:state.name})));
            paragraph(states,'Editorial line crossings of approximate state shapes. Scenario counts describe sensitivity to path assumptions, not observed passage, probabilities or seasonal occupancy.');
            if(crossings.length) {
              const list=document.createElement('ul');states.append(list);
              for(const crossing of crossings) {
                const item=document.createElement('li');item.dataset.stateCode=crossing.code;list.append(item);
                const anchor=document.createElement('a');anchor.href=`index.html?state=${encodeURIComponent(crossing.code)}#state-title`;anchor.textContent=`${crossing.code} · ${crossing.name}`;item.append(anchor);
                item.append(document.createTextNode(` · ${crossing.nominal_crossing?'nominal crossing':'scenario-only crossing'} · ${crossing.crossing_scenario_count}/${crossing.scenario_count} declared scenarios`));
              }
            } else paragraph(states,'No candidate crossing recorded; physical current passage remains unresolved.');
          } else paragraph(states,'State crossing inventory unavailable. The route map and current record remain available.');
          previewLink(content,'Full route card, measurements and sources ↓','#'+row.id);
          previewLink(content,'Current record →',current.object_url);
        }
        paths.forEach((path,index)=>{const button=document.createElement('button');button.type='button';button.textContent=paths.length>1?path.row.route_extent_kind:'Reference route';button.addEventListener('click',()=>showPath(path,index));tabs.append(button);});
        const requestedIndex=paths.findIndex(path=>path.row.id===requestedRoute);
        const initialIndex=requestedIndex<0?0:requestedIndex;
        showPath(paths[initialIndex],initialIndex);
      } else {
        const decision=componentDecisions.find(row=>'current:'+row.current_id===current.id);
        if(decision) {
          const members=decision.known_component_currents.map(item=>currents.find(row=>row.id==='current:'+item.current_id)).filter(Boolean);
          const memberIds=new Set(members.map(row=>row.id));
          layer.querySelectorAll('[data-current-id]').forEach(el=>el.classList.toggle('route-atlas-related',memberIds.has(el.dataset.currentId)));
          const coordinates=members.flatMap(member=>{
            const routes=reportsById.get(member.id.replace(/^current:/,''))||[];
            return routes.length?routes.flatMap(path=>path.report.coordinates_lon_lat):member.map_features.filter(f=>f.geometry.type==='Point').map(f=>f.geometry.coordinates);
          });
          fit(coordinates);
          paragraph(panel,'Known components · inventory coverage may be incomplete. Each component has its own scope, layer and time convention. No single family or system length is established; do not sum overlapping routes.');
          const list=document.createElement('ul');list.className='route-atlas-components';panel.append(list);
          for(const member of members) {
            const item=document.createElement('li');list.append(item);currentAtlasLink(item,member);
            const routes=reportsById.get(member.id.replace(/^current:/,''))||[];
            item.append(document.createTextNode(routes.length?` · ${routes.length} reference-route card${routes.length===1?'':'s'}`:member.capabilities.reported_length?' · source-reported length available; route card pending':' · route pending; name locator only'));
          }
          byId('route-atlas-status').textContent=`${current.label} · ${members.length} known components. Highlighted features belong to the listed components; they are not a continuous family or system route.`;
          if(changed(current))byId('route-atlas-status').textContent+=' '+changeDescription(current);
        } else if(!dated.length&&!sectionRecords.some(row=>'current:'+row.current_id===current.id))paragraph(panel,current.capabilities.reported_length?'Reference-route card pending. A source-reported length is available in the current record; the name locator does not show the measured path.':'Reference route pending. The atlas shows a name locator; its route and length remain unresolved.');
        previewLink(panel,'Open current record →',current.object_url);
      }
      if(current.id==='current:antarctic-slope')previewLink(panel,'Observed M6 velocity · monthly and seasonal charts →','query.html?q='+encodeURIComponent(JSON.stringify({collection:'current_velocity_samples',limit:100}))+'#query-chart-section');
      if(showDated) {
        showDated(dated.find(feature=>feature.geometry_id===requestedGeometry)||dated[0]);
        link.href=current.object_url;link.textContent='Open current evidence record →';
      }
      if(current.id==='current:gulf-stream-system'&&window.initAtlasTimeline)timelineCleanup=window.initAtlasTimeline(panel,current,{svg,layer,fit,pathData,make,ns,shareSelection,requestedDate,requestedSeries});
      const parents=componentDecisions.filter(row=>row.known_component_currents.some(item=>'current:'+item.current_id===current.id));
      if(parents.length) {
        const related=document.createElement('section');related.className='route-atlas-parent-families';panel.append(related);
        paragraph(related,'Browse related family or system records · membership does not establish continuity or additive length.');
        for(const parent of parents) {
          const record=currents.find(row=>row.id==='current:'+parent.current_id);
          if(record)currentAtlasLink(paragraph(related,''),record);
        }
      }
      for(const measurement of sectionRecords.filter(row=>'current:'+row.current_id===current.id)) {
        const coordinates=window.currentSectionLocator.coordinates(measurement);
        window.currentSectionLocator.render(panel,measurement);
        if(!paths.length&&!dated.length) {
          fit(coordinates);
          if(!restoredView&&view[2]<120)setView([view[0]-(120-view[2])/2,view[1]-(60-view[3])/2,120,60]);
          byId('route-atlas-status').textContent=`${current.label} · ${measurement.time_precision==='month'?'reported':'dated'} section latitude-span locator (${window.currentSectionLocator.timeLabel(measurement)}); current axis and full width remain unresolved.`;
          if(changed(current))byId('route-atlas-status').textContent+=' '+changeDescription(current);
        }
      }
      if(current.scope_notes?.length) {
        const reviews=document.createElement('section');reviews.className='route-atlas-scope-reviews';panel.append(reviews);
        const heading=document.createElement('h4');heading.textContent='Source scope review';reviews.append(heading);
        for(const note of current.scope_notes) {
          paragraph(reviews,note.summary);
          if(current.id==='current:red-sea-saline-overflow') {
            const audit=current.scope_audits?.find(row=>row.current_id==='red-sea-saline-overflow');
            if(audit?.reported_reach&&audit.whole_current_length_km===null) {
              const evidence=document.createElement('section');evidence.className='route-atlas-reported-reach';reviews.append(evidence);
              const heading=document.createElement('h5');heading.textContent='Reported winter reach';evidence.append(heading);
              const reach=audit.reported_reach;
              paragraph(evidence,`About ${reach.approximate_length_km} km · plume speed ${reach.threshold_operator} ${reach.velocity_threshold_m_s} m/s. ${reach.layer_thickness_range_m.join('–')} m is layer thickness, not a fixed depth interval. Source cruise context: ${reach.campaign_context.start} to ${reach.campaign_context.end}; exact reach occupation dates unresolved. This is a sampled reach, not a whole-current length or reconstructed map axis.`);
              const branches=document.createElement('ul');branches.className='route-atlas-outflow-branches';evidence.append(branches);
              for(const branch of audit.branches){const item=document.createElement('li');item.dataset.componentId=branch.id;item.textContent=`${branch.label} · ${branch.component_role.replaceAll('_',' ')} · local source component; canonical identity pending`;branches.append(item);}
              const details=document.createElement('details');evidence.append(details);const title=document.createElement('summary');title.textContent='Channel dimensions · geographic context';details.append(title);
              for(const row of audit.channel_dimension_context)paragraph(details,`${row.source}: about ${row.approximate_length_km} km long and ${row.approximate_width_km} km wide · ${row.metric.replaceAll('_',' ')}.`);
              paragraph(details,audit.source_consistency_note+' These are not current width estimates or a statistical length interval.');
            }
          }
          if(current.id==='current:persian-gulf-saline-overflow') {
            const audit=current.scope_audits?.find(row=>row.current_id==='persian-gulf-saline-overflow');
            if(audit?.width_metric==='author_reported_half_salinity_contrast_water_mass_core_width'&&audit.whole_current_width_km===null&&audit.whole_current_length_km===null) {
              const heading=document.createElement('h5');heading.textContent='Published local core measurements';reviews.append(heading);
              paragraph(reviews,'Water-mass core widths use half the salinity contrast with surrounding water. Section distances use the author’s coordinate from R13; they are not a mapped current axis. These sections combine locations and occupations, not annual extrema.');
              const wrapper=document.createElement('div');wrapper.className='route-atlas-local-dimensions';reviews.append(wrapper);
              const table=document.createElement('table');wrapper.append(table);
              const caption=document.createElement('caption');caption.textContent='GOGP99 · October–November 1999';table.append(caption);
              const head=document.createElement('thead'),headrow=document.createElement('tr');table.append(head);head.append(headrow);
              for(const text of ['Section(s)','Source distance from R13 (km)','Approximate core width (km)']){const cell=document.createElement('th');cell.scope='col';cell.textContent=text;headrow.append(cell);}
              const body=document.createElement('tbody');table.append(body);
              const distances=new Map(audit.reported_section_distances.rows.flatMap(row=>row.sections.map(id=>[id,row.distance_km])));
              for(const row of audit.reported_local_core_widths) {
                const tr=document.createElement('tr');body.append(tr);
                const values=[row.sections.join(' / '),row.sections.map(id=>`${id}: ${distances.get(id)}`).join('; '),row.width_range_km?row.width_range_km.join('–'):String(row.approximate_width_km)];
                values.forEach((text,index)=>{const cell=document.createElement(index===0?'th':'td');if(index===0)cell.scope='row';cell.textContent=text;tr.append(cell);});
              }
            }
          }
          previewLink(reviews,'Review source scope and remaining gates',`../${note.audit_file}`);
          previewLink(reviews,'Naming / scope source',note.source_url);
          for(const source of note.supporting_sources||[]) {
            const context=paragraph(reviews,'');
            previewLink(context,source.label,source.url);
            context.append(document.createTextNode(` · ${source.locator}. ${source.access}`));
          }
          for(const proposal of note.related_proposed_currents||[]) {
            previewLink(paragraph(reviews,'Proposed separate current · '),proposal.name,`#inventory-addition-${proposal.id}`);
          }
          for(const ident of note.related_current_ids||[]) {
            const record=currents.find(row=>row.id==='current:'+ident);
            if(record)currentAtlasLink(paragraph(reviews,'Related current record · '),record);
          }
        }
      }
    }
    for(const current of currents) {
      const option=document.createElement('option');option.value=current.id;option.textContent=current.label;byId('route-atlas-select').append(option);
      for(const path of reportsById.get(current.id.replace(/^current:/,''))||[]) {
        const line=make('path',{d:pathData(path.report.coordinates_lon_lat),class:'route-atlas-line','vector-effect':'non-scaling-stroke'},routeLayer);
        line.dataset.currentId=current.id;interactive(line,current.label+' — editorial reference route',()=>chooseCurrent(current));
      }
      for(const feature of datedFeatures(current)) {
        const line=make('path',{d:pathData(feature.geometry.coordinates),class:'route-atlas-dated-line '+feature.role,'vector-effect':'non-scaling-stroke'},datedLayer);
        line.dataset.currentId=current.id;line.dataset.geometryId=feature.geometry_id;line.dataset.atlasLabel=current.label+' · '+datedLabel(feature);
        interactive(line,line.dataset.atlasLabel,()=>chooseCurrent(current,feature.geometry_id));
      }
      for(const measurement of sectionRecords.filter(row=>'current:'+row.current_id===current.id)) {
        const coordinates=window.currentSectionLocator.coordinates(measurement);
        const line=make('path',{d:pathData(coordinates),class:'route-atlas-section-locator','vector-effect':'non-scaling-stroke'},sectionLayer);
        line.dataset.currentId=current.id;line.dataset.measurementId=measurement.id;
        line.dataset.atlasLabel=`${current.label} · ${window.currentSectionLocator.timeLabel(measurement)} reported section latitude span, not a current axis`;
        interactive(line,line.dataset.atlasLabel,()=>chooseCurrent(current));
      }
      const point=current.map_features.find(f=>f.geometry.type==='Point')?.geometry.coordinates;
      if(point){const mark=pointMarker(point,current.label,'route-atlas-station',stationLayer);mark.dataset.currentId=current.id;interactive(mark,current.label,()=>chooseCurrent(current));}
    }
    function chooseEddy(eddy) {
      clearSelection();byId('route-atlas-eddy-select').value=eddy.id;
      byId('route-atlas-eddy-toggle').checked=true;eddyLayer.style.display='';
      const feature=eddy.map_features.find(f=>f.geometry.type==='Polygon')||eddy.map_features[0];
      if(!feature)return;
      sectionGround=true;
      fit(feature.geometry.type==='Point'?[feature.geometry.coordinates]:feature.geometry.coordinates.flat());
      eddyLayer.querySelectorAll('[data-eddy-ids]').forEach(el=>el.classList.toggle('selected',JSON.parse(el.dataset.eddyIds).includes(eddy.id)));
      const link=byId('route-atlas-card-link');link.hidden=false;link.href=eddy.object_url;link.textContent='Open eddy record →';
      const kind=feature.role==='shared_regional_gateway'?'Shared regional gateway; this name has no individual center or footprint here.'
        : feature.geometry.type==='Polygon'?`Stored ${feature.role==='dated_figure_ssh_contour_proxy'?'figure-derived SSH contour proxy':'operational polygon'} · observation ${eddy.latest_observation_date||'date unresolved'}. Historical snapshot, not live extent.`
        : feature.role==='approximate_reported_center'?'Approximate source-reported center; no footprint or trajectory established.'
        : 'Source geography locator; this point does not establish an eddy footprint or trajectory.';
      byId('route-atlas-status').textContent=`${eddy.label} · ${kind}${changed(eddy)?' '+changeDescription(eddy):''}`;
      const panel=preview(eddy.label);paragraph(panel,kind);
      const radial=sources['research/astrid-2000-radial-scale-scope-audit.json'];
      if(radial?.entity_id===eddy.id)window.renderEddyRadialScales(panel,radial);
      const radiusAudit=sources['research/agulhas-guerra-2022-ring-radius-scope-audit.json'];
      const radiusOwner=eddy.id.replace(/^eddy:geography:/,'');
      if(radiusAudit?.entities?.[radiusOwner])window.renderPublishedRingRadii(panel,radiusAudit.entities[radiusOwner],'research/agulhas-guerra-2022-ring-radius-scope-audit.json',radiusOwner);
      const map=document.createElementNS(ns,'svg');map.classList.add('route-atlas-eddy-map');map.setAttribute('viewBox',view.join(' '));map.setAttribute('role','img');map.setAttribute('aria-label',`${eddy.label} · ${kind}`);panel.append(map);
      map.classList.toggle('updated',changed(eddy));
      if(changed(eddy))paragraph(panel,changeDescription(eddy));
      make('image',{href:`../figures/ocean-motion-${view[2]<160?'closeup':'dashboard'}-ground.svg`,x:60,y:90,width:1480,height:740},map);
      if(feature.geometry.type==='Point') {
        const marker=pointMarker(feature.geometry.coordinates,eddy.label,'route-atlas-eddy',map);
        marker.setAttribute('tabindex','0');marker.setAttribute('aria-label',`${eddy.label} · ${kind}`);
        marker.querySelector('circle').setAttribute('r',view[2]/1480*8);
        const name=marker.querySelector('text');name.setAttribute('font-size',view[2]/1480*18);name.setAttribute('x',view[2]/1480*12);name.setAttribute('y',-view[2]/1480*12);
        make('title',{},marker).textContent=`${eddy.label} · ${kind}`;
      } else make('path',{d:feature.geometry.coordinates.map(r=>pathData(r,true)).join(' '),class:'route-atlas-eddy-footprint','vector-effect':'non-scaling-stroke','fill-rule':'evenodd'},map);
      previewLink(panel,'Open eddy record →',eddy.object_url);shareSelection(panel,eddy.id);
      const states=document.createElement('section');states.className='route-atlas-eddy-state-links';panel.append(states);
      const heading=document.createElement('h4');heading.textContent='OSW state evidence';states.append(heading);
      paragraph(states,'Relations retain their source scope and observation date. A locator or center point does not establish whole-eddy containment; dated outlines are historical snapshots.');
      if(eddy.state_evidence?.length) {
        const list=document.createElement('ul');states.append(list);
        for(const evidence of eddy.state_evidence) {
          const item=document.createElement('li');item.dataset.stateCode=evidence.state_code;item.dataset.evidenceKind=evidence.kind;list.append(item);
          const anchor=document.createElement('a');anchor.href=`index.html?state=${encodeURIComponent(evidence.state_code)}#state-title`;anchor.textContent=`${evidence.state_code} · ${evidence.state_name}`;item.append(anchor);
          item.append(document.createTextNode(` · ${evidence.label} · ${evidence.observation_date||'exact observation date unresolved'} · `));
          const receipt=document.createElement('a');receipt.href='../'+evidence.source_file;receipt.textContent='Evidence receipt';receipt.title=evidence.source_record_id;item.append(receipt);
        }
      } else paragraph(states,'No state evidence recorded here; physical intersection and containment remain unresolved.');
    }
    const groups=new Map();
    for(const eddy of eddies) {
      const option=document.createElement('option');option.value=eddy.id;option.textContent=eddy.label;byId('route-atlas-eddy-select').append(option);
      for(const feature of eddy.map_features) {
        const key=feature.role==='shared_regional_gateway'?feature.role+JSON.stringify(feature.geometry.coordinates):eddy.id+feature.role;
        if(!groups.has(key))groups.set(key,{feature,members:[]});groups.get(key).members.push(eddy);
      }
    }
    for(const {feature,members} of groups.values()) {
      const label=members.length>1?`${members.length} names · regional gateway`:members[0].label;
      let mark;
      if(feature.geometry.type==='Point')mark=pointMarker(feature.geometry.coordinates,label,'route-atlas-eddy',eddyLayer);
      else if(feature.geometry.type==='Polygon')mark=make('path',{d:feature.geometry.coordinates.map(r=>pathData(r,true)).join(' '),class:'route-atlas-eddy-footprint','vector-effect':'non-scaling-stroke','fill-rule':'evenodd'},eddyLayer);
      else continue;
      mark.dataset.eddyIds=JSON.stringify(members.map(e=>e.id));
      interactive(mark,label,()=>{
        if(members.length===1)chooseEddy(members[0]);
        else {
          history.replaceState(null,'',selectionAddress(null));clearSelection();fit([feature.geometry.coordinates]);mark.classList.add('selected');byId('route-atlas-card-link').hidden=true;
          byId('route-atlas-status').textContent=`${label}. Choose an individual name from the Eddy selector; these are not ${members.length} observed centers.`;
          const updated=members.filter(changed);
          if(updated.length)byId('route-atlas-status').textContent+=` ${updated.length} updated names: ${updated.map(row=>row.label).join(', ')}.`;
          byId('route-atlas-eddy-select').focus({preventScroll:true});
        }
      });
    }
    refreshDirectory=window.initAtlasDirectory([...currents,...eddies],{
      select:row=>row.type==='named_current'?chooseCurrent(row):chooseEddy(row),
      selected:()=>byId('route-atlas-select').value||byId('route-atlas-eddy-select').value,
      changed,changeDescription,stateJoin,stateChanged:code=>{
        refreshStateMap(code);
        const share=byId('route-atlas-preview').querySelector('[data-atlas-share]');
        if(share)share.href=location.href;
      }
    });
    window.initAtlasStateNavigation(svg,{
      dragged:()=>dragged,
      select:code=>{reset();refreshDirectory.selectState(code);byId('atlas-directory').scrollIntoView({block:'start'});byId('atlas-directory-state').focus({preventScroll:true});}
    }).then(refresh=>{refreshStateMap=refresh;refreshDirectory();});
    renderUpdates();
    byId('route-atlas-refresh').addEventListener('click',()=>location.reload());
    byId('route-atlas-seen').addEventListener('click',()=>{markSeen();renderUpdates();reset();});
    window.addEventListener('storage',event=>{if(event.key===seenKey){readBaseline();if(!baseline)markSeen();renderUpdates();}});
    byId('route-atlas-select').addEventListener('change',()=>{const current=currents.find(r=>r.id===byId('route-atlas-select').value);if(current)chooseCurrent(current);else reset();});
    byId('route-atlas-eddy-select').addEventListener('change',()=>{const eddy=eddies.find(r=>r.id===byId('route-atlas-eddy-select').value);if(eddy)chooseEddy(eddy);else reset();});
    byId('route-atlas-eddy-toggle').addEventListener('change',()=>{eddyLayer.style.display=byId('route-atlas-eddy-toggle').checked?'':'none';});
    byId('route-atlas-in').addEventListener('click',()=>zoom(.7));byId('route-atlas-out').addEventListener('click',()=>zoom(1/.7));byId('route-atlas-world').addEventListener('click',reset);
    svg.setAttribute('tabindex','0');
    document.addEventListener('pointerdown',()=>{restoredView=null;},{capture:true});
    document.addEventListener('keydown',()=>{restoredView=null;},{capture:true});
    svg.addEventListener('keydown',event=>{
      if(event.target!==svg)return;
      const moves={ArrowLeft:[-.2,0],ArrowRight:[.2,0],ArrowUp:[0,-.2],ArrowDown:[0,.2]};
      if(moves[event.key]){event.preventDefault();restoredView=null;const [x,y]=moves[event.key];setView([view[0]+x*view[2],view[1]+y*view[3],view[2],view[3]],true);}
      else if(event.key==='+'||event.key==='='){event.preventDefault();zoom(.7);}
      else if(event.key==='-'){event.preventDefault();zoom(1/.7);}
      else if(event.key==='Home'){event.preventDefault();reset();}
    });
    svg.addEventListener('wheel',event=>{event.preventDefault();const box=svg.getBoundingClientRect();zoom(event.deltaY<0?.85:1/.85,(event.clientX-box.left)/box.width,(event.clientY-box.top)/box.height);},{passive:false});
    const pointers=new Map();let pinch=null;
    function pointerPair() {
      const [a,b]=[...pointers.values()];
      return {x:(a.x+b.x)/2,y:(a.y+b.y)/2,distance:Math.hypot(a.x-b.x,a.y-b.y)};
    }
    svg.addEventListener('pointerdown',event=>{
      if(event.button!==0)return;
      restoredView=null;
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
      if(pointers.size===1){dragged=false;drag={x:event.clientX,y:event.clientY,view:[...view]};}
      else if(pointers.size===2){pinch={...pointerPair(),view:[...view]};drag=null;dragged=true;for(const id of pointers.keys())svg.setPointerCapture(id);}
      if(event.target===svg||event.target.tagName==='image')svg.setPointerCapture(event.pointerId);
    });
    svg.addEventListener('pointermove',event=>{
      if(!pointers.has(event.pointerId))return;
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
      const box=svg.getBoundingClientRect();
      if(pinch&&pointers.size>=2){
        const pair=pointerPair();if(pinch.distance<1||pair.distance<1)return;
        const width=Math.max(minimumViewWidth,Math.min(1480,pinch.view[2]*pinch.distance/pair.distance));
        setView([pinch.view[0]+(pinch.x-box.left)/box.width*pinch.view[2]-(pair.x-box.left)/box.width*width,
          pinch.view[1]+(pinch.y-box.top)/box.height*pinch.view[3]-(pair.y-box.top)/box.height*width/2,width,width/2],true);
        return;
      }
      if(!drag)return;
      const dx=event.clientX-drag.x,dy=event.clientY-drag.y;if(Math.hypot(dx,dy)<5)return;
      dragged=true;svg.setPointerCapture(event.pointerId);
      setView([drag.view[0]-dx/box.width*drag.view[2],drag.view[1]-dy/box.height*drag.view[3],drag.view[2],drag.view[3]],true);
    });
    function endPointer(event) {
      if(!pointers.delete(event.pointerId))return;
      pinch=null;
      const remaining=[...pointers.values()][0];
      drag=remaining?{...remaining,view:[...view]}:null;
    }
    window.addEventListener('pointerup',endPointer);window.addEventListener('pointercancel',endPointer);
    window.restoreReferenceRouteAtlas=()=>{
      const url=new URL(location.href),id=url.searchParams.get('atlas-feature');
      restoredView=readView(url.searchParams.get('atlas-view'));restoringSelection=true;
      const current=currents.find(row=>row.id===id),eddy=eddies.find(row=>row.id===id);
      if(current)chooseCurrent(current);else if(eddy)chooseEddy(eddy);else reset();
      if(restoredView)setView(restoredView,true);
      restoringSelection=false;
    };
    if(location.hash==='#route-atlas'||!location.hash)window.restoreReferenceRouteAtlas();else reset(false);
  } catch(error){byId('route-atlas-status').textContent=`Global current map unavailable: ${error.message}. Route cards remain available below.`;}
};
