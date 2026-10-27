"use strict";
window.renderPublishedCurrentSpeeds=function(parent,scene,inspect){
  if(!scene||scene.kind!=='published_current_speed_statistics')return;
  const ns='http://www.w3.org/2000/svg';
  const html=(tag,text,container)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;container.append(n);return n;};
  const svgNode=(tag,attrs,container,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;container.append(n);return n;};
  inspect ||= (collection,id)=>{location.href='query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:id}],limit:100}));};
  html('h3',scene.title,parent);html('p',scene.scope,parent);
      const panel=html('section',undefined,parent);panel.style.cssText='min-width:0;overflow-wrap:anywhere';
      const rows=scene.records,chart=svgNode('svg',{viewBox:`0 0 880 ${rows.length*38+65}`,role:'img','aria-label':'Matching regional speed summaries. Lines show observed minima to maxima; dots show medians. Sample ranges are not confidence intervals.'},panel);
      chart.style.cssText='display:block;width:100%;max-width:1000px;height:auto';
      const x=value=>230+value/2*540;
      rows.forEach((row,index)=>{
        const y=25+index*38,label=row.statistic_period==='monthly'?new Date(Date.UTC(2000,row.month-1,1)).toLocaleString('en',{month:'short',timeZone:'UTC'}):row.season;
        svgNode('text',{x:8,y:y+5,'font-size':15,fill:'currentColor'},chart,`${label} · n=${row.observation_count}`);
        svgNode('line',{x1:x(row.minimum),x2:x(row.maximum),y1:y,y2:y,stroke:'#387a9c','stroke-width':4},chart);
        svgNode('circle',{cx:x(row.median),cy:y,r:5,fill:'#387a9c'},chart);
        svgNode('text',{x:800,y:y+5,'font-size':14,fill:'currentColor'},chart,row.median.toFixed(2));
      });
      for(const tick of [0,.5,1,1.5,2])svgNode('text',{x:x(tick),y:rows.length*38+30,'text-anchor':'middle','font-size':14,fill:'currentColor'},chart,`${tick}`);
      html('p','Speed in m/s. Lines: observed sample minima–maxima. Dots and right-hand values: medians. Filtering changes the displayed records.',panel);
      const scroller=html('div',undefined,panel);scroller.style.overflowX='auto';scroller.tabIndex=0;scroller.setAttribute('role','region');scroller.setAttribute('aria-label','Speed statistics table; scroll horizontally for all columns');
      const table=html('table',undefined,scroller);html('caption','Matching published regional speed summaries (m/s)',table);
      const header=html('tr',undefined,html('thead',undefined,table));
      for(const label of ['Period','Observations','Min','Max','Mean','Median','SD','Record']){const cell=html('th',label,header);cell.scope='col';}
      const body=html('tbody',undefined,table);
      for(const row of rows){const tr=html('tr',undefined,body);for(const value of [row.statistic_period==='monthly'?`Month ${row.month}`:row.season,row.observation_count,row.minimum,row.maximum,row.mean,row.median,row.standard_deviation])html('td',String(value),tr);const button=html('button','Inspect',html('td',undefined,tr));button.type='button';button.onclick=()=>inspect('current_speed_statistics',row.id);}
      html('p','Months and seasons summarize overlapping observations. SD describes sample variability. Neither SD nor observed extrema are measurement error or a confidence interval. Drogue loss corrections and unequal sampling remain relevant.',panel);
      for(const conflict of scene.source_conflicts)html('p',conflict,panel);
      const source=html('a','Original observational study',html('p',undefined,panel));source.href=scene.source_url;
      for(const [label,path] of [['Full monthly context chart',scene.monthly_figure],['Full seasonal context chart',scene.seasonal_figure]]){const link=html('a',label,html('p',undefined,panel));link.href='../'+path;}

};
