"use strict";
(() => {
  const main=document.querySelector('main');if(!main)return;
  const section=document.createElement('section');section.id='working-current-catalogue';section.style.cssText='border:1px solid #587681;padding:1rem;margin:1rem 0';
  const h=document.createElement('h2');h.textContent='Working current catalogue';section.append(h);
  const status=document.createElement('p');status.textContent='Loading accepted current identities…';status.setAttribute('aria-live','polite');section.append(status);main.prepend(section);
  const worker=new Worker('query-worker.js?v=current-catalogue-1');
  const stop=()=>worker.terminate();const timer=setTimeout(()=>{status.textContent='Current catalogue unavailable. Open the query page to inspect the dataset.';stop();},120000);
  worker.onerror=()=>{clearTimeout(timer);status.textContent='Current catalogue unavailable.';stop();};
  worker.onmessage=({data:{id,result}})=>{
    if(!result.ok){clearTimeout(timer);status.textContent='Current catalogue unavailable: '+result.error;stop();return;}
    if(id===1){worker.postMessage({id:2,action:'query',value:{collection:'entities',filters:[{field:'type',op:'eq',value:'named_current'}],limit:1}});return;}
    if(id===2){status.textContent=`${result.total} accepted named currents in the working catalogue. The v0.1 package below retains its historical 100-name scope.`;worker.postMessage({id:3,action:'query',value:{collection:'current_identity_admissions',limit:100}});return;}
    if(id===3){
      const list=document.createElement('ul');section.append(list);
      for(const row of result.rows){const li=document.createElement('li'),a=document.createElement('a');a.textContent=row.entity.label;a.href='object.html?id='+encodeURIComponent(row.entity_id);li.append(a,document.createTextNode(' · identity admitted; inspect scoped dimensions and remaining gaps'));list.append(li);}
      const p=document.createElement('p'),a=document.createElement('a');a.href='../research/ocean-current-working-catalogue.json';a.textContent='Download the effective working catalogue (draft 0.2)';p.append(a);section.append(p);
      const query=document.createElement('p'),all=document.createElement('a');
      all.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'entities',filters:[{field:'type',op:'eq',value:'named_current'}],limit:200}));
      all.textContent='Query all accepted current identities';query.append(all);section.append(query);
      const dimensions=document.createElement('p'),ranked=document.createElement('a'),download=document.createElement('a');
      ranked.href='query.html?q='+encodeURIComponent(JSON.stringify({collection:'length_assessments',filters:[{field:'rank_eligible',op:'eq',value:true}],sort:{field:'published_length_km',direction:'desc'},limit:100}));ranked.textContent='Ranked source-reported length estimates';
      download.href='../research/ocean-current-working-measurements.json';download.textContent='Download working measurement records';
      dimensions.append(ranked,document.createTextNode(' · '),download);section.append(dimensions);
      section.dataset.engine='rust-osw-query-v1';window.oswCurrentIdentityAdmissions=result;clearTimeout(timer);stop();
    }
  };
  worker.postMessage({id:1,action:'load'});
})();
