(function (root) {
  "use strict";
  const exchangeCodes = new Set(["ANTA", "APLR", "FKLD", "HUMB", "SANT", "SSTC"]);
  const eventCodes = new Set(["GFST", "NWCS"]);
  function cards(code) {
    const exchange = exchangeCodes.has(code);
    const event = eventCodes.has(code);
    return [
      { id:"column", title:"Ocean Column", href:`../column/?province=${encodeURIComponent(code)}`, available:true, text:"Open this state’s declared vertical address and bathymetry context. Seed and footprint limits remain stated there." },
      { id:"exchange", title:"Exchange Observatory", href:exchange ? `../exchange/?province=${encodeURIComponent(code)}&depth=0-200m&month=201802` : "../exchange/", available:exchange, text:exchange ? "A bounded 2018 Drake native-grid temperature screen is available for this state." : "No bounded Drake native-grid temperature passport is committed for this state." },
      { id:"event", title:"Heat-event route", href:event ? "../event/?scene=event" : "../event/", available:event, text:event ? (code === "GFST" ? "The 2026 primary surface-event route is state-addressed in GFST; it is not transported heat." : "One small GFST-to-NWCS lineage branch is state-addressed here; it is not transported heat.") : "No committed state-addressed evidence from the guided 2026 event route is available for this state." }
    ];
  }
  root.OSWStateHandoffs = { exchangeCodes, eventCodes, cards };
})(window);
