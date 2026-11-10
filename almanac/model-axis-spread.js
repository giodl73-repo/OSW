"use strict";
(() => {
  let serial=0;
  window.renderModelAxisSpread=function(parent,records,inspect,options={}) {
    const rows=(records||[]).filter(r=>r.phase_kind==='published_model_axis_spread_scale');
    if(!rows.length)return;
    const section=document.createElement('section');section.className='model-axis-spread';
    section.style.cssText='min-width:0;max-width:100%;margin:.8rem 0;padding:.7rem;border:1px solid #a7c5cf;border-radius:.3rem';parent.append(section);
    const add=(tag,text,container=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
    add(options.headingTag||'h4','Published model axis-distance scale');
    add('p','About 100 km → 130 km in the authors’ reported model change. This scale measures mean distance from a weighted axis; it does not give two current edges.');
    const details=add('details');details.open=!!options.open;
    add('summary','View the comparison, definition and source',details);
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg'),id='model-axis-spread-'+(++serial);
    svg.setAttribute('viewBox','0 0 320 160');svg.setAttribute('role','img');svg.setAttribute('aria-labelledby',id+'-title '+id+'-desc');
    svg.style.cssText='display:block;width:100%;max-width:560px';details.append(svg);
    const shape=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;svg.append(n);return n;};
    shape('title',{id:id+'-title'},'Two approximate author-reported model axis-distance states');
    shape('desc',{id:id+'-desc'},'From about 100 to about 130 kilometres in the 1960–2014 western Pacific OFES analysis. These summary states are not the time-series extrema, full current width or exact dated observations.');
    for(const value of [0,75,150]){const x=60+value/150*200;shape('line',{x1:x,x2:x,y1:30,y2:135,stroke:'#c5cdd1'});shape('text',{x,y:20,'text-anchor':'middle',fill:'#203642','font-size':16},value+' km');}
    rows.forEach((row,i)=>{
      const y=45+i*48,c=row.model_axis_spread_context;
      const matching=!options.matchingIds||options.matchingIds.includes(row.id);
      shape('text',{x:0,y:y+17,fill:'#203642','font-size':16},c.reported_change_state==='from'?'From':'To');
      shape('rect',{x:60,y,width:row.approximate_width_km/150*200,height:23,fill:matching?'#176b82':'#71828a','data-model-scale-id':row.id,'data-value-km':row.approximate_width_km});
      shape('text',{x:270,y:y+17,fill:'#203642','font-size':16},row.approximate_width_km+' km');
    });
    const table=add('table',undefined,details);table.style.cssText='width:100%;min-width:0;max-width:100%;table-layout:fixed;font-size:inherit';
    add('caption','Approximate reported states; exact state dates are unextracted',table);
    const header=add('tr',undefined,add('thead',undefined,table));
    for(const name of ['Reported state','Scale W (km)',...(options.matchingIds?['Query match']:[])])add('th',name,header).scope='col';
    const body=add('tbody',undefined,table);
    for(const row of rows){
      const tr=add('tr',undefined,body);tr.dataset.modelScaleId=row.id;
      add('td',row.model_axis_spread_context.reported_change_state==='from'?'From':'To',tr);add('td','~'+row.approximate_width_km,tr);
      if(options.matchingIds)add('td',options.matchingIds.includes(row.id)?'Matches query':'Source context',tr);
      if(row.id===options.selectedId)tr.style.fontWeight='bold';
    }
    add('p','Definition: integrate zonal velocity over 0–150 m, retain the eastward weight, find its weighted latitude axis, then average the absolute distance from that axis. Latitude integration is 0–10°N; the published diagnostic averages 135–155°E and uses a 13-month running mean.',details);
    add('p','The original Figure 8 plots latitude degrees. The 100 and 130 km summaries above are transcribed directly from the authors’ conclusion; OSW has not converted the plotted curve, reproduced the estimator from model fields or assigned exact endpoint dates.',details);
    add('p','Model context: OFES 1960–2014 with NCEP–NCAR forcing, 0.1° grid and 54 vertical levels. The two states do not bound every value in the plotted series. Width uncertainty, whole-current width and annual extrema remain unknown.',details);
    add('p','W is a mean absolute axis distance. It is not RMS spread, Gaussian standard deviation, a half-peak span or a full width obtained by doubling. The paper’s wind-forcing comparison limits claims of a uniquely verified long-term observational trend.',details);
    add('p','The separate 2013 OSCAR component diagnostic at 140°W retains its own method and unresolved physical-width gates.',details);
    const source=add('a','Inspect exact model-scale source records',add('p',undefined,details));
    source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:rows[0].source_file,pointer:'/measurements',limit:100}));
    const original=add('a','Original paper · university-hosted copy',add('p',undefined,details));original.href=rows[0].source_url;
    add('p',rows[0].source_citation,details);
    const doi=add('a','Publisher DOI',add('p',undefined,details));doi.href='https://doi.org/10.1002/2016JC012190';
    for(const row of rows){
      const label='Inspect reported '+row.model_axis_spread_context.reported_change_state+' state';
      if(inspect){const button=add('button',label,add('p',undefined,details));button.type='button';button.onclick=()=>inspect('widths',row.id);}
      else{const anchor=add('a',label,add('p',undefined,details));anchor.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'widths',filters:[{field:'id',op:'eq',value:row.id}],limit:100}));}
    }
  };
})();
