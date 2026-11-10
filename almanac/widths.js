"use strict";
(async()=>{
  const $=id=>document.getElementById(id),add=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const explain=value=>value===null?'Not specified':typeof value==='string'?value:Array.isArray(value)?value.map(explain).join('; '):typeof value==='object'?Object.entries(value).filter(([k,v])=>k!=='id'&&v!==null).map(([k,v])=>`${k.replaceAll('_',' ')}: ${explain(v)}`).join('; '):String(value),number=value=>value.toLocaleString(undefined,{maximumFractionDigits:3});
  function quantity(r){
    if(r.point_km!==null)return `≈ ${number(r.point_km)} km`;
    if(r.range_km)return `${r.range_km.map(number).join('–')} km · source range`;
    if(r.lower_bound_km!==null)return `${r.lower_bound_exclusive?'>':'≥'} ${number(r.lower_bound_km)} km`;
    if(r.upper_bound_km!==null)return `${r.upper_bound_exclusive?'<':'≤'} ${number(r.upper_bound_km)} km`;
    const c=r.constraint;if(c?.reference_range_km)return `Within ≈ ${c.reference_range_km.map(number).join('–')} km · confinement`;
    return c?.source_notation||`Source constraint: ${number(c?.reference_scale_km??c?.value_km)} km`;
  }
  function link(label,url,parent){const a=add('a',label,parent);a.href=url;return a;}
  try{
    const response=await fetch('../research/current-width-register-v1.json');if(!response.ok)throw Error('Width register unavailable');const data=await response.json();
    if(data.schema!=='osw.current-width-register.v1'||data.records.length!==111||new Set(data.records.map(r=>r.entity_id)).size!==111)throw Error('Incomplete width identity inventory');
    const byId=new Map(data.evidence.map(r=>[r.id,r])),metrics=[...new Set(data.evidence.map(r=>r.metric))].sort();
    for(const metric of metrics){const option=add('option',data.evidence.find(r=>r.metric===metric).metric_label,$('width-metric'));option.value=metric;}
    const c=data.counts;$('width-summary').textContent=`${c.retained_scoped_records} retained scoped records across ${c.identities_with_retained_scoped_evidence} identities · ${c.new_qualified_reference_records} new qualified reference · ${c.identities_without_direct_width_reference} identities still without a direct width reference`;
    function renderRecord(r,parent){
      const box=add('div',undefined,parent);box.className='width-record';box.dataset.evidenceId=r.id;
      add('h3',quantity(r),box).className='width-value';add('p',r.metric_label,box);
      if(r.evidence_role==='new_qualified_reference')add('strong','Qualified reference · not a new paired-boundary measurement',box);
      add('p',r.scope||'Geographic scope is not specified for this quantity; inspect the retained source.',box);
      add('p','Layer: '+(r.layer||'Not independently specified for this quantity.'),box);
      add('p','Time: '+(r.time?explain(r.time):r.phase_label||'No exact width occupation assigned.'),box);
      add('p','Boundary definition: '+(r.operator?explain(r.operator):'Not numerically specified in this source description.'),box);
      if(r.range_interpretation)add('p',r.range_interpretation,box);
      if(r.zero_range_endpoint_as_reported)add('p','Zero is an explicitly reported range endpoint, not a missing-data code. No mean width or independent absence claim is inferred.',box);
      if(r.constraint?.is_rigorous_upper_bound===false)add('p','This source description is not a rigorous upper bound. No paired-edge width or representative midpoint is inferred.',box);
      if(r.uncertainty_km!==null)add('p','Source uncertainty: '+explain(r.uncertainty_km)+' km. Retain the source definition.',box);
      if(r.reported_standard_deviation_km!==null)add('p','Source standard deviation: '+number(r.reported_standard_deviation_km)+' km; not automatically an uncertainty interval.',box);
      if(r.quality_note)add('p',explain(r.quality_note),box);
      if(r.source_citation)add('p',r.source_citation,box);
      if(r.source_locator)add('p',r.source_locator,box);
      if(r.source_url)link('Original source',r.source_url,box);
      link('Retained source record','../'+r.source_file,box);
      add('span','Source location: '+r.source_pointer,box).className='width-note';
      add('span','Local/definition-specific evidence. Whole-current representative width and annual extrema are not inferred.',box).className='width-note';
    }
    function render(){
      const search=$('width-search').value.trim().toLowerCase(),filter=$('width-filter').value,metric=$('width-metric').value;
      const valueOption=$('width-order').querySelector('option[value="value"]');valueOption.disabled=metric==='all';if(metric==='all')$('width-order').value='name';
      valueOption.textContent=metric==='all'?'Value · select one definition':'Largest point record · one definition';
      const select=r=>r.evidence_ids.map(id=>byId.get(id)).filter(e=>metric==='all'||e.metric===metric);
      let rows=data.records.filter(r=>(!search||`${r.name} ${r.basin||''}`.toLowerCase().includes(search))&&(filter==='all'||filter==='direct'&&r.evidence_ids.length>0||filter===r.status)&&(metric==='all'||select(r).length));
      const point=r=>Math.max(...select(r).map(e=>e.point_km??-1),-1);
      rows.sort($('width-order').value==='value'?(a,b)=>point(b)-point(a)||a.name.localeCompare(b.name):(a,b)=>a.name.localeCompare(b.name));
      $('width-results').textContent=`${rows.length} ${rows.length===1?'identity':'identities'} shown. Values keep their definitions; no whole-current width ranking is implied.`;
      $('width-rows').replaceChildren();
      for(const row of rows){
        const tr=add('tr',undefined,$('width-rows'));tr.dataset.currentId=row.entity_id;
        const cell=label=>{const td=add('td',undefined,tr);td.dataset.label=label;return td;};
        const identity=cell('Current');link(row.name,row.current_card_url,identity);add('span',`${row.basin||''} · ${row.identity_level}`,identity).className='width-note';
        const values=cell('Source quantities'),evidence=select(row),body=cell('Scope and evidence');
        if(evidence.length){
          if(evidence.length===1){add('strong',quantity(evidence[0]),values);add('span',evidence[0].metric_label,values).className='width-note';}
          else{add('strong',`${evidence.length} separate source records`,values);add('span',`${new Set(evidence.map(r=>r.metric)).size} definitions · no pooled range or midpoint`,values).className='width-note';}
          const details=add('details',undefined,body);add('summary',`Inspect ${evidence.length===1?'value and source':'values and sources'}`,details);
          for(const r of evidence)renderRecord(r,details);
          for(const group of data.compatible_seasonal_groups.filter(g=>'current:'+g.current_id===row.entity_id&&g.measurement_ids.every(id=>evidence.some(e=>e.id===id)))){
            add('p','Compatible seasonal comparison: '+group.interpretation,details);
          }
        }else if(row.member_references.length){
          add('strong','Member-specific widths',values);add('span','No parent width assigned or added.',values).className='width-note';
          const details=add('details',undefined,body);add('summary','Inspect family members',details);
          for(const member of row.member_references){const p=add('p',undefined,details);link(member.name,member.current_card_url,p);add('span',` · ${member.evidence_ids.length} scoped records`,p);for(const id of member.evidence_ids)renderRecord(byId.get(id),details);}
        }else{add('strong','Width reference still needed',values).className='width-missing';add('p',row.next_action,body);}
        const query={collection:'width_samples',filters:[{field:'current_id',op:'eq',value:row.entity_id.replace('current:','')}],limit:100};
        link('Inspect available time samples','query.html?q='+encodeURIComponent(JSON.stringify(query)),body);
      }
    }
    $('width-controls').addEventListener('submit',event=>event.preventDefault());
    for(const id of ['width-search','width-filter','width-metric','width-order'])$(id).addEventListener(id==='width-search'?'input':'change',render);
    window.oswCurrentWidthRegister=data;render();
  }catch(error){$('width-summary').textContent=error.message;}
})();
