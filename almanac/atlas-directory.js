"use strict";
window.initAtlasDirectory = function(rows, api) {
  const root=document.getElementById('atlas-directory');
  const search=root.querySelector('input'),filter=root.querySelector('select');
  const stateFilter=root.querySelector('#atlas-directory-state'),stateNote=root.querySelector('.atlas-directory-state-note');
  const list=root.querySelector('.atlas-directory-list'),status=root.querySelector('[role=status]');
  const normalize=text=>text.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const states=new Map(Object.entries(api.stateJoin?.states||{}).map(([code,state])=>[code,state.name]));
  for(const row of rows)for(const evidence of row.state_evidence||[])if(!states.has(evidence.state_code))states.set(evidence.state_code,evidence.state_name);
  for(const [code,name] of [...states].sort((a,b)=>a[0].localeCompare(b[0]))) {
    const option=document.createElement('option');option.value=code;option.textContent=`${code} · ${name}`;stateFilter.append(option);
  }
  const requestedState=new URL(location.href).searchParams.get('atlas-state');
  if(states.has(requestedState))stateFilter.value=requestedState;
  else if(requestedState){const url=new URL(location.href);url.searchParams.delete('atlas-state');history.replaceState(null,'',url);}
  const items=[...rows].sort((a,b)=>a.label.localeCompare(b.label)).map(row=>{
    const current=row.type==='named_current';
    const roles=row.map_features.map(feature=>feature.role);
    const evidence=current
      ? roles.includes('editorial_reference_route')?'Reference route'
        : roles.some(role=>role.startsWith('dated_'))?'Dated geometry':'Locator only'
      : roles.includes('shared_regional_gateway')?'Shared gateway'
        : row.map_features.some(feature=>feature.geometry.type==='Polygon')?'Dated outline'
        : roles.includes('approximate_reported_center')?'Reported center':'Locator only';
    const button=document.createElement('button');button.type='button';
    button.dataset.featureId=row.id;button.className='atlas-directory-item';
    const name=document.createElement('span');name.textContent=row.label;
    const detail=document.createElement('small');
    const baseDetail=`${current?'Current':row.type==='operational_eddy_detection'?'Detection':'Eddy'} · ${evidence}`;
    detail.textContent=baseDetail;
    button.append(name,detail);list.append(button);
    button.addEventListener('click',()=>{
      api.select(row);
      document.getElementById('route-atlas-workspace').scrollIntoView({block:'start'});
    });
    const relations=new Map();
    if(current)for(const [code,state] of Object.entries(api.stateJoin?.states||{})) {
      const matches=(state.route_candidates||[]).filter(route=>'current:'+route.current_id===row.id);
      if(matches.length)relations.set(code,matches.some(route=>route.nominal_crossing)?'Nominal reference-route crossing':'Alternative reference-route crossing only');
    }
    else for(const record of row.state_evidence||[]) {
      const label=`${record.label}${record.observation_date?' · '+record.observation_date:''}`;
      const prior=relations.get(record.state_code);relations.set(record.state_code,prior?prior+'; '+label:label);
    }
    return {row,button,detail,baseDetail,relations,evidence,current,text:normalize(row.label+' '+evidence)};
  });
  function refresh() {
    const words=normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible=0,currentCount=0,eddyCount=0;
    for(const item of items) {
      const updated=api.changed(item.row);
      const relation=stateFilter.value?item.relations.get(stateFilter.value):null;
      const match=(!stateFilter.value||Boolean(relation))&&words.every(word=>item.text.includes(word))&&
        (filter.value==='all'||filter.value==='currents'&&item.current||
          filter.value==='eddies'&&!item.current||filter.value==='updated'&&updated);
      item.button.hidden=!match;visible+=Number(match);
      if(match){if(item.current)currentCount++;else eddyCount++;}
      item.detail.textContent=item.baseDetail+(relation?' · '+relation:'');
      item.button.classList.toggle('updated',updated);
      item.button.setAttribute('aria-pressed',String(api.selected()===item.row.id));
      item.button.title=(relation||item.evidence)+(updated?' · '+api.changeDescription(item.row):'');
      item.button.setAttribute('aria-label',`${item.row.label} · ${item.current?'Current':item.row.type==='operational_eddy_detection'?'Detection':'Eddy'} · ${item.evidence}${relation?' · '+relation:''}${updated?' · Updated since saved baseline':''}`);
    }
    status.textContent=`${visible} of ${rows.length} entries · ${rows.filter(row=>row.type==='named_current').length} currents · ${rows.filter(row=>row.type==='named_eddy').length} named eddies · ${rows.filter(row=>row.type==='operational_eddy_detection').length} dated detections${visible?'':'. No matching entries; change the search or filter.'}`;
    stateNote.replaceChildren();
    if(stateFilter.value) {
      const anchor=document.createElement('a');anchor.href=`index.html?state=${encodeURIComponent(stateFilter.value)}#state-title`;anchor.textContent=`${stateFilter.value} · ${states.get(stateFilter.value)}`;
      stateNote.append(anchor,document.createTextNode(` · ${currentCount} current and ${eddyCount} eddy/detection entries match the active filters. Reference-route crossings use declared editorial scenarios; eddy links retain their source scope and date. These do not establish full-current passage or whole-eddy containment.`));
    } else stateNote.textContent='OSW state filter uses recorded route-scenario crossings and eddy state evidence. No recorded link does not prove physical absence.';
    if(!api.stateJoin)stateNote.append(document.createTextNode(' Current route-state links are unavailable; only saved eddy evidence can be filtered.'));
    api.stateChanged?.(stateFilter.value);
  }
  search.addEventListener('input',refresh);filter.addEventListener('change',refresh);
  stateFilter.addEventListener('change',()=>{
    const url=new URL(location.href);url.searchParams.delete('atlas-state');if(stateFilter.value)url.searchParams.set('atlas-state',stateFilter.value);
    history.replaceState(null,'',url);refresh();
  });
  refresh.selectState=code=>{if(states.has(code)){stateFilter.value=code;stateFilter.dispatchEvent(new Event('change'));}};
  refresh();return refresh;
};
