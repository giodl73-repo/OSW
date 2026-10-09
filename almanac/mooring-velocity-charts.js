"use strict";
window.oswMooringVelocityCharts={render(scene,inspect,root,registerStop){
  const ns='http://www.w3.org/2000/svg';
  const html=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const node=(tag,attrs,parent,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const fmt=x=>Number(x).toLocaleString('en',{maximumFractionDigits:2});
  for(const [index,panel] of scene.panels.entries()){
    const article=html('article',undefined,root);article.className='query-chart-panel';article.dataset.panel=panel.id;
    html('h3',panel.title,article);
    html('p',panel.component==='eastward'?'Positive: eastward. Negative: westward.':'Positive: northward. Negative: southward.',article);
    const frame=html('div',undefined,article);frame.className='query-chart-frame';
    const svg=node('svg',{viewBox:'0 0 640 300',role:'group','aria-labelledby':`velocity-title-${index}`},frame);
    node('title',{id:`velocity-title-${index}`},svg,panel.title+' (cm/s). Fixed source axes; select a point for coverage and source.');
    const [lo,hi]=panel.y_domain_cm_s,y=v=>245-(v-lo)/(hi-lo)*215,x=i=>64+i/Math.max(1,panel.source_count-1)*545;
    for(let i=0;i<=4;i++){const v=lo+(hi-lo)*i/4;node('line',{x1:64,x2:609,y1:y(v),y2:y(v),stroke:'#b9c9d2'},svg);node('text',{x:57,y:y(v)+4,'text-anchor':'end','font-size':12},svg,fmt(v));}
    node('line',{x1:64,x2:609,y1:y(0),y2:y(0),stroke:'#334c5c'},svg);
    node('text',{x:64,y:18,'font-size':12},svg,'cm/s');
    node('text',{x:64,y:281,'font-size':12},svg,panel.series_kind==='monthly'?'Feb 2017':'Jan');
    node('text',{x:609,y:281,'text-anchor':'end','font-size':12},svg,panel.series_kind==='monthly'?'Feb 2021':'Dec');
    for(const p of panel.points){
      const mark=node('g',{role:'button',tabindex:0,'data-sample':p.sample_id,class:'chart-sample chart-velocity'},svg);
      const description=`${p.label}: ${fmt(p.value_cm_s)} cm/s; ${p.available_pairs} available pairs; ${fmt(p.coverage_fraction*100)}% hourly coverage; years ${p.years.join(', ')}${p.partial_month?'; partial month':''}.`;
      mark.setAttribute('aria-label',description);node('title',{},mark,description);
      if(p.interannual_span_cm_s){const [a,b]=p.interannual_span_cm_s;node('path',{d:`M${x(p.x_index)},${y(a)}V${y(b)}M${x(p.x_index)-4},${y(a)}H${x(p.x_index)+4}M${x(p.x_index)-4},${y(b)}H${x(p.x_index)+4}`,stroke:'#587d93',fill:'none'},mark);}
      node('circle',{cx:x(p.x_index),cy:y(p.value_cm_s),r:5,fill:p.partial_month?'#a7682e':'#16677c'},mark);
      if(p.partial_month)node('path',{d:`M${x(p.x_index)},${y(p.value_cm_s)-9}l9 9 -9 9 -9 -9Z`,fill:'none',stroke:'#a7682e'},mark);
      const open=()=>inspect('current_velocity_samples',p.sample_id);mark.addEventListener('click',open);mark.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open();}});
    }
    html('p',panel.series_kind==='monthly'?'Available paired readings averaged per calendar month. Diamond outlines mark partial months. Missing hours are omitted; points are not interpolated.':'Equal weight per complete year-month mean. Whiskers show the span of those monthly means across years; they are not confidence intervals.',article);
    const choice=html('label','Inspect reading ',article),select=html('select',undefined,choice);
    for(const p of panel.points){const option=html('option',p.label,select);option.value=p.sample_id;}
    const open=html('button','Open selected reading',article);open.type='button';open.addEventListener('click',()=>inspect('current_velocity_samples',select.value));
    const play=html('button','Play readings',article);play.type='button';play.setAttribute('aria-pressed','false');
    const reading=html('p',undefined,article);reading.setAttribute('aria-live','polite');
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');let timer=null;
    const stop=()=>{clearInterval(timer);timer=null;play.textContent='Play readings';play.setAttribute('aria-pressed','false');play.disabled=reduced.matches||panel.points.length<2;};registerStop(stop);
    const show=()=>{const p=panel.points[select.selectedIndex];for(const mark of svg.querySelectorAll('[data-sample]'))mark.classList.toggle('velocity-selected',mark.dataset.sample===p.sample_id);reading.textContent=`${p.label}: ${fmt(p.value_cm_s)} cm/s · ${fmt(p.coverage_fraction*100)}% hourly coverage · ${p.available_pairs} pairs.`;};
    select.addEventListener('change',()=>{stop();show();});
    play.addEventListener('click',()=>{if(timer!==null){stop();return;}if(reduced.matches)return;if(select.selectedIndex===panel.points.length-1)select.selectedIndex=0;show();play.textContent='Pause readings';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(select.selectedIndex===panel.points.length-1){stop();return;}select.selectedIndex++;show();},1000);});
    html('p','Playback highlights one source reading per second. Gaps retain their calendar positions; no interpolation or moving geographic footprint. Manual selection remains available with reduced motion.',article);stop();show();
    const source=html('a','Darelius et al. (2024) · PANGAEA · CC BY 4.0',article);source.href=scene.source_url;
  }
}};
