"use strict";
window.renderCurrentWidthSourceReview=function(container,scene,inspect){
  if(!scene)return;
  const review=scene.review,source=scene.source;
  const section=document.createElement('section');section.className='current-width-source-review';section.dataset.current=scene.current_id;
  section.style.cssText='border:1px solid #587681;padding:.8rem;margin:1rem 0;max-width:100%;box-sizing:border-box';container.append(section);
  const add=(tag,text,parent=section)=>{const n=document.createElement(tag);n.textContent=text;parent.append(n);return n;};
  add('h4',scene.label+' · width evidence unresolved');
  const status=add('dl','');status.style.cssText='display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:.35rem .8rem;margin:.6rem 0';
  for(const [label,value] of [['Current width','Unknown'],['Annual width range','Unknown'],['New measurement','None admitted']]){
    const term=add('dt',label,status),valueNode=add('dd',value,status);valueNode.style.margin='0';valueNode.style.fontWeight='600';
  }
  add('p',review.finding);
  const details=add('details','');
  const summary=add('summary','Source method and next evidence',details);summary.style.cssText='min-height:44px;padding:.35rem 0;box-sizing:border-box';
  if(review.cross_source_guard)add('p','The 100 km value in the separate 1997 comparison belongs to the western Agulhas Front. It does not establish the eastern current width. That comparison used parsed text; its original pages were not visually reviewed.',details);
  if(review.control_volume_context)add('p','The selected box lies 3/8° north and south of the 700 m isobath west of Portland. The contour locates an analysis domain; it is not a 700 m sampling layer or a pair of measured current edges.',details);
  if(review.temporal_product_guard)add('p',review.temporal_product_guard,details);
  add('p','Next evidence needed: '+review.next_required_evidence,details);
  add('p',scene.current_id==='south-indian'?'Original conclusion on printed page 430 visually reviewed. OCR searched all 10 pages for discovery; full visual review is not claimed.':'Appendix B/C on original page 17 visually reviewed. Dataset and method context came from parsed text; full visual review of all 20 pages is not claimed.',details);
  const links=add('p','',details);links.style.cssText='display:flex;flex-wrap:wrap;gap:.5rem 1rem';
  const receipt=add('a','Inspect original-source receipt',links);receipt.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:source.acquisition_file,pointer:'',limit:100}));
  const paper=add('a','Open primary paper',links);paper.href=source.source_url;
  const scope=add('a','Inspect review and source limits');scope.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:scene.source_pointer,limit:100}));
  for(const link of [scope,receipt,paper])link.style.cssText='min-height:44px;display:inline-flex;align-items:center';
  if(inspect){const button=add('button','Inspect source-review record');button.type='button';button.style.minHeight='44px';button.onclick=()=>inspect('diagnostics',scene.diagnostic_id);}
};
