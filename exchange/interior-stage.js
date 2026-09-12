"use strict";

const interiorLedger = window.OSW_STATE_INTERIOR_LEDGER;

function interiorDefinition(grid, term, value) {
  const wrapper = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
  dt.textContent = term; dd.textContent = value; wrapper.append(dt, dd); grid.append(wrapper);
}

function interiorList(id, rows, empty) {
  const target = document.querySelector(id); target.replaceChildren();
  if (!rows.length) { const item = document.createElement("li"); item.textContent = empty; target.append(item); return; }
  rows.forEach(row => { const item = document.createElement("li"); item.textContent = row; target.append(item); });
}

function renderInterior() {
  const content = interiorLedger.contents[0], grid = document.querySelector("#interior-address-grid");
  grid.replaceChildren();
  [["State", interiorLedger.address.province], ["Depth", interiorLedger.address.depth_support], ["Valid time", interiorLedger.valid_time], ["Property", "potential temperature"], ["Evidence", "model screen"], ["Support", `${(content.support.fraction * 100).toFixed(1)}% of ${content.support.valid_native_t_cells.toLocaleString()} native T cells`]].forEach(([term, value]) => interiorDefinition(grid, term, value));
  const body = document.querySelector("#interior-contents-body"); body.replaceChildren();
  const values = [content.property, content.units, `${content.distribution.median_degC.toFixed(2)} °C`, `${content.distribution.p25_degC.toFixed(2)}–${content.distribution.p75_degC.toFixed(2)} °C`, content.support.valid_native_t_cells.toLocaleString(), "model screen · uncertainty not estimated"];
  const row = document.createElement("tr"); values.forEach(value => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); }); body.append(row);
  interiorList("#interior-overlays", interiorLedger.overlays.map(item => item.relation), "No dynamic overlay is admitted for this pilot. This is unknown, not evidence that the state has no features.");
  interiorList("#interior-links", interiorLedger.internal_links.map(item => item.relation), "No internal pathway, transfer, convergence, or transformation is admitted for this pilot.");
  interiorList("#interior-unknowns", interiorLedger.unknowns.map(item => `${item.relation.replaceAll("_", " ")}: ${item.reason}`), "No named unknowns.");
  document.querySelector("#interior-boundary-context").textContent = `SANT ↔ ${interiorLedger.boundary_context.counterpart_state}: ${interiorLedger.boundary_context.reason} It remains ${interiorLedger.boundary_context.join_status.replaceAll("_", " ")}.`;
  document.querySelector("#interior-summary").textContent = "This first ledger has one contents record and five named unknown relationship classes. It is a state address account, not a dynamic-state diagnosis or a budget.";
}
