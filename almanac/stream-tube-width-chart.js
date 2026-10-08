"use strict";
window.renderStreamTubeWidths=function(container,records){
  const rows=records.filter(r=>r.phase_kind==='synoptic_stream_tube_section');if(!rows.length)return;
  const node=(tag,text,parent=container)=>{const e=document.createElement(tag);if(text)e.textContent=text;parent.append(e);return e;};
  node('h4','August 2015 · stream-tube definitions');
  const figure=node('figure');figure.style.margin='0';
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);
  svg.classList.add('stream-tube-width-chart');svg.setAttribute('viewBox',`0 0 500 ${rows.length*80+45}`);svg.setAttribute('role','img');
  svg.setAttribute('aria-label',rows.map(r=>`${r.phase_label}: ${r.approximate_width_km} kilometres${r.stream_tube_context.threshold_sensitivity_cases.length?', threshold sensitivity cases '+r.stream_tube_context.threshold_sensitivity_cases.map(c=>`${c.width_km} kilometres at ${c.velocity_m_s} metres per second`).join(', '):', transport constrained'}`).join('; ')+'. Separate definitions, not seasonal variation or confidence intervals. Section A shares a single source tube.');
  svg.style.cssText='display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  const x=v=>40+420*v/75;
  rows.forEach((r,i)=>{
    const c=r.stream_tube_context,y=58+i*80;
    add('text',{x:16,y:y-26,'font-size':26,fill:'#102f3b'},`${c.section_id} · tube ${c.stream_tube} · ${r.approximate_width_km} km`);
    const cases=c.threshold_sensitivity_cases;
    if(cases.length){add('line',{x1:x(cases[0].width_km),x2:x(cases[1].width_km),y1:y,y2:y,stroke:'#176b82','stroke-width':3,'stroke-dasharray':'5 4'});for(const item of cases)add('line',{x1:x(item.width_km),x2:x(item.width_km),y1:y-7,y2:y+7,stroke:'#176b82','stroke-width':2});}
    add(c.stream_tube===1?'circle':'rect',c.stream_tube===1?{cx:x(r.approximate_width_km),cy:y,r:6,fill:'#176b82'}:{x:x(r.approximate_width_km)-6,y:y-6,width:12,height:12,fill:'#176b82'});
  });
  const y=rows.length*80+8;add('line',{x1:40,x2:460,y1:y,y2:y,stroke:'#526c77'});
  for(const v of [0,25,50,75])add('text',{x:x(v),y:y+25,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);
  node('figcaption','Circles: tube 1 at 0.04 m/s. Dashed spans: its two threshold cases, 0.02 and 0.08 m/s. Squares: tube 2 with a 1.3 Sv transport constraint (within 10%). These are alternative boundaries, not confidence intervals or seasonal changes. A1 and A2 share one source tube.',figure);
  const table=node('table');table.className='stream-tube-width-table';table.style.cssText='width:100%;min-width:0;table-layout:fixed;overflow-wrap:anywhere';
  const header=node('tr',null,node('thead',null,table));for(const text of ['Section / tube','Width','Threshold cases']){const th=node('th',text,header);th.scope='col';}
  const body=node('tbody',null,table);
  for(const r of rows){const c=r.stream_tube_context,tr=node('tr',null,body),th=node('th',`${c.section_id} / ${c.stream_tube}`,tr);th.scope='row';node('td',`${r.approximate_width_km} km`,tr);node('td',c.threshold_sensitivity_cases.length?c.threshold_sensitivity_cases.map(v=>`${v.velocity_m_s} m/s: ${v.width_km} km`).join('; '):'Transport constrained; width error unknown',tr);}
  node('p','AW means Atlantic Water; 1 Sv is one million cubic metres per second. Its property-defined layer varies with position and seabed. Exact section dates and geographic width edges remain unextracted. This snapshot establishes no annual width range, occupied footprint or whole-current length.');
  const link=node('a','Query all six width records');link.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'widths',filters:[{field:'current_id',op:'eq',value:'west-spitsbergen'}],limit:100}));
};
