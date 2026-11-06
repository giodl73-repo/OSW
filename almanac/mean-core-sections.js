"use strict";
window.renderMeanCoreSections=function(parent,scene,inspect,options={}){
  if(scene?.kind!=='published_mean_core_sections'||!Array.isArray(scene.records)||!scene.records.length)return;
  const node=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const link=(label,url,container)=>{const a=node('a',label,container);a.href=url;return a;};
  const svgNode=(tag,attrs,container)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value] of Object.entries(attrs))n.setAttribute(key,String(value));container.append(n);return n;};
  const number=value=>typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('en-US'):'Unknown';
  inspect||=((collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));});
  const wrapper=node(options.collapsed?'details':'section',undefined,parent);wrapper.className='mean-core-sections';wrapper.style.cssText='min-width:0;overflow-wrap:anywhere';
  if(options.collapsed)node('summary',`${scene.records.length} model mean-core sections · 1994–2016 · offshore extent, depth and area`,wrapper);
  const panel=options.collapsed?node('div',undefined,wrapper):wrapper;
  node('h3',scene.title,panel);node('p',scene.scope,panel);node('p',scene.boundary,panel);node('p',scene.definition,panel);
  node('p',`${scene.records.length} matching section record${scene.records.length===1?'':'s'}. Each record retains its source component.`,panel);
  node('p','Separate scales, each starting at zero: teal offshore extent 0–240 km; ochre maximum contour depth 0–1,400 m.',panel);
  for(const row of scene.records){
    const card=node('article',undefined,panel);card.setAttribute('data-mean-core-id',row.id);
    card.style.cssText='min-width:0;border:1px solid #b7ced2;border-radius:.5rem;padding:1rem;margin:1rem 0';
    node('h4',`${row.place} · ${number(Math.abs(row.latitude_degrees_north))}°S`,card);
    node('p',String(row.source_component).replaceAll('_',' '),card);
    const values=node('dl',undefined,card);
    for(const [label,value,unit] of [['Offshore extent',row.offshore_extent_km,'km'],['Maximum contour depth',row.maximum_depth_m,'m'],['Cross-sectional area',row.section_area_km2,'km²']]){
      const dt=node('dt',label,values);dt.style.fontSize='.9rem';
      const dd=node('dd',`${number(value)} ${unit}`,values);dd.style.cssText='font-size:1.1rem;font-weight:700;margin:.2rem 0 .6rem';
    }
    const chart=svgNode('svg',{viewBox:'0 0 300 64',role:'img','aria-label':`${row.place}: offshore extent ${number(row.offshore_extent_km)} km; maximum contour depth ${number(row.maximum_depth_m)} m. Separate scales of240km and1400m; dimensions of mean model flow.`},card);
    chart.style.cssText='display:block;width:100%;max-width:600px;height:auto';
    for(const [value,maximum,y,color] of [[row.offshore_extent_km,240,18,'#087f8c'],[row.maximum_depth_m,1400,46,'#ad5c14']]){
      svgNode('line',{x1:12,x2:288,y1:y,y2:y,stroke:'#cbdcdd','stroke-width':2},chart);
      if(typeof value==='number'&&Number.isFinite(value))svgNode('circle',{cx:12+value/maximum*276,cy:y,r:5,fill:color},chart);
    }
    node('p','Regional model mean. Annual dimension ranges and numerical uncertainty are unknown.',card);
    const action=node('button','Inspect section record',card);action.type='button';action.onclick=()=>inspect('current_mean_core_sections',row.id);
    link('Source table record','query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:100})),node('p',undefined,card));
  }
  node('p',scene.labeling_note,panel);
  link('Original study',scene.source_url,node('p',undefined,panel));
  link('Full five-section context chart','../'+scene.figure,node('p',undefined,panel));
  link('Compact context chart','../'+scene.compact_figure,node('p',undefined,panel));
  link('Open current atlas','reference-routes.html?atlas-feature='+encodeURIComponent(scene.records[0].entity_id)+'#route-atlas',node('p',undefined,panel));
};
