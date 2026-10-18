"use strict";
window.renderKuroshioFilteredWidths=function(container,scene,inspect,options={}){
  if(!scene||scene.kind!=='kuroshio_filtered_width_curve')return;
  const section=document.createElement('section');section.className='kuroshio-filtered-width';section.style.cssText='max-width:100%;min-width:0;border:1px solid #587681;padding:.8rem;margin:1rem 0;box-sizing:border-box';container.append(section);
  const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const link=(label,href,parent=section)=>{const n=node('a',label,parent);n.href=href;n.style.cssText='display:inline-flex;align-items:center;min-height:44px';return n;};
  node('h4',scene.title);node('p',scene.scope);
  node('p',`${scene.sample_count} readings · 1993–2008 · half-year-filtered curve · ±5 km graphical reading allowance`);
  const details=node('details','');details.open=Boolean(options.open);const summary=node('summary','View filtered curve, readings and source',details);summary.style.cssText='min-height:44px;padding:.35rem 0;box-sizing:border-box';
  const figure=node('figure','',details);figure.style.margin='1rem 0';const img=node('img',undefined,figure);img.src='../'+scene.figure_file;img.alt=scene.figure_alt;img.loading='lazy';img.style.cssText='display:block;width:100%;height:auto;background:white';
  node('figcaption',scene.figure_alt,figure);link('Open filtered-width figure at full size','../'+scene.figure_file,figure);
  for(const text of scene.cautions)node('p',text,details);
  const label=node('label','Year on published plot ',details),select=node('select',undefined,label);select.style.cssText='min-height:44px;max-width:100%';
  const years=[...new Set(scene.samples.map(s=>s.plot_year_label))];for(const year of years){const option=node('option',String(year),select);option.value=String(year);}
  const status=node('p','',details);status.setAttribute('aria-live','polite');
  const scroll=node('div','',details);scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Filtered width readings; scroll horizontally to compare columns');scroll.style.cssText='max-width:100%;overflow-x:auto';
  const table=node('table','',scroll);table.style.cssText='width:100%;min-width:420px;border-collapse:collapse;font-size:.9rem';
  const caption=node('caption','Month labels are graphical positions, not raw monthly means or exact observation dates.',table);caption.style.textAlign='left';
  const tr=node('tr','',node('thead','',table));for(const title of ['Plot position','Reading (km)','Graphical interval (km)','Inspect']){const th=node('th',title,tr);th.scope='col';th.style.cssText='padding:.4rem;text-align:left';}
  const body=node('tbody','',table);
  const sampleQuery=id=>({collection:'width_samples',filters:[{field:'id',op:'eq',value:id}],limit:1});
  function renderYear(){body.replaceChildren();const rows=scene.samples.filter(s=>s.plot_year_label===Number(select.value));status.textContent=`${rows.length} filtered-curve plot readings for ${select.value}; filtering and source uncertainty remain distinct from the graphical allowance.`;
    for(const sample of rows){const row=node('tr','',body);node('td',sample.sample_label,row);node('td',sample.value_km===null?'Unresolved':String(sample.value_km),row);node('td',sample.plot_reading_interval_km?.join('–')||'Unknown',row);const cell=node('td','',row);
      if(inspect){const button=node('button','Inspect reading',cell);button.type='button';button.setAttribute('aria-label','Inspect reading '+sample.sample_label);button.style.minHeight='44px';button.onclick=()=>inspect('width_samples',sample.id);}
      else link('Inspect reading','query.html?q='+encodeURIComponent(JSON.stringify(sampleQuery(sample.id))),cell).setAttribute('aria-label','Inspect reading '+sample.sample_label);
      for(const cell of row.children)cell.style.cssText+=';padding:.4rem;border-bottom:1px solid #587681';
    }
  }
  select.addEventListener('change',renderYear);renderYear();
  const query={collection:'width_samples',filters:[{field:'sample_family',op:'eq',value:scene.sample_family}],sort:{field:'plot_year',direction:'asc'},limit:250};
  link('Query all 192 filtered plot readings','query.html?q='+encodeURIComponent(JSON.stringify(query)),node('p','',details));
  link('Inspect exact filtered-width source data','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:'',limit:100})),node('p','',details));
  link('Published source',scene.source_url,node('p','',details));node('p',scene.source_citation+' '+scene.source_locator,details);
};
