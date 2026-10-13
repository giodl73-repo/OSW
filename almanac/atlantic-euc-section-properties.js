(() => {
  window.renderAtlanticEucSectionProperties = (card, audit) => {
    const data=audit.section_properties;
    const el=(tag,text,parent)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;parent?.append(n);return n;};
    const panel=el('section',null,card);panel.className='atlantic-euc-section-properties';
    el('h4','Original 4°W campaign core properties',panel);
    el('p',data.display_caption,panel);
    el('p','Drifting-ship profiles relative to 500 m assumed motionless. Exact station latitudes and numerical errors unknown. Table I and II date claims are retained separately.',panel);
    const ns='http://www.w3.org/2000/svg';
    for(const [field,title,unit,maximum] of [['maximum_eastward_speed_cm_s','Maximum eastward speed','cm/s',120],['maximum_speed_depth_m','Depth of the speed maximum','m',80]]) {
      const figure=el('figure',null,panel);figure.style.margin='0 0 1rem';
      el('h5',`${title} (${unit})`,figure);
      const svg=document.createElementNS(ns,'svg');figure.append(svg);
      const h=100+data.records.length*70;svg.setAttribute('viewBox',`0 0 520 ${h}`);svg.setAttribute('role','img');
      svg.setAttribute('aria-label',`${title} (${unit}) at 4 degrees west. Eight campaign records in table order. Two hollow markers indicate unresolved dates. Complete values and both dates follow in the table.`);
      svg.style.cssText='width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';
      const add=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!=null)n.textContent=text;svg.append(n);return n;};
      const x=v=>145+330*v/maximum;
      add('line',{x1:x(0),x2:x(maximum),y1:62,y2:62,stroke:'#53646b'});
      for(const v of [0,maximum/2,maximum])add('text',{x:x(v),y:90,'font-size':30,'text-anchor':'middle',fill:'#102f3b'},v);
      data.records.forEach((row,i)=>{
        const y=130+i*70;
        add('text',{x:20,y:y+8,'font-size':30,fill:'#102f3b'},row.campaign+(row.date_conflict?' *':''));
        const point=add('circle',{cx:x(row[field]),cy:y,r:9,fill:row.date_conflict?'#f6f5ef':'#126278',stroke:'#126278','stroke-width':3});
        const tooltip=document.createElementNS(ns,'title');tooltip.textContent=`CAP ${row.campaign}: ${row[field]} ${unit}; Table II ${row.table_ii_date_text}; Table I ${row.table_i_campaign_period}${row.date_conflict?'; unresolved date conflict':''}`;point.append(tooltip);
        add('text',{x:x(row[field]),y:y-17,'font-size':30,'text-anchor':row[field]>maximum*.8?'end':'middle',fill:'#102f3b'},row[field]);
      });
      el('figcaption','Campaign categories, not a timeline. * Hollow marker: date conflict. No connecting line or seasonal interpolation.',figure);
    }
    const details=el('details',null,panel);el('summary','All eight records and original date claims',details);
    const wrap=el('div',null,details);wrap.style.overflowX='auto';
    const table=el('table',null,wrap);el('caption','Table II core properties; Table I campaign periods',table);
    const header=el('tr',null,el('thead',null,table));
    for(const text of ['Campaign / station','Table II date','Table I period','Speed (cm/s)','Core depth (m)','Date status'])el('th',text,header).scope='col';
    const body=el('tbody',null,table);
    for(const row of data.records){const tr=el('tr',null,body);el('th',`${row.campaign} / ${row.station_label}`,tr).scope='row';for(const value of [row.table_ii_date_text,row.table_i_campaign_period,row.maximum_eastward_speed_cm_s,row.maximum_speed_depth_m,row.date_conflict?'Unresolved conflict':'Compatible month / campaign period'])el('td',value,tr);}
    const source=el('a','Read original paper · Tables I/II and Figure 2',el('p',null,panel));source.href=data.source_url;
    const query=el('a','Query all original section records',el('p',null,panel));const url=new URL('query.html',location.href);url.searchParams.set('source-q',JSON.stringify({document:'research/atlantic-euc-layer-island-scope-audit.json',pointer:'/section_properties/records',limit:100}));query.href=url;
    el('p','Campaign width remains unresolved. The transport cutoff ≥20 cm/s in the upper 200 m and the separate approximate 200 km FAO background summary do not supply paired width boundaries for these campaigns.',panel);
  };
})();
