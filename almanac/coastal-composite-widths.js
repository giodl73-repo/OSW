"use strict";
window.renderCoastalCompositeWidths=(()=>{
  const ns='http://www.w3.org/2000/svg',images=new Map();
  function node(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function svgNode(tag,attrs,parent,text){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
  function link(text,href,parent){const n=node('a',text,parent);n.href=href;return n;}
  function scroll(parent,minWidth){const n=node('div',undefined,parent);n.className='coastal-composite-scroll';n.style.cssText='max-width:100%;overflow-x:auto';n.tabIndex=0;n.dataset.minWidth=minWidth;n.setAttribute('aria-label','Scrollable source chart or table');n.addEventListener('focus',()=>{n.style.outline='3px solid #ad7406';});n.addEventListener('blur',()=>{n.style.outline='';});return n;}
  function checkedImage(source){
    const key=source.asset_sha256;
    if(!images.has(key))images.set(key,(async()=>{
      const response=await fetch('../'+source.asset_file);if(!response.ok)throw Error('Source figure request failed');
      const bytes=await response.arrayBuffer();
      const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
      if(digest!==key||bytes.byteLength!==source.asset_bytes)throw Error('Source figure integrity check failed');
      return URL.createObjectURL(new Blob([bytes],{type:'image/png'}));
    })());
    return images.get(key);
  }
  return function(parent,scene,selectedId=null,inspect=null){
    if(!scene||scene.kind!=='coastal_composite_widths')return;
    const panel=node('section',undefined,parent);panel.className='coastal-composite-widths';panel.style.cssText='min-width:0;max-width:100%';
    node('h4',scene.title,panel);node('p',scene.scope,panel);node('p',scene.method,panel);
    const frame=scroll(panel,760),svg=svgNode('svg',{viewBox:scene.view_box.join(' '),role:'img','aria-label':'Seven spatial composite widths in kilometres. Select a section from the table below.'},frame);
    svg.style.cssText='display:block;width:760px;max-width:none;font-size:16px;background:#f6f5ef;color:#102f3b';
    for(const tick of scene.ticks){const x=125+525*tick/scene.axis_max_km;svgNode('line',{x1:x,x2:x,y1:32,y2:350,stroke:'#d4dde0'},svg);svgNode('text',{x,y:373,'text-anchor':'middle',fill:'#102f3b'},svg,tick+' km');}
    for(const bar of scene.bars){
      const active=selectedId?bar.id===selectedId:bar.matching;
      const group=svgNode('g',{'data-section-id':bar.id,'data-selected':String(active)},svg);
      svgNode('text',{x:12,y:bar.y+18,fill:'#102f3b'},group,'Section '+bar.section_number);
      svgNode('rect',{x:bar.x,y:bar.y,width:bar.width,height:bar.height,fill:active?'#176b82':'#8caaae',stroke:active?'#102f3b':'none','stroke-width':2},group);
      svgNode('text',{x:bar.x+bar.width+8,y:bar.y+18,fill:'#102f3b'},group,bar.width_km+' km');
    }
    node('p','Bars share a zero-based width axis. Pale bars provide source context outside the selection. No width error bars are supplied.',panel);
    const tableFrame=scroll(panel,920),table=node('table',undefined,tableFrame);table.style.cssText='min-width:920px;font-size:14px';
    node('caption','Published section properties · Tables 1–2 and section 4',table);
    const head=node('tr',undefined,node('thead',undefined,table));
    for(const text of ['Section','Width km','Mean depth m','Depth range m','Transport Sv','Winter profiles','Summer profiles','Transect km','Median bin km','Mean / peak velocity m/s']){const th=node('th',text,head);th.scope='col';}
    const body=node('tbody',undefined,table);
    for(const bar of scene.bars){
      const row=bar.record,p=row.original_regional_context.source_properties,tr=node('tr',undefined,body);tr.dataset.sectionId=bar.id;
      const cell=node('th',undefined,tr);cell.scope='row';
      const selected=selectedId?bar.id===selectedId:bar.matching;
      if(selectedId&&selected)tr.setAttribute('aria-current','true');
      if(inspect){const button=node('button','Section '+bar.section_number,cell);button.type='button';button.addEventListener('click',()=>inspect('widths',row.id));}
      else {const a=link('Section '+bar.section_number,'seasons.html?current=antarctic-coastal&phase='+encodeURIComponent(bar.id),cell);a.style.cssText='display:inline-flex;align-items:center;min-height:44px';}
      node('small',selectedId?(selected?'Selected':'Other section'):(selected?'Query match':'Source context'),cell);
      for(const text of [bar.width_km,p.source_mean_depth_m,p.source_depth_range_m.join('–'),p.source_alongshore_transport_sv,p.winter_profiles,p.summer_profiles,p.cross_shelf_section_length_km,p.moving_median_bin_km,p.source_mean_geostrophic_velocity_m_s+' / '+p.source_peak_geostrophic_velocity_m_s])node('td',String(text),tr);
    }
    node('p',scene.sampling_note,panel);node('p',scene.property_note,panel);
    const figure=node('figure',undefined,panel);figure.style.cssText='margin:1em 0;max-width:100%;min-width:0';
    const mapFrame=scroll(figure,720),status=node('p','Verifying published source map…',mapFrame);status.className='coastal-source-image-status';status.setAttribute('role','status');
    checkedImage(scene.source_image).then(url=>{
      if(!panel.isConnected)return;
      const img=node('img',undefined,mapFrame);img.className='coastal-source-image';img.src=url;
      img.alt='Published Figure 3: seal-profile locations for composite sections 1–7 along the West Antarctic Peninsula and Bellingshausen Sea. Profile locations do not mark current boundaries.';
      img.width=scene.source_image.pixel_dimensions[0];img.height=scene.source_image.pixel_dimensions[1];
      img.style.cssText='display:block;width:100%;min-width:720px;max-width:100%;height:auto';status.textContent='Source map verified';
    }).catch(error=>{status.textContent=error.message+'. Source map unavailable.';status.dataset.error='true';});
    const caption=node('figcaption',scene.source_image.figure_role+' ',figure);
    link('Figure 3 · Schubert et al. (2021)',scene.source_url,caption);caption.append(document.createTextNode(' · '));link('CC BY 4.0','https://creativecommons.org/licenses/by/4.0/',caption);
    node('p',scene.source_citation,panel);
    const original=node('p',undefined,panel);link('Read the original paper (PDF)','../'+scene.source_image.source_document_file,original);
    link('Inspect the published values and extraction scope','query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.audit_file,pointer:'/measurements',limit:50})),panel);
    panel.append(document.createTextNode(' · '));
    link('Query the seven width records','query.html?q='+encodeURIComponent(JSON.stringify({collection:'widths',filters:[{field:'current_id',op:'eq',value:'antarctic-coastal'}],limit:100})),panel);
  };
})();
