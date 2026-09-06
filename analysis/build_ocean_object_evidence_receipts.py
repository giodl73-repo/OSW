"""Build worked evidence receipts from existing, checksum-pinned OSW artifacts."""

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "research" / "ocean-object-classification.csv"
OUTPUT = ROOT / "research" / "ocean-object-evidence-receipts.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_js(path):
    text = path.read_text(encoding="utf-8")
    payload = text.split("=", 1)[1].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    return json.loads(payload)


def source(path, payload):
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256(path),
        "embedded_schema": payload["schema"],
    }
    if payload.get("source_sha256"):
        result["upstream_response_sha256"] = payload["source_sha256"]
    return result


def evaluation(objects, object_id, result, finding):
    row = objects[object_id]
    return {
        "object_id": object_id,
        "preferred_name": row["preferred_name"],
        "required_identity_test": row["identity_test"],
        "result": result,
        "finding": finding,
    }


def build(output_path=OUTPUT):
    with REGISTRY.open(encoding="utf-8", newline="") as handle:
        objects = {row["object_id"]: row for row in csv.DictReader(handle)}

    sst_path = ROOT / "atlas" / "data" / "oisst-anomaly-2026-08-01.js"
    argo_path = ROOT / "atlas" / "data" / "argo-temperature-anomaly-300dbar-2026-07.js"
    arctic_path = ROOT / "research" / "osw-m3-oras5-arctic-transport-pilot-201802.json"
    nordic_path = ROOT / "research" / "osw-m4-oras5-nordic-surface-heat-2018.json"
    mhw_path = ROOT / "research" / "osw-d1-noaa-crw-mhw-point-2026.json"
    footprint_path = ROOT / "research" / "osw-d2-noaa-crw-mhw-footprint-20260801.json"
    lineage_path = ROOT / "research" / "osw-d3-noaa-crw-mhw-lineage-2026.json"
    gap_path = ROOT / "research" / "osw-d4-noaa-crw-mhw-gap-identity-2026.json"
    sensitivity_path = ROOT / "research" / "osw-d5-noaa-crw-mhw-tracking-sensitivity-2026.json"
    branch_path = ROOT / "research" / "osw-d6-noaa-crw-mhw-branch-sensitivity-2026.json"
    family_path = ROOT / "research" / "osw-d7-noaa-crw-mhw-lineage-family-2026.json"
    pruning_path = ROOT / "research" / "osw-d8-noaa-crw-mhw-family-pruning-2026.json"
    typed_gap_path = ROOT / "research" / "osw-d9-noaa-crw-mhw-typed-gap-graph-2026.json"
    bridge_crosscheck_path = ROOT / "research" / "osw-d10-oisst-mhw-bridge-crosscheck-2026.json"
    rtofs_advection_path = ROOT / "research" / "osw-d11-rtofs-mhw-horizontal-advection-2026.json"
    gfs_surface_flux_path = ROOT / "research" / "osw-d12-gfs-surface-flux-screen-2026.json"
    upper_ocean_storage_path = ROOT / "research" / "osw-d13-rtofs-mhw-upper-ocean-storage-2026.json"
    upper_ocean_advection_path = ROOT / "research" / "osw-d14-rtofs-mhw-upper-ocean-advection-2026.json"
    sst = load_js(sst_path)
    argo = load_js(argo_path)
    arctic = json.loads(arctic_path.read_text(encoding="utf-8"))
    nordic = json.loads(nordic_path.read_text(encoding="utf-8"))
    mhw = json.loads(mhw_path.read_text(encoding="utf-8"))
    footprint = json.loads(footprint_path.read_text(encoding="utf-8"))
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    gap = json.loads(gap_path.read_text(encoding="utf-8"))
    sensitivity = json.loads(sensitivity_path.read_text(encoding="utf-8"))
    branch = json.loads(branch_path.read_text(encoding="utf-8"))
    family = json.loads(family_path.read_text(encoding="utf-8"))
    pruning = json.loads(pruning_path.read_text(encoding="utf-8"))
    typed_gap = json.loads(typed_gap_path.read_text(encoding="utf-8"))
    bridge_crosscheck = json.loads(bridge_crosscheck_path.read_text(encoding="utf-8"))
    rtofs_advection = json.loads(rtofs_advection_path.read_text(encoding="utf-8"))
    gfs_surface_flux = json.loads(gfs_surface_flux_path.read_text(encoding="utf-8"))
    upper_ocean_storage = json.loads(upper_ocean_storage_path.read_text(encoding="utf-8"))
    upper_ocean_advection = json.loads(upper_ocean_advection_path.read_text(encoding="utf-8"))

    receipts = [
        {
            "receipt_id": "OER001",
            "title": "One-day OISST anomaly field",
            "primary_claim": "observationally constrained sea-surface temperature anomaly field",
            "evidence_origin": "observational_analysis",
            "claim_stage": "field",
            "evidence_status": "supported_with_boundary",
            "representation": "gridded_surface_raster",
            "registry_matches": [],
            "source_artifact": source(sst_path, sst),
            "measurement": {
                "variable": sst["variable"],
                "units": sst["units"],
                "vertical_support": "sea surface",
                "time_support": sst["date"],
                "spatial_support": f'{sst["shape"][0]} x {sst["shape"][1]} display grid at {sst["display_stride"]}-cell stride',
                "baseline": sst["baseline"],
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "not_tested", "One anomaly day does not test event duration and the full marine-heatwave threshold rule.")
            ],
            "supports": ["where the mapped surface was warmer or cooler than the declared climatology on the stated day"],
            "does_not_support": ["marine heatwave", "ocean heat content", "heat transport", "causal attribution"],
            "next_evidence": "Apply a documented percentile, duration, gap, and spatial rule to a continuous daily series.",
            "boundary": sst["boundary"],
        },
        {
            "receipt_id": "OER002",
            "title": "One-level Argo temperature-anomaly analysis",
            "primary_claim": "observationally constrained potential-temperature anomaly at 300 dbar",
            "evidence_origin": "observational_analysis",
            "claim_stage": "field",
            "evidence_status": "supported_with_boundary",
            "representation": "gridded_pressure_surface_raster",
            "registry_matches": [],
            "source_artifact": source(argo_path, argo),
            "measurement": {
                "variable": argo["variable"],
                "units": argo["units"],
                "vertical_support": f'{argo["pressure_dbar"]:g} dbar pressure surface',
                "time_support": argo["month"],
                "spatial_support": f'{argo["shape"][0]} x {argo["shape"][1]} objectively mapped grid ending at 64.5 degrees south',
                "baseline": argo["baseline"],
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ001", "not_tested", "One temperature anomaly level does not establish a volumetric temperature-salinity or source signature."),
                evaluation(objects, "OBJ109", "not_tested", "Heat content requires vertical integration, density/heat-capacity convention, geometry, and a reference state."),
            ],
            "supports": ["the sign and magnitude of mapped temperature anomaly at the declared pressure and month"],
            "does_not_support": ["water mass", "absolute temperature", "ocean heat content", "heat transport", "Antarctic shelf delivery"],
            "next_evidence": "Combine quality-controlled vertical temperature and salinity profiles with layer geometry and an explicit heat-content convention.",
            "boundary": argo["boundary"],
        },
        {
            "receipt_id": "OER003",
            "title": "February 2018 Arctic gateway transports",
            "primary_claim": "reanalysis-derived volume and reference-relative advective heat transport across three declared native-grid sections",
            "evidence_origin": "assimilative_reanalysis",
            "claim_stage": "integrated_quantity",
            "evidence_status": "supported_with_boundary",
            "representation": "section_integrals",
            "registry_matches": ["OBJ032", "OBJ107", "OBJ108"],
            "source_artifact": source(arctic_path, arctic),
            "measurement": {
                "variable": "normal velocity, wet face area, potential temperature, and salinity comparison classes",
                "units": "Sv and PW",
                "vertical_support": "full wet model section",
                "time_support": arctic["month"],
                "spatial_support": "Fram Strait plus two explicitly different Barents section meanings",
                "baseline": "heat transport shown for -1.9, 0, and 2 degrees C reference temperatures",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ032", "pass", "Each section has explicit native-face geometry, orientation, wet cells, and semantics."),
                evaluation(objects, "OBJ107", "pass", "Normal velocity is integrated over wet face area with signed branches and net transport."),
                evaluation(objects, "OBJ108", "pass", "Velocity, temperature, face area, sign, and reference temperature are integrated and sensitivity-tested."),
            ],
            "supports": ["one-month reanalysis gateway volume transport", "one-month reference-relative advective heat transport", "opposing signed branches"],
            "does_not_support": ["heat convergence", "heat storage tendency", "causal attribution", "climatology", "universal Atlantic Water boundary"],
            "next_evidence": "Close a control volume with all boundary sections, surface exchange, storage tendency, and compatible time sampling.",
            "boundary": arctic["boundary"],
        },
        {
            "receipt_id": "OER004",
            "title": "2018 Nordic ocean-surface heat exchange",
            "primary_claim": "reanalysis-derived ocean surface heat flux integrated over a declared Nordic control area",
            "evidence_origin": "assimilative_reanalysis",
            "claim_stage": "integrated_quantity",
            "evidence_status": "supported_with_boundary",
            "representation": "area_integral_time_series",
            "registry_matches": ["OBJ035", "OBJ110"],
            "source_artifact": source(nordic_path, nordic),
            "measurement": {
                "variable": "net downward ocean surface heat flux",
                "units": "W m-2, TW, and ZJ",
                "vertical_support": "air-ocean surface boundary",
                "time_support": "twelve monthly means in 2018",
                "spatial_support": f'{nordic["inside_wet_t_cell_count"]} wet T cells; {nordic["room_surface_area_m2"]:.3e} m2',
                "baseline": "positive downward into the ocean",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ035", "pass", "The surface integral uses the exact wet-cell footprint of a separately receipted control volume."),
                evaluation(objects, "OBJ110", "pass", "Flux density is integrated with native cell areas, sign convention, valid coverage, and monthly duration."),
                evaluation(objects, "OBJ109", "not_tested", "Surface exchange is one tendency term and does not measure the room's heat inventory or storage change."),
            ],
            "supports": ["2018 monthly and annual surface heat exchange over the declared room"],
            "does_not_support": ["ocean heat content", "advective convergence", "complete heat budget", "Arctic heat delivery", "causal attribution"],
            "next_evidence": "Add full-depth heat-content tendency and consistently sampled advective and unresolved boundary terms.",
            "boundary": nordic["boundary"],
        },
        {
            "receipt_id": "OER005",
            "title": "July–August 2026 North Atlantic marine heatwave detection",
            "primary_claim": "duration-qualified marine heatwave at one NOAA CRW surface pixel",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "detected_object",
            "evidence_status": "supported_with_boundary",
            "representation": "point_event_time_series",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(mhw_path, mhw),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave category",
                "units": "ordinal category 0–5",
                "vertical_support": "sea surface",
                "time_support": f'{mhw["event_window"]["start"]} through {mhw["event_window"]["end"]}',
                "spatial_support": "one exact 0.05-degree pixel at 42.125 degrees north, 49.875 degrees west",
                "baseline": mhw["method"]["upstream_climatology"],
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", mhw["identity_evaluation"]["result"], mhw["identity_evaluation"]["finding"])
            ],
            "supports": ["one duration-qualified surface marine heatwave at the declared pixel and window", "daily NOAA intensity categories within the event"],
            "does_not_support": ["spatial heatwave footprint", "subsurface marine heatwave", "ocean heat content", "heat transport", "causal attribution", "ecological impact"],
            "next_evidence": "Detect adjacent pixels with the same rule, define spatial connectivity, and track the resulting footprint through time.",
            "boundary": mhw["boundary"],
        },
        {
            "receipt_id": "OER006",
            "title": "1 August 2026 connected North Atlantic marine-heatwave footprint",
            "primary_claim": "daily connected marine-heatwave footprint containing the duration-qualified anchor pixel",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "detected_object",
            "evidence_status": "supported_with_boundary",
            "representation": "native_grid_connected_component",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(footprint_path, footprint),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave category",
                "units": "ordinal category 0–5 and square kilometres",
                "vertical_support": "sea surface",
                "time_support": footprint["date"],
                "spatial_support": f'{footprint["summary"]["pixel_count"]} four-neighbor connected native 0.05-degree pixels; {footprint["summary"]["area_km2"]:.1f} km2',
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; component is anchored to duration-qualified OSW-D1",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "pass", footprint["identity_evaluation"]["finding"] + " The anchor's duration test passes in OER005.")
            ],
            "supports": ["one connected daily surface footprint containing the OSW-D1 event anchor", "native-grid area and category composition on the declared day"],
            "does_not_support": ["one spatiotemporally tracked footprint across the full event", "subsurface marine heatwave", "material water mass", "ocean heat content", "heat transport", "causal attribution", "ecological impact"],
            "next_evidence": "Connect daily components through time with a declared overlap, split, merge, minimum-area, and persistence policy.",
            "boundary": footprint["boundary"],
        },
        {
            "receipt_id": "OER007",
            "title": "July–August 2026 primary-overlap North Atlantic heatwave lineage",
            "primary_claim": "one explicitly governed lineage of inherited daily marine-heatwave footprints",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "tracked_object",
            "evidence_status": "supported_with_boundary",
            "representation": "time_ordered_connected_components",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(lineage_path, lineage),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave categories linked by exact native-pixel overlap",
                "units": "days, pixels, square kilometres, overlap fractions, and centroid kilometres",
                "vertical_support": "sea surface",
                "time_support": f'{lineage["tracked_window"]["start"]} through {lineage["tracked_window"]["end"]}',
                "spatial_support": f'{lineage["tracked_window"]["day_count"]} daily native-grid connected components',
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; OSW greatest-intersection lineage policy",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "pass", lineage["identity_evaluation"]["finding"])
            ],
            "supports": ["one reproducible primary-overlap footprint lineage", "daily shape, area, centroid, intensity composition, and transition diagnostics", "a spatial break on 2026-08-11 under exact-overlap inheritance"],
            "does_not_support": ["one inevitable event identity under every tracking policy", "reconnection across the point event's category-zero gap", "material parcel advection", "subsurface extent", "heat content", "heat transport", "causal attribution", "ecological impact"],
            "next_evidence": "Run connectivity, minimum-overlap, split/merge, and gap-bridging sensitivities; independently seed the post-gap footprint and compare the two lineages.",
            "boundary": lineage["boundary"],
        },
        {
            "receipt_id": "OER008",
            "title": "August 2026 temporal-gap identity bakeoff",
            "primary_claim": "marine-heatwave footprint identity changes under two declared temporal-continuity policies",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "policy_bakeoff_with_exact_overlap",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(gap_path, gap),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave categories and native-pixel footprint overlap",
                "units": "pixels and overlap fractions",
                "vertical_support": "sea surface",
                "time_support": "2026-08-10 through 2026-08-12, with post-gap lineage checked through 2026-08-18",
                "spatial_support": "pre-gap and post-gap native-grid four-neighbor components",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; zero- versus one-day gap policies",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", gap["identity_evaluation"]["finding"])
            ],
            "supports": ["separation under uninterrupted daily inheritance", "reconnection under a declared one-day temporal gap", "122 exact shared pixels requiring zero spatial dilation"],
            "does_not_support": ["continuous threshold evidence on August 11", "a uniquely correct identity policy", "materially identical water parcels", "subsurface continuity", "mechanism", "causal attribution", "ecological impact"],
            "next_evidence": "Test minimum-overlap thresholds and alternative connectivity, then compare physical drivers before choosing a public event-naming policy.",
            "boundary": gap["boundary"],
        },
        {
            "receipt_id": "OER009",
            "title": "North Atlantic heatwave tracking-policy robustness bakeoff",
            "primary_claim": "marine-heatwave lineage lifetime sensitivity to spatial connectivity and minimum overlap",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "connectivity_by_overlap_policy_matrix",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(sensitivity_path, sensitivity),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave categories linked by native-grid overlap",
                "units": "days, pixels, and intersection-over-union",
                "vertical_support": "sea surface",
                "time_support": "2026-07-20 through 2026-08-20",
                "spatial_support": "lineage containing the OSW-D1 anchor under four- and eight-neighbor connectivity",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; five overlap-acceptance policies per connectivity",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", sensitivity["identity_evaluation"]["finding"])
            ],
            "supports": ["identical lifetimes and exact gap footprints under four- and eight-neighbor connectivity for this case", "one extra corner-connected cell on three of 21 eight-neighbor daily components", "a 21-day lifetime at any exact overlap or IoU at least 0.10", "an 18-day plateau at IoU at least 0.20 or 0.25", "a shape-change edge from August 7 to 8 with 216 exact shared cells but IoU 0.198"],
            "does_not_support": ["universal equivalence of four- and eight-neighbor connectivity", "a uniquely correct overlap threshold", "material parcel continuity", "subsurface continuity", "physical mechanism", "causal attribution", "ecological impact"],
            "next_evidence": "Test alternative branch-selection and split/merge policies, then compare atmospheric forcing and ocean advection around the sensitive August 7–12 interval.",
            "boundary": sensitivity["boundary"],
        },
        {
            "receipt_id": "OER010",
            "title": "North Atlantic heatwave split/merge branch-policy bakeoff",
            "primary_claim": "marine-heatwave lineage sensitivity to the score used to select one overlapping branch",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "branch_selection_policy_bakeoff",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(branch_path, branch),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave components linked by four alternative overlap scores",
                "units": "days, pixels, and overlap fractions",
                "vertical_support": "sea surface",
                "time_support": "2026-07-20 through 2026-08-20",
                "spatial_support": "four-neighbor lineage containing the OSW-D1 anchor",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; at least one exact shared native-grid cell",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", branch["identity_evaluation"]["finding"])
            ],
            "supports": ["cell-for-cell agreement among largest-intersection, greatest-IoU, and largest-overlapping-component policies for 21 days", "a 14-day fraction-only lineage that selects a 12-cell splinter on July 30 and a one-cell splinter on August 3", "a demonstrated denominator hazard when candidate-inherited fraction is used without a scale constraint"],
            "does_not_support": ["a uniquely correct branch-selection policy", "universal failure of inherited-fraction scores", "material parcel continuity", "physical mechanism", "causal attribution", "ecological impact"],
            "next_evidence": "Add an explicit minimum-size or two-sided-overlap contract, test split/merge graph representations that preserve multiple branches, then compare atmospheric forcing and ocean advection.",
            "boundary": branch["boundary"],
        },
        {
            "receipt_id": "OER011",
            "title": "North Atlantic heatwave multi-branch lineage family",
            "primary_claim": "complete exact-overlap family of daily marine-heatwave components reachable from the anchor",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "tracked_object",
            "evidence_status": "supported_with_boundary",
            "representation": "directed_acyclic_component_lineage_graph",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(family_path, family),
            "measurement": {
                "variable": "NOAA CRW daily marine heatwave components and adjacent-day exact overlap",
                "units": "nodes, directed edges, pixels, square kilometres, and overlap fractions",
                "vertical_support": "sea surface",
                "time_support": "2026-07-21 through 2026-08-10",
                "spatial_support": "all four-neighbor components reachable from the OSW-D1 anchor without size pruning",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; exact native-grid overlap",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "pass", family["identity_evaluation"]["finding"])
            ],
            "supports": ["a 28-node, 29-edge exact-overlap lineage family containing the 21-node D3 primary trunk", "five split nodes and one merge node", "seven off-primary components: five terminate and two merge back", "a largest off-primary component of 54 pixels"],
            "does_not_support": ["one uniquely privileged heir at every split", "continuity across the August 11 threshold gap", "material parcel genealogy", "subsurface continuity", "physical mechanism", "causal attribution", "ecological impact"],
            "next_evidence": "Test graph pruning and temporal-gap edges explicitly, then compare atmospheric forcing and ocean advection without treating graph topology as mechanism.",
            "boundary": family["boundary"],
        },
        {
            "receipt_id": "OER012",
            "title": "North Atlantic heatwave lineage-family area-pruning ladder",
            "primary_claim": "lineage-family topology sensitivity to minimum daily component area",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "anchor_connected_graph_pruning_ladder",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(pruning_path, pruning),
            "measurement": {
                "variable": "OSW-D7 daily component area and exact-overlap graph topology",
                "units": "square kilometres, nodes, edges, splits, and merges",
                "vertical_support": "sea surface",
                "time_support": "2026-07-21 through 2026-08-10",
                "spatial_support": "anchor-connected induced graph under six minimum-area thresholds",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; OSW-D7 four-neighbor exact-overlap family",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", pruning["identity_evaluation"]["finding"])
            ],
            "supports": ["the same 21-node primary trunk at every tested threshold from zero through 1,500 km2", "side-component counts of seven, four, four, two, one, and zero across the pruning ladder", "loss of merge topology at 500 km2", "a trunk-only graph at 1,500 km2"],
            "does_not_support": ["a uniquely correct minimum component area", "that removed components are erroneous or physically unimportant", "resolution-independent thresholds", "temporal-gap continuity", "material parcel continuity", "physical mechanism", "ecological impact"],
            "next_evidence": "Add an explicitly typed temporal-gap edge to the family graph, then test whether physical-driver fields explain the sensitive intervals.",
            "boundary": pruning["boundary"],
        },
        {
            "receipt_id": "OER013",
            "title": "North Atlantic heatwave explicitly typed temporal-gap graph",
            "primary_claim": "policy-conditioned graph extension across one threshold-inactive day",
            "evidence_origin": "derived_observation_product",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "multi_edge_type_temporal_component_graph",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(typed_gap_path, typed_gap),
            "measurement": {
                "variable": "OSW-D7 exact-daily family plus OSW-D4 post-gap primary lineage and endpoint overlap",
                "units": "nodes, edges, days, pixels, and overlap fractions",
                "vertical_support": "sea surface",
                "time_support": "2026-07-21 through 2026-08-18 with 2026-08-11 explicitly threshold-inactive",
                "spatial_support": "pre-gap complete family and post-gap governed primary lineage",
                "baseline": "NOAA CRW CoralTemp 1985–2012 climatology; adjacent exact-overlap and typed one-day-gap edge policies",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", typed_gap["identity_evaluation"]["finding"])
            ],
            "supports": ["a strict 28-node, 29-edge graph ending August 10", "a conditional 35-node, 36-edge graph reaching August 18", "one typed bridge with 122 exact shared endpoint cells, IoU 0.2542, one inactive day, and zero spatial dilation", "zero August 10 footprint cells threshold-active on the intervening August 11 field"],
            "does_not_support": ["threshold continuity on August 11", "interpolated August 11 footprint", "a complete post-gap branch family", "material parcel continuity", "physical mechanism", "causal attribution", "ecological impact"],
            "next_evidence": "Build the complete post-gap branch family if needed, then compare atmospheric forcing and ocean advection around August 7–12.",
            "boundary": typed_gap["boundary"],
        },
        {
            "receipt_id": "OER014",
            "title": "Separate-product OISST cross-check of the North Atlantic threshold bridge",
            "primary_claim": "threshold-category return without a collocated separate-product local SST rebound",
            "evidence_origin": "observational_analysis",
            "claim_stage": "identity_sensitivity",
            "evidence_status": "supported_with_boundary",
            "representation": "paired_product_fixed_box_surface_temperature_crosscheck",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(bridge_crosscheck_path, bridge_crosscheck),
            "measurement": {
                "variable": "daily OISST at the nearest anchor cell and area-weighted over a fixed North Atlantic box, paired with the CRW anchor category",
                "units": "degrees C and category",
                "vertical_support": "sea surface",
                "time_support": "2026-08-07 through 2026-08-12",
                "spatial_support": "nearest 0.25-degree OISST cell and fixed 12-by-17-cell box around the 0.05-degree CRW anchor",
                "baseline": "absolute OISST temperature; paired CRW category retains the CoralTemp 1985–2012 climatology",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "policy_dependent", bridge_crosscheck["identity_evaluation"]["finding"])
            ],
            "supports": ["CRW anchor category 0 to 1 from August 11 to 12", "0.13 C cooling at the nearest separate-product OISST cell over the same transition", "0.160 C warming of the fixed-box mean and 0.18 C warming of its maximum"],
            "does_not_support": ["interchangeability of OISST and CoralTemp", "a local reheating explanation for category return", "moving-object heat content", "surface-flux attribution", "horizontal or vertical advection", "causation"],
            "next_evidence": bridge_crosscheck["next_evidence"],
            "boundary": bridge_crosscheck["boundary"],
        },
        {
            "receipt_id": "OER015",
            "title": "RTOFS surface horizontal-advection screen across the North Atlantic bridge",
            "primary_claim": "horizontal advection is not the dominant RTOFS box-mean warming term from August 11 to 12",
            "evidence_origin": "operational_assimilative_model",
            "claim_stage": "mechanism_hypothesis",
            "evidence_status": "supported_with_boundary",
            "representation": "partial_surface_temperature_tendency_decomposition",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(rtofs_advection_path, rtofs_advection),
            "measurement": {
                "variable": "daily surface-temperature tendency, endpoint-mean horizontal-advection tendency, unresolved remainder, and diagnostic mixed-layer thickness",
                "units": "degrees C per day and metres",
                "vertical_support": "RTOFS surface standard level; mixed-layer thickness supplied as context",
                "time_support": "five daily intervals from 2026-08-07 through 2026-08-12 at 00 UTC",
                "spatial_support": "4,221 RTOFS curvilinear-grid centers in a fixed 39.5-43.5 N, 52-47 W box",
                "baseline": "RTOFS HYCOM 93.1 n024 nowcast snapshots; eight-neighbor tangent-plane temperature gradients with four-neighbor sensitivity",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "not_tested", "The partial RTOFS tendency screen tests a possible physical contribution, not the CoralTemp threshold object's identity rule.")
            ],
            "supports": ["0.5396 C/day RTOFS box-mean warming from August 11 to 12", "0.0708 C/day endpoint-mean horizontal-advection contribution, or 13.1% of the same-sign box tendency", "0.4688 C/day unresolved remainder", "anchor horizontal advection of -0.109 C/day opposing 0.601 C/day modeled warming", "diagnostic box-mean mixed-layer shoaling from 19.497 to 7.801 m"],
            "does_not_support": ["model-native tracer-budget closure", "surface-flux attribution", "vertical-advection or entrainment attribution", "assimilation-increment attribution", "validation against separate SST analyses", "material parcel tracking", "causation"],
            "next_evidence": rtofs_advection["next_evidence"],
            "boundary": rtofs_advection["boundary"],
        },
        {
            "receipt_id": "OER016",
            "title": "GFS surface-energy screen across the North Atlantic bridge",
            "primary_claim": "positive forecast-derived surface heat gain is contemporaneous and material but does not close the modeled August 11 to 12 warming scale",
            "evidence_origin": "operational_forecast_model",
            "claim_stage": "mechanism_hypothesis",
            "evidence_status": "supported_with_boundary",
            "representation": "cross_system_mixed_layer_energy_scale_screen",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(gfs_surface_flux_path, gfs_surface_flux),
            "measurement": {
                "variable": "daily GFS net downward surface heat flux and mixed-layer-equivalent temperature tendency using RTOFS diagnostic layer thickness",
                "units": "W m-2 and degrees C per day",
                "vertical_support": "air-ocean surface flux scaled by start and endpoint-mean RTOFS diagnostic mixed-layer thickness",
                "time_support": "five 00-to-00 UTC daily intervals from 2026-08-07 through 2026-08-12",
                "spatial_support": "34-by-42 GFS Gaussian-grid subset bilinearly sampled at 4,221 RTOFS grid centers in the fixed North Atlantic box",
                "baseline": "four non-overlapping six-hour averages from each 00 UTC GFS cycle; representative seawater density and heat capacity; native, floored, and box-mean depth variants",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "not_tested", "The cross-system forcing screen tests a possible energy contribution, not the CoralTemp threshold object's identity rule.")
            ],
            "supports": ["+112.61 W/m2 GFS box-mean net downward surface heat flux from August 11 to 12", "+0.1219 to +0.3381 C/day mixed-layer warming scale across declared box-slab and native-depth variants", "+0.1800 C/day using a 5 m minimum start-depth sensitivity", "surface-flux sign reversal from loss on August 7-9 to gain on August 10-11"],
            "does_not_support": ["native GFS or RTOFS heat-budget closure", "an atmospheric reanalysis result", "uniform deposition of shortwave energy within the mixed layer", "vertical-advection, entrainment, mixing, or assimilation attribution", "independent validation", "causation"],
            "next_evidence": gfs_surface_flux["next_evidence"],
            "boundary": gfs_surface_flux["boundary"],
        },
        {
            "receipt_id": "OER017",
            "title": "RTOFS fixed-depth upper-ocean storage screen across the North Atlantic bridge",
            "primary_claim": "surface intensification accompanies genuine modeled 0-50 m fixed-column heat gain from August 11 to 12",
            "evidence_origin": "operational_assimilative_model",
            "claim_stage": "mechanism_hypothesis",
            "evidence_status": "supported_with_boundary",
            "representation": "fixed_depth_standard_level_heat_storage_proxy",
            "registry_matches": ["OBJ046", "OBJ109"],
            "source_artifact": source(upper_ocean_storage_path, upper_ocean_storage),
            "measurement": {
                "variable": "daily RTOFS potential-temperature change and constant-rho-Cp fixed-column storage tendency",
                "units": "degrees C and W m-2",
                "vertical_support": "15 standard-depth samples from 0 through 50 m; trapezoidal fixed-column integrations to 10, 20, 30, and 50 m",
                "time_support": "five 00-to-00 UTC daily intervals from 2026-08-07 through 2026-08-12",
                "spatial_support": "4,221 RTOFS curvilinear-grid centers in the fixed 39.5-43.5 N, 52-47 W box",
                "baseline": "day-to-day potential-temperature difference; constant temperature reference cancels under declared representative density and heat capacity",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "not_tested", "The fixed-depth storage screen tests event anatomy, not the CoralTemp threshold object's identity rule."),
                evaluation(objects, "OBJ109", "policy_dependent", "The calculation earns a fixed-depth storage proxy but not native-layer ocean heat content because it uses standard-depth interpolation and constant representative rho and cp."),
            ],
            "supports": ["+0.5396 C surface warming and +0.0997 C fixed 0-50 m column-mean warming from August 11 to 12", "+236.03 W/m2 RTOFS fixed-column storage tendency", "surface warming 5.412 times the fixed-column mean change", "+112.61 W/m2 GFS surface gain equal to 47.7% of the cross-system box storage scale", "+1739.02 W/m2 anchor storage tendency too large for the +87.08 W/m2 local GFS surface gain alone"],
            "does_not_support": ["native-layer ocean heat content", "native RTOFS tracer-budget closure", "observed upper-ocean storage", "vertical-process attribution", "assimilation-increment attribution", "causation"],
            "next_evidence": upper_ocean_storage["next_evidence"],
            "boundary": upper_ocean_storage["boundary"],
        },
        {
            "receipt_id": "OER018",
            "title": "RTOFS depth-integrated horizontal-advection screen across the North Atlantic bridge",
            "primary_claim": "horizontal advection is a major modeled 0-50 m box-scale term despite its small surface-only contribution",
            "evidence_origin": "operational_assimilative_model",
            "claim_stage": "mechanism_hypothesis",
            "evidence_status": "supported_with_boundary",
            "representation": "cross_system_partial_fixed_column_budget_screen",
            "registry_matches": ["OBJ046"],
            "source_artifact": source(upper_ocean_advection_path, upper_ocean_advection),
            "measurement": {
                "variable": "endpoint-mean offline horizontal potential-temperature advection integrated through fixed standard-depth columns",
                "units": "W m-2 equivalent column tendency",
                "vertical_support": "15 standard-depth temperature and horizontal-velocity samples from 0 through 50 m; integrations to 10, 20, 30, and 50 m",
                "time_support": "five 00-to-00 UTC daily intervals from 2026-08-07 through 2026-08-12",
                "spatial_support": "4,217 gradient-valid RTOFS grid centers within the fixed 4,221-cell North Atlantic box",
                "baseline": "local tangent-plane eight-neighbor temperature gradients with four-neighbor sensitivity and constant representative density and heat capacity",
            },
            "identity_evaluations": [
                evaluation(objects, "OBJ046", "not_tested", "The depth-integrated motion screen tests event anatomy, not the CoralTemp threshold object's identity rule.")
            ],
            "supports": ["+171.21 W/m2 offline RTOFS 0-50 m horizontal-advection scale from August 11 to 12", "horizontal advection equal to 72.5% of the +236.03 W/m2 fixed-column storage scale", "horizontal advection increasing from +21.01 W/m2 in 0-10 m to +171.21 W/m2 in 0-50 m", "surface plus horizontal scales totaling 120.2% of storage with a -47.79 W/m2 cross-system partial residual", "+715.66 W/m2 anchor horizontal advection with +936.28 W/m2 still unresolved"],
            "does_not_support": ["native RTOFS tracer flux", "conservative horizontal heat convergence", "native GFS/RTOFS budget closure", "vertical-process attribution", "assimilation-increment attribution", "causation"],
            "next_evidence": upper_ocean_advection["next_evidence"],
            "boundary": upper_ocean_advection["boundary"],
        },
    ]

    payload = {
        "schema": "osw.ocean-object-evidence-receipts.v1",
        "purpose": "Separate where evidence came from, what claim stage it reached, and whether a named object's identity test passed.",
        "vocabularies": {
            "evidence_origin": ["observational_analysis", "derived_observation_product", "assimilative_reanalysis", "operational_assimilative_model", "operational_forecast_model", "simulation", "conceptual_synthesis"],
            "claim_stage": ["field", "candidate", "detected_object", "tracked_object", "identity_sensitivity", "integrated_quantity", "mechanism_hypothesis"],
            "evidence_status": ["supported", "supported_with_boundary", "provisional", "insufficient"],
            "identity_result": ["pass", "fail", "not_tested", "policy_dependent"],
        },
        "receipt_count": len(receipts),
        "receipts": receipts,
    }
    Path(output_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


if __name__ == "__main__":
    result = build()
    print(f'wrote {result["receipt_count"]} evidence receipts')
