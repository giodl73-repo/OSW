"use strict";
(() => {
  const $ = id => document.getElementById(id), ns = 'http://www.w3.org/2000/svg';
  const edition = new URL(location.href).searchParams.get('atlas-edition');
  const screened = edition === 'preview-screened';
  const candidate = screened || edition === 'preview-candidate';
  const dataRoot = screened ? 'preview-data-screened-v1' : (candidate ? 'preview-data-candidate-v1' : 'display-data-v1');
  const world = [60,90,1480,740], cache = new Map();
  let entries=[], byId=new Map(), selected=null, view=[...world], generation=0, drag=null, contextById={};
  const node=(tag,text,parent)=>{const e=document.createElement(tag);if(text!==null)e.textContent=text;if(parent)parent.append(e);return e;};
  const human=key=>String(key).replaceAll('_',' ').replace(/\bkm2\b/g,'km²');
  const typeName=key=>({named_current:'Current',named_eddy:'Named eddy source record',operational_eddy_detection:'Dated eddy detection'})[key]||human(key);
  const formatNumber=value=>value.toLocaleString(undefined,{maximumSignificantDigits:21});
  const mapMeaning=role=>{
    if(/locator|gateway|reported_center/.test(role))return 'A location or regional starting point; it does not show the feature’s boundary or size.';
    if(/reference_route/.test(role))return 'An approximate drawn reference route; it is not a measured boundary or a live track.';
    if(/diagnostic|streamline|contour/.test(role))return 'A source-specific model or field trace. It is not automatically the current’s axis or boundary.';
    if(/front/.test(role))return 'A dated analyzed front; it describes that source and date, rather than the entire current.';
    if(/polygon/.test(role))return 'A source-specific outline for a dated record; it is not a permanent boundary.';
    return 'Source geography with a specific evidence role. Open the technical map roles for its exact classification.';
  };
  const sourceURL=value=>{if(typeof value!=='string'||!value.trim())return null;try{const u=new URL(value,location.href);return ['http:','https:'].includes(u.protocol)?u.href:null;}catch{return null;}};
  async function verified(path, expected) {
    const response=await fetch(path,{cache:expected?'force-cache':'no-cache'});if(!response.ok)throw Error(`Could not load atlas record (HTTP ${response.status})`);
    const bytes=await response.arrayBuffer();if(bytes.byteLength>2400000)throw Error('Atlas record exceeds its expected size');
    if(expected){const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==expected)throw Error('Atlas record does not match this snapshot');}
    let value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
    if(value.schema==='osw.preview-json-envelope.v1'){
      if(value.encoding!=='gzip+base64'||!Number.isInteger(value.decoded_bytes)||value.decoded_bytes<0||value.decoded_bytes>=2500000)throw Error('Invalid preview record envelope');
      if(typeof DecompressionStream==='undefined')throw Error('This preview needs a browser with gzip decompression support');
      const compressed=Uint8Array.from(atob(value.payload),c=>c.charCodeAt(0)),reader=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();
      const chunks=[];let size=0;try{while(true){const next=await reader.read();if(next.done)break;size+=next.value.length;if(size>value.decoded_bytes)throw Error('Preview record exceeds its declared decoded size');chunks.push(next.value);}}finally{await reader.cancel();}
      if(size!==value.decoded_bytes)throw Error('Incomplete preview record');const decoded=new Uint8Array(size);let offset=0;for(const chunk of chunks){decoded.set(chunk,offset);offset+=chunk.length;}
      const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',decoded))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==value.decoded_sha256)throw Error('Preview record decoded checksum mismatch');
      value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(decoded));
    }
    return value;
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
      const target=new URL(location.href);target.searchParams.set('atlas-feature',row.id);target.searchParams.delete('atlas-view');const group=mapElement('a',{href:target.href,'aria-label':row.label,class:`${row.type.includes('eddy')?'eddy ':''}${row.id===selected?'selected':''}`},$('ocean-features'));group.dataset.featureId=row.id;
      let plotted=false;
      for(const f of row.display_features){if(f.omitted_reason)continue;const p=f.projected;if(p?.point){mapElement('circle',{cx:p.point[0],cy:p.point[1],r:view[2]/220},group);plotted=true;}else if(p?.d){mapElement('path',{d:p.d,class:f.kind==='Polygon'?'polygon':''},group);plotted=true;}}
      if(!plotted){group.remove();continue;}
      mapElement('title',{},group).textContent=row.label;
      const hint=()=>{$('map-hover').textContent=`${row.label} · choose to open its evidence`;};group.addEventListener('pointerenter',hint);group.addEventListener('focus',hint);
      group.addEventListener('click',event=>{event.preventDefault();if(drag?.moved)return;choose(row.id,{focus:true,push:true});});
    }
    $('feature-choice').value=rows.some(r=>r.id===selected)?selected:'';$('feature-choice').disabled=false;$('filter-count').textContent=`${rows.length} of ${entries.length} records in this view. Unlocated records remain available by name.`;
    const status=$('search-status');status.hidden=!$('feature-search').value.trim();status.replaceChildren();
    if(!status.hidden){node('span',rows.length?`${rows.length} matching ${rows.length===1?'record':'records'} in the selected category. `:'No matching names in the selected category. Try another name or choose “All features”. ',status);const clear=node('button','Clear search',status);clear.type='button';clear.addEventListener('click',()=>{$('feature-search').value='';render();$('feature-search').focus();});}
  }
  function evidenceRows(label,rows,parent,sources,{open=false,note=''}={}) {
    if(!rows.length)return;const section=node('details',null,parent);section.className='evidence-group';section.open=open;node('summary',`${label} · ${rows.length} ${rows.length===1?'reference':'references'}`,section);if(note)node('p',note,section);
    let filled=false;function fill(){if(filled)return;filled=true;
    for(const row of rows){const item=node('div',null,section);item.className='evidence-item';
      node('p',human(row.label||row.quantity||row.metric||row.evidence_role||row.kind||label),item);
      for(const key of ['scope','scope_note','spatial_scope','temporal_scope','definition','qualification','note','interpretation','method_note'])if(typeof row[key]==='string'&&row[key])node('p',row[key],item);
      const fields=Object.entries(row).filter(([k,v])=>/(?:_km|_m|_dbar|_km2|_days)$/.test(k)&&(typeof v==='number'||Array.isArray(v)&&v.every(n=>typeof n==='number')));
      if((typeof row.value==='number'||Array.isArray(row.value)&&row.value.every(n=>typeof n==='number'))&&typeof(row.unit||row.units)==='string')fields.unshift([`${human(row.quantity||row.metric||'value')} (${row.unit||row.units})`,row.value]);
      if(fields.length){const dl=node('dl',null,item);for(const[k,v]of fields){node('dt',human(k),dl);node('dd',Array.isArray(v)?v.map(formatNumber).join(' to '):formatNumber(v),dl);}}
      const ids=[...new Set([row.source_id,row.method_source_id,...(row.supporting_source_ids||[])].filter(Boolean))];
      for(const id of ids){const source=sources.find(s=>s.id===id);if(!source)continue;const citation=node('p',null,item);citation.className='citation';node('span',id===row.method_source_id?'Method: ':'Source: ',citation);const url=sourceURL(source.url);if(url){const link=node('a',source.title||source.label||id,citation);link.href=url;link.target='_blank';link.rel='noopener noreferrer';}else node('span',source.title||source.label||id,citation);}
      const direct=sourceURL(row.source_url);if(direct){const citation=node('p',null,item);citation.className='citation';const a=node('a',row.source_citation||'Primary source or data attribution',citation);a.href=direct;a.target='_blank';a.rel='noopener noreferrer';}
      const context=contextById[row.source_context_id];if(context){const detail=node('details',null,item);node('summary','Method and source context',detail);detail.addEventListener('toggle',()=>{if(!detail.open||detail.dataset.filled)return;detail.dataset.filled='true';node('p',context.title||human(row.source_context_id),detail);if(context.interpretation)node('p',context.interpretation,detail);const method=sourceURL(context.url||context.source_url);if(method){const p=node('p',null,detail),a=node('a',context.context_role?'OSW method record':'Context source',p);a.href=method;a.target='_blank';a.rel='noopener noreferrer';}const metadata=context.retained_bibliographic_metadata?.bibliographic_strings;for(const text of metadata?.citation||metadata?.source_citation||[])node('p',text,detail);for(const url of new Set([context.primary_data_provider_url,...(context.primary_data_provider_urls||[]),...(metadata?.source_url||[]),...(metadata?.primary_url||[])].filter(Boolean))){const safe=sourceURL(url);if(safe){const p=node('p',null,detail),a=node('a','Primary source or data attribution',p);a.href=safe;a.target='_blank';a.rel='noopener noreferrer';}}});}
      const detail=node('details',null,item);node('summary','Exact values, qualifiers, and method',detail);detail.addEventListener('toggle',()=>{if(detail.open&&!detail.querySelector('pre'))node('pre',JSON.stringify(row,null,2),detail);});
    }
    }section.addEventListener('toggle',()=>{if(section.open)fill();});if(open)fill();
  }
  async function choose(id,{focus=false,push=false,fit=true}={}) {
    const row=byId.get(id);if(!row)return;const ticket=++generation;selected=id;
    if($('feature-kind').value!=='all'&&$('feature-kind').value!==row.type)$('feature-kind').value=row.type;
    $('record-name').textContent=row.label;$('record-status').textContent='Loading this record…';$('record-content').replaceChildren();
    if(fit){const candidates=row.display_features.filter(f=>Array.isArray(f.view_box)&&!f.omitted_reason);const target=candidates.find(f=>f.kind==='LineString'&&String(f.role).includes('reference'))||candidates.find(f=>f.kind==='LineString')||candidates[0];if(target)setView(target.view_box,false);}
    render();address(push);if(focus){$('record-name').focus({preventScroll:true});if(matchMedia('(max-width:60rem)').matches)$('current-card').scrollIntoView({block:'start'});}
    try{
      let record=cache.get(id);if(!record){record=await verified(`${dataRoot}/${row.record.path}?v=${row.record.sha256}`,row.record.sha256);if(record.id!==id||record.object.id!==id)throw Error('Record identity does not match the selected name');cache.set(id,record);}
      if(ticket!==generation)return;
      const body=$('record-content');$('record-status').textContent=`${typeName(row.type)} · ${row.basin||'basin unspecified'}`;
      const mapped=row.display_features.filter(f=>!f.omitted_reason),meaning=node('section',null,body);meaning.className='map-meaning';node('h3','What this map shows',meaning);
      if(mapped.length){for(const text of new Set(mapped.map(f=>mapMeaning(String(f.role||'')))))node('p',text,meaning);}else node('p','No supported map geometry is stored for this record. Its identity and evidence are still available by name.',meaning);
      const roles=[...new Set(row.display_features.map(f=>human(f.role||f.omitted_reason||f.kind)))];if(roles.length){const technical=node('details',null,meaning);node('summary','Technical map roles',technical);node('p',roles.join('; ')+'.',technical);}
      for(const note of record.object.scope_notes||[])if(typeof note==='string')node('p',note,body);
      if(typeof record.object.identity_scope_note==='string'&&record.object.identity_scope_note)node('p',record.object.identity_scope_note,body);
      const links=node('p',null,body);links.className='record-links';const back=node('a','Back to the world map',links);back.href='#ocean-map';back.addEventListener('click',event=>{event.preventDefault();setView(world);$('ocean-map').focus({preventScroll:true});$('ocean-map').scrollIntoView({block:'start'});});const rich=node('a','Open the full research map card',links);rich.href=`reference-routes.html?atlas-layout=map&atlas-feature=${encodeURIComponent(id)}#route-atlas`;
      const download=node('a',candidate?'Download this record’s encoded package':'Download this scoped record',links);download.href=`${dataRoot}/${row.record.path}`;
      evidenceRows('Measurement references',record.measurements,body,record.sources,{open:true,note:'Read each number with its scope and source. References may describe different reaches, dates, or definitions; they are not automatically comparable.'});evidenceRows('Width references',record.widths,body,record.sources,{note:'Width depends on where, when, and how the edge of a current is defined. Open a reference to inspect its exact qualifications.'});evidenceRows('Drawn reference routes',record.reference_routes,body,record.sources,{note:'These distances follow approximate editorial paths. They belong to a different measurement class from published physical current lengths.'});
      evidenceRows('Depth references',record.depth_references||[],body,record.sources,{note:'These are scoped depth or thickness references, not a whole-current depth profile. Metres and pressure in dbar are separate units. Some values describe instruments, water masses, thresholds, or integration limits rather than a physical current bottom. Method contexts explain admission and do not add independent measurements. This private candidate still requires final source and bundle checks.'});
      if(!record.measurements.length&&!record.widths.length&&!record.reference_routes.length)node('p','This display record has no joined numeric measurement rows. Missing evidence is not zero; the full research view may contain additional source context.',body);
      if(record.sources.length){const details=node('details',null,body);node('summary',`Sources · ${record.sources.length}`,details);const list=node('ul',null,details);for(const source of record.sources){const li=node('li',null,list),url=sourceURL(source.url);if(url){const link=node('a',source.title||source.label||source.id,li);link.href=url;link.target='_blank';link.rel='noopener noreferrer';}else li.textContent=source.title||source.label||source.id;}}
    }catch(error){if(ticket!==generation)return;$('record-status').textContent=`This record could not be loaded: ${error.message}. Choose it again to retry.`;}
  }
  $('feature-search').addEventListener('input',render);$('feature-kind').addEventListener('change',render);$('feature-choice').addEventListener('change',event=>{if(event.target.value)choose(event.target.value,{focus:true,push:true});});
  $('map-world').addEventListener('click',()=>setView(world));$('map-in').addEventListener('click',()=>zoom(.5));$('map-out').addEventListener('click',()=>zoom(2));
  $('copy-view').addEventListener('click',async()=>{const status=$('share-status');status.hidden=false;try{await navigator.clipboard.writeText($('share-view').href);status.textContent='View link copied. It includes your selected feature and map zoom.';}catch{status.textContent='Copy is unavailable in this browser. Use “View link” to copy the address from its link menu.';}});
  $('ocean-map').addEventListener('keydown',event=>{let next=[...view];const moves={ArrowLeft:[-.12,0],ArrowRight:[.12,0],ArrowUp:[0,-.12],ArrowDown:[0,.12]};if(moves[event.key]){event.preventDefault();next[0]+=view[2]*moves[event.key][0];next[1]+=view[3]*moves[event.key][1];setView(next);}else if(['+','=','-','Home'].includes(event.key)){event.preventDefault();if(event.key==='Home')setView(world);else zoom(event.key==='-'?2:.5);}});
  $('ocean-map').addEventListener('pointerdown',event=>{if(event.button!==0||event.target.closest('a'))return;drag={x:event.clientX,y:event.clientY,view:[...view],moved:false};$('ocean-map').setPointerCapture(event.pointerId);});
  $('ocean-map').addEventListener('pointermove',event=>{if(!drag)return;const rect=$('ocean-map').getBoundingClientRect(),dx=event.clientX-drag.x,dy=event.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;setView([drag.view[0]-dx/rect.width*drag.view[2],drag.view[1]-dy/rect.height*drag.view[3],drag.view[2],drag.view[3]],false);});
  for(const event of ['pointerup','pointercancel'])$('ocean-map').addEventListener(event,()=>{if(drag)address();drag=null;});
  function restoredView(){const values=(new URL(location.href).searchParams.get('atlas-view')||'').split(',').map(Number);return values.length===4&&values.every(Number.isFinite)&&values[2]>0?values:null;}
  addEventListener('popstate',()=>{const url=new URL(location.href),v=restoredView();setView(v||world,false);const id=url.searchParams.get('atlas-feature');if(byId.has(id))choose(id,{fit:!v});else{selected=null;generation++;$('record-name').textContent='Choose a current or eddy';$('record-status').textContent='Select a name or map feature.';$('record-content').replaceChildren();render();}});
  (async()=>{try{
    const review=candidate?await verified(`preview-review-v1/${screened?'screened-manifest':'manifest'}.json`):null;
    const build=await verified(`${dataRoot}/build.json`,review?.data_build_sha256||review?.candidate_build_sha256);if(candidate?(build.schema!=='osw.preview-data-projection.v1'||build.counts?.named_current!==111):(build.status!=='PASS_DISPLAY_EXPORT_ONLY'||build.current_count!==111))throw Error('Unsupported display snapshot');const pin=build.files.find(f=>f.path==='index.json');if(!pin)throw Error('Missing inventory receipt');
    if(candidate){const basePin=build.files.find(f=>f.path==='depth-contexts.json'),extraPin=review.files.find(f=>f.path==='contexts.json');if(!basePin||!extraPin)throw Error('Missing depth citation metadata');const original=await verified(`${dataRoot}/depth-contexts.json`,basePin.sha256),extra=await verified('preview-review-v1/contexts.json',extraPin.sha256);if(extra.candidate_build_sha256!==review.candidate_build_sha256)throw Error('Citation supplement targets another snapshot');contextById={...original.contexts};for(const[id,context]of Object.entries(extra.contexts)){if(!Object.hasOwn(contextById,id)||Object.keys(contextById[id]).length)throw Error('Citation supplement would replace a nonempty context');contextById[id]=context;}}
    const index=await verified(`${dataRoot}/index.json?v=${pin.sha256}`,pin.sha256);if(index.schema!==(candidate?'osw.preview-display-index.v1':'osw.atlas-display-index.v1')||index.counts.named_current!==111||(!candidate&&index.entries.length!==build.object_count))throw Error('Incomplete atlas inventory');
    entries=[...index.entries].sort((a,b)=>a.label.localeCompare(b.label));byId=new Map(entries.map(r=>[r.id,r]));if(byId.size!==entries.length)throw Error('Duplicate inventory identity');
    $('inventory-status').textContent=`${index.counts.named_current} current identities · ${index.counts.named_eddy||0} named-eddy source records · ${index.counts.operational_eddy_detection||0} dated detections. A frozen research snapshot, not a live feed; evidence availability varies.`;
    if(candidate){document.querySelector('.eyebrow').textContent=screened?'Private data candidate · data-scope check passed · interface review unfinished':'Private integrated data candidate · source review unfinished';$('inventory-status').textContent=`111 current identities · ${index.counts.named_eddy} retained named-eddy records · ${index.depth_reference_count} scoped depth references. ${index.eddy_source_reference_count} additional eddy evidence references are stored separately from canonical identities. This candidate is not approved for public publication.`;const detection=$('feature-kind').querySelector('[value="operational_eddy_detection"]');if(detection)detection.remove();const example=document.querySelector('.quick-guide a');if(example)example.href=`?atlas-edition=${screened?'preview-screened':'preview-candidate'}&atlas-feature=current%3Aagulhas`;}
    const v=restoredView();setView(v||world,false);render();const id=new URL(location.href).searchParams.get('atlas-feature');if(id&&byId.has(id))await choose(id,{fit:!v});else if(id)$('record-status').textContent='That name is not in this snapshot. Choose a name from the inventory.';
  }catch(error){$('inventory-status').textContent=`Atlas inventory unavailable: ${error.message}. Reload to retry.`;}})();
})();
