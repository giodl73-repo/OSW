/* Render native source-image viewports without constructing geographic geometry. */
window.renderEddySourcePanels = function(parent,scene) {
  if(!scene||scene.kind!=='named_eddy_source_panels')return;
  const add=(tag,text,host=parent)=>{const el=document.createElement(tag);if(text!=null)el.textContent=text;host.append(el);return el;};
  const figure=add('figure',null);figure.className='eddy-source-panels';figure.dataset.engine=scene.engine;
  figure.style.margin='1rem 0';figure.style.minWidth='0';
  add('h3',`${scene.name} · dated source panels`,figure);
  add('p',`${scene.panels.length} regional field panels during this shedding event. Select a date to inspect the original source view.`,figure);
  add('p',scene.field_definition,figure);
  const controls=add('div',null,figure);controls.style.display='flex';controls.style.flexWrap='wrap';controls.style.gap='.5rem';
  const previous=add('button','Previous date',controls);previous.type='button';
  const label=add('label','Source panel date ',controls);const select=add('select',null,label);select.className='eddy-source-panel-date';
  for(const row of scene.panels){const option=add('option',row.observation_date,select);option.value=row.id;}
  const next=add('button','Next date',controls);next.type='button';
  const status=add('p',null,figure);status.className='eddy-source-panel-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const ns='http://www.w3.org/2000/svg';const svg=document.createElementNS(ns,'svg');
  svg.setAttribute('role','img');svg.style.width='100%';svg.style.maxWidth='528px';svg.style.display='block';figure.append(svg);
  const image=document.createElementNS(ns,'image');image.setAttribute('href',scene.image_href);image.setAttribute('x','0');image.setAttribute('y','0');
  image.setAttribute('width',scene.image_size_pixels[0]);image.setAttribute('height',scene.image_size_pixels[1]);svg.append(image);
  const link=add('a','Inspect this panel’s source row',figure);
  function update(){const index=select.selectedIndex;const row=scene.panels[index];
    svg.setAttribute('viewBox',row.crop_pixels_xywh.join(' '));svg.setAttribute('aria-label',`${scene.name} shedding event, ${row.observation_date}, Figure ${scene.figure_number} panel ${index+1}. Source crop; colors show deep reference pressure and the bold curve is the surface Loop Current contour. No numerical eddy boundary extracted.`);
    status.textContent=`${row.observation_date} · source panel ${index+1} of ${scene.panels.length} · row ${row.source_row}, column ${row.source_column}. Ring geometry and physical OSW state relations unresolved.`;
    link.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_document,pointer:scene.source_pointer+'/panels/'+index,limit:25}));
    previous.disabled=index===0;next.disabled=index===scene.panels.length-1;
  }
  select.addEventListener('change',update);previous.addEventListener('click',()=>{select.selectedIndex--;update();});next.addEventListener('click',()=>{select.selectedIndex++;update();});update();
  add('figcaption',`${scene.source_caption} Selected panel is a cropped source view. See the complete figure below for longitude/latitude axes and the original color legend.`,figure);
  add('p',scene.claim_limit,figure);
  add('p',`Contour value printed in the Methods: ${scene.contour_definition.source_literal}. The physical unit remains unresolved; no numerical contour is reconstructed.`,figure);
  const full=add('details',null,figure);add('summary','Complete original figure, axes and color legend',full);
  const scroll=add('div',null,full);scroll.style.overflowX='auto';scroll.tabIndex=0;scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Complete original figure; scroll horizontally to inspect');
  const original=add('img',null,scroll);original.src=scene.image_href;original.alt=`Complete Figure ${scene.figure_number}: ${scene.name} event regional maps on ${scene.panels.length} printed dates, geographic axes, CPIES locations, bathymetry, surface Loop Current contours and original SSH_ref color legend. ${scene.claim_limit}`;
  original.style.width=scene.image_size_pixels[0]+'px';original.style.maxWidth='none';original.style.height='auto';
  const originalLink=add('a','Open original figure image',full);originalLink.href=scene.image_href;
  add('p',scene.display_transformation+' '+scene.copyright,figure);
  const source=add('a',scene.source_citation,figure);source.href=scene.source_url;
  add('span',' · ',figure);const license=add('a','CC BY 4.0',figure);license.href=scene.license_url;
};
