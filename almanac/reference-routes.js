(() => {
  const initialAddress=location.href;
  let userInteracted=false;
  let linkedCardObserver=null,linkedCardFrame=null,linkedCardTarget=null;
  function releaseLinkedCard() {
    linkedCardObserver?.disconnect();linkedCardObserver=null;
    if(linkedCardFrame!==null)cancelAnimationFrame(linkedCardFrame);
    linkedCardFrame=null;linkedCardTarget=null;
  }
  for(const type of ['pointerdown','keydown','wheel','touchstart'])document.addEventListener(type,()=>{
    userInteracted=true;releaseLinkedCard();
  },{capture:true,passive:true});
  document.addEventListener('focusin',event=>{
    if(linkedCardTarget&&event.target!==linkedCardTarget)releaseLinkedCard();
  },true);
  const revealInitialCard=()=>{if(!userInteracted&&location.href===initialAddress)revealLinkedCard();};
  const node = (tag, text, parent) => { const el = document.createElement(tag); if (text != null) el.textContent = text; if (parent) parent.append(el); return el; };
  const number = value => Number(value).toLocaleString("en-US");
  const link = (text, href, parent, external = false) => { const el = node("a", text, parent); el.href = href; if (external) { el.target = "_blank"; el.rel = "noopener noreferrer"; } return el; };
  const objectHref = id => `object.html?id=${encodeURIComponent(id)}`;
  window.oswAtlasSourcesReady = new Promise((resolve,reject)=>{
    const worker=new Worker('query-worker.js?v=atlas-cartography-9');
    const timer=setTimeout(()=>finish(Error('Atlas data request timed out')),90000);
    const finish=(error,result)=>{clearTimeout(timer);worker.terminate();if(error){byId('route-atlas-status').textContent=`Atlas unavailable: ${error.message}`;reject(error);}else resolve(result);};
    worker.onerror=()=>finish(Error('Rust atlas data worker failed'));
    worker.onmessage=async event=>{const {id,result}=event.data;
      if(!result.ok){finish(Error(result.error));return;}
      if(id===1){worker.postMessage({id:2,action:'atlas'});return;}
      try {
        window.oswCartography=await window.createOswCartography(result.engine_binary);
        delete result.engine_binary;
        window.oswAtlasSnapshot=result;
        byId('route-status').dataset.engine=result.engine;
        const docs=Object.fromEntries(Object.entries(result.sources_json).map(([path,raw])=>[path,JSON.parse(raw)]));
        finish(null,docs);
      } catch(error){finish(error);}
    };
    worker.postMessage({id:1,action:'load'});
  });
  async function load(path) {
    const docs=await window.oswAtlasSourcesReady,key=path.replace(/^\.\.\//,'');
    if(!Object.hasOwn(docs,key))throw Error(`Atlas source unavailable: ${key}`);
    return docs[key];
  }
  const byId = id => document.getElementById(id);
  function revealLinkedCard() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = byId(id);
    if (!target || !target.matches('.route-card, .current-model-card, .inventory-addition-card, .current-admission-card, #route-atlas')) return;
    releaseLinkedCard();
    if (id === 'route-atlas') {
      if (window.restoreReferenceRouteAtlas) window.restoreReferenceRouteAtlas();
      else if (!new URL(location.href).searchParams.has('atlas-feature')) window.returnToReferenceRouteAtlas?.();
      target.tabIndex = -1;
    }
    target.focus({ preventScroll: true });
    target.scrollIntoView({ block: 'start', behavior: 'instant' });
    linkedCardTarget=target;
    const address=location.href;
    const align=()=>{
      linkedCardFrame=null;
      if(linkedCardTarget!==target||location.href!==address||!target.isConnected){releaseLinkedCard();return;}
      target.scrollIntoView({block:'start',behavior:'instant'});
    };
    const schedule=()=>{
      if(linkedCardFrame===null)linkedCardFrame=requestAnimationFrame(align);
    };
    // Atlas previews and late image sizing can move a distant card after the
    // hash handler. Keep that heading aligned until the next user gesture.
    linkedCardObserver=new ResizeObserver(schedule);
    linkedCardObserver.observe(document.body);
    schedule();
  }
  window.addEventListener('hashchange', revealLinkedCard);
  document.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor) return;
    let target;
    try { target = byId(decodeURIComponent(anchor.hash.slice(1))); } catch (_) { return; }
    if (!target?.matches('.route-card, .current-model-card, .inventory-addition-card, .current-admission-card, #route-atlas')) return;
    event.preventDefault();
    if (target.id === 'route-atlas') window.returnToReferenceRouteAtlas?.();
    if (location.hash !== anchor.hash) history.pushState(null, '', anchor.hash);
    revealLinkedCard();
  });
  function renderProposedWidths(row, card) {
    if(row.section_width_evidence?.length){
      node('h4','Additional measurements for this proposed branch',card);
      for(const r of row.section_width_evidence){
        node('p',`${r.width_range_km.join('–')} km · ${r.layer} ${r.boundary_rule}`,card);
        node('p','Proposed identity only; no dimensions assigned to Norwegian Current or Norwegian Coastal Current.',card);
      }
      const q={collection:'proposed_widths',filters:[{field:'proposed_current_id',op:'eq',value:row.proposed_id}],limit:20};
      link('Compare proposed branch section widths','query.html?q='+encodeURIComponent(JSON.stringify(q))+'#query-chart-section',node('p',null,card));
    }
    if (!row.width_scope_audit) return;
    const records=row.width_evidence;node('h4','Source-supported branch widths',card);
    if(!records.length) {
      node('p','System width remains unknown. Branch widths cannot be added.',card);
      for(const id of row.component_proposed_ids)link('Inspect '+id.replaceAll('-',' '),`#inventory-addition-${id}`,node('p',null,card));
      return;
    }
    const bosse=r=>r.measurement_type==='published_corrected_glider_front_width_summary';
    const label=r=>r.width_range_km?`${r.width_range_km.join('–')} km reported branch span`:bosse(r)?`${r.approximate_width_km} ± ${r.author_reported_error_km} km reported front width`:`About ${r.approximate_width_km} km surface scale`;
    const figure=node('figure',null,card);figure.style.margin='0';const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
    svg.classList.add('proposed-width-chart');svg.dataset.owner=row.proposed_id;
    const h=records.length*90+42;svg.setAttribute('viewBox',`0 0 500 ${h}`);svg.setAttribute('role','img');
    svg.setAttribute('aria-label',row.name+': '+records.map(r=>r.width_range_km?`${r.source_publication_year} reported branch span ${r.width_range_km.join(' to ')} kilometres, no midpoint`:bosse(r)?`${r.source_publication_year} corrected glider front width ${r.approximate_width_km} kilometres, reported plus or minus ${r.author_reported_error_km} kilometres, statistic interpretation pending`:`${r.source_publication_year} ADT surface scale about ${r.approximate_width_km} kilometres, no numeric uncertainty supplied`).join('; ')+'. Different methods; not a width trend, annual range or confidence interval.');
    svg.style.cssText='width:100%;max-width:650px;background:#f6f5ef;color:#102f3b';figure.append(svg);
    const add=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;svg.append(n);};
    const x=v=>50+390*v/75;
    records.forEach((r,i)=>{
      const y=70+i*90;
      add('text',{x:20,y:y-45,'font-size':26,fill:'#102f3b'},`${r.source_publication_year} · ${r.width_range_km?'reported branch span':bosse(r)?'glider front span':'ADT surface scale'}`);
      if(r.width_range_km){
        const [low,high]=r.width_range_km;
        add('line',{x1:x(low),x2:x(high),y1:y,y2:y,stroke:'#176b82','stroke-width':5});
        for(const v of [low,high]){add('line',{x1:x(v),x2:x(v),y1:y-6,y2:y+6,stroke:'#176b82','stroke-width':2});add('text',{x:x(v),y:y-15,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);}
      }else{add('circle',{cx:x(r.approximate_width_km),cy:y,r:5,fill:'#176b82'});add('text',{x:x(r.approximate_width_km),y:y-15,'text-anchor':'middle','font-size':26,fill:'#102f3b'},bosse(r)?`${r.approximate_width_km} ± ${r.author_reported_error_km} km`:`About ${r.approximate_width_km} km`);}
    });
    const y=records.length*90+8;add('line',{x1:50,x2:440,y1:y,y2:y,stroke:'#526c77'});
    for(const v of [0,25,50,75])add('text',{x:x(v),y:y+25,'text-anchor':'middle','font-size':26,fill:'#102f3b'},`${v} km`);
    node('figcaption','Different methods and smoothing: this comparison establishes no width trend, annual range or confidence interval. Range records have no selected midpoint. Reported plus/minus statistics retain their source meaning; confidence level and annual physical ranges are not inferred.',figure);
    for(const r of records.filter(bosse))node('p',r.error_interpretation,figure);
    if(records.some(r=>r.measurement_type==='published_ADT_surface_branch_scale'))node('p','ADT means absolute dynamic topography; the surface scale comes from altimetry-derived geostrophic flow.',card);
    node('p','All records are local branch evidence for proposed identities, with distinct sections and methods. Whole-current dimensions remain unresolved.',card);
    for(const r of records){
      const detail=node('details',null,card);detail.id='proposed-width-'+r.id;
      node('summary',label(r),detail);
      if(bosse(r))node('p',`Corrected 2020-09-28. ${r.error_interpretation}`,detail);
      node('p',`${r.geographic_scope} ${r.layer} ${r.boundary_rule}`,detail);
      node('p',`${r.temporal_interpretation} ${r.source_access}`,detail);
      link(r.source_citation,r.source_url,node('p',null,detail),true);
    }
    const url=new URL('query.html',location.href);url.searchParams.set('source-q',JSON.stringify({document:row.width_scope_audit.file,pointer:'/measurements',filters:[{field:'record.proposed_current_id',op:'eq',value:row.proposed_id}],limit:10}));
    link('Query these branch-width records',url.href,node('p',null,card));
    if(row.proposed_id==='norwegian-atlantic-front'){
      link('Inspect original-mission source alignment','../figures/norwegian-front-glider-source-alignment.svg',node('p',null,card));
      const source=new URL('query.html',location.href);source.searchParams.set('source-q',JSON.stringify({document:'research/norwegian-front-glider-source-alignment.json',pointer:'/missions/0/DAC_records',limit:20}));
      link('Query retained glider current records',source.href,node('p',null,card));
    }
    if(row.proposed_id==='norwegian-atlantic-front')node('p','The 2010 study discusses a broader time-mean frontal flow but gives no new numeric width. Its mean width remains unknown. The corrected 2019 glider result belongs to the Mohn Ridge and does not fill that 2010 Svinoy mean.',card);
  }
  let catalog;
  load("../research/ocean-current-inventory-expansion-candidates.json").then(async value => {
    const admissions=await load('../research/norwegian-atlantic-slope-working-admission.json');
    const coastalPath='research/indian-current-identity-query-contract-v1.json';
    const coastal=window.oswAtlasSnapshot?.sources_json[coastalPath]
      ? await load('../'+coastalPath) : null;
    const acceptedEntries=[...admissions.entries,...(coastal?.additions.current_identity_admissions||[])];
    const listed=new Set(value.entries.map(row=>row.proposed_id));
    const coastalCards=(coastal?.additions.current_identity_admissions||[])
      .filter(admitted=>!listed.has(admitted.proposal_id)).map(admitted=>{
        const source=coastal.additions.sources.find(row=>row.id===admitted.source_id);
        return {proposed_id:admitted.proposal_id,name:admitted.entity.label,
          proposed_kind:'named current',identity_scope:admitted.entity.identity_scope_note,
          evidence:source?[{citation:source.label||source.title,url:source.url,
            locator:admitted.source_locator,supports:'Names this current and describes its qualitative scope. Measurements retain their separate source support.'}]:[],
          remaining_gates:[
            'Review reported measurements with their own dates, layers and boundary rules.',
            admitted.route_planning_decision.next_action,
            'Obtain repeated dated evidence before annual ranges or seasonal geometry.']};
      });
    const asar=await load('../research/hansen-2011-asar-surface-width-admissions.json');
    const measured=await load('../research/southern-east-madagascar-prose-dimension-admissions.json').catch(()=>null);
    const cardRows=[...value.entries,...coastalCards];
    for (const row of cardRows) {
      const admitted=acceptedEntries.find(r=>r.proposal_id===row.proposed_id);
      const numeric=measured?.current_id===row.proposed_id?measured:null;
      const card = node("section", null, byId("inventory-addition-cards")); card.id = `inventory-addition-${row.proposed_id}`; card.className = admitted?'current-admission-card':'inventory-addition-card'; card.tabIndex = -1;
      node("h3", row.name, card);
      const navigation = node("p", null, card);
      link(admitted?'Link to this current':'Link to this proposed current', `#${card.id}`, navigation);
      navigation.append(document.createTextNode(" · "));
      link("Back to current atlas", "#route-atlas", navigation);
      node("p", `${admitted?'Source-supported':'Proposed'} classification: ${row.proposed_kind}. ${admitted?.entity?.identity_scope_note||row.identity_scope}`, card);
      node("p", admitted?'Current identity admitted to the working catalogue. Quantitative measurements, routes and annual ranges retain their separate review gates.':'Inventory addition pending review; no whole-current length or rank admitted.', card);
      if(admitted){
        link('Open accepted current record',objectHref(admitted.entity_id),node('p',null,card));
        const q={collection:'current_identity_admissions',filters:[{field:'id',op:'eq',value:admitted.id}],limit:1};
        link('Query the identity admission','query.html?q='+encodeURIComponent(JSON.stringify(q)),node('p',null,card));
      }
      if(admitted && row.proposed_id==='norwegian-atlantic-slope'){
        const evidence=node('section',null,card);evidence.className='nwasc-admitted-dimensions';
        node('h4','Admitted source reports · separately scoped',evidence);
        node('p',`Approximate 3,500 km broad historical eastern-branch extent, working reported-length rank ${admissions.working_published_ranks[admitted.entity_id]}. Six local width records retain different source definitions. These are not six independent new observations, a mapped axis or a seasonal range.`,evidence);
        const image=node('img',null,evidence);image.src='../'+admissions.figure_file;image.alt='Norwegian Atlantic Slope Current: broad historical reported extent and six separately scoped width records. No whole-current width or annual range.';image.style.cssText='width:100%;max-width:1040px;height:auto';
        link('Open reported-dimension summary',image.src,node('p',null,evidence));
        const q={collection:'widths',filters:[{field:'current_id',op:'eq',value:row.proposed_id}],limit:10};
        link('Query all admitted local widths','query.html?q='+encodeURIComponent(JSON.stringify(q)),node('p',null,evidence));
        link('Download the effective measurement records','../research/ocean-current-measurements-aleutian-edition.json',node('p',null,evidence));
        const asarSection=node('section',null,card);asarSection.className='asar-width-admissions';
        node('h4','Additional ASAR surface-width reports',asarSection);
        node('p','August2007-July2010 weighted mean surface field:60km FWHM at P1;36km at Svinoy conditional on partition at the200m isobath. These two records supplement the six earlier scoped reports above. Mixed45km P2 and60km S1 profiles are excluded from separate-current widths. No annual range or width error is supplied.',asarSection);
        const asarImage=node('img',null,asarSection);asarImage.src='../'+asar.figure_file;asarImage.alt='Local mean-field reports: NwASC60km FWHM and36km conditional partition; NCC about30km. Mixed profiles excluded. No seasonal range.';asarImage.style.cssText='width:100%;max-width:1040px;height:auto';
        link('Open ASAR local-width comparison',asarImage.src,node('p',null,asarSection));
        const asarQuery={collection:'diagnostics',filters:[{field:'id',op:'eq',value:asar.id}],limit:1};
        link('Query ASAR width source report','query.html?q='+encodeURIComponent(JSON.stringify(asarQuery)),node('p',null,asarSection));
        node('p','Earlier proposal-stage source records below are retained for traceability; the admission above gives their current status. The approximately3,500km broad historical extent may overlap downstream West Spitsbergen naming; lengths are not additive.',evidence);
      }
      if(numeric){
        node('p',`Source-reported approximate branch extent: 650 km (working reported-length rank ${admissions.working_published_ranks['current:southern-east-madagascar']}). Scoped near-surface survey width: about 120 km in April 2001. These reports do not establish geographic edges, annual ranges or a width ranking.`,card);
        const q={collection:'current_measurement_admissions',filters:[{field:'entity_id',op:'eq',value:numeric.entity_id}],limit:1};
        link('Query the dimension admission and source definitions','query.html?q='+encodeURIComponent(JSON.stringify(q)),node('p',null,card));
        const diagnostic=node('section',null,card);diagnostic.id='southern-east-madagascar-route-definition';
        node('h4','Earlier route experiments · retained',diagnostic);
        node('p','All 27 initial coastal scenarios crossed both the coarse and finer land masks. The earlier offshore alternative is approximately 900 km with different endpoints from the published approximately 650 km extent. Neither earlier experiment was admitted. A new coast-following geographic reference is available below; a measured current axis and annual geometry remain unresolved.',diagnostic);
        const image=node('img',null,diagnostic);image.src='../figures/southern-east-madagascar-route-definition-diagnostic.svg';
        image.alt='Rejected coastal experiment and unadmitted offshore navigation alternative. No verified current axis or annual geometry.';
        image.style.cssText='width:100%;max-width:1200px;height:auto';
        link('Open route comparison figure',image.src,node('p',null,diagnostic));
        const dq={collection:'diagnostics',filters:[{field:'id',op:'eq',value:'diagnostic:southern-east-madagascar-route-definition'}],limit:1};
        link('Query all route experiments and unresolved definitions','query.html?q='+encodeURIComponent(JSON.stringify(dq)),node('p',null,diagnostic));
        link('Inspect the coastal reference map and all 27 conventions','#southern-east-madagascar-coastal-reference-curve',node('p',null,card));
        const atlas=new URL(location.href);atlas.searchParams.set('atlas-layout','map');atlas.searchParams.set('atlas-feature',numeric.entity_id);atlas.searchParams.set('atlas-route','southern-east-madagascar-coastal-reference-curve');atlas.hash='route-atlas';
        link('Find this current on the global atlas',atlas.href,node('p',null,card));
      }
      for (const evidence of row.evidence) {
        link(evidence.citation, evidence.url, node("p", null, card), true);
        node("p", `${evidence.locator} ${evidence.supports}`, card);
        if (evidence.source_access) node("p", `Source access: ${evidence.source_access}`, card);
      }
      renderProposedWidths(row,card);
      if(row.source_dimensions){
        const d=row.source_dimensions,section=node('section',null,card);section.className='proposed-source-dimensions';
        node('h4','Reported dimensions · separate measurement scopes',section);
        const figure=node('figure',null,section);figure.style.margin='0';
        const image=node('img',null,figure);image.src='../'+(numeric?.figure_file||admitted?.identity_figure_file||d.figure_file);
        image.alt=`${row.name}: ${d.records.map(r=>`about ${r.value_km} km reported ${r.dimension}`).join('; ')}. Separate supports, not a footprint or annual range.`;
        image.style.cssText='width:100%;max-width:960px;height:auto';
        node('figcaption',d.interpretation,figure);
        for(const r of d.records){
          const detail=node('details',null,section);detail.dataset.measurement=r.id;
          node('summary',`About ${number(r.value_km)} km reported ${r.dimension}`,detail);
          node('p',`${r.support} Source: ${r.source_locator}.`,detail);
          node('p',r.observed_period?`Survey period: ${r.observed_period}.`:'No observation period assigned to this contextual length.',detail);
          node('p','Uncertainty and geographic edge coordinates are not supplied. No annual mean or annual extrema admitted.',detail);
        }
        node('p',d.source_license,section);
        link(d.source_citation,d.source_url,node('p',null,section),true);
        const q={document:'research/ocean-current-inventory-expansion-candidates.json',pointer:'/entries',filters:[{field:'record.proposed_id',op:'eq',value:row.proposed_id}],limit:1};
        link('Query this current and its reported dimensions','query.html?source-q='+encodeURIComponent(JSON.stringify(q)),node('p',null,section));
      }
      if(row.proposed_id==='norwegian-atlantic-slope'){
        const meanCoreFile='research/norwegian-baumann-2026-mean-core-widths.json';
        if(window.oswAtlasSnapshot.sources_json[meanCoreFile]){
          const mean=node('section',null,card);mean.className='nwasc-mean-core';
          node('h4','Published section support · static mean-core extents',mean);
          load('../'+meanCoreFile).then(report=>{
            const image=node('img',null,mean);image.src='../'+report.figure_file;image.style.cssText='display:block;width:100%;max-width:900px;height:auto';
            image.alt='Svinøy: about50km at50m depth. Gimsøy: about50km horizontal extent of a variable-depth core. Static1993–2022 mean fields; no seasonal range.';
            for(const r of report.measurements){
              const detail=node('details',null,mean);detail.dataset.measurement=r.id;
              node('summary',r.phase_label+' · about '+r.approximate_width_km+' km',detail);
              node('p',r.layer,detail);node('p',r.boundary_rule,detail);node('p',r.temporal_interpretation,detail);
              node('p','Salinity ≥35.16g/kg; core starts at50m. The '+r.scope_isobath_m+'m isobath constrains section scope, not measurement depth. Uncertainty and paired geographic edges are unspecified.',detail);
              node('p',r.source_locator,detail);
            }
            node('p','Proposed slope branch only; no dimensions assigned to Norwegian Current or Norwegian Coastal Current. The separate50km heat-budget box is a model assumption. No seasonal playback, geographic envelope or width trend.',mean);
            const q={collection:'proposed_widths',filters:[{field:'proposed_current_id',op:'eq',value:row.proposed_id},{field:'measurement_type',op:'eq',value:'published_mean_field_transport_core_extent'}],limit:10};
            link('Query both static mean-core spans','query.html?q='+encodeURIComponent(JSON.stringify(q))+'#query-chart-section',node('p',null,mean));
            const sq={document:meanCoreFile,pointer:'',limit:100};
            link('Inspect exact core-definition report','query.html?source-q='+encodeURIComponent(JSON.stringify(sq)),node('p',null,mean));
            link('Original publication · CC BY4.0','../'+report.original_pdf,node('p',null,mean));
            node('p',report.raw_data_availability,mean);
          }).catch(error=>node('p','Mean-core source unavailable: '+error.message,mean));
        }
        const evidence=node('section',null,card);evidence.id='norwegian-slope-reported-dimensions';
        node('h4','Additional reported dimensions · provisional',evidence);
        load('../research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json').then(report=>{
          const figure=node('figure',null,evidence);figure.style.margin='0';
          const image=node('img',null,figure);image.src='../'+report.figure_file;
          image.alt='About 3,500 km reported branch length; about 40 km local annual mean flow width at Svinøy. Original source acquisition and identity admission pending.';
          image.style.cssText='width:100%;max-width:680px;height:auto';
          node('figcaption','Separate geographic supports. These provisional reports establish no seasonal range, occupied route, current area or ranking.',figure);
          for(const r of report.measurements){
            const detail=node('details',null,evidence);
            node('summary',`About ${number(r.value_km)} km reported ${r.dimension}`,detail);
            node('p',`${r.support} ${r.locator}`,detail);
            for(const exclusion of r.context_exclusions||[])node('p',exclusion,detail);
          }
          node('p',report.source.access,evidence);
          link(report.source.citation,report.source.url,node('p',null,evidence),true);
          const q={document:'research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json',pointer:'/measurements',limit:10};
          link('Query the two provisional source reports','query.html?source-q='+encodeURIComponent(JSON.stringify(q)),node('p',null,evidence));
        }).catch(error=>node('p','Additional reported dimensions unavailable: '+error.message,evidence));
      }
      const gates=numeric?[
        'Recover paired velocity boundaries, fixed width-layer support and quantitative uncertainty before physical current-width admission.',
        'Acquire and review original figures before figure-dependent measurement, digitization or route reconstruction.',
        'Obtain repeated dated evidence before annual ranges, seasonal geometry or physical state intersections.'
      ]:admitted?.remaining_measurement_gates||row.remaining_gates;
      const list = node("ul", null, card); for (const gate of gates) node("li", gate, list);
    }
    const acceptedCount=cardRows.filter(row=>acceptedEntries.some(admitted=>admitted.proposal_id===row.proposed_id)).length;
    byId("inventory-addition-status").textContent = `${cardRows.length-acceptedCount} pending inventory additions; ${acceptedCount} identities admitted beyond the historical 100-name package. Coverage is incomplete.`;
    requestAnimationFrame(revealInitialCard);
  }).catch(error => { byId("inventory-addition-status").textContent = `Inventory additions unavailable: ${error.message}`; });
  const widthInventoryReady = load("../research/ocean-current-width-inventory.json").then(async base => {
    const supplemental=window.oswAtlasSnapshot.supplemental_widths||[];
    const measurements=[...base.measurements,...supplemental];
    const admitted=(window.oswAtlasSnapshot.admitted_current_decisions||[]).filter(r=>!base.current_decisions.some(b=>b.current_id===r.current_id)).map(r=>({...r,
      width_decision:r.measurement_ids.length?'scoped_width_evidence_present':'width_not_assessed',whole_current_width_km:null,
      next_action:'Recover paired velocity edges, width-layer support and repeated observations before physical widths, annual ranges or geographic intersections.'}));
    const decisions=[...base.current_decisions,...admitted].map(r=>({...r,measurement_ids:[...new Set([...(r.measurement_ids||[]),...supplemental.filter(w=>w.current_id===r.current_id).map(w=>w.id)])]}));
    const value={...base,measurements,current_decisions:decisions,counts:{...base.counts,currents:decisions.length,
      measurements:measurements.length,currents_with_scoped_width_evidence:new Set(measurements.map(w=>w.current_id)).size}};
    for (const row of value.measurements) {
      const tr = node("tr", null, byId("width-rows")); tr.id = `width-${row.id}`;
      link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.reported_width_constraint ? `${row.reported_width_constraint.source_notation} reported size constraint; representative width unknown` : row.approximate_width_km == null ? `${row.width_range_km.map(number).join("–")} km ${row.phase_kind === "mean_offshore_extent_range" ? "offshore extent of mean surface flow; not full width or annual extrema" : row.phase_kind === "seasonal_mean_width_range" ? "author-reported seasonal mean span; not annual extrema" : row.phase_kind === "campaign_hydrographic_core" ? "reported local salinity-core span; not annual extrema" : "reported typical regional range"}` : `About ${number(row.approximate_width_km)} km${row.phase_kind === "survey_layer_median_threshold_width" ? ` ±${number(row.reported_total_error_km)} km reported total error; layer median` : ""}${row.phase_kind === "climatological_core_distribution" ? ` median across longitudes (${row.width_range_km.map(number).join("–")} km spatial range; not seasonal extrema)` : row.phase_kind === "survey_profile_composite" ? " fitted profile scale (not full width)" : row.phase_kind === "dated_band_section" ? " described subsurface band span (not full width)" : row.phase_kind === "month_dated_section" ? (row.angular_span_conversion?.source_reported_latitude_limits_degrees ? " described meridional band span (not fixed-depth full width)" : " reported section span (converted from latitude degrees)") : row.phase_kind === "ensemble_profile_band" ? " reported offshore flow-band span" : row.phase_kind === "ensemble_angular_summary" ? ` (source ${row.ensemble_angular_context.source_reported_latitude_span_degrees}° latitude; shared general summary)` : ""}`, tr);
      if(row.phase_kind==='model_snapshot_width_summary')tr.cells[1].append(document.createTextNode(' · local model snapshot'));
      node("td", row.time_convention, tr);
      const scope = node("td", row.geographic_scope, tr);
      node("p", row.layer, scope); node("p", row.boundary_rule, scope);
      node("p", `${row.measurement_type.replaceAll("_", " ")}; not a uniform whole-current width.`, scope);
      node("p", `Metric: ${row.width_metric.replaceAll("_", " ")}. ${row.section_orientation}`, scope);
      if (row.source_quality_note) node("p", row.source_quality_note, scope);
      const source = node("td", null, tr); link(row.source_citation, row.source_url, source, true); node("p", row.source_locator, source);
    }
    for (const summary of value.seasonal_summaries) {
      const card = node("section", null, byId("width-seasonal-summaries")); card.id = `width-seasonal-${summary.current_id}`;
      const current = value.current_decisions.find(row => row.current_id === summary.current_id);
      node("h3", `${current.name}: ${summary.reported_seasonal_value_span_km.map(number).join("–")} km reported seasonal span`, card);
      node("p", summary.interpretation, card);
    }
    for (const row of value.current_decisions) {
      const tr = node("tr", null, byId("width-decision-rows")); tr.id = `width-decision-${row.current_id}`;
      link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.width_decision.replaceAll("_", " "), tr);
      const action = node("td", row.next_action, tr);
      const derived=value.derived_width_series_candidates?.find(candidate=>candidate.current_id===row.current_id);
      if(derived){node("p","Separate derived section-width candidate still requires scientific review.",action);link("Inspect derived section-width candidate",derived.visual_url||"../"+derived.file,node("p",null,action));}
      const span=value.section_span_diagnostics?.find(diagnostic=>diagnostic.current_id===row.current_id);
      if(span){node("p",span.scope_note,action);link("Map local component spans",span.visual_url,node("p",null,action));}
      const review = value.review_assessments?.find(review => review.current_id === row.current_id);
      if (review) {
        node("p", review.reason, action);
        for (const evidence of review.evidence) {
          link(evidence.citation, evidence.url, node("p", null, action), true);
          node("p", `${evidence.locator} ${evidence.supports}`, action);
        }
      }
    }
    const counts = value.counts;
    byId("width-status").textContent = `${counts.measurements} scoped width records for ${counts.currents_with_scoped_width_evidence} of ${counts.currents} currents; ${counts.currents_with_existing_mentions_pending_review} have existing mentions pending source review; ${counts.currents_with_derived_width_candidates_pending_review} have candidate series with no scoped width records; ${counts.currents_with_sources_reviewed_no_numeric_width} reviewed without a comparable numeric current width; ${counts.currents_with_section_span_diagnostics_width_unresolved} have component-span diagnostics with width unresolved; ${counts.currents_not_assessed} not yet assessed. Source-specific pending candidates may coexist with other scoped records. No annual whole-current widths admitted.`;
    return value;
  }).catch(error => { byId("width-status").textContent = `Width evidence unavailable: ${error.message}`; return null; });
  const seasonalRoutesReady = load("../research/ocean-current-seasonal-route-frames.json").catch(() => ({frames:[]}));
  function renderQueue() {
    const query = byId("route-query").value.trim().toLocaleLowerCase();
    const coverage = byId("route-coverage").value;
    const strategy = byId("route-strategy").value;
    const rows = catalog.remaining_current_decisions.filter(row => (!query || `${row.name} ${row.current_id} ${row.ledger_kind} ${row.route_strategy_label} ${row.existing_scope}`.toLocaleLowerCase().includes(query)) && (coverage === "all" || (coverage === "candidate" ? row.candidate_ids.length : !row.candidate_ids.length)) && (strategy === "all" || row.route_strategy_id === strategy));
    const body = byId("route-queue-rows"); body.replaceChildren();
    for (const row of rows) {
      const tr = node("tr", null, body); tr.id = `decision-${row.current_id}`; link(row.name, objectHref(`current:${row.current_id}`), node("td", null, tr));
      node("td", row.existing_length_evidence_status.replaceAll("_", " "), tr);
      const planning = node("td", null, tr);
      node("strong", row.route_strategy_label, planning);
      node("p", `Ledger kind: ${row.ledger_kind}`, planning);
      node("p", row.next_action, planning);
      if (row.candidate_ids.length) node("p", `Scope work: ${row.strategy_next_action}`, planning);
      if (row.component_inventory_status === 'no_component_records_in_current_ledger') node("p", "Basin-member records have not yet been added to this inventory. This does not mean the flows are absent.", planning);
      if (row.known_component_currents.length) {
        const details = node("details", null, planning); node("summary", "Known component records (coverage may be incomplete)", details);
        for (const component of row.known_component_currents) link(component.name, objectHref(`current:${component.current_id}`), node("p", null, details));
      }
      const decision = node("td", null, tr);
      if (!row.candidate_ids.length) node("span", "Route not constructed", decision);
      else for (const id of row.candidate_ids) { const p = node("p", null, decision); const candidate = catalog.candidates.find(item => item.id === id); link(`Inspect ${candidate.route_extent_kind}`, `#${id}`, p); }
      const scope = node("td", row.existing_scope || "Scope unresolved", tr);
      if (row.name_source_url) { scope.append(document.createTextNode(" · ")); link("Naming source", row.name_source_url, scope, true); }
    }
    byId("queue-count").textContent = `${rows.length} of ${catalog.remaining_current_decisions.length} remaining currents`;
  }
  load("../research/ocean-current-working-reference-routes.json").then(async value => {
    catalog = window.oswAtlasSnapshot?.working_reference_routes || value;
    for (const strategy of catalog.planning_taxonomy.strategies) {
      const option = node("option", `${strategy.label} (${strategy.current_count})`, byId("route-strategy")); option.value = strategy.id;
      const tr = node("tr", null, byId("strategy-rows")); node("th", strategy.label, tr).scope = "row";
      node("td", `${strategy.current_count} records · ${strategy.unbuilt_count} awaiting routes`, tr);
      node("td", strategy.description, tr);
    }
    const [reports, seasonalRoutes] = await Promise.all([Promise.all(catalog.candidates.map(row => row.report_inline || load(`../${row.candidate_file}`))), seasonalRoutesReady]);
    const body = byId("reference-route-rows");
    for (const id of catalog.reference_route_length_order) {
      const row = catalog.candidates.find(item => item.id === id);
      const tr = node("tr", null, body); tr.id = `comparison-${id}`; link(row.name, `#${id}`, node("td", null, tr));
      node("td", `≈ ${number(row.approximate_reference_path_km)} km`, tr);
      node("td", window.OSWReferenceRouteText.range(row), tr);
      const sensitivity = node("td", null, tr), bounds = row.ordering_sensitivity.envelope_position_bounds;
      node("span", bounds[0] === bounds[1] ? `Position ${bounds[0]} within retained envelopes` : `Positions ${bounds[0]}–${bounds[1]} within retained envelopes`, sensitivity);
      if (row.ordering_sensitivity.overlapping_candidate_ids.length) {
        const details = node("details", null, sensitivity);
        node("summary", "Overlapping route envelopes", details);
        for (const otherId of row.ordering_sensitivity.overlapping_candidate_ids) {
          const other = catalog.candidates.find(item => item.id === otherId);
          link(other.name, `#${otherId}`, node("p", null, details));
        }
      }
      node("td", row.scope, tr);
    }
    for (let index = 0; index < catalog.candidates.length; index++) {
      const row = catalog.candidates[index], report = reports[index];
      const card = node("section", null, byId("route-cards")); card.id = row.id; card.className = "route-card";
      card.tabIndex = -1;
      node("h3", `${row.name} · ${row.route_extent_kind}`, card);
      link("Link to this route card", `#${row.id}`, node("p", null, card));
      const back = link("Back to global current map ↑", '#route-atlas', node("p", null, card));

      node("p", window.OSWReferenceRouteText.summary(row), card);
      node("p", row.scope, card);
      if(row.comparison_group==='osw_abstract_supported_regional_references')node('p','Regional editorial route based on the published abstract. Whole-current endpoints, physical axis and annual range remain unresolved. Excluded from length ordering.',card).className='warning';
      if (report.parent_current_id) {
        const relation = node("p", report.parent_scope_note + " ", card);
        const parent = catalog.candidates.find(item => item.current_id === report.parent_current_id);
        link("Inspect parent current route", parent ? `#${parent.id}` : objectHref(`current:${report.parent_current_id}`), relation);
      }
      if(row.comparison_group==='osw_source_anchor_connections')node('p','Source-reference connection only. Bend probes are geometry sensitivity, with no uncertainty or seasonal interpretation. This connection is excluded from whole-current and reference-route length ordering.',card).className='warning';
      if (row.comparison_group === "osw_studied_reach_routes") node("p", "Studied reach only. Excluded from reference-route ordering above.", card).className = "warning";
      if(row.comparison_group==='osw_offshore_coastal_reference_curves')node('p','Coast-following geographic reference only. Kept separate from waypoint-route ordering and published current lengths. Projected offsets are not current widths; no measured axis or seasonal geometry.',card).className='warning';
      if(row.comparison_group==='osw_offshore_coastal_reference_curves'){
        link('Natural Earth coastline source and map scale','https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/',node('p',null,card),true);
        const compare=node('details',null,card);node('summary','Compare the earlier routes against both coastlines',compare);
        const map=node('img',null,compare);map.src='../figures/madagascar-coastline-comparison.svg';map.alt='The earlier coastal routes intersect both land products; the farther-offshore alternatives clear both. Same54 routes, no fitted vertices.';map.loading='lazy';map.style.cssText='width:100%;max-width:1400px;height:auto';
        link('Open coastline comparison figure',map.src,node('p',null,compare));
        const q={collection:'diagnostics',filters:[{field:'id',op:'eq',value:'diagnostic:madagascar-coastline-comparison'}],limit:1};
        link('Query all 54 paired coastline checks','query.html?q='+encodeURIComponent(JSON.stringify(q)),node('p',null,compare));
      }
      const image = node("img", null, card); image.className = "route-map"; image.src = `../${row.figure}`; image.alt = `${row.name}: schematic editorial route with labeled gates. ${window.OSWReferenceRouteText.hasRange(row)?'Approximate length and scenario limits are provided in the surrounding text.':'Approximate regional length is provided in the surrounding text; endpoints and dimension ranges remain unresolved.'}`;
      const compactFigure=window.OSWReferenceRouteText.compactFigure(row,report);
      if(compactFigure){
        const responsive=document.createElement('picture'),mobile=document.createElement('source');
        mobile.media='(max-width:480px)';mobile.srcset=`../${compactFigure}`;
        image.replaceWith(responsive);responsive.append(mobile,image);
      }
      if(report.rendering_role==='derived_inline_source_reference_card_not_additional_observation')node('p','The comparison figure shows both source-coordinate conventions and their retained bend probes. This card describes the selected connection; neither convention is a measured whole-current axis.',card);
      // Reserve map height so earlier image loads cannot move the linked card.
      image.width = 800;
      image.height = Math.round(800 * (report.figure_aspect_ratio||report.map_view_box[3] / report.map_view_box[2]));
      link("Open route map at full size", `../${row.figure}`, node("p", null, card));
      node("p", report.coordinate_selection, card);
      if(report.source_reference_anchors){const list=node('ul',null,card);for(const anchor of report.source_reference_anchors)node('li',`${anchor.id}: ${anchor.source_notation}; nominal source reference coordinate.`,list);}
      if(row.current_id==='kuroshio')window.renderKuroshioDaily(card,window.oswAtlasSnapshot?.kuroshio_daily_scene);
      if(row.current_id==='agulhas')window.renderAgulhasReportedDimensions(card,window.oswAtlasSnapshot?.agulhas_reported_scene);
      node("p", `Layer: ${report.layer} Time convention: ${report.time_convention}`, card);
      node("p", report.scenario_rule, card);
      const source = node("p", "Source: ", card); link(report.source_citation, report.source_url, source, true);
      node("p", `Source locator: ${row.source_locator}`, card);
      if (report.source_anchor_observations?.length) {
        node("p", "Source frontal crossings · sampled separately; not current-axis endpoints", card);
        const anchors = node("ul", null, card);
        for (const anchor of report.source_anchor_observations) {
          const [lon,lat] = anchor.longitude_latitude;
          node("li", `${Math.abs(lon)}° ${lon < 0 ? "W" : "E"}, ${Math.abs(lat)}° ${lat < 0 ? "S" : "N"} · ${anchor.observed_period.start} to ${anchor.observed_period.end} (month precision) · observed front crossing, not velocity core`, anchors);
        }
      }
      for (const support of report.supporting_sources || []) {
        const citation = node("p", "Supporting source: ", card); link(window.OSWReferenceRouteText.supportCitation(support), support.url, citation, true);
        node("p", `${support.locator} ${support.role || ""}`, card);
      }
      const regionContext=window.OSWReferenceRouteText.regionContext(row,report);
      const geography = node("p", regionContext.label, card);
      for (const state of regionContext.codes) { link(state, objectHref(`state:${state}`), geography); geography.append(document.createTextNode(" ")); }
      if(regionContext.note)node('p',regionContext.note,card);
      if(report.state_scope_note)node('p',report.state_scope_note,card);
      const tile = report.nasa_movie_context.find(item => item.tile_id === report.recommended_nasa_tile_id);
      if (tile) link(`Open complete-route NASA crop ${tile.tile_id} (geographic context)`, tile.url, card, true);
      const details = node("details", null, card); node("summary", "Method and remaining review", details);
      node("p", report.method, details); node("p", report.map_land_check, details);
      const list = node("ul", null, details); for (const gate of row.remaining_gates) node("li", gate, list);
      window.renderMeanCoreSections(card,window.oswAtlasSnapshot?.mean_core_section_scenes?.[row.current_id],undefined,{collapsed:true});
      window.renderCurrentDimensionEvidence(card,window.oswAtlasSnapshot?.current_dimension_evidence_scenes?.[row.current_id],undefined,{collapsed:true});
      const phase = seasonalRoutes.frames.find(frame => frame.route_candidate_file === row.candidate_file);
      link("Widths and seasonal evidence", `seasons.html?current=${encodeURIComponent(row.current_id)}${phase ? `&phase=${encodeURIComponent(phase.id)}` : ""}`, node("p", null, card));
      if(row.current_id==='zeehan')window.renderQualitativeCurrentCalendar(card,await load('../research/zeehan-ridgway-2007-seasonal-scope-audit.json'));
      if(row.current_id==='atlantic-equatorial-undercurrent')window.renderAtlanticEucSectionProperties(card,await load('../research/atlantic-euc-layer-island-scope-audit.json'));
      if(report.rendering_role==='derived_inline_source_reference_card_not_additional_observation'){
        link('Download source reference candidates (JSON)',`../${row.candidate_file}`,card);
        link('Download all retained reference calculations (JSON)',`../${report.calculation_file}`,node('p',null,card));
      }else link("Download coordinates, all scenarios and joins (JSON)", `../${row.candidate_file}`, card);
    }
    if(window.oswAtlasSnapshot?.kuroshio_daily_scene&&!catalog.candidates.some(r=>r.current_id==='kuroshio')){
      const card=node('section',null,byId('route-cards'));card.id='kuroshio-2024-model-card';card.className='current-model-card';card.tabIndex=-1;
      node('h3','Kuroshio · dated regional model map card',card);
      node('p','Regional source geometry and measurements. This is separate from the whole-current reference-route catalogue.',card);
      link('Link to this model map card','#'+card.id,node('p',null,card));
      link('Back to Kuroshio on the global map','reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio#route-atlas',node('p',null,card)).dataset.kuroshioMapReturn='true';
      window.renderKuroshioDaily(card,window.oswAtlasSnapshot.kuroshio_daily_scene);
    }
    const counts = catalog.counts;
    byId("route-status").textContent = `${counts.route_candidates} route candidates for ${counts.currents_with_route_candidates} of ${counts.accepted_current_names} currents; ${counts.currents_without_any_reference_card} currents have no reference card. ${counts.currents_without_route_candidates} are on the remaining-length worklist. Published length reports and geographic routes are separate evidence. Scientific review pending.`;
    byId("route-query").addEventListener("input", renderQueue); byId("route-coverage").addEventListener("change", renderQueue); byId("route-strategy").addEventListener("change", renderQueue); renderQueue();
    requestAnimationFrame(revealInitialCard);
    window.initReferenceRouteAtlas?.(catalog, reports, await widthInventoryReady, seasonalRoutes);
  }).catch(error => { byId("route-status").textContent = `Route inventory unavailable: ${error.message}`; });
})();
