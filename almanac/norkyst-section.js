(() => {
  const el = id => document.getElementById(id);
  const ns = 'http://www.w3.org/2000/svg';
  let data, timer = null, mapToken = 0;
  function stop() { if (timer !== null) clearInterval(timer); timer = null; el('section-play').textContent = 'Play snapshots'; }
  function node(tag, attrs, text) { const n = document.createElementNS(ns, tag); for (const [key, value] of Object.entries(attrs)) n.setAttribute(key, value); if (text) n.textContent = text; return n; }
  function render() {
    const frame = data.frames[Number(el('section-month').value)];
    const address=new URL(location.href);address.searchParams.set('date',frame.date);history.replaceState(null,'',address);
    el('section-time').textContent = `${frame.sample_time_utc} · Norkyst v3 hindcast · 10 m depth · hourly snapshot`;
    const map = data.mapFrames.frames[Number(el('section-month').value)];
    const image=el('section-map'), token=++mapToken;image.hidden=true;el('section-map-status').textContent='Loading selected map…';image.src=`../${map.figure}`;image.alt=`Regional Norkyst salinity and instantaneous flow at ${frame.sample_time_utc}, 10 m depth; fixed profile section shown independently.`;
    image.decode().then(()=>{if(token===mapToken){image.hidden=false;el('section-map-status').textContent='';image.dataset.sampleTime=frame.sample_time_utc;}}).catch(()=>{if(token===mapToken){stop();el('section-map-status').textContent='Selected map unavailable; profile source remains inspectable.';}});
    const chart = el('section-chart'); chart.replaceChildren();
    const end = frame.profile.at(-1).distance_from_section_start_km;
    const x = v => 85 + v / end * 770;
    const panels = [{top:60, height:170, min:32, max:35.5, keys:['salinity'], colors:['#007e8a'], title:'Salinity · dimensionless'}, {top:325, height:170, min:-0.8, max:0.8, keys:['u_eastward','v_northward'], colors:['#a8470a','#315eb8'], title:'Velocity · m/s · orange eastward, blue northward'}];
    for (const panel of panels) {
      const values = data.frames.flatMap(f => f.profile.flatMap(p => panel.keys.map(k => p[k]))).filter(v => v !== null);
      const min = Math.min(panel.min, ...values), max = Math.max(panel.max, ...values);
      const y = v => panel.top + panel.height * (1 - (v-min)/(max-min));
      chart.append(node('text', {x:85, y:panel.top-20, 'font-size':19}, panel.title));
      for (let i=0;i<=4;i++) { const value = min+(max-min)*i/4; chart.append(node('line',{x1:85,x2:855,y1:y(value),y2:y(value),stroke:'#d2dce0'}),node('text',{x:72,y:y(value)+5,'text-anchor':'end','font-size':16},value.toFixed(2))); }
      for (const tick of [0,50,100,150,200]) { chart.append(node('text',{x:x(tick),y:panel.top+panel.height+25,'text-anchor':'middle','font-size':16},String(tick))); }
      for (const [index,key] of panel.keys.entries()) { let path='', open=false; for (const p of frame.profile) { if (p[key] === null) {open=false;continue;} path += `${open?'L':'M'}${x(p.distance_from_section_start_km).toFixed(2)},${y(p[key]).toFixed(2)} `; open=true; } chart.append(node('path',{d:path,fill:'none',stroke:panel.colors[index],'stroke-width':3})); }
    }
    chart.append(node('text',{x:470,y:565,'text-anchor':'middle','font-size':18},'Distance from selected section start · km'));
    const rows = el('section-rows'); rows.replaceChildren();
    for (const point of frame.profile) { const tr = document.createElement('tr'); for (const key of ['distance_from_section_start_km','salinity','u_eastward','v_northward']) { const td=document.createElement('td'); td.textContent=point[key] === null ? 'Unavailable' : point[key].toFixed(3); tr.append(td); } rows.append(tr); }
    const link = document.createElement('a'); link.href = frame.source_url; link.textContent = 'Pinned source subset at MET Norway'; el('section-source').replaceChildren(link);
  }
  el('section-month').addEventListener('change',()=>{stop();render();});
  el('section-play').addEventListener('click',()=>{ if(timer !== null) return stop(); el('section-play').textContent='Pause snapshots'; timer=setInterval(()=>{el('section-month').value=(Number(el('section-month').value)+1)%data.frames.length;render();},2200); });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  window.oswCheckedAtlasReady.then(({documents})=>{
    const value=documents['research/norkyst-ingoy-2024-section-timeline.json'],maps=documents['research/norkyst-ingoy-2024-map-frames.json'];
    if(!value||!maps)throw new Error('Checked model profiles/maps unavailable');
    if(maps.frames.length!==value.frames.length || maps.frames.some((map,i)=>map.sample_time_utc!==value.frames[i].sample_time_utc || map.receipt_sha256!==value.frames[i].receipt_sha256)) throw new Error('Map/profile source mismatch');
    value.mapFrames=maps;
    data=value; for(const [i,frame] of data.frames.entries()){const o=document.createElement('option');o.value=i;o.textContent=frame.date;el('section-month').append(o);}
    const requested=new URL(location.href).searchParams.get('date'),selected=data.frames.findIndex(frame=>frame.date===requested);el('section-month').value=String(selected>=0?selected:0);
    el('section-month').disabled=false;el('section-play').disabled=false;el('section-status').textContent='12 pinned hourly model snapshots; no monthly averages or annual extrema.';el('section-method').textContent=data.interpolation;el('section-credit').textContent=data.credit;render();
  }).catch(error=>{stop();el('section-status').textContent=error.message;});
})();
