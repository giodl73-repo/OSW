"use strict";
(() => {
  const $ = id => document.getElementById(id), ns = 'http://www.w3.org/2000/svg';
  const world = [60,90,1480,740], cache = new Map();
  let entries=[], byId=new Map(), selected=null, view=[...world], generation=0, drag=null;
  const node=(tag,text,parent)=>{const e=document.createElement(tag);if(text!==null)e.textContent=text;if(parent)parent.append(e);return e;};
  const human=key=>String(key).replaceAll('_',' ').replace(/\bkm2\b/g,'km²');
  const sourceURL=value=>{if(typeof value!=='string'||!value.trim())return null;try{const u=new URL(value,location.href);return ['http:','https:'].includes(u.protocol)?u.href:null;}catch{return null;}};
  async function verified(path, expected) {
    const response=await fetch(path,{cache:expected?'force-cache':'no-cache'});if(!response.ok)throw Error(`Could not load atlas record (HTTP ${response.status})`);
    const bytes=await response.arrayBuffer();if(bytes.byteLength>2400000)throw Error('Atlas record exceeds its expected size');
    if(expected){const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==expected)throw Error('Atlas record does not match this snapshot');}
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
  }
  function address(push=false) {
    const url=new URL(location.href);if(selected)url.searchParams.set('atlas-feature',selected);else url.searchParams.delete('atlas-feature');
    url.searchParams.set('atlas-view',view.map(n=>Number(n.toFixed(5))).join(','));
    (push?history.pushState:history.replaceState).call(history,null,'',url);$('share-view').href=url.href;
  }
  function setView(next,save=true) {
    const w=Math.max(8,Math.min(1480,next[2]));view=[Math.max(60,Math.min(1540-w,next[0])),Math.max(90,Math.min(830-w/2,next[1])),w,w/2];
    $('ocean-map').setAttribute('viewBox',view.join(' '));for(const p of $('ocean-features').querySelectorAll('circle'))p.setAttribute('r',w/220);if(save)address();
  }
  function zoom(factor){const w=view[2]*factor;setView([view[0]+(view[2]-w)/2,view[1]+(view[3]-w/2)/2,w,w/2]);}
  function visible(){const q=$('feature-search').value.trim().toLocaleLowerCase(),kind=$('feature-kind').value;return entries.filter(r=>(kind==='all'||r.type===kind)&&(!q||`${r.label} ${r.basin||''} ${r.id}`.toLocaleLowerCase().includes(q)));}
  function mapElement(tag,attrs,parent){const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,String(v));parent.append(e);return e;}
  function render() {
    const rows=visible();$('feature-choice').replaceChildren(new Option('Choose a name',''));$('feature-list').replaceChildren();$('ocean-features').replaceChildren();
    for(const row of rows){
      $('feature-choice').append(new Option(row.label,row.id));
      const button=node('button',row.label,$('feature-list'));button.type='button';button.setAttribute('aria-pressed',String(row.id===selected));button.addEventListener('click',()=>choose(row.id,{focus:true,push:true}));
      const group=mapElement('a',{href:`?atlas-feature=${encodeURIComponent(row.id)}`,'aria-label':row.label,class:`${row.type.includes('eddy')?'eddy ':''}${row.id===selected?'selected':''}`},$('ocean-features'));group.dataset.featureId=row.id;
      let plotted=false;
      for(const f of row.display_features){if(f.omitted_reason)continue;const p=f.projected;if(p?.point){mapElement('circle',{cx:p.point[0],cy:p.point[1],r:view[2]/220},group);plotted=true;}else if(p?.d){mapElement('path',{d:p.d,class:f.kind==='Polygon'?'polygon':''},group);plotted=true;}}
      if(!plotted){group.remove();continue;}
      mapElement('title',{},group).textContent=row.label;
      const hint=()=>{$('map-hover').textContent=`${row.label} · choose to open its evidence`;};group.addEventListener('pointerenter',hint);group.addEventListener('focus',hint);
      group.addEventListener('click',event=>{event.preventDefault();if(drag?.moved)return;choose(row.id,{focus:true,push:true});});
    }
    $('feature-choice').value=rows.some(r=>r.id===selected)?selected:'';$('feature-choice').disabled=false;$('filter-count').textContent=`${rows.length} of ${entries.length} records in this view. Unlocated records remain available by name.`;
  }
  function evidenceRows(label,rows,parent) {
    if(!rows.length)return;const section=node('section',null,parent);section.className='evidence-group';node('h3',`${label} · ${rows.length} ${rows.length===1?'record':'records'}`,section);
    for(const row of rows){const item=node('div',null,section);item.className='evidence-item';
      node('p',human(row.label||row.quantity||row.metric||row.evidence_role||row.kind||label),item);
      for(const key of ['scope','scope_note','note','interpretation','method_note'])if(typeof row[key]==='string'&&row[key])node('p',row[key],item);
      const fields=Object.entries(row).filter(([k,v])=>/(?:_km|_m|_dbar|_km2|_days)$/.test(k)&&(typeof v==='number'||Array.isArray(v)&&v.every(n=>typeof n==='number')));
      if((typeof row.value==='number'||Array.isArray(row.value)&&row.value.every(n=>typeof n==='number'))&&typeof(row.unit||row.units)==='string')fields.unshift([`${human(row.quantity||row.metric||'value')} (${row.unit||row.units})`,row.value]);
      if(fields.length){const dl=node('dl',null,item);for(const[k,v]of fields){node('dt',human(k),dl);node('dd',Array.isArray(v)?v.map(n=>n.toLocaleString()).join(' to '):v.toLocaleString(),dl);}}
      const detail=node('details',null,item);node('summary','Inspect the exact evidence record',detail);node('pre',JSON.stringify(row,null,2),detail);
    }
  }
  async function choose(id,{focus=false,push=false,fit=true}={}) {
    const row=byId.get(id);if(!row)return;const ticket=++generation;selected=id;
    if($('feature-kind').value!=='all'&&$('feature-kind').value!==row.type)$('feature-kind').value=row.type;
    $('record-name').textContent=row.label;$('record-status').textContent='Loading this record…';$('record-content').replaceChildren();
    if(fit){const candidates=row.display_features.filter(f=>Array.isArray(f.view_box)&&!f.omitted_reason);const target=candidates.find(f=>f.kind==='LineString'&&String(f.role).includes('reference'))||candidates.find(f=>f.kind==='LineString')||candidates[0];if(target)setView(target.view_box,false);}
    render();address(push);if(focus){$('record-name').focus({preventScroll:true});if(matchMedia('(max-width:60rem)').matches)$('current-card').scrollIntoView({block:'start'});}
    try{
      let record=cache.get(id);if(!record){record=await verified(`display-data-v1/${row.record.path}?v=${row.record.sha256}`,row.record.sha256);if(record.id!==id||record.object.id!==id)throw Error('Record identity does not match the selected name');cache.set(id,record);}
      if(ticket!==generation)return;
      const body=$('record-content');$('record-status').textContent=`${human(row.type)} · ${row.basin||'basin unspecified'} · ${human(row.identity_level||'source-scoped identity')}`;
      const mapped=row.display_features.filter(f=>!f.omitted_reason);node('p',mapped.length?'The map shows this record’s available source geography. Each geometry retains its own evidence role.':'No supported map geometry is stored for this record. Its identity and evidence are still available.',body);
      const roles=[...new Set(row.display_features.map(f=>human(f.role||f.omitted_reason||f.kind)))];if(roles.length)node('p','Map roles: '+roles.join('; ')+'.',body);
      for(const note of record.object.scope_notes||[])if(typeof note==='string')node('p',note,body);
      const links=node('p',null,body);links.className='record-links';const back=node('a','Back to the world map',links);back.href='#ocean-map';back.addEventListener('click',event=>{event.preventDefault();setView(world);$('ocean-map').focus({preventScroll:true});$('ocean-map').scrollIntoView({block:'start'});});const rich=node('a','Open the full research map card',links);rich.href=`reference-routes.html?atlas-layout=map&atlas-feature=${encodeURIComponent(id)}#route-atlas`;
      const download=node('a','Download this scoped record',links);download.href=`display-data-v1/${row.record.path}`;
      evidenceRows('Published measurement evidence',record.measurements,body);evidenceRows('Width evidence',record.widths,body);evidenceRows('Editorial reference routes',record.reference_routes,body);
      if(!record.measurements.length&&!record.widths.length&&!record.reference_routes.length)node('p','This display record has no joined numeric measurement rows. Missing evidence is not zero; the full research view may contain additional source context.',body);
      if(record.sources.length){const details=node('details',null,body);node('summary',`Sources · ${record.sources.length}`,details);const list=node('ul',null,details);for(const source of record.sources){const li=node('li',null,list),url=sourceURL(source.url);if(url){const link=node('a',source.title||source.label||source.id,li);link.href=url;link.target='_blank';link.rel='noopener noreferrer';}else li.textContent=source.title||source.label||source.id;}}
    }catch(error){if(ticket!==generation)return;$('record-status').textContent=`This record could not be loaded: ${error.message}. Choose it again to retry.`;}
  }
  $('feature-search').addEventListener('input',render);$('feature-kind').addEventListener('change',render);$('feature-choice').addEventListener('change',event=>{if(event.target.value)choose(event.target.value,{focus:true,push:true});});
  $('map-world').addEventListener('click',()=>setView(world));$('map-in').addEventListener('click',()=>zoom(.5));$('map-out').addEventListener('click',()=>zoom(2));
  $('ocean-map').addEventListener('keydown',event=>{let next=[...view];const moves={ArrowLeft:[-.12,0],ArrowRight:[.12,0],ArrowUp:[0,-.12],ArrowDown:[0,.12]};if(moves[event.key]){event.preventDefault();next[0]+=view[2]*moves[event.key][0];next[1]+=view[3]*moves[event.key][1];setView(next);}else if(['+','=','-','Home'].includes(event.key)){event.preventDefault();if(event.key==='Home')setView(world);else zoom(event.key==='-'?2:.5);}});
  $('ocean-map').addEventListener('pointerdown',event=>{if(event.button!==0||event.target.closest('a'))return;drag={x:event.clientX,y:event.clientY,view:[...view],moved:false};$('ocean-map').setPointerCapture(event.pointerId);});
  $('ocean-map').addEventListener('pointermove',event=>{if(!drag)return;const rect=$('ocean-map').getBoundingClientRect(),dx=event.clientX-drag.x,dy=event.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;setView([drag.view[0]-dx/rect.width*drag.view[2],drag.view[1]-dy/rect.height*drag.view[3],drag.view[2],drag.view[3]],false);});
  for(const event of ['pointerup','pointercancel'])$('ocean-map').addEventListener(event,()=>{if(drag)address();drag=null;});
  function restoredView(){const values=(new URL(location.href).searchParams.get('atlas-view')||'').split(',').map(Number);return values.length===4&&values.every(Number.isFinite)&&values[2]>0?values:null;}
  addEventListener('popstate',()=>{const url=new URL(location.href),v=restoredView();setView(v||world,false);const id=url.searchParams.get('atlas-feature');if(byId.has(id))choose(id,{fit:!v});else{selected=null;generation++;$('record-name').textContent='Choose a current or eddy';$('record-status').textContent='Select a name or map feature.';$('record-content').replaceChildren();render();}});
  (async()=>{try{
    const build=await verified('display-data-v1/build.json');if(build.status!=='PASS_DISPLAY_EXPORT_ONLY'||build.current_count!==111)throw Error('Unsupported display snapshot');const pin=build.files.find(f=>f.path==='index.json');if(!pin)throw Error('Missing inventory receipt');
    const index=await verified(`display-data-v1/index.json?v=${pin.sha256}`,pin.sha256);if(index.schema!=='osw.atlas-display-index.v1'||index.counts.named_current!==111||index.entries.length!==build.object_count)throw Error('Incomplete atlas inventory');
    entries=[...index.entries].sort((a,b)=>a.label.localeCompare(b.label));byId=new Map(entries.map(r=>[r.id,r]));if(byId.size!==entries.length)throw Error('Duplicate inventory identity');
    $('inventory-status').textContent=`${index.counts.named_current} current identities · ${index.counts.named_eddy||0} named eddies · ${index.counts.operational_eddy_detection||0} dated detections. Evidence availability varies.`;
    const v=restoredView();setView(v||world,false);render();const id=new URL(location.href).searchParams.get('atlas-feature');if(id&&byId.has(id))await choose(id,{fit:!v});else if(id)$('record-status').textContent='That name is not in this snapshot. Choose a name from the inventory.';
  }catch(error){$('inventory-status').textContent=`Atlas inventory unavailable: ${error.message}. Reload to retry.`;}})();
})();
