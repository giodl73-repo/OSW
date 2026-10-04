"use strict";

const interiorLedger = window.OSW_STATE_INTERIOR_LEDGER;
const interiorDynamics = window.OSW_INTRA_STATE_DYNAMICS;

function interiorDefinition(grid, term, value) {
  const wrapper = document.createElement("div"), dt = document.createElement("dt"), dd = document.createElement("dd");
  dt.textContent = term; dd.textContent = value; wrapper.append(dt, dd); grid.append(wrapper);
}

function interiorList(id, rows, empty) {
  const target = document.querySelector(id); target.replaceChildren();
  if (!rows.length) { const item = document.createElement("li"); item.textContent = empty; target.append(item); return; }
  rows.forEach(row => { const item = document.createElement("li"); item.textContent = row; target.append(item); });
}

function renderDensityMonthTable() {
  const bin = document.querySelector("#interior-density-bin").value;
  const body = document.querySelector("#interior-density-monthly-body");
  body.replaceChildren();
  const format = value => Math.abs(value) < 0.0005 ? "0.000" : `${value > 0 ? "+" : ""}${value.toFixed(3)}`;
  interiorDynamics.bounded_results.annual_density_boundary_comparison.forEach(month => {
    const item = month.strata.find(stratum => stratum.id === bin);
    const controls = item.control_centered_net_outward_Sv;
    const centered = item.primary_centered_net_outward_Sv, upstream = item.primary_upstream_net_outward_Sv;
    const sign = Math.abs(centered) < 0.0005 || Math.abs(upstream) < 0.0005 ? "Near zero" : Math.sign(centered) === Math.sign(upstream) ? "Same sign" : "Changes sign";
    const row = document.createElement("tr");
    [month.valid_time.slice(0, 7), `${(item.primary_inventory_volume_fraction * 100).toFixed(2)}%`, format(centered), format(upstream), `${format(Math.min(...controls))} to ${format(Math.max(...controls))}`, sign].forEach(value => {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    });
    body.append(row);
  });
}

document.querySelector("#interior-density-bin").addEventListener("change", renderDensityMonthTable);

function renderCutoffSummary() {
  const cutoff = interiorDynamics.bounded_results.density_cutoff_sensitivity_summary;
  const july = cutoff.july_middle_high_all_boxes_methods_shifts_outward ? "July's middle-high bin stays outward across the shifted cutoffs, both collocation methods, and all four boxes" : "July's middle-high bin changes sign under at least one cutoff, method, or control";
  const august = Math.sign(cutoff.august_primary_baseline_centered_Sv) === Math.sign(cutoff.august_primary_baseline_upstream_Sv) ? "August's primary baseline sign agrees between methods." : "August's primary baseline sign changes between methods.";
  const lighter = cutoff.raised_cutoff_lighter_bin_present_july_october ? "Raising the cutoffs removes the baseline lighter-bin absence from July through October." : "The lighter-bin absence persists under the raised cutoffs.";
  document.querySelector("#interior-cutoff-result").textContent = `${july}. The primary centered July range is ${cutoff.july_primary_centered_range_Sv[0].toFixed(3)}–${cutoff.july_primary_centered_range_Sv[1].toFixed(3)} Sv. ${august} ${lighter}`;
}

function renderJulyRepeatTable() {
  const body = document.querySelector("#interior-july-repeat-body");
  body.replaceChildren();
  const format = value => `${value > 0 ? "+" : ""}${value.toFixed(3)}`;
  interiorDynamics.bounded_results.july_repeat_sign_summary.years.forEach(year => {
    const minimum = year.minimum_tested_case;
    const detail = `${minimum.box.replaceAll("_", " ")}, ${minimum.scheme.replaceAll("_", " ")}, ${minimum.method.startsWith("upstream") ? "upstream" : "centered"}`;
    const row = document.createElement("tr");
    [year.month.slice(0, 4), format(year.primary_baseline_centered_Sv), format(year.primary_baseline_upstream_Sv), `${format(minimum.net_outward_Sv)} (${detail})`, year.predeclared_sign_pass ? "Pass" : "Fail"].forEach(value => {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    });
    body.append(row);
  });
}

function renderJulyEnsembleTable() {
  const summary = interiorDynamics.bounded_results.july_ensemble_sign_summary;
  const body = document.querySelector("#interior-july-ensemble-body");
  body.replaceChildren();
  const format = value => `${value > 0 ? "+" : ""}${value.toFixed(3)}`;
  summary.members.forEach(member => {
    const row = document.createElement("tr");
    [member.member, format(member.primary_baseline_centered_Sv), format(member.primary_baseline_upstream_Sv), format(member.east_control_baseline_upstream_Sv), member.predeclared_sign_pass ? "Pass" : "Fail"].forEach(value => {
      const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
    });
    body.append(row);
  });
  document.querySelector("#interior-july-ensemble-result").textContent = `${summary.decision.pass_count} of ${summary.decision.member_count} members pass the strict four-box sign rule. The east-control baseline upstream sign ${summary.decision.east_control_baseline_upstream_sign_varies ? "varies" : "agrees"} across members. This is within-product sensitivity, not independent replication.`;
}

function renderInterior() {
  const content = interiorLedger.contents[0], grid = document.querySelector("#interior-address-grid");
  grid.replaceChildren();
  [["State", interiorLedger.address.province], ["Depth", interiorLedger.address.depth_support], ["Valid time", interiorLedger.valid_time], ["Property", "potential temperature"], ["Evidence", "model screen"], ["Support", `${(content.support.fraction * 100).toFixed(1)}% of ${content.support.valid_native_t_cells.toLocaleString()} native T cells`]].forEach(([term, value]) => interiorDefinition(grid, term, value));
  const body = document.querySelector("#interior-contents-body"); body.replaceChildren();
  const values = [content.property, content.units, `${content.distribution.median_degC.toFixed(2)} °C`, `${content.distribution.p25_degC.toFixed(2)}–${content.distribution.p75_degC.toFixed(2)} °C`, content.support.valid_native_t_cells.toLocaleString(), "model screen · uncertainty not estimated"];
  const row = document.createElement("tr"); values.forEach(value => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); }); body.append(row);
  interiorList("#interior-overlays", interiorLedger.overlays.map(item => `${item.relation.replaceAll("_", " ")}: ${item.finding} ${item.boundary}`), "No overlay is admitted for this pilot. This is unknown, not evidence that the state has no features.");
  interiorList("#interior-links", interiorLedger.internal_links.map(item => item.relation), "No internal pathway, transfer, convergence, or transformation is admitted to this archived contents ledger. Separate current-geometry screens are listed below and are not numerically joined here.");
  interiorList("#interior-unknowns", interiorLedger.unknowns.map(item => `${item.relation.replaceAll("_", " ")}: ${item.reason}`), "No named unknowns.");
  document.querySelector("#interior-boundary-context").textContent = `SANT ↔ ${interiorLedger.boundary_context.counterpart_state}: ${interiorLedger.boundary_context.reason} It remains ${interiorLedger.boundary_context.join_status.replaceAll("_", " ")}.`;
  const covered = interiorDynamics.relation_coverage;
  interiorList("#interior-dynamics-coverage", covered.map(item => `${item.relation.replaceAll("_", " ")}: ${item.status.replaceAll("_", " ")}. ${item.evidence || item.reason} ${item.non_claim || item.required_evidence || ""}`), "No separate dynamics synthesis is available.");
  renderCutoffSummary();
  renderJulyRepeatTable();
  renderJulyEnsembleTable();
  renderDensityMonthTable();
  const repeatDecision = interiorDynamics.bounded_results.july_repeat_sign_summary.decision;
  document.querySelector("#interior-summary").textContent = `The archived ledger has one contents record and five named unknown relationship classes. Separate current-geometry screens add bounded kinematics, temperature and density structure, and closed-box horizontal terms. The strict three-July repeat-year sign rule ${repeatDecision === "repeat_year_sign_screen_pass" ? "passes" : "fails"}. These values are not joined to the archived ledger and do not form a transformation diagnosis or budget.`;
}
