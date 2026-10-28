"use strict";
window.oswDashboardEvidenceSchema={
  validFingerprints(fingerprints,groups){
    if(!fingerprints||typeof fingerprints!=='object'||Array.isArray(fingerprints))return false;
    return Object.keys(groups).every(key=>
      key==='mean_model_core_sections'&&!Object.hasOwn(fingerprints,key)||typeof fingerprints[key]==='string');
  },
  validCapabilities(capabilities,labels,contextMetrics){
    if(!capabilities||typeof capabilities!=='object'||Array.isArray(capabilities))return false;
    const optional=new Set(['section_transport','model_dimension_samples','axis_normal_samples','reported_model_core_sections']);
    return Object.keys(labels).every(key=>{
      const present=Object.hasOwn(capabilities,key);
      if(!present&&(optional.has(key)||Object.hasOwn(contextMetrics,key)))return true;
      return Number.isInteger(capabilities[key])&&capabilities[key]>=0;
    });
  }
};
