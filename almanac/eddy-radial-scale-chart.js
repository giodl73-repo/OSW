"use strict";
window.renderEddyRadialScales=function(container,audit){
  const rows=audit.measurements,figure=document.createElement('figure');figure.className='eddy-radial-scales';figure.style.cssText=container.matches('td,th')?'margin:1rem 0;width:450px':'margin:1rem 0;max-width:650px';container.append(figure);
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);svg.setAttribute('viewBox','0 0 500 225');svg.setAttribute('role','img');svg.setAttribute('aria-label','Astrid, March 2000 study: 120 km maximum-speed radius; 140 km integration limit. Different model definitions, not a seasonal range or measured footprint.');svg.style.cssText='display:block;width:100%;background:#f6f5ef;color:#102f3b';
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);};
  rows.forEach((r,i)=>{const y=40+i*80;add('text',{x:20,y,'font-size':26,fill:'#102f3b'},`${r.value_km} km ${i?'integration limit':'maximum-speed radius'}`);add('line',{x1:25,x2:475,y1:y+25,y2:y+25,stroke:'#899ba3'});add('circle',{cx:25+450*r.value_km/150,cy:y+25,r:7,fill:'#176b82'});});
  for(const v of [0,150])add('text',{x:v?475:25,y:210,'font-size':26,'text-anchor':v?'end':'start',fill:'#102f3b'},`${v} km`);
  const caption=document.createElement('figcaption');caption.textContent='March 2000 study · two-layer diagnostic model, 10 °C thermocline. Different definitions; numerical uncertainty unknown. These do not establish a closed footprint, diameter, area, seasonal change or OSW state containment.';figure.append(caption);
  const source=document.createElement('a');source.textContent='Query radius definitions and source audit';source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:'research/astrid-2000-radial-scale-scope-audit.json',pointer:'/measurements',limit:10}));figure.append(source);
};
window.renderPublishedRingRadii=function(container,evidence,sourceFile,owner){
  const figure=document.createElement('figure');figure.className='published-ring-radii';figure.style.cssText=container.matches('td,th')?'margin:1rem 0;width:450px':'margin:1rem 0;max-width:650px';container.append(figure);
  const rows=evidence.measurements,ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);
  const height=rows.length*110+45;
  svg.setAttribute('viewBox',`0 0 500 ${height}`);svg.setAttribute('role','img');
  svg.setAttribute('aria-label',`${evidence.name}: published altimetric equivalent-radius source claims. Filled points have consistent values; hollow points retain unresolved disagreements. Not annual extrema, a confidence interval or a closed footprint.`);
  svg.style.cssText='display:block;width:100%;background:#f6f5ef;color:#102f3b';
  const add=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text)e.textContent=text;svg.append(e);return e;};
  const x=value=>25+450*value/100;
  rows.forEach((row,i)=>{
    const base=i*110,values=[...new Set(row.source_claims.map(c=>c.value_km))].sort((a,b)=>a-b);
    add('text',{x:20,y:base+25,'font-size':26,fill:'#102f3b'},`${row.period_label} · ${row.value_km===null?'unresolved':row.value_km+' km'}`);
    add('line',{x1:25,x2:475,y1:base+55,y2:base+55,stroke:'#899ba3'});
    values.forEach((value,j)=>{
      const point=add('circle',{cx:x(value),cy:base+55,r:6,fill:row.radius_conflict?'#f6f5ef':'#176b82',stroke:'#176b82','stroke-width':2});
      point.dataset.measurementId=row.id;point.dataset.valueKm=value;
      if(row.radius_conflict)add('text',{x:x(value),y:base+(j?45:86),'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${value}`);
    });
  });
  for(const v of[0,100])add('text',{x:x(v),y:height-10,'font-size':26,'text-anchor':v?'end':'start',fill:'#102f3b'},`${v} km radius`);
  const caption=document.createElement('figcaption');caption.textContent='Separate source section records, not a continuous time series. Filled points: consistent reported radius. Hollow points: conflicting source values, not an uncertainty interval. Numerical radius uncertainty unknown. Equivalent-area circles do not establish an occupied footprint, diameter, annual cycle or OSW state containment.';figure.append(caption);
  const list=document.createElement('ul');figure.append(list);
  for(const row of rows){const item=document.createElement('li');item.textContent=`${row.period_label}: ${row.source_claims.map(c=>`${c.value_km} km (${c.reported_period}; ${c.source_locator})`).join('; ')}${row.date_conflict?' · year conflict unresolved; body/table/panel support 2010, caption says 2019.':''}`;list.append(item);}
  const source=document.createElement('a');source.textContent='Query radius claims and source conflicts';source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:sourceFile,pointer:'/entities/'+owner+'/measurements',limit:20}));figure.append(source);
};
