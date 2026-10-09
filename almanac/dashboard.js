(() => {
  const $ = id => document.getElementById(id);
  const labels = {observed_velocity:'Observed velocity summaries',radius_evidence:'Scoped radius evidence',reported_length:'Published ranked length',reference_route:'Editorial reference route',scoped_width:'Scoped width evidence',geometry:'Geometry beyond a locator',time_samples:'Time samples / phase records',source_connectivity:'Source-described current links',scope_notes:'Source scope notes',dated_diagnostics:'Dated method diagnostics',flow_network:'Passage networks',passage_transport:'Observed passage transport'};
  const kinds = {named_current:'Current',named_eddy:'Named eddy',operational_eddy_detection:'Dated detection'};
  const key = 'osw-motion-dashboard-seen-v2';
  const groupLabels = {identity:'Identity',sources:'Sources',claims:'Claims / reviews',measurements:'Measurements',routes_geometry:'Routes / geometry',media:'Media links',time_evidence:'Time evidence'};
  let data, baseline, busy = false, interval, client, renderGeneration=0;
  function rustClient() {
    const worker=new Worker('query-worker.js?v=5');
    let sequence=0;const pending=new Map();
    const rejectAll=message=>{for(const item of pending.values()){clearTimeout(item.timer);item.reject(Error(message));}pending.clear();};
    worker.onerror=()=>rejectAll('Rust dashboard worker failed');
    worker.onmessage=event=>{const {id,result}=event.data,item=pending.get(id);if(!item)return;clearTimeout(item.timer);pending.delete(id);result.ok?item.resolve(result):item.reject(Error(result.error));};
    return {
      request(action,value){return new Promise((resolve,reject)=>{const id=++sequence,timer=setTimeout(()=>{pending.delete(id);reject(Error('Rust dashboard request timed out'));},90000);pending.set(id,{resolve,reject,timer});worker.postMessage({id,action,value});});},
      close(){rejectAll('Dashboard snapshot replaced');worker.terminate();}
    };
  }
  let selectedIds = [], selectedNote = '';
  const ns='http://www.w3.org/2000/svg';
  const regions={world:[60,90,1480,740],atlantic:[390,100,580,680],pacific:[1070,180,470,580],'pacific-east':[60,180,530,580],indian:[960,230,400,540],gulf:[370,315,120,95],mediterranean:[800,255,190,110],arctic:[630,100,410,235]};
  const svgElement=(tag,attrs,parent)=>{const el=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);parent.append(el);return el;};
  try { baseline = JSON.parse(localStorage.getItem(key)); } catch (_) { baseline = null; }
  if (!baseline || typeof baseline !== 'object' || Array.isArray(baseline)) baseline = null;
  const element = (tag,text,parent) => { const el=document.createElement(tag); if(text!=null) el.textContent=text; if(parent) parent.append(el); return el; };
  const link = (label,url,parent) => { const a=element('a',label,parent); a.href=url; };
  const atlasUrl = row => ['dated_diagnostics','flow_network','passage_transport'].includes($('dashboard-metric').value)&&row.evidence_links?.length ? row.evidence_links[0].url : `reference-routes.html?atlas-feature=${encodeURIComponent(row.id)}#route-atlas`;
  const changed = row => baseline && baseline[row.id]?.fingerprint !== row.fingerprint;
  function markSeen() {
    baseline = Object.fromEntries(data.entries.map(r => [r.id,{fingerprint:r.fingerprint,sections:r.section_fingerprints}]));
    try { localStorage.setItem(key,JSON.stringify(baseline)); } catch (_) { /* Session baseline remains usable. */ }
  }
  function selectMapRows(rows, note) {
    selectedIds=rows.map(r=>r.id);
    selectedNote=note;
    const panel=$('dashboard-schematic').hidden?$('dashboard-map-detail'):$('dashboard-schematic-detail');panel.hidden=false;panel.replaceChildren();
    if(panel.id==='dashboard-schematic-detail'){const close=element('button','Close',panel);close.addEventListener('click',()=>{panel.hidden=true;selectedIds=[];});}
    element('h3',rows.length===1?rows[0].label:`${rows.length} names at this gateway`,panel);
    element('p',note,panel).className='map-scope';
    const metric=$('dashboard-metric').value;
    for(const row of rows){const item=element('div',null,panel);item.className='map-selected-record';link(row.label,atlasUrl(row),element('h4',null,item));element('p',`${kinds[row.type]} · ${row.capabilities[metric]?`${row.capabilities[metric]} ${labels[metric].toLowerCase()} records`:'Selected evidence not recorded'}${changed(row)?' · Updated':''}`,item);link('Explore atlas',atlasUrl(row),item);link('Object record',row.object_url,item);if(row.route_url)link('Explore route',row.route_url,item);if(row.season_url)link('Seasons',row.season_url,item);for(const series of row.series)link(series.label,series.url,item);for(const evidence of row.evidence_links||[])link(evidence.label,evidence.url,item);for(const note of row.scope_notes||[]){element('p',note.summary,item);link(note.label,note.source_url,item);}}
  }
  function renderSchematic(visible,metric,scene) {
    const panels=$('dashboard-schematic-panels');panels.replaceChildren();
    const currents=visible.filter(r=>r.type==='named_current'),eddies=visible.filter(r=>r.type!=='named_current');
    $('dashboard-schematic-summary').textContent=`${currents.length} named current stations · ${eddies.length} eddy records · ${visible.filter(r=>r.capabilities[metric]>0).length} objects with selected evidence. Every filtered current is labeled below.`;
    const interactive=(el,rows,note)=>{el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',rows.length===1?rows[0].label:`${rows.length} eddy records in ${rows[0].basin}`);el.addEventListener('click',()=>selectMapRows(rows,note));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectMapRows(rows,note);}});};
    const world=$('dashboard-beck-features');world.replaceChildren();const box=regions[$('dashboard-region').value];$('dashboard-beck-map').setAttribute('viewBox',box.join(' '));
    const size=scene.size,byId=new Map(visible.map(row=>[row.id,row]));
    const connectionLayer=svgElement('g',{},world),routeLayer=svgElement('g',{},world),eddyLayer=svgElement('g',{},world),stationLayer=svgElement('g',{},world);
    $('dashboard-show-all').textContent=`Show all ${scene.total_currents} currents`;
    for(const route of scene.routes){const row=byId.get(route.id);const line=svgElement('path',{d:route.d,stroke:route.color,'stroke-width':3,fill:'none','stroke-linejoin':'round','vector-effect':'non-scaling-stroke',class:'beck-line'},routeLayer);interactive(line,[row],route.note);svgElement('title',{},line).textContent=row.label+' — editorial route, schematic geometry';}
    for(const item of scene.stations){const row=byId.get(item.id),x=item.x,y=item.y;
      const station=svgElement('g',{class:`beck-station${item.covered?' lit':''}${item.updated?' updated':''}`,'data-current-id':row.id,'data-station-number':item.number,'data-world-x':x,'data-world-y':y,transform:`translate(${x} ${y})`},stationLayer);
      svgElement('circle',{r:size*12,class:'station-core','vector-effect':'non-scaling-stroke'},station);
      svgElement('text',{'text-anchor':'middle',y:4*size,'font-size':11*size,class:'station-number','aria-hidden':'true'},station).textContent=item.number;
      if(item.leader_d)svgElement('path',{d:item.leader_d,class:'beck-label-leader',stroke:'#79929e','stroke-width':.7,'vector-effect':'non-scaling-stroke',fill:'none','pointer-events':'none'},station);
      svgElement('text',{x:item.label_x,y:item.label_y,'font-size':18*size,class:'beck-name'},station).textContent=row.label;
      svgElement('title',{},station).textContent=row.label;interactive(station,[row],item.note);
    }
    $('dashboard-station-count').textContent=`${scene.in_view} / ${scene.total_currents} current stations in view · ${scene.routed_currents} filtered currents with reference paths`;
    for(const item of scene.connections){const connection=data.connections.find(c=>c.id===item.id),rows=currents.filter(row=>[connection.subject_id,connection.object_id].includes(row.id));
      const line=svgElement('path',{d:item.d,class:'beck-connection','data-connection-id':connection.id},connectionLayer);svgElement('title',{},line).textContent=connection.scope;line.setAttribute('role','button');line.setAttribute('tabindex','0');line.setAttribute('aria-label',connection.scope);
      const select=()=>{selectMapRows(rows,`${connection.predicate.replaceAll("_"," ")}. ${connection.scope} ${connection.vertical_scope} ${connection.time_scope} The dashed line connects diagram identities; no measured junction, transport or footprint is claimed.`);const panel=$('dashboard-schematic-detail');link('Read the source',connection.source_url,panel);element('p',`Source location: ${connection.source_locator}`,panel);};line.addEventListener('click',select);line.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});
    }
    for(const item of scene.eddy_gateways){const rows=item.ids.map(id=>byId.get(id)),r=8*size;
      const gateway=svgElement('g',{transform:`translate(${item.x} ${item.y})`,class:'beck-eddy-gateway'},eddyLayer);svgElement('path',{d:`M0,${-r}L${r},0L0,${r}L${-r},0Z`,fill:item.covered?'#54e5c5':'#102b36',stroke:item.updated?'#ffc663':'#f0c486','stroke-width':2,'vector-effect':'non-scaling-stroke'},gateway);svgElement('text',{x:12*size,y:5*size,'font-size':10*size,class:'beck-name'},gateway).textContent=`${rows.length} eddy records`;svgElement('title',{},gateway).textContent=item.basin;
      interactive(gateway,rows,`${item.basin}: regional inventory gateway displaced for schematic readability. This symbol is not any eddy center, footprint or connection to a current.`);
    }
    for(const group of scene.panels){const name=group.name,rows=group.rows.map(item=>byId.get(item.id));const panel=element('section',null,panels);panel.className='schematic-panel';element('h3',`${name} · ${rows.length}`,panel);const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 540 ${group.height}`);svg.setAttribute('aria-label',name+' current stations');panel.append(svg);
      const color=group.color;group.rows.forEach(item=>{const row=byId.get(item.id),y=item.y,station=svgElement('g',{class:`schematic-station${row.capabilities[metric]>0?' lit':''}${changed(row)?' updated':''}`,'data-current-id':row.id},svg);
        svgElement('rect',{x:8,y:y-17,width:522,height:34,fill:'transparent'},station);
        svgElement('path',{d:item.track_d,stroke:color,'stroke-width':5,fill:'none','stroke-linejoin':'round'},station);
        svgElement('circle',{cx:88,cy:y,r:7,class:'station-core'},station);
        svgElement('text',{x:106,y:y+5,'font-size':14,fill:'#e4f5f5'},station).textContent=`${item.number}. ${row.label}`;
        interactive(station,[row],`Schematic identity station in ${name}; no connection to neighboring tracks is asserted. Basin: ${row.basin}.`);
      });
    }
    if(eddies.length){const panel=element('section',null,panels);panel.className='schematic-panel eddy-panel';element('h3',`Eddy regional groups · ${eddies.length} records`,panel);for(const group of scene.eddy_groups){const basin=group.basin,rows=group.ids.map(id=>byId.get(id));const button=element('button',null,panel);button.className='schematic-eddy-group';const covered=group.covered_count;element('span','◇',button).className=covered?'eddy-symbol lit':'eddy-symbol';element('span',`${basin} · ${rows.length} ${rows.length===1?'record':'records'} · ${covered} with evidence${rows.some(changed)?' · Updated':''}`,button);button.addEventListener('click',()=>selectMapRows(rows,`Regional inventory group: ${covered} of ${rows.length} records have selected evidence. This diagram asserts no individual positions, footprints or current–eddy connection.`));}}
  }
  function renderMap(visible,metric,scene) {
    const root=$('dashboard-map-features');root.replaceChildren();
    const box=regions[$('dashboard-region').value];$('dashboard-map').setAttribute('viewBox',box.join(' '));
    const layer=svgElement('g',{transform:scene.display_transform},root),radius=box[2]/1480*7;
    const byId=new Map(visible.map(row=>[row.id,row]));
    const activate=(el,rows,note)=>{el.setAttribute('tabindex','0');el.setAttribute('role','button');const title=`${rows.length===1?rows[0].label:`${rows.length} names: ${rows.slice(0,3).map(r=>r.label).join(', ')}…`} — ${rows.filter(r=>r.capabilities[metric]>0).length} with selected evidence`;el.setAttribute('aria-label',title);svgElement('title',{},el).textContent=title;el.addEventListener('click',()=>selectMapRows(rows,note));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectMapRows(rows,note);}});};
    for(const feature of scene.features){
      const rows=feature.entity_ids.map(id=>byId.get(id));
      if(rows.some(row=>!row))throw Error('Map refers to an object outside the selected records');
      const primitive=feature.primitive,covered=feature.covered_count,classes=`${covered?' lit':''}${feature.updated?' updated':''}`;
      if(feature.kind==='path'){
        const path=svgElement('path',{d:primitive.d,class:'atlas-route'+classes},layer);activate(path,rows,feature.note);continue;
      }
      const mark=svgElement('g',{class:'atlas-marker'+classes,transform:`translate(${feature.display_x} ${feature.display_y})`},root);
      svgElement('circle',{r:radius*1.8,class:'marker-hit'},mark);
      if(feature.group)svgElement('path',{d:`M0,${-radius*1.5}L${radius*1.5},0L0,${radius*1.5}L${-radius*1.5},0Z`,class:'marker-core'},mark);else svgElement('circle',{r:radius,class:'marker-core'},mark);
      if(feature.group)svgElement('text',{x:radius*2.3,y:radius*.5,'font-size':radius*2,class:'marker-label'},mark).textContent=`${covered}/${rows.length}`;
      activate(mark,rows,`${feature.group?`${feature.group}: ${covered} of ${rows.length} filtered names have selected evidence. `:''}${feature.note}`);
    }
    $('dashboard-map-summary').textContent=`${scene.mapped_objects} of ${visible.length} filtered objects have map evidence or a regional gateway; ${scene.unmapped_objects} have no map placement. Regional views crop the world map; all filtered records remain available in Record cards.${scene.omitted_features.length?` ${scene.omitted_features.length} source geometries could not be drawn.`:''}`;
    const selection=visible.filter(r=>selectedIds.includes(r.id));if(selection.length)selectMapRows(selection,selectedNote);else if(selectedIds.length){selectedIds=[];$('dashboard-map-detail').replaceChildren();element('p','The selected records are outside these filters. Select another light.', $('dashboard-map-detail'));}
  }
  async function render() {
    const generation=++renderGeneration,active=client,metric=$('dashboard-metric').value,type=$('dashboard-type').value;
    const request={text:$('dashboard-search').value,metric,covered_only:$('dashboard-covered').checked,changed_only:$('dashboard-changed').checked,changed_ids:data.entries.filter(changed).map(r=>r.id),view_box:regions[$('dashboard-region').value]};
    if(type!=='all')request.record_type=type;
    $('dashboard-status').dataset.pending='true';
    try {
    const selection=await active.request('dashboard_select',request);
    if(generation!==renderGeneration||active!==client)return;
    const ids=new Set(selection.ids),visible=data.entries.filter(r=>ids.has(r.id)),updates=selection.changed_count;
    window.oswDashboardSelection={request,result:selection};
    const grid=$('dashboard-grid');grid.replaceChildren();
    for(const row of visible) {
      const has=row.capabilities[metric]>0, card=element('article',null,grid);card.className=`motion-card${has?' lit':''}${changed(row)?' updated':''}`;card.dataset.id=row.id;
      element('span',kinds[row.type],card).className='object-kind';
      if(changed(row)) element('span',' · Updated',card).className='change-key';
      link(row.label,atlasUrl(row),element('h3',null,card));element('p',row.basin,card);
      if(changed(row)) {
        const previous=baseline[row.id];
        const groups=Object.keys(groupLabels).filter(k=>previous?.sections?.[k]!==row.section_fingerprints[k]);
        element('p',previous ? `${groups.length?groups.map(k=>groupLabels[k]).join(', '):'Record content'} changed` : 'New inventory record',card).className='change-reason';
      }
      const selected=element('p',null,card);selected.className='selected-evidence';const dot=element('span',null,selected);dot.className=`signal${has?' on':''}`;dot.setAttribute('aria-hidden','true');element('span',`${labels[metric]}: ${has?`${row.capabilities[metric]} record${row.capabilities[metric]===1?'':'s'}`:'not recorded'}`,selected);
      link('Explore atlas',atlasUrl(row),card);
      const metadata=element('details',null,card);element('summary','Evidence, sources & links',metadata);
      link('Object record',row.object_url,metadata);
      const list=element('ul',null,metadata);for(const [field,label] of Object.entries(labels))if(row.capabilities[field])element('li',`${label}: ${row.capabilities[field]}`,list);
      element('p',`${row.recorded_claims.toLocaleString()} recorded claims · ${row.nasa_links} NASA links`,metadata);
      element('p',`Latest dated evidence: ${row.latest_observation_date || 'exact observation date not recorded'}`,metadata);
      element('p',`${row.linked_source_count} linked release sources. Candidate sources are available through route and series links.`,metadata);
      for(const [status,count] of Object.entries(row.claim_review_counts))element('p',`${count.toLocaleString()} claims: ${status.replaceAll('_',' ')}`,metadata);
      const links=element('p',null,metadata);links.className='record-links';if(row.route_url)link('Route',row.route_url,links);if(row.season_url)link('Seasons',row.season_url,links);for(const series of row.series)link(series.label,series.url,links);
      for(const evidence of row.evidence_links||[])link(evidence.label,evidence.url,links);
      for(const connection of row.connections||[])link('Current-link source',connection.source_url,links);
      for(const note of row.scope_notes||[]){element('p',note.summary,metadata);link(note.label,note.source_url,links);}
    }
    $('dashboard-empty').hidden=visible.length!==0;
    $('dashboard-status').textContent=`${visible.length} of ${selection.total} objects shown · ${selection.covered_count} with ${labels[metric].toLowerCase()} · ${updates} changed since marked seen`;
    $('dashboard-seen').disabled=updates===0;
    renderMap(visible,metric,selection.map_scene);
    renderSchematic(visible,metric,selection.beck_scene);
    } catch(error) {if(generation===renderGeneration&&active===client)$('dashboard-status').textContent=`Selection failed: ${error.message}. The previous selection remains visible.`;}
    finally {if(generation===renderGeneration)$('dashboard-status').dataset.pending='false';}
  }
  async function refresh() {
    if(busy)return;busy=true;$('dashboard-refresh').disabled=true;
    let candidate;
    try {
      candidate=rustClient();await candidate.request('load');
      const loaded=await candidate.request('dashboard'),next=JSON.parse(loaded.snapshot_json);
      if(next.schema!=='osw.motion-dashboard.v1'||next.fingerprint_version!==2||!Array.isArray(next.entries)||!next.counts||new Set(next.entries.map(r=>r.id)).size!==next.entries.length||next.entries.some(r=>!kinds[r.type]||typeof r.label!=='string'||typeof r.fingerprint!=='string'||!r.section_fingerprints||Object.keys(groupLabels).some(k=>typeof r.section_fingerprints[k]!=='string')||!r.claim_review_counts||!Number.isInteger(r.linked_source_count)||!r.capabilities||Object.keys(labels).some(k=>!Number.isInteger(r.capabilities[k])||r.capabilities[k]<0)||!Array.isArray(r.series)||!Array.isArray(r.scope_notes)||!Array.isArray(r.evidence_links)||r.evidence_links.some(e=>typeof e.label!=='string'||typeof e.url!=='string'))||Object.keys(kinds).some(k=>next.counts[k]!==next.entries.filter(r=>r.type===k).length))throw Error('Unsupported or incomplete coverage snapshot');
      if(next.entries.some(r=>!Array.isArray(r.map_features)))throw Error('Snapshot has no atlas location evidence');
      data=next;
      const previous=client;client=candidate;candidate=null;previous?.close();
      window.oswDashboardSnapshot={...loaded,snapshot:next};
      $('dashboard-status').dataset.engine=loaded.engine;
      const first=!baseline;if(first)markSeen();
      const totals=$('dashboard-totals');totals.replaceChildren();for(const [kind,count] of Object.entries(data.counts)){const tile=element('div',null,totals);tile.className='dashboard-total';element('strong',count,tile);element('span',kind==='named_current'?'Currents':kind==='named_eddy'?'Named eddies':'Dated detections',tile);}
      $('dashboard-update-note').textContent=`Coverage snapshot built ${data.built_at_utc}. ${first?'First visit establishes your comparison snapshot. ':''}Update indicators compare record contents with your last marked snapshot. Checking reloads available data; it does not acquire new provider observations.`;
      const proposals=$('dashboard-proposals');proposals.replaceChildren();link(`${data.proposed_current_additions} additional current names await inventory review`,'reference-routes.html#inventory-addition-cards',proposals);
      await render();
    } catch(error) { $('dashboard-status').textContent=`Update check failed: ${error.message}.${data?' Showing the previously loaded snapshot.':''}`; }
    finally {candidate?.close();busy=false;$('dashboard-refresh').disabled=false;}
  }
  for(const id of ['dashboard-search','dashboard-type','dashboard-metric','dashboard-covered','dashboard-changed'])$(id).addEventListener(id==='dashboard-search'?'input':'change',()=>{if(data)render();});
  $('dashboard-refresh').addEventListener('click',refresh);$('dashboard-seen').addEventListener('click',()=>{if(data){markSeen();render();}});
  $('dashboard-auto').addEventListener('change',()=>{clearInterval(interval);if($('dashboard-auto').checked)interval=setInterval(()=>{if(!document.hidden)refresh();},60000);});
  const switchView=view=>{$('dashboard-atlas').hidden=view!=='map';$('dashboard-grid').hidden=view!=='cards';$('dashboard-schematic').hidden=view!=='schematic';$('dashboard-schematic-detail').hidden=true;for(const [id,name]of [['dashboard-map-view','map'],['dashboard-card-view','cards'],['dashboard-schematic-view','schematic']])$(id).setAttribute('aria-pressed',String(view===name));$('dashboard-region').disabled=view==='cards';};
  $('dashboard-map-view').addEventListener('click',()=>switchView('map'));$('dashboard-card-view').addEventListener('click',()=>switchView('cards'));$('dashboard-schematic-view').addEventListener('click',()=>switchView('schematic'));$('dashboard-region').addEventListener('change',()=>{if(data)render();});
  $('dashboard-show-all').addEventListener('click',()=>{
    $('dashboard-search').value='';$('dashboard-type').value='all';$('dashboard-covered').checked=false;$('dashboard-changed').checked=false;$('dashboard-region').value='world';
    switchView('schematic');if(data)render();
  });
  switchView('schematic');
  refresh();
})();
