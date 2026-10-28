"use strict";
window.renderPublishedCurrentSpeeds=function(parent,scene,inspect){
  if(scene?.kind==='published_seasonal_core_velocities')return window.renderPublishedSeasonalCoreVelocities(parent,scene,inspect);
  if(!scene||scene.kind!=='published_current_speed_statistics')return;
  const ns='http://www.w3.org/2000/svg';
  const html=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const svgNode=(tag,attrs,container,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;container.append(n);return n;};
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
      const panel=html('section',undefined,parent);panel.className='published-current-speeds';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
      html('h3',scene.title,panel);html('p',scene.scope,panel);
      const rows=scene.records,chart=svgNode('svg',{viewBox:`0 0 800 ${rows.length*28+55}`,role:'img','aria-label':'Matching regional speed summaries. Lines show observed minima to maxima; dots show medians. Sample ranges are not confidence intervals.'},panel);
      chart.style.cssText='display:block;width:100%;max-width:1000px;height:auto';
      const marks=[],ticks=[];
      rows.forEach((row,index)=>{
        const y=25+index*28,label=row.statistic_period==='monthly'?new Date(Date.UTC(2000,row.month-1,1)).toLocaleString('en',{month:'short',timeZone:'UTC'}):row.season;
        svgNode('text',{x:8,y:y+5,'font-size':14,fill:'currentColor'},chart,`${label} · n=${row.observation_count}`);
        const line=svgNode('line',{y1:y,y2:y,stroke:'#387a9c','stroke-width':4},chart);
        const dot=svgNode('circle',{cy:y,r:5,fill:'#387a9c'},chart);
        const median=svgNode('text',{y:y+5,'font-size':14,fill:'currentColor'},chart,row.median.toFixed(2));
        marks.push({row,line,dot,median});
      });
      for(const value of [0,.5,1,1.5,2])ticks.push({value,node:svgNode('text',{y:rows.length*28+30,'text-anchor':'middle','font-size':13,fill:'currentColor'},chart,`${value}`)});
      let previousWidth;
      const layout=available=>{const width=Math.max(240,Math.min(1000,available||800));if(width===previousWidth)return;previousWidth=width;chart.setAttribute('viewBox',`0 0 ${width} ${rows.length*28+55}`);const x=value=>112+value/2*(width-170);for(const {row,line,dot,median} of marks){line.setAttribute('x1',x(row.minimum));line.setAttribute('x2',x(row.maximum));dot.setAttribute('cx',x(row.median));median.setAttribute('x',width-45);}for(const {value,node} of ticks){node.setAttribute('x',x(value));node.setAttribute('visibility',width<280&&!Number.isInteger(value)?'hidden':'visible');}};
      layout(panel.clientWidth);
      if(typeof ResizeObserver!=='undefined'){const observer=new ResizeObserver(entries=>{if(!panel.isConnected){observer.disconnect();return;}layout(entries[0].contentRect.width);});observer.observe(panel);}
      html('p','Speed in m/s. Lines: observed sample minima–maxima. Dots and right-hand values: medians. Filtering changes the displayed records.',panel);
      const scroller=html('div',undefined,panel);scroller.style.overflowX='auto';scroller.tabIndex=0;scroller.setAttribute('role','region');scroller.setAttribute('aria-label','Speed statistics table; scroll horizontally for all columns');
      const table=html('table',undefined,scroller);html('caption','Matching published regional speed summaries (m/s)',table);
      const header=html('tr',undefined,html('thead',undefined,table));
      for(const label of ['Period','Observations','Min','Max','Mean','Median','SD','Record','Source']){const cell=html('th',label,header);cell.scope='col';}
      const body=html('tbody',undefined,table);
      for(const row of rows){const tr=html('tr',undefined,body);for(const value of [row.statistic_period==='monthly'?`Month ${row.month}`:row.season,row.observation_count,row.minimum,row.maximum,row.mean,row.median,row.standard_deviation])html('td',String(value),tr);const button=html('button','Inspect',html('td',undefined,tr));button.type='button';button.onclick=()=>inspect('current_speed_statistics',row.id);const sourceCell=html('td',undefined,tr);if(row.source_pointer){const a=html('a','Source table record',sourceCell);a.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:scene.source_file,pointer:row.source_pointer,limit:50}));}else html('span','Source pointer unavailable',sourceCell);}
      html('p','Months and seasons summarize overlapping observations. SD describes sample variability. Neither SD nor observed extrema are measurement error or a confidence interval. Drogue loss corrections and unequal sampling remain relevant.',panel);
      for(const conflict of scene.source_conflicts)html('p',conflict,panel);
      const source=html('a','Original observational study',html('p',undefined,panel));source.href=scene.source_url;
      for(const [label,path] of [['Full monthly context chart',scene.monthly_figure],['Full seasonal context chart',scene.seasonal_figure]]){const link=html('a',label,html('p',undefined,panel));link.href='../'+path;}

};

window.renderPublishedSeasonalCoreVelocities=function(parent,scene,inspect){
  if(!scene||scene.kind!=='published_seasonal_core_velocities'||!scene.records?.length)return;
  const ns='http://www.w3.org/2000/svg';
  const html=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const svgNode=(tag,attrs,container)=>{const n=document.createElementNS(ns,tag);for(const [key,value] of Object.entries(attrs))n.setAttribute(key,String(value));container.append(n);return n;};
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
  const panel=html('section',undefined,parent);panel.className='published-current-speeds published-seasonal-core-velocities';panel.style.cssText='min-width:0;overflow-wrap:anywhere';
  html('h3',scene.title,panel);html('p',scene.scope,panel);
  html('p','Approximate points, reported intervals and greater-than thresholds are different estimates. The intervals below are not error bars or confidence intervals.',panel);
  const scroller=html('div',undefined,panel);scroller.style.cssText='max-width:100%;overflow-x:auto';scroller.tabIndex=0;scroller.setAttribute('role','region');scroller.setAttribute('aria-label','Published core-velocity estimates; scroll horizontally for layer and source details');
  const table=html('table',undefined,scroller);table.style.minWidth='780px';html('caption','Matching XBT-derived seasonal core-velocity estimates (m/s)',table);
  const header=html('tr',undefined,html('thead',undefined,table));
  for(const [index,label] of ['Current','Estimate','Season','Layer','Record','Source'].entries()){const th=html('th',label,header);th.scope='col';th.style.whiteSpace='nowrap';if(index===0)th.style.width='4rem';if(index>=4)th.style.width='5rem';}
  const body=html('tbody',undefined,table);
  const x=value=>20+value/0.55*550;
  const discrepancies=new Map();
  for(const row of scene.records){
    const tr=html('tr',undefined,body);
    tr.setAttribute('data-core-velocity-id',row.id);
    const current=html('td',row.current_scope.source_label,tr);current.style.width='4rem';current.style.whiteSpace='nowrap';
    const cell=html('td',undefined,tr);html('span',row.display,cell);
    const graphic=svgNode('svg',{viewBox:'0 0 600 40',role:'img','aria-label':`${row.label}: ${row.display}. This is a seasonal-fit estimate, not a sample range or confidence interval.`},cell);
    graphic.style.cssText='display:block;width:100%;min-width:130px;max-width:280px;height:24px';
    svgNode('line',{x1:20,x2:570,y1:20,y2:20,stroke:'#bdcbd5','stroke-width':1},graphic);
    const common={stroke:'#3264ad','stroke-width':4};
    if(row.estimate_kind==='approximate_point'){
      svgNode('circle',{cx:x(row.value_m_s),cy:20,r:6,fill:'#3264ad'},graphic);
    }else if(row.estimate_kind==='approximate_prose_interval'){
      svgNode('line',{x1:x(row.interval_m_s[0]),x2:x(row.interval_m_s[1]),y1:20,y2:20,...common},graphic);
    }else if(row.estimate_kind==='reported_greater_than'){
      const start=x(row.lower_threshold_m_s);
      svgNode('circle',{cx:start,cy:20,r:6,fill:'none',...common},graphic);
      svgNode('line',{x1:start+12,x2:start+62,y1:20,y2:20,...common},graphic);
      svgNode('polyline',{points:`${start+50},12 ${start+62},20 ${start+50},28`,fill:'none',...common},graphic);
    }
    html('td',row.season_label,tr);html('td',row.current_scope.layer,tr);
    const recordCell=html('td',undefined,tr);recordCell.style.whiteSpace='nowrap';
    const button=html('button','Inspect',recordCell);button.type='button';button.onclick=()=>inspect('current_core_velocity_estimates',row.id);
    const sourceCell=html('td',undefined,tr);sourceCell.style.whiteSpace='nowrap';
    const source=html('a','Source record',sourceCell);source.href='query.html?source-q='+encodeURIComponent(JSON.stringify({document:row.source_file,pointer:row.source_pointer,limit:50}));
    for(const item of row.method_discrepancies||[])discrepancies.set(item.current_id,item.detail);
  }
  html('p','Small graphics share a 0–0.55 m/s scale. Text gives the source precision. No exact seasonal month windows, row-specific observation counts or numeric uncertainty are supplied.',panel);
  for(const detail of discrepancies.values())html('p',detail,panel);
  html('p','XBT sampling context: 2000–2010, with 31 selected sections shared across these currents. January, May and June each have one section; February has none. These rows exclude the 1993–2010 satellite-based reconstruction. They cannot supply seasonal length, width or map animation.',panel);
  const original=html('a','Original study and methods',html('p',undefined,panel));original.href=scene.source_url;
  const context=html('a','Full published-estimate comparison',html('p',undefined,panel));context.href='../'+scene.full_context_figure;
};
