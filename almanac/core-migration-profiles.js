/* Source-plot displacement stays separate from length, width and annual geometry. */
(() => {
  const collection='current_core_migration_profiles',ns='http://www.w3.org/2000/svg';
  const html=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const svg=(tag,attrs,parent,text)=>{const n=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.append(n);return n;};
  const number=value=>Number(value).toFixed(2);
  function url(row){return 'query.html?q='+encodeURIComponent(JSON.stringify({collection,filters:[{field:'id',op:'eq',value:row.id}],limit:1}))+'&inspect='+encodeURIComponent(row.id)+'#query-chart-section';}
  function render(parent,scene,inspect,options={}){
    if(!scene||scene.kind!=='published_core_migration_profiles'||!Array.isArray(scene.records)||!scene.records.length)return null;
    const shell=html(options.collapsed?'details':'section',undefined,parent);shell.className='core-migration-profiles';
    html(options.collapsed?'summary':options.headingTag||'h3',scene.title||'How the southern branch moved with depth',shell);
    const body=html('div',undefined,shell);html('p',scene.scope,body);
    html('p','Source period: 1960–2020. These are approximate readings of a published depth profile; no annual series or exact endpoint displacement is reconstructed.',body);
    const note=html('p',scene.operator_note||'Plot-reading intervals are pixel-pick allowances, not confidence intervals. The underlying IAP field has a 1° grid. No whole-current length, width, footprint or seasonal animation is established.',body);note.className='core-migration-scope';
    html('p',`${scene.records.length} matching source-plot readings. Points show only matching records; unselected depths are not interpolated.`,body);
    const panels=html('div',undefined,body);panels.className='core-migration-panels';
    for(const longitude of [...new Set(scene.records.map(r=>r.section_longitude_degrees_east))].sort((a,b)=>a-b)){
      const rows=scene.records.filter(r=>r.section_longitude_degrees_east===longitude).sort((a,b)=>a.sampling_depth_m-b.sampling_depth_m);
      const panel=html('section',undefined,panels);html('h4',`${Math.abs(longitude)}°W section`,panel);
      const chart=svg('svg',{viewBox:'0 0 360 500',role:'group','aria-label':`${rows.length} matching core-migration readings at ${Math.abs(longitude)} degrees west`},panel);chart.classList.add('core-migration-chart');
      const left=62,top=38,width=273,height=365,x=v=>left+width*v/1.2,y=d=>top+(d-50)/550*height;
      for(const value of [0,.4,.8,1.2]){
        svg('path',{d:`M${x(value)} ${top}V${top+height}`,class:'core-migration-grid'},chart);
        svg('text',{x:x(value),y:top+height+29,'text-anchor':'middle'},chart,String(value));
      }
      for(const depth of [50,100,150,200,250,300,350,400,450,500,550,600]){
        svg('path',{d:`M${left} ${y(depth)}H${left+width}`,class:'core-migration-grid'},chart);
        svg('text',{x:left-10,y:y(depth)+5,'text-anchor':'end'},chart,String(depth));
      }
      svg('text',{x:14,y:20},chart,'Depth (m)');svg('text',{x:14,y:height+top+62},chart,'Poleward migration (degrees latitude)');
      for(const row of rows){
        const lo=row.plot_reading_interval_degrees[0],hi=row.plot_reading_interval_degrees[1],cy=y(row.sampling_depth_m),cx=x(row.approximate_migration_degrees);
        const mark=svg('g',{tabindex:0,role:'button','data-core-profile-id':row.id,'aria-label':`${Math.abs(longitude)}°W, ${row.sampling_depth_m}m, approximately ${number(row.approximate_migration_degrees)} degrees poleward; inspect source reading`},chart);
        svg('title',{},mark,`${row.sampling_depth_m}m: ≈${number(row.approximate_migration_degrees)}°. Reading allowance ${number(lo)}–${number(hi)}°; not physical uncertainty.`);
        svg('path',{d:`M${x(lo)} ${cy}H${x(hi)}M${x(lo)} ${cy-5}V${cy+5}M${x(hi)} ${cy-5}V${cy+5}`,class:'core-migration-interval'},mark);
        svg('circle',{cx,cy,r:5,class:'core-migration-point'},mark);
        svg('circle',{cx,cy,r:13,fill:'transparent'},mark);
        const activate=()=>{if(inspect)inspect(collection,row.id);else location.href=url(row);};
        mark.addEventListener('click',activate);mark.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});
      }
    }
    const records=html('details',undefined,body);html('summary','Values and exact source records',records);
    const list=html('ul',undefined,records);list.className='core-migration-records';
    for(const row of scene.records){
      const item=html('li',undefined,list);
      html('span',`${Math.abs(row.section_longitude_degrees_east)}°W · ${row.sampling_depth_m}m · ≈${number(row.approximate_migration_degrees)}° poleward`,item);
      html('span',`Reading allowance ${row.plot_reading_interval_degrees.map(number).join('–')}°${row.interval_includes_zero?' (includes zero)':''}; not a confidence interval.`,item);
      const link=html('a','Inspect source reading',item);link.href=url(row);
      if(inspect)link.addEventListener('click',event=>{event.preventDefault();inspect(collection,row.id);});
    }
    const links=html('p',undefined,body);links.className='core-migration-links';
    const source=html('a','Publication and methods',links);source.href=scene.source_url;
    if(scene.figure){const figure=html('a','Complete source-profile redraw',links);figure.href='../'+scene.figure;}
    return shell;
  }
  window.renderCoreMigrationProfiles=render;
})();
