(() => {
  window.renderQualitativeCurrentCalendar = (card, audit) => {
    const data=audit.seasonal_calendar;
    const add=(tag,text,parent)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;parent?.append(n);return n;};
    const panel=add('section',null,card);panel.className='qualitative-current-calendar';
    add('h4','Seasonal calendar · source interpretation',panel);
    add('p','Select a month to explore the reported behavior. Categories have no numerical strength scale.',panel);
    const controls=add('div',null,panel);controls.setAttribute('role','group');controls.setAttribute('aria-label','Calendar month');
    controls.style.cssText='display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.35rem';
    const names=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const output=add('div',null,panel);output.setAttribute('aria-live','polite');output.setAttribute('aria-atomic','true');
    const buttons=[];
    const choose=month=>{
      buttons.forEach((button,i)=>{
        const selected=i+1===month;button.setAttribute('aria-pressed',String(selected));
        button.textContent=names[i]+(selected?' ✓':'');button.style.fontWeight=selected?'700':'400';
      });
      output.replaceChildren();add('h5',names[month-1]+' · reported seasonal context',output);
      const list=add('ul',null,output);
      for(const id of data.months[month-1].claim_ids){const claim=data.claims.find(c=>c.id===id);const item=add('li',null,list);add('strong',claim.label+': ',item);add('span',claim.summary,item);add('small',` ${claim.locator}. Reference: ${claim.reference_state}.`,item);}
    };
    names.forEach((name,i)=>{const b=add('button',name,controls);b.type='button';b.style.cssText='min-height:44px;min-width:0;padding:.45rem .1rem;font:inherit;white-space:nowrap';b.setAttribute('aria-label',name+' seasonal claims');b.addEventListener('click',()=>choose(i+1));buttons.push(b);});
    choose(6);
    add('p','Map context: the existing static editorial route uses Ridgway & Condie (2004). Month selection does not change its geometry. Seasonal widths, lengths and speed amplitudes remain unknown.',panel);
    const provenance=add('details',null,panel);add('summary','Source methods and unresolved information',provenance);
    for(const value of [audit.field_context.seasonal_operator,'Altimetry: '+audit.field_context.altimetry_period+'. CMDT mean: '+audit.field_context.cmdt_mean_period+'.',audit.field_context.cars,audit.field_context.layer,audit.source.access])add('p',value,provenance);
    const a=add('a','Read Ridgway (2007)',add('p',null,panel));a.href=audit.source.url;
    const q=add('a','Query the six seasonal claims',add('p',null,panel));const url=new URL('query.html',location.href);url.searchParams.set('source-q',JSON.stringify({document:'research/zeehan-ridgway-2007-seasonal-scope-audit.json',pointer:'/seasonal_calendar/claims',limit:100}));q.href=url;
  };
})();
