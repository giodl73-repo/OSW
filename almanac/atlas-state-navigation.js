"use strict";
window.initAtlasStateNavigation = async function(svg, api) {
  const ns='http://www.w3.org/2000/svg';
  const note=document.getElementById('atlas-state-map-note');
  try {
    const response=await fetch('../figures/ocean-motion-dashboard-ground.svg');
    if(!response.ok)throw Error('State shapes unavailable');
    const source=new DOMParser().parseFromString(await response.text(),'image/svg+xml');
    if(source.querySelector('parsererror'))throw Error('Invalid state shapes');
    const groups=[...source.querySelectorAll('g[data-code]')];
    if(groups.length!==56||new Set(groups.map(group=>group.dataset.code)).size!==56)throw Error('Incomplete state shapes');
    if(groups.some(group=>!group.dataset.name||!group.querySelector('path[d]')||[...group.querySelectorAll('path')].some(path=>!path.getAttribute('d')?.trim())))throw Error('Missing state geometry');
    const maskSource=source.querySelector('#interactive-ocean-only');
    if(!maskSource)throw Error('Ocean mask unavailable');
    const defs=document.createElementNS(ns,'defs'),mask=document.createElementNS(ns,'mask');
    mask.id='atlas-state-ocean-mask';
    for(const shape of maskSource.children) {
      if(!['rect','path'].includes(shape.localName))continue;
      const clone=document.createElementNS(ns,shape.localName);
      for(const name of ['d','x','y','width','height','fill','fill-rule'])if(shape.hasAttribute(name))clone.setAttribute(name,shape.getAttribute(name));
      mask.append(clone);
    }
    const clip=document.createElementNS(ns,'clipPath'),ocean=document.createElementNS(ns,'path');
    clip.id='atlas-state-ocean-clip';
    ocean.setAttribute('d','M60 90H1540V830H60Z '+[...maskSource.querySelectorAll('path')].map(path=>path.getAttribute('d')).join(' '));
    ocean.setAttribute('clip-rule','evenodd');clip.append(ocean);
    defs.append(mask,clip);svg.insertBefore(defs,document.getElementById('route-atlas-features'));
    const layer=document.createElementNS(ns,'g');layer.id='atlas-state-navigation';
    layer.setAttribute('mask','url(#atlas-state-ocean-mask)');layer.setAttribute('clip-path','url(#atlas-state-ocean-clip)');svg.insertBefore(layer,document.getElementById('route-atlas-features'));
    for(const group of groups) {
      const button=document.createElementNS(ns,'g');button.classList.add('atlas-state-region');
      button.dataset.stateCode=group.dataset.code;button.setAttribute('role','button');button.setAttribute('tabindex','0');
      const label=`${group.dataset.code} · ${group.dataset.name} · show recorded current and eddy links`;
      button.setAttribute('aria-label',label);const title=document.createElementNS(ns,'title');title.textContent=label;button.append(title);
      for(const sourcePath of group.querySelectorAll('path')) {
        const path=document.createElementNS(ns,'path');path.setAttribute('d',sourcePath.getAttribute('d'));path.setAttribute('vector-effect','non-scaling-stroke');button.append(path);
      }
      button.addEventListener('click',()=>{if(!api.dragged())api.select(group.dataset.code);});
      button.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();api.select(group.dataset.code);}});
      layer.append(button);
    }
    note.textContent='Select an OSW region on the map to see its recorded current and eddy links. State shapes are approximate cartograms; current paths and eddy markers remain individually selectable. State names are available on hover and in keyboard labels.';
    return code=>{
      for(const button of layer.children)button.setAttribute('aria-pressed',String(button.dataset.stateCode===code));
    };
  } catch(_) {
    note.textContent='Clickable state shapes are unavailable. Use the OSW state selector in the inventory index.';
    return ()=>{};
  }
};
