"use strict";
window.renderPublishedCoordinateSpan=function(container,row,inspect){
  const context=row?.published_section_context;if(!context)return;
  const figure=document.createElement('figure');figure.className='published-coordinate-section-span';figure.style.margin='0';container.append(figure);
  const html=(tag,text)=>{const n=document.createElement(tag);n.textContent=text;figure.append(n);return n;};
  html('h4','Published local section span');
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');figure.append(svg);
  svg.setAttribute('viewBox','0 0 500 150');svg.setAttribute('role','img');
  svg.setAttribute('aria-label',`${row.name}: approximately ${row.approximate_width_km} km nominal section span at 37 N, calculated by OSW between published limits 14.8 W and 13.5 W using WGS84. Not a whole-current or flow-normal width; physical uncertainty unknown.`);
  svg.style.cssText='display:block;width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
  const mark=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;svg.append(n);};
  mark('text',{x:250,y:43,'text-anchor':'middle','font-size':32,fill:'#102f3b'},`~${row.approximate_width_km} km`);
  mark('line',{x1:35,x2:465,y1:78,y2:78,stroke:'#176b82','stroke-width':5});
  for(const x of [35,465])mark('line',{x1:x,x2:x,y1:66,y2:90,stroke:'#102f3b','stroke-width':2});
  mark('text',{x:35,y:126,'font-size':28,fill:'#102f3b'},'14.8 W');
  mark('text',{x:465,y:126,'text-anchor':'end','font-size':28,fill:'#102f3b'},'13.5 W');
  html('figcaption','ORCA northern section at 37 N, stations 19–23. The coordinates are source-reported; the kilometre separation is an OSW WGS84 calculation. This is a section-distance diagram, not a current axis or geographic footprint.');
  html('p',row.time_convention);
  html('p',row.layer);
  html('p','Whole-current and flow-normal widths, physical uncertainty and annual range remain unknown. Source coordinate datum is unresolved; WGS84 is a calculation convention.');
  html('p','Primary publisher HTML and institutional PDF parsed text reviewed. Original PDF bytes and page images have not been acquired.');
  const source=html('a','Inspect section limits, calculation and source');
  source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:context.audit_file,pointer:'/measurement',limit:100}));
  source.style.cssText='display:block;padding:.6rem 0;min-height:44px';
  const paper=html('a','Open primary paper');paper.href=row.source_url;paper.style.cssText='display:block;padding:.6rem 0;min-height:44px';
  if(inspect){const button=html('button','Inspect measurement');button.type='button';button.style.minHeight='44px';button.onclick=()=>inspect('widths',row.id);}
};
