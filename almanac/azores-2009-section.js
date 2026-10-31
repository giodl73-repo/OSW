"use strict";
window.renderAzores2009Section=function(parent,scene,selectedId,inspect){
  if(!scene||scene.kind!=='azores_2009_section_review')return;
  if(selectedId&&!scene.records.some(r=>r.id===selectedId||'current:'+r.current_id===selectedId))return;
  const add=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const section=add('section',undefined,parent);section.className='azores-section-review';section.style.cssText='min-width:0;max-width:100%';
  add('h4',scene.title,section);add('p',scene.scope,section);
  const figure=add('figure',undefined,section);figure.style.margin='0';
  const image=add('img',undefined,figure);image.src='../'+scene.figure_file;image.style.cssText='display:block;width:100%;max-width:880px;height:auto';
  image.alt='At 24.5 W: Azores Countercurrent stations 42-46, 36.25-35.25 N, westward; Azores Current stations 49-53, 34.5-33.5 N, eastward. Each reported section span is about 110 km. Not current length or annual variability.';
  add('figcaption','One occupation: 26 Oct-1 Nov 2009 in the methods. Figure 1 says fall 2010; the source date conflict remains unresolved.',figure);
  const full=add('a','Open section diagram at full size',figure);full.href='../'+scene.figure_file;full.style.cssText='display:block;min-height:44px';
  for(const [index,row] of scene.records.entries()){
    const matching=row.id===selectedId||'current:'+row.current_id===selectedId||scene.matching_ids.includes(row.id);
    const item=add('section',undefined,section);item.dataset.widthId=row.id;
    add('h5',row.name+(matching?' / selected record':''),item);
    const enrichment=scene.enrichments.find(r=>r.id===row.id);
    add('p','Stations '+enrichment.north_boundary.station+'-'+enrichment.south_boundary.station+' / '+enrichment.flow_direction+' / about '+row.approximate_width_km+' km.',item);
    add('p',enrichment.vertical_support,item);
    const links=add('p',undefined,item);
    if(inspect){const b=add('button','Inspect width record',links);b.type='button';b.onclick=()=>inspect('widths',row.id);}
    else{const a=add('a','Inspect width record',links);a.href='seasons.html?current='+encodeURIComponent(row.current_id)+'&phase='+encodeURIComponent(row.id);}
    const a=add('a','Inspect exact source record',links);a.style.cssText='display:block;min-height:44px';a.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.bindings_file,pointer:'/records/'+index,limit:50}));
  }
  add('p','Width uncertainty and annual ranges remain unknown. Separate ADCP depth averages are not a fixed width layer.',section);
  const links=add('p',undefined,section);
  const review=add('a','Original-source review and remaining gaps',links);review.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,limit:50}));review.style.cssText='display:block;min-height:44px';
  const source=add('a','Published paper',links);source.href=scene.source_url;
};
