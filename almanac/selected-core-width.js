"use strict";
window.renderSelectedCoreWidth=function(container,row,inspect,options={}){
  const c=row?.selected_core_context;if(!c)return;
  const panel=document.createElement('section');panel.className='selected-core-width';panel.dataset.selectedCoreId=row.id;
  panel.style.cssText='border:1px solid #587681;padding:.8rem;margin:1rem 0;box-sizing:border-box;max-width:100%;overflow-wrap:anywhere';container.append(panel);
  let content=panel;
  const add=(tag,text,parent=content)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  add('h4','West Spitsbergen Current: selected core width');
  const facts=add('dl','');facts.style.cssText='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.35rem .8rem';
  for(const [label,value] of [['Published local core width',row.approximate_width_km+' km'],['Reported standard deviation',row.width_standard_deviation_km+' km'],['Whole-current width','Unknown'],['Annual width range','Unknown']]){add('dt',label,facts);add('dd',value,facts).style.cssText='margin:0;font-weight:600';}
  add('p',row.standard_deviation_interpretation);
  const details=add('details','');details.open=!!inspect||!!options.open;
  const summary=add('summary','View published statistic, sampling and sources',details);summary.style.cssText='min-height:44px;padding:.35rem 0;box-sizing:border-box';content=details;
  const figure=add('figure','');figure.style.margin='1rem 0';const image=add('img',undefined,figure);image.src='../'+c.figure_file;image.alt='Published local WSC core width of 28 km with reported standard deviation 7 km, and three discontinuous mission sampling windows. Not annual extrema or geographic current edges.';image.loading='lazy';image.style.cssText='display:block;width:100%;height:auto;background:white';
  add('figcaption','Selected high-transport sections at 77.25 N. The whisker is reported standard deviation; it is not an observed minimum/maximum or confidence interval.',figure);
  const full=add('a','Open figure at full size',figure);full.href='../'+c.figure_file;full.style.cssText='display:inline-flex;align-items:center;min-height:44px';
  const table=add('table','');table.style.cssText='width:100%;min-width:0;max-width:100%;table-layout:fixed;border-collapse:collapse;white-space:normal;overflow-wrap:anywhere;font-size:.9rem';
  add('caption','Mission target-section windows from Table 1; counts describe all study sections, not the unextracted selected-width subset.',table);
  const tr=add('tr','',add('thead','',table));for(const title of ['ID','Start','End','Count']){const th=add('th',title,tr);th.scope='col';if(title==='ID')th.setAttribute('aria-label','Mission');if(title==='Count')th.setAttribute('aria-label','Number of study sections');th.style.cssText='text-align:left;padding:.3rem;border-bottom:1px solid #587681';}
  const body=add('tbody','',table);for(const w of c.section_windows){const tr=add('tr','',body);for(const value of [w.mission,w.start,w.end,w.sections])add('td',String(value),tr).style.cssText='padding:.3rem;border-bottom:1px solid #587681';}
  add('p',row.layer);add('p',row.boundary_rule);
  add('p','Glider hydrographic shear uses a satellite surface-current reference. The 2 km display grid uses a 40 km horizontal mapping scale. The exact selected section count, per-section widths and geographic edges are unextracted.');
  add('p','This statistic is separate from the 2015 stream-tube widths. Neither metric establishes a whole-current width or annual variation.');
  const source=add('a','Inspect published width and method');source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:100}));source.style.cssText='display:flex;align-items:center;min-height:44px';
  const paper=add('a','Original paper · CC BY 4.0');paper.href=row.source_url;paper.style.cssText='display:flex;align-items:center;min-height:44px';add('p',row.source_citation+' '+row.source_locator);
  if(inspect){const button=add('button','Inspect selected-core width record');button.type='button';button.style.minHeight='44px';button.onclick=()=>inspect('widths',row.id);}
  else{const link=add('a','Open selected-core width query');link.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'widths',filters:[{field:'id',op:'eq',value:row.id}],limit:100}))+'#query-chart-section';link.style.cssText='display:flex;align-items:center;min-height:44px';}
};
