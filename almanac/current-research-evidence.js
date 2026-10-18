"use strict";
window.renderCurrentResearchEvidence=function(container,scene,inspect,options={}){
  if(!scene)return;
  const section=document.createElement('section');section.className='current-research-evidence';section.dataset.current=scene.current_id;
  section.style.cssText='border:1px solid #587681;padding:.8rem;margin:1rem 0;max-width:100%;box-sizing:border-box';container.append(section);
  const add=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  add('h4',scene.title);
  const facts=add('dl','');facts.style.cssText='display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.35rem .8rem;margin:.6rem 0;overflow-wrap:anywhere';
  for(const fact of scene.facts){const term=add('dt',fact.label,facts),value=add('dd',fact.value,facts);value.style.cssText='margin:0;font-weight:600';}
  add('p',scene.finding);
  const details=add('details','');if(options.open)details.open=true;
  const summary=add('summary','View analysis, method and sources',details);summary.style.cssText='min-height:44px;padding:.35rem 0;box-sizing:border-box';
  const figure=add('figure','',details);figure.style.margin='1rem 0';
  const image=add('img',undefined,figure);image.src='../'+scene.figure_file;image.alt=scene.figure_alt;image.loading='lazy';image.style.cssText='display:block;width:100%;height:auto;background:white';
  const caption=add('figcaption',scene.figure_alt,figure);caption.setAttribute('aria-live','polite');
  const fullFigure=add('a','Open figure at full size',figure);fullFigure.href=image.src;fullFigure.style.cssText='display:inline-flex;align-items:center;min-height:44px';
  if(scene.additional_figures?.length){
    const label=add('label','Analysis view ',details),select=add('select',undefined,label);
    select.style.cssText='min-height:44px;max-width:100%';
    const choices=[{file:scene.figure_file,alt:scene.figure_alt,label:'Monthly regional maps'},
      ...scene.additional_figures.map((f,i)=>({...f,label:i===0?'Monthly mean sections':'Monthly temporal variability'}))];
    choices.forEach((choice,index)=>{const option=add('option',choice.label,select);option.value=String(index);});
    select.addEventListener('change',()=>{const choice=choices[Number(select.value)];image.src='../'+choice.file;image.alt=choice.alt;caption.textContent=choice.alt;fullFigure.href=image.src;});
  }
  for(const note of scene.notes)add('p',note,details);
  const table=add('table','',details);table.style.cssText='width:100%;min-width:0;max-width:100%;table-layout:fixed;border-collapse:collapse;overflow-wrap:anywhere;white-space:normal;font-size:.9rem';
  add('caption',scene.table.caption,table);const head=add('tr','',add('thead','',table));
  for(const title of scene.table.headers){const th=add('th',title,head);th.scope='col';th.style.cssText='padding:.35rem;text-align:left;border-bottom:1px solid #587681';}
  const body=add('tbody','',table);for(const row of scene.table.rows){const tr=add('tr','',body);for(const value of row){const td=add('td',value,tr);td.style.cssText='padding:.35rem;border-bottom:1px solid #587681';}}
  add('p','Next evidence needed: '+scene.next_evidence,details);
  const links=add('ul','',details);
  for(const source of scene.source_links){const link=add('a',source.label,add('li','',links));link.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:source.document,pointer:source.pointer,limit:100}));link.style.cssText='display:inline-flex;align-items:center;min-height:44px';}
  const original=add('a','Open primary source',details);original.href=scene.original_url;original.style.cssText='display:inline-flex;align-items:center;min-height:44px';
  if(inspect){const button=add('button','Inspect research evidence record');button.type='button';button.style.minHeight='44px';button.onclick=()=>inspect('diagnostics',scene.diagnostic_id);}
  else{const link=add('a','Open research query');link.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'diagnostics',filters:[{field:'id',op:'eq',value:scene.diagnostic_id}],limit:100}))+'#query-chart-section';link.style.cssText='display:inline-flex;align-items:center;min-height:44px';}
};
