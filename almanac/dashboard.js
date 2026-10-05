(() => {
  const $ = id => document.getElementById(id);
  const labels = {reported_length:'Published ranked length',reference_route:'Editorial reference route',scoped_width:'Scoped width evidence',geometry:'Geometry beyond a locator',time_samples:'Time samples / phase records',source_connectivity:'Source-described current links',scope_notes:'Source scope notes',dated_diagnostics:'Dated method diagnostics',flow_network:'Passage networks',passage_transport:'Observed passage transport'};
  const kinds = {named_current:'Current',named_eddy:'Named eddy',operational_eddy_detection:'Dated detection'};
  const key = 'osw-motion-dashboard-seen-v2';
  const groupLabels = {identity:'Identity',sources:'Sources',claims:'Claims / reviews',measurements:'Measurements',routes_geometry:'Routes / geometry',media:'Media links',time_evidence:'Time evidence'};
  let data, baseline, busy = false, interval;
  let selectedIds = [], selectedNote = '';
  const ns='http://www.w3.org/2000/svg';
  const regions={world:[60,90,1480,740],atlantic:[390,100,580,680],pacific:[1070,180,470,580],'pacific-east':[60,180,530,580],indian:[960,230,400,540],gulf:[370,315,120,95],mediterranean:[800,255,190,110],arctic:[630,100,410,235]};
  const project=([lon,lat])=>[60+(lon+180)/360*1480,90+(90-lat)/180*740];
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
  function renderSchematic(visible,metric) {
    const panels=$('dashboard-schematic-panels');panels.replaceChildren();
    const currents=visible.filter(r=>r.type==='named_current'),eddies=visible.filter(r=>r.type!=='named_current');
    $('dashboard-schematic-summary').textContent=`${currents.length} named current stations · ${eddies.length} eddy records · ${visible.filter(r=>r.capabilities[metric]>0).length} objects with selected evidence. Every filtered current is labeled below.`;
    const groups=new Map();
    const groupFor=row=>{const b=row.basin.toLowerCase();return /mediterranean|adriatic|aegean|black sea/.test(b)?'Mediterranean and neighboring seas':/southern|antarctic/.test(b)?'Southern Ocean':/indian|arabian|bengal|oman/.test(b)?'Indian Ocean':/pacific|china|japan|tasman|austral|new guinea/.test(b)?'Pacific and connected seas':/atlantic|greenland|gulf of mexico|caribbean|baffin|labrador|norwegian|arctic/.test(b)?'Atlantic and Arctic':'Other and multiple basins';};
    for(const row of currents){const group=groupFor(row);if(!groups.has(group))groups.set(group,[]);groups.get(group).push(row);}
    const colors=['#ec657a','#51c8db','#f0bc4e','#b897f0','#65dcb3','#f19855'];let groupIndex=0;
    const interactive=(el,rows,note)=>{el.setAttribute('tabindex','0');el.setAttribute('role','button');el.setAttribute('aria-label',rows.length===1?rows[0].label:`${rows.length} eddy records in ${rows[0].basin}`);el.addEventListener('click',()=>selectMapRows(rows,note));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectMapRows(rows,note);}});};
    const world=$('dashboard-beck-features');world.replaceChildren();const box=regions[$('dashboard-region').value];$('dashboard-beck-map').setAttribute('viewBox',box.join(' '));
    const snap=coordinate=>project(coordinate).map(v=>Math.round(v/8)*8),size=box[2]/1480,stationPositions=new Map(),placed=[];
    const stationNumbers=new Map(data.entries.filter(row=>row.type==='named_current').map((row,i)=>[row.id,i+1]));
    const separateStation=point=>{const origin=point.map((v,i)=>Math.max(i?104:74,Math.min(v,i?816:1526)));for(let ring=0;ring<40;ring++){const candidates=[];for(let dx=-ring;dx<=ring;dx++)for(let dy=-ring;dy<=ring;dy++)if(Math.max(Math.abs(dx),Math.abs(dy))===ring)candidates.push([origin[0]+dx*16,origin[1]+dy*16]);candidates.sort((a,b)=>Math.hypot(a[0]-origin[0],a[1]-origin[1])-Math.hypot(b[0]-origin[0],b[1]-origin[1]));for(const p of candidates)if(p[0]>=74&&p[0]<=1526&&p[1]>=104&&p[1]<=816&&!placed.some(q=>Math.hypot(p[0]-q[0],p[1]-q[1])<30)){placed.push(p);return p;}}throw Error('Unable to separate current stations');};
    const connectionLayer=svgElement('g',{},world);
    const routeLayer=svgElement('g',{},world),eddyLayer=svgElement('g',{},world),stationLayer=svgElement('g',{},world);
    const totalCurrents=data.entries.filter(row=>row.type==='named_current').length;
    $('dashboard-show-all').textContent=`Show all ${totalCurrents} currents`;
    const labelPosition=(x,y,label)=>[Math.max(box[0]+3*size,Math.min(x+10*size,box[0]+box[2]-label.length*10*size-3*size)),Math.max(box[1]+20*size,Math.min(y-10*size,box[1]+box[3]-5*size))];
    currents.forEach((row,i)=>{
      const color=colors[i%colors.length],route=row.map_features.find(f=>f.role==='editorial_reference_route');
      if(route){let previous;const commands=[];for(const coordinate of route.geometry.coordinates){const p=snap(coordinate);if(!previous||Math.abs(p[0]-previous[0])>740)commands.push(`M${p}`);else{const dx=p[0]-previous[0],dy=p[1]-previous[1],diagonal=Math.min(Math.abs(dx),Math.abs(dy));commands.push(`L${previous[0]+Math.sign(dx)*diagonal},${previous[1]+Math.sign(dy)*diagonal}L${p}`);}previous=p;}
        const line=svgElement('path',{d:commands.join(' '),stroke:color,'stroke-width':3,fill:'none','stroke-linejoin':'round','vector-effect':'non-scaling-stroke',class:'beck-line'},routeLayer);interactive(line,[row],`Octilinear simplification of an editorial route. ${route.note}`);svgElement('title',{},line).textContent=row.label+' — editorial route, schematic geometry';}
      const point=route?route.geometry.coordinates[Math.floor(route.geometry.coordinates.length/2)]:row.map_features.find(f=>f.geometry.type==='Point')?.geometry.coordinates;if(!point)return;
      const [x,y]=separateStation(snap(point));
      stationPositions.set(row.id,[x,y]);
      const station=svgElement('g',{class:`beck-station${row.capabilities[metric]>0?' lit':''}${changed(row)?' updated':''}`,'data-current-id':row.id,'data-station-number':stationNumbers.get(row.id),'data-world-x':x,'data-world-y':y,transform:`translate(${x} ${y})`},stationLayer);
      svgElement('circle',{r:size*12,class:'station-core','vector-effect':'non-scaling-stroke'},station);
      svgElement('text',{'text-anchor':'middle',y:4*size,'font-size':11*size,class:'station-number','aria-hidden':'true'},station).textContent=stationNumbers.get(row.id);
      const [labelX,labelY]=labelPosition(x,y,row.label);
      if(Math.abs(labelY-y)>23*size)svgElement('path',{d:`M0,0L${labelX-x},${labelY-y-3*size}`,class:'beck-label-leader',stroke:'#79929e','stroke-width':.7,'vector-effect':'non-scaling-stroke',fill:'none','pointer-events':'none'},station);
      svgElement('text',{x:labelX-x,y:labelY-y,'font-size':18*size,class:'beck-name'},station).textContent=row.label;
      svgElement('title',{},station).textContent=row.label;
      interactive(station,[row],`Schematic station for ${row.label}. ${route?'Placed along an editorial reference route.':'Only a name locator is available; no route is drawn.'} Diagram placement is not an observed core, endpoint or intersection.`);
    });
    const inView=[...stationPositions.values()].filter(([x,y])=>x>=box[0]&&x<=box[0]+box[2]&&y>=box[1]&&y<=box[1]+box[3]).length;
    const routed=currents.filter(row=>row.map_features.some(f=>f.role==='editorial_reference_route')).length;
    $('dashboard-station-count').textContent=`${inView} / ${totalCurrents} current stations in view · ${routed} filtered currents with reference paths`;
    for(const connection of data.connections||[]){const a=stationPositions.get(connection.subject_id),b=stationPositions.get(connection.object_id);if(!a||!b)continue;const rows=currents.filter(row=>[connection.subject_id,connection.object_id].includes(row.id));let d;
      if(Math.abs(a[0]-b[0])>740){const right=a[0]>b[0]?a:b,left=a[0]>b[0]?b:a;d=`M${right}H1540M60,${left[1]}H${left[0]}`;}else{const dx=b[0]-a[0],dy=b[1]-a[1],diagonal=Math.min(Math.abs(dx),Math.abs(dy));d=`M${a}L${a[0]+Math.sign(dx)*diagonal},${a[1]+Math.sign(dy)*diagonal}L${b}`;}
      const line=svgElement('path',{d,class:'beck-connection','data-connection-id':connection.id},connectionLayer);svgElement('title',{},line).textContent=connection.scope;line.setAttribute('role','button');line.setAttribute('tabindex','0');line.setAttribute('aria-label',connection.scope);
      const select=()=>{selectMapRows(rows,`${connection.predicate.replaceAll("_"," ")}. ${connection.scope} ${connection.vertical_scope} ${connection.time_scope} The dashed line connects diagram identities; no measured junction, transport or footprint is claimed.`);const panel=$('dashboard-schematic-detail');link('Read the source',connection.source_url,panel);element('p',`Source location: ${connection.source_locator}`,panel);};line.addEventListener('click',select);line.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select();}});
    }
    const eddyBasins=new Map();for(const row of eddies){if(!eddyBasins.has(row.basin))eddyBasins.set(row.basin,[]);eddyBasins.get(row.basin).push(row);}
    for(const [basin,rows]of eddyBasins){const features=rows.flatMap(r=>r.map_features),point=features.find(f=>f.geometry.type==='Point');const outline=features.find(f=>f.geometry.type==='Polygon');const coordinate=point?.geometry.coordinates||outline?.geometry.coordinates[0][0];if(!coordinate)continue;const [x,y]=snap(coordinate),r=8*size;
      const gateway=svgElement('g',{transform:`translate(${x+12*size} ${y+16*size})`,class:'beck-eddy-gateway'},eddyLayer);svgElement('path',{d:`M0,${-r}L${r},0L0,${r}L${-r},0Z`,fill:rows.some(row=>row.capabilities[metric]>0)?'#54e5c5':'#102b36',stroke:rows.some(changed)?'#ffc663':'#f0c486','stroke-width':2,'vector-effect':'non-scaling-stroke'},gateway);svgElement('text',{x:12*size,y:5*size,'font-size':10*size,class:'beck-name'},gateway).textContent=`${rows.length} eddy records`;svgElement('title',{},gateway).textContent=basin;
      interactive(gateway,rows,`${basin}: regional inventory gateway displaced for schematic readability. This symbol is not any eddy center, footprint or connection to a current.`);
    }
    for(const [name,rows]of groups){const panel=element('section',null,panels);panel.className='schematic-panel';element('h3',`${name} · ${rows.length}`,panel);const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 540 ${rows.length*38+18}`);svg.setAttribute('aria-label',name+' current stations');panel.append(svg);
      const color=colors[groupIndex++%colors.length];rows.forEach((row,i)=>{const y=i*38+24,station=svgElement('g',{class:`schematic-station${row.capabilities[metric]>0?' lit':''}${changed(row)?' updated':''}`,'data-current-id':row.id},svg);
        svgElement('rect',{x:8,y:y-17,width:522,height:34,fill:'transparent'},station);
        svgElement('path',{d:`M16,${y+9}H40L49,${y}H88`,stroke:color,'stroke-width':5,fill:'none','stroke-linejoin':'round'},station);
        svgElement('circle',{cx:88,cy:y,r:7,class:'station-core'},station);
        svgElement('text',{x:106,y:y+5,'font-size':14,fill:'#e4f5f5'},station).textContent=`${stationNumbers.get(row.id)}. ${row.label}`;
        interactive(station,[row],`Schematic identity station in ${name}; no connection to neighboring tracks is asserted. Basin: ${row.basin}.`);
      });
    }
    if(eddies.length){const panel=element('section',null,panels);panel.className='schematic-panel eddy-panel';element('h3',`Eddy regional groups · ${eddies.length} records`,panel);const basins=new Map();for(const row of eddies){if(!basins.has(row.basin))basins.set(row.basin,[]);basins.get(row.basin).push(row);}for(const [basin,rows]of basins){const button=element('button',null,panel);button.className='schematic-eddy-group';const covered=rows.filter(r=>r.capabilities[metric]>0).length;element('span','◇',button).className=covered?'eddy-symbol lit':'eddy-symbol';element('span',`${basin} · ${rows.length} ${rows.length===1?'record':'records'} · ${covered} with evidence${rows.some(changed)?' · Updated':''}`,button);button.addEventListener('click',()=>selectMapRows(rows,`Regional inventory group: ${covered} of ${rows.length} records have selected evidence. This diagram asserts no individual positions, footprints or current–eddy connection.`));}}
  }
  function renderMap(visible,metric) {
    const layer=$('dashboard-map-features');layer.replaceChildren();
    const box=regions[$('dashboard-region').value];$('dashboard-map').setAttribute('viewBox',box.join(' '));
    const radius=box[2]/1480*7, points=new Map();let placed=0;
    const activate=(el,rows,note)=>{el.setAttribute('tabindex','0');el.setAttribute('role','button');const title=`${rows.length===1?rows[0].label:`${rows.length} names: ${rows.slice(0,3).map(r=>r.label).join(', ')}…`} — ${rows.filter(r=>r.capabilities[metric]>0).length} with selected evidence`;el.setAttribute('aria-label',title);svgElement('title',{},el).textContent=title;el.addEventListener('click',()=>selectMapRows(rows,note));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectMapRows(rows,note);}});};
    for(const row of visible){if(row.map_features?.length)placed++;
      for(const feature of row.map_features||[]){const g=feature.geometry;
        if(g.type==='Point'){const k=feature.group||`${row.id}:${g.coordinates.join(',')}`;if(!points.has(k))points.set(k,{coordinate:g.coordinates,rows:[],note:feature.note,group:feature.group});const point=points.get(k);if(!point.rows.includes(row))point.rows.push(row);continue;}
        const lines=g.type==='LineString'?[g.coordinates]:g.type==='Polygon'?g.coordinates:[];
        for(const line of lines){let previous;const commands=[];for(const coordinate of line){const p=project(coordinate);commands.push(`${!previous||Math.abs(p[0]-previous[0])>740?'M':'L'}${p.join(',')}`);previous=p;}
          const path=svgElement('path',{d:commands.join(' '),class:`atlas-route${row.capabilities[metric]>0?' lit':''}${changed(row)?' updated':''}`},layer);activate(path,[row],`${feature.role.replaceAll('_',' ')}. ${feature.note}`);}
      }
    }
    for(const point of points.values()){const [x,y]=project(point.coordinate),covered=point.rows.filter(r=>r.capabilities[metric]>0).length,updated=point.rows.some(changed);
      const mark=svgElement('g',{class:`atlas-marker${covered?' lit':''}${updated?' updated':''}`,transform:`translate(${x} ${y})`},layer);
      svgElement('circle',{r:radius*1.8,class:'marker-hit'},mark);
      if(point.group)svgElement('path',{d:`M0,${-radius*1.5}L${radius*1.5},0L0,${radius*1.5}L${-radius*1.5},0Z`,class:'marker-core'},mark);else svgElement('circle',{r:radius,class:'marker-core'},mark);
      if(point.group){svgElement('text',{x:radius*2.3,y:radius*.5,'font-size':radius*2,class:'marker-label'},mark).textContent=`${covered}/${point.rows.length}`;}
      activate(mark,point.rows,`${point.group?`${point.group}: ${covered} of ${point.rows.length} filtered names have selected evidence. `:''}${point.note}`);
    }
    $('dashboard-map-summary').textContent=`${placed} of ${visible.length} filtered objects have map evidence or a regional gateway; ${visible.length-placed} have no map placement. Regional views crop the world map; all filtered records remain available in Record cards.`;
    const selection=visible.filter(r=>selectedIds.includes(r.id));if(selection.length)selectMapRows(selection,selectedNote);else if(selectedIds.length){selectedIds=[];$('dashboard-map-detail').replaceChildren();element('p','The selected records are outside these filters. Select another light.', $('dashboard-map-detail'));}
  }
  function render() {
    const metric=$('dashboard-metric').value, query=$('dashboard-search').value.trim().toLocaleLowerCase(), type=$('dashboard-type').value;
    const updates=data.entries.filter(changed).length;
    const visible=data.entries.filter(r => (type==='all'||r.type===type) && `${r.label} ${r.basin}`.toLocaleLowerCase().includes(query) && (!$('dashboard-covered').checked||r.capabilities[metric]>0) && (!$('dashboard-changed').checked||changed(r)));
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
    $('dashboard-status').textContent=`${visible.length} of ${data.entries.length} objects shown · ${data.entries.filter(r=>r.capabilities[metric]>0).length} with ${labels[metric].toLowerCase()} · ${updates} changed since marked seen`;
    $('dashboard-seen').disabled=updates===0;
    renderMap(visible,metric);
    renderSchematic(visible,metric);
  }
  async function refresh() {
    if(busy)return;busy=true;$('dashboard-refresh').disabled=true;
    try {
      const response=await fetch('../research/ocean-motion-dashboard.json',{cache:'no-store'});if(!response.ok)throw Error(`HTTP ${response.status}`);
      const next=await response.json();
      if(next.schema!=='osw.motion-dashboard.v1'||next.fingerprint_version!==2||!Array.isArray(next.entries)||!next.counts||new Set(next.entries.map(r=>r.id)).size!==next.entries.length||next.entries.some(r=>!kinds[r.type]||typeof r.label!=='string'||typeof r.fingerprint!=='string'||!r.section_fingerprints||Object.keys(groupLabels).some(k=>typeof r.section_fingerprints[k]!=='string')||!r.claim_review_counts||!Number.isInteger(r.linked_source_count)||!r.capabilities||Object.keys(labels).some(k=>!Number.isInteger(r.capabilities[k])||r.capabilities[k]<0)||!Array.isArray(r.series)||!Array.isArray(r.scope_notes)||!Array.isArray(r.evidence_links)||r.evidence_links.some(e=>typeof e.label!=='string'||typeof e.url!=='string'))||Object.keys(kinds).some(k=>next.counts[k]!==next.entries.filter(r=>r.type===k).length))throw Error('Unsupported or incomplete coverage snapshot');
      if(next.entries.some(r=>!Array.isArray(r.map_features)))throw Error('Snapshot has no atlas location evidence');
      data=next;
      const first=!baseline;if(first)markSeen();
      const totals=$('dashboard-totals');totals.replaceChildren();for(const [kind,count] of Object.entries(data.counts)){const tile=element('div',null,totals);tile.className='dashboard-total';element('strong',count,tile);element('span',kind==='named_current'?'Currents':kind==='named_eddy'?'Named eddies':'Dated detections',tile);}
      $('dashboard-update-note').textContent=`Coverage snapshot built ${data.built_at_utc}. ${first?'First visit establishes your comparison snapshot. ':''}Update indicators compare record contents with your last marked snapshot. Checking reloads available data; it does not acquire new provider observations.`;
      const proposals=$('dashboard-proposals');proposals.replaceChildren();link(`${data.proposed_current_additions} additional current names await inventory review`,'reference-routes.html#inventory-addition-cards',proposals);
      render();
    } catch(error) { $('dashboard-status').textContent=`Update check failed: ${error.message}.${data?' Showing the previously loaded snapshot.':''}`; }
    finally {busy=false;$('dashboard-refresh').disabled=false;}
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
