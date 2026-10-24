"use strict";
window.renderAgulhasReportedDimensions=function(container,scene){
  if(scene?.kind!=='agulhas_reported_dimensions')return;
  const section=document.createElement('section');section.className='agulhas-reported-dimensions';section.style.cssText='border:1px solid #587681;padding:.8rem;margin:1rem 0;min-width:0;overflow-wrap:anywhere';container.append(section);
  const node=(tag,text,parent=section)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const link=(text,url)=>{const a=node('a',text,node('p'));a.href=url;a.style.cssText='display:inline-flex;align-items:center;min-height:44px';return a;};
  node('h4','Agulhas · separately scoped source descriptions');
  const image=node('img');image.src='../'+scene.figure_file;image.alt='Reported coastal extent about 1,000 km, an existing unranked variant; typical core description about 200 km. Separate quantities, with no geographic edges or annual range.';image.style.cssText='display:block;max-width:900px;width:100%;height:auto';
  const dl=node('dl');for(const [term,value]of [['Coastal extent','About 1,000 km; existing source variant, excluded from the whole-current length ranking.'],['Typical core description','About 200 km; contextual literature description, not independent observations.'],['Observation date / averaging period','Unspecified. The publication year is not a measurement date.'],['Width layer / boundaries / uncertainty','Unspecified. No numeric velocity cutoff, paired edges or error is supplied.'],['Comparison with ACT','The 219 km ACT time-mean section span is a different metric. These values do not define a 200–219 km range.']]){node('dt',term,dl).style.fontWeight='bold';node('dd',value,dl).style.margin='0 0 .6rem';}
  node('p','No whole-current width, annual range, geographic envelope or seasonal playback follows from these descriptions. The existing broader geographic floor and reference route have different length scopes.');
  link('Inspect the scoped core-width record','query.html?q='+encodeURIComponent(JSON.stringify({collection:'widths',filters:[{field:'id',op:'eq',value:scene.width_record.id}],limit:1})));
  link('Inspect exact dimension report','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:'',limit:100})));
  link('Original publication · CC BY 4.0','../'+scene.original_pdf);
  link('Publisher and citation',scene.source_url);
  link('Download effective measurement records','../'+scene.effective_measurements_file);
};
