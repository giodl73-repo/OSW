"use strict";
window.oswRegionalModelAtlas=(()=>{
  const scene=(snapshot,id)=>snapshot?.regional_model_length_scenes?.[id.replace(/^current:/,'')]||null;
  const qualified=s=>(s?.readings||[]).filter(r=>typeof r.length_km==='number'&&Number.isFinite(r.length_km)&&r.geometry?.type==='LineString'&&r.geometry.coordinates?.length>1);
  const nominal=s=>qualified(s).filter(r=>r.kernel_cells===s.series.nominal_kernel_cells);
  const selection=(s,id)=>qualified(s).find(r=>r.id===id)||nominal(s)[0]||null;
  function draw({scene:s,currentId,parent,make,pathData,interactive,onSelect}){
    return qualified(s).map(row=>{
      const line=make('path',{d:pathData(row.geometry.coordinates),class:'route-atlas-regional-model-line','vector-effect':'non-scaling-stroke'},parent);
      line.dataset.currentId=currentId;line.dataset.modelReadingId=row.id;
      line.dataset.modelNominal=String(row.kernel_cells===s.series.nominal_kernel_cells);
      const label=`Indian SEC · SON ${row.provider_year} · kernel ${row.kernel_cells} · regional model-grid trace · about ${row.approximate_length_km.toLocaleString('en-US')} km. Whole-current length unknown.`;
      line.dataset.atlasLabel=label;interactive(line,label,()=>onSelect(row));return line;
    });
  }
  return {scene,qualified,nominal,selection,draw};
})();
