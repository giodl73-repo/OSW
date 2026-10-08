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
