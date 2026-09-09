(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.OSWEventScenes = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const SCENES = [
    {
      id: "event", number: "01", label: "Event", question: "What was tracked?",
      evidence: "DERIVED OBSERVATION PRODUCT", evidenceKey: "derived",
      figure: "../figures/osw-d3-noaa-crw-mhw-lineage-2026.svg",
      figureAlt: "Twenty-one daily threshold footprints linked into a primary surface lineage, with overlap strength and ambiguity shown through time.",
      primary: "d3", finding: "identity_evaluation.finding", limitation: "boundary",
      secondaryFinding: { source: "d9", path: "identity_evaluation.finding", label: "Gap-policy result" },
      time: { source: "d3", start: "tracked_window.start", end: "tracked_window.end" },
      facts: { variable: "NOAA CRW marine-heatwave category", depth: "surface pixel state", space: "native-grid connected footprints" },
      sources: [
        ["d1", "../research/osw-d1-noaa-crw-mhw-point-2026.json", "osw.detected-ocean-object.v1"],
        ["d3", "../research/osw-d3-noaa-crw-mhw-lineage-2026.json", "osw.tracked-ocean-footprint.v1"],
        ["d9", "../research/osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json", "osw.ocean-object-typed-gap-graph.v1"]
      ],
      stats: [
        { source: "d3", path: "tracked_window.day_count", label: "Primary lineage", unit: "days", digits: 0 },
        { source: "d3", path: "summary.maximum_daily_area_km2", label: "Largest daily footprint", unit: "km²", digits: 1 }
      ],
      receipt: "../research/osw-d3-noaa-crw-mhw-lineage-2026.json"
    },
    {
      id: "surface", number: "02", label: "Surface", question: "Did a second surface product see the sensitive interval?",
      evidence: "DERIVED CROSS-PRODUCT COMPARISON", evidenceKey: "cross-product",
      figure: "../figures/osw-d10-oisst-mhw-bridge-crosscheck-2026.svg",
      figureAlt: "A matched comparison of CoralTemp threshold state and OISST surface-temperature changes around the bridge interval.",
      primary: "d10", finding: "identity_evaluation.finding", limitation: "boundary",
      time: { source: "d10", start: "days.4.date", end: "days.5.date" },
      facts: { variable: "OISST temperature and CRW threshold category", depth: "surface", space: "nearest cell plus fixed comparison box" },
      sources: [["d10", "../research/osw-d10-oisst-mhw-bridge-crosscheck-2026.json", "osw.ocean-object-oisst-bridge-crosscheck.v1"]],
      stats: [
        { source: "d10", path: "bridge_day_comparison.oisst_anchor_change_c", label: "Nearest OISST cell", unit: "°C", digits: 2, signed: true },
        { source: "d10", path: "bridge_day_comparison.oisst_fixed_box_mean_change_c", label: "Fixed-box OISST mean", unit: "°C", digits: 2, signed: true }
      ],
      receipt: "../research/osw-d10-oisst-mhw-bridge-crosscheck-2026.json"
    },
    {
      id: "boundary", number: "03", label: "Sky–ocean boundary", question: "What surface-energy direction and scale did GFS show?",
      evidence: "OPERATIONAL FORECAST / MODEL SCREEN", evidenceKey: "model-screen",
      figure: "../figures/osw-d12-gfs-surface-flux-screen-2026.svg",
      figureAlt: "Surface-energy components and their positive-downward net scale for the August 11 to 12 bridge interval.",
      primary: "d12", finding: "bridge_evaluation.finding", limitation: "boundary",
      time: { source: "d12", start: "intervals.4.start", end: "intervals.4.end" },
      facts: { variable: "net downward surface energy flux", depth: "air–sea interface", space: "GFS box mapped to RTOFS centers" },
      sources: [["d12", "../research/osw-d12-gfs-surface-flux-screen-2026.json", "osw.ocean-object-gfs-surface-flux-screen.v1"]],
      stats: [{ source: "d12", path: "bridge_evaluation.gfs_box_net_downward_surface_flux_w_m2", label: "Box net downward flux", unit: "W m⁻²", digits: 2, signed: true }],
      receipt: "../research/osw-d12-gfs-surface-flux-screen-2026.json"
    },
    {
      id: "column", number: "04", label: "Column", question: "Did the upper 50 m store heat?",
      evidence: "OPERATIONAL ASSIMILATIVE-MODEL SCREEN", evidenceKey: "model-screen",
      figure: "../figures/osw-d13-rtofs-mhw-upper-ocean-storage-2026.svg",
      figureAlt: "Surface and fixed-column temperature changes with 0 to 50 metre storage tendency for the bridge interval.",
      primary: "d13", finding: "bridge_evaluation.finding", limitation: "boundary",
      time: { source: "d13", start: "intervals.4.start", end: "intervals.4.end" },
      facts: { variable: "fixed-column storage tendency", depth: "0–50 m", space: "4,221-cell fixed North Atlantic box" },
      sources: [["d13", "../research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json", "osw.ocean-object-rtofs-upper-ocean-storage-screen.v1"]],
      stats: [
        { source: "d13", path: "bridge_evaluation.box_zero_to_50_m_storage_tendency_w_m2", label: "0–50 m storage tendency", unit: "W m⁻²", digits: 2, signed: true },
        { source: "d13", path: "bridge_evaluation.gfs_surface_flux_fraction_of_rtofs_storage_scale", label: "GFS surface / RTOFS storage", unit: "%", digits: 1, percent: true }
      ],
      receipt: "../research/osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
    },
    {
      id: "motion", number: "05", label: "Motion", question: "How did horizontal advection compare with the storage scale?",
      evidence: "OFFLINE MODEL-DERIVED SCREEN", evidenceKey: "model-screen",
      figure: "../figures/osw-d14-rtofs-mhw-upper-ocean-advection-2026.svg",
      figureAlt: "Depth-integrated horizontal-advection scales compared with fixed-column storage and crossed-system surface energy.",
      primary: "d14", finding: "bridge_evaluation.finding", limitation: "boundary",
      time: { source: "d14", start: "intervals.4.start", end: "intervals.4.end" },
      facts: { variable: "offline horizontal-advection scale", depth: "0–50 m", space: "4,217 gradient-valid fixed-box cells" },
      sources: [["d14", "../research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json", "osw.ocean-object-rtofs-upper-ocean-advection-screen.v1"]],
      stats: [
        { source: "d14", path: "bridge_evaluation.rtofs_offline_0_50_m_horizontal_advection_w_m2", label: "Horizontal advection", unit: "W m⁻²", digits: 2, signed: true },
        { source: "d14", path: "bridge_evaluation.horizontal_advection_fraction_of_storage", label: "Advection / storage", unit: "%", digits: 1, percent: true },
        { source: "d14", path: "bridge_evaluation.cross_system_partial_residual_w_m2", label: "Unresolved partial residual", unit: "W m⁻²", digits: 2, signed: true }
      ],
      receipt: "../research/osw-d14-rtofs-mhw-upper-ocean-advection-2026.json",
      onward: "../exchange/?stage=events"
    }
  ];

  function getPath(value, path) {
    return path.split(".").reduce(function (current, key) {
      if (current == null || !Object.prototype.hasOwnProperty.call(current, key)) throw new Error("Missing selector: " + path);
      return current[key];
    }, value);
  }

  function sceneById(id) { return SCENES.find(function (scene) { return scene.id === id; }) || SCENES[0]; }

  function validate(scene, payloads) {
    scene.sources.forEach(function (source) {
      const payload = payloads[source[0]];
      if (!payload) throw new Error("Missing source: " + source[0]);
      if (payload.schema !== source[2]) throw new Error("Unexpected schema for " + source[0] + ": " + String(payload.schema));
    });
    scene.stats.forEach(function (stat) { getPath(payloads[stat.source], stat.path); });
    getPath(payloads[scene.primary], scene.finding);
    getPath(payloads[scene.primary], scene.limitation);
    return true;
  }

  function formatStat(stat, raw) {
    const value = stat.percent ? raw * 100 : raw;
    const sign = stat.signed && value > 0 ? "+" : "";
    return sign + Number(value).toFixed(stat.digits) + " " + stat.unit;
  }

  function model(scene, payloads) {
    validate(scene, payloads);
    const primary = payloads[scene.primary];
    const secondary = scene.secondaryFinding ? getPath(payloads[scene.secondaryFinding.source], scene.secondaryFinding.path) : null;
    return {
      finding: getPath(primary, scene.finding),
      limitation: getPath(primary, scene.limitation),
      secondary: secondary,
      time: getPath(payloads[scene.time.source], scene.time.start) + " → " + getPath(payloads[scene.time.source], scene.time.end),
      stats: scene.stats.map(function (stat) { return { label: stat.label, value: formatStat(stat, getPath(payloads[stat.source], stat.path)) }; })
    };
  }

  return { SCENES: SCENES, getPath: getPath, sceneById: sceneById, validate: validate, formatStat: formatStat, model: model };
});
