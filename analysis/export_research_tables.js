"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..");
const appPath = path.join(root, "atlas", "app.js");
const appSource = fs.readFileSync(appPath, "utf8");
const zoneMatch = appSource.match(/const legacyZones = [\s\S]*?\nconst markers =/);

if (!zoneMatch) throw new Error("Could not locate the Atlas zone catalog");

const catalogProgram = `${zoneMatch[0].replace(/\nconst markers =$/, "")}\nJSON.stringify(zones);`;
const zones = JSON.parse(vm.runInNewContext(catalogProgram, Object.create(null), { timeout: 1000 }));

function csvCell(value) {
  const text = Array.isArray(value) ? value.join(" | ") : String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function csv(headers, rows) {
  return [headers, ...rows]
    .map(row => row.map(csvCell).join(","))
    .join("\n") + "\n";
}

const zoneHeaders = [
  "catalog_version", "number", "id", "name", "kind", "map_label", "role",
  "lens", "depth_class", "properties", "basis", "depth", "persistence", "evidence_class", "source_ids", "families", "summary",
  "inferential_boundary", "primary_or_register_source"
];
const zoneRows = zones.map(zone => {
  const [evidenceClass, sourceIds = ""] = zone.evidence.split(" · ");
  return [
    "atlas-08", zone.n, zone.id, zone.name, zone.kind, zone.label, zone.role,
    zone.lens, zone.depthClass, zone.properties, zone.basis, zone.depth, zone.clock, evidenceClass, sourceIds, zone.families, zone.summary,
    zone.boundary, zone.source
  ];
});

const claimHeaders = [
  "claim_id", "statement", "evidence_class", "supported_by",
  "does_not_establish", "references"
];
const claimRows = [
  [
    "C1",
    "Land-ocean geometry differs strongly between counterpart northern and southern latitude rows.",
    "observed-product geometry",
    "Fixed OISST analyzed-water mask and complete paired-row scan.",
    "ACC strength; frontal permeability; heat content; heat transport.",
    "10.1016/0967-0637(95)00021-W | 10.1029/2008JC005108"
  ],
  [
    "C2",
    "Absolute SST, SST anomaly, and estimated analysis error tell different stories at the same cell.",
    "observed surface fields",
    "Co-located NOAA OISST variables sst, anom, and err.",
    "Subsurface conditions; causal attribution; total energy.",
    "10.25921/RE9P-PT57 | 10.3389/fmars.2019.00416"
  ],
  [
    "C3",
    "Reservoir, pathway, anomaly, buried layer, and gate are candidate map roles for organizing ocean-heat questions.",
    "explanatory synthesis",
    "Mechanism-separated visual grammar and literature-qualified examples.",
    "An optimal classification; fixed boundaries; exhaustive coverage.",
    "10.1029/2022RG000781"
  ],
  [
    "C4",
    "Closing Drake Passage reorganizes Southern Ocean climate in an idealized coupled-model counterfactual.",
    "model counterfactual",
    "A coupled Drake-closure experiment read beside paleoclimate attribution evidence.",
    "A feasible intervention; unique outcome; modern ice-loss forecast; gateway-only causation.",
    "10.1175/JCLI-D-15-0554.1 | 10.1038/nature13597"
  ]
];

fs.writeFileSync(path.join(root, "research", "zone-catalog.csv"), csv(zoneHeaders, zoneRows), "utf8");
fs.writeFileSync(path.join(root, "research", "claims-ledger.csv"), csv(claimHeaders, claimRows), "utf8");

console.log(`Wrote ${zoneRows.length} zones and ${claimRows.length} claims.`);
