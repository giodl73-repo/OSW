"""Build a reproducible, source-scoped OSW ocean motion data package."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import shutil
import io
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse, urlsplit

from build_ocean_motion_claims import apply_claim_reviews, build_claims
from build_kraken_footprint_candidate import build as build_kraken_proxy
from build_footprint_movie_context import build as build_footprint_context


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
OUTPUT = ROOT / "almanac" / "release" / "v0.1.0"
INPUTS = {
    "currents": "ocean-current-almanac.json",
    "lengths": "ocean-current-length-evidence.json",
    "illustrated_spans": "ocean-current-illustrated-spans.json",
    "gate_distances": "ocean-current-gate-distances.json",
    "nasa_crosswalk": "ocean-current-nasa-crosswalk.json",
    "eddies": "ocean-eddy-name-inventory.json",
    "named_eddy_published_observations": "named-loop-eddy-published-observations.json",
    "loop_name_date_conflict": "loop-eddy-cameron-darwin-name-date-conflict.json",
    "kraken_figure": "kraken-2013-figure2-state-audit.json",
    "named_current_published_observations": "named-current-published-observations.json",
    "states": "ocean-current-state-relation-matrix.json",
    "nasa_objects": "nasa-perpetual-ocean-objects.json",
    "nasa_catalog": "nasa-perpetual-ocean-atlas-catalog.json",
    "nasa_tiles": "nasa-perpetual-ocean-tile-join.json",
    "nasa_state_tiles": "nasa-perpetual-ocean-state-tile-join.json",
    "noaa_manifest": "noaa-munster-eddy-seasonal-manifest-2021-2023.json",
    "crossref_metadata": "ocean-motion-crossref-metadata.json",
    "nasa_svs_metadata": "ocean-motion-nasa-svs-metadata.json",
    "source_metadata_overrides": "ocean-motion-source-metadata-overrides.json",
    "source_use_reviews": "ocean-motion-source-use-reviews.json",
    "claim_reviews": "ocean-motion-claim-reviews.json",
    "ranked_length_editorial_reviews": "ocean-motion-ranked-length-editorial-reviews.json",
    "taxonomy": "ocean-motion-taxonomy.json",
    "current_atlas_index": "ocean-current-atlas-index.json",
    "nasa_motion_forms": "nasa-perpetual-ocean-motion-forms.json",
    "gulf_stream_front": "gulf-stream-navo-front-20260928.json",
    "gulf_stream_front_states": "gulf-stream-navo-state-snapshot-20260928.json",
    "navo_operational_eddies": "navo-freddies-eddy-snapshot-20260925.json",
    "navo_operational_eddy_states": "navo-freddies-eddy-state-join-20260925.json",
    "lsa_geostrophic_source": "noaa-lsa-geostrophic-gulf-stream-20260925.json",
    "gulf_stream_geostrophic_path": "gulf-stream-geostrophic-path-20260925.json",
}
VERSION = "0.1.0"
RELEASE_DOCUMENTS = ("METHODS.md", "CHANGELOG.md", "CLAIM-REVIEW-WORKFLOW.md",
                     "RANKED-LENGTH-EVIDENCE-AUDIT.md",
                     "DATASET-CITATION-DRAFT.json")


def read(name: str) -> dict:
    return json.loads((RESEARCH / INPUTS[name]).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_id(url: str) -> str:
    return "source:" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def material_use_class(url: str) -> str:
    host = urlsplit(url).hostname or ""
    if host == "www.nature.com" and "/articles/s41598-018-29582-5" in url:
        return "figure_derived_measurement_and_factual_claim"
    if host == "www.horizonmarine.com" and "/loop-current-eddies" in url:
        return "compiled_name_and_date_records"
    if host == "coastwatch.noaa.gov" and "MUNSTER_v1_eddyident_" in url:
        return "derived_dated_observations"
    if host == "ocean.weather.gov" and "/gulf_stream_text.php" in url:
        return "derived_dated_observations"
    if host == "www.ncei.noaa.gov" and "/satellite_analysis/nafreddy.zip" in url:
        return "derived_dated_observations"
    if host == "coastwatch.noaa.gov" and "/rads/sla/" in url:
        return "derived_dated_observations"
    if host.endswith("arcgis.com") and "/FeatureServer/11" in url:
        return "derived_cartographic_measurements"
    if host.endswith("marineregions.org"):
        return "gazetteer_name_crosswalk"
    if host == "svs.gsfc.nasa.gov":
        return "media_navigation_and_source_description"
    return "source_scoped_factual_claim"


def main() -> None:
    data = {key: read(key) for key in INPUTS}
    currents = data["currents"]["entries"]
    current_atlas_index = data["current_atlas_index"]["entries"]
    nasa_motion_forms = data["nasa_motion_forms"]["objects"]
    lengths = {item["current_id"]: item for item in data["lengths"]["entries"]}
    spans = {item["current_id"]: item for item in data["illustrated_spans"]["entries"]}
    gate_distances = {item["current_id"]: item for item in data["gate_distances"]["entries"]}
    crosswalk = {item["current_id"]: item for item in data["nasa_crosswalk"]["entries"]}
    eddies = data["eddies"]["entries"]
    published_named_eddy_observations = data["named_eddy_published_observations"]["entries"]
    kraken_figure_candidate = data["kraken_figure"]["state_candidate"]
    kraken_ssh_candidate = data["kraken_figure"]["dated_ssh_footprint_candidate"]
    assert kraken_figure_candidate["id"] == "published:kraken-2013"
    assert kraken_figure_candidate["state_code"] == "CAMR"
    assert len(kraken_figure_candidate["observation_dates"]) == 3
    published_named_current_observations = data["named_current_published_observations"]["entries"]
    nasa = data["nasa_objects"]["objects"]
    nasa_tiles = data["nasa_tiles"]["tiles"]
    assert len(nasa_tiles) == 70
    catalog = {item["id"]: item for item in data["nasa_catalog"]["records"]}
    state_matrix = data["states"]["states"]
    snapshot_receipts = data["noaa_manifest"]["snapshots"]
    assert len(snapshot_receipts) == data["noaa_manifest"]["snapshot_count"] == 12
    snapshot_inputs = [Path(receipt["path"]).name for receipt in snapshot_receipts]
    assert len(set(snapshot_inputs)) == len(snapshot_inputs)
    snapshots = [(receipt, json.loads((RESEARCH / filename).read_text(encoding="utf-8")))
                 for receipt, filename in zip(snapshot_receipts, snapshot_inputs)]
    current_ids = {item["id"] for item in currents}
    nasa_ids = {item["id"] for item in nasa}
    assert len(current_ids) == len(currents) == len(lengths) == len(crosswalk)
    assert set(spans) == current_ids
    assert set(current_atlas_index) == current_ids
    assert set(nasa_motion_forms) == nasa_ids
    assert len(eddies) == data["eddies"]["record_count"]
    assert len(state_matrix) == data["states"]["state_count"]
    front_receipt = data["gulf_stream_front"]
    front_states = data["gulf_stream_front_states"]
    assert front_receipt["date"] == front_states["date"] == "2026-09-28"
    assert front_receipt["source_response_sha256"] == front_states["source_response_sha256"]
    assert set(front_states["states"]) == set(state_matrix)
    assert set(front_states["front_lengths_km"]) == set(front_receipt["fronts"])

    sources: dict[str, dict] = {}
    source_use_reviews = {row["url"]: row for row in data["source_use_reviews"]["entries"]}
    assert len(source_use_reviews) == len(data["source_use_reviews"]["entries"])
    crossref_by_doi = {record["doi"].casefold(): record for record in data["crossref_metadata"]["records"]}
    nasa_svs_by_url = {record["source_url"]: record for record in data["nasa_svs_metadata"]["records"]}
    override_by_url = {record["url"]: record for record in data["source_metadata_overrides"]["entries"]}

    def add_source(url: str, kind: str = "external", label: str | None = None) -> str:
        if not url:
            raise ValueError("Source URL cannot be empty")
        sid = source_id(url)
        default_label = Path(url).name if kind == "OSW source ledger" else urlparse(url).netloc
        sources.setdefault(sid, {"id": sid, "url": None if kind == "OSW source ledger" else url,
                                 "path": "source-ledgers/" + Path(url).name if kind == "OSW source ledger" else None,
                                 "repository_path": url if kind == "OSW source ledger" else None,
                                 "label": label or default_label,
                                 "rights_status": "OSW authored; upstream terms still need audit" if kind == "OSW source ledger" else "pending source terms audit",
                                 "kind": kind})
        if kind == "external":
            sources[sid]["material_use_class"] = material_use_class(url)
            # True also for exported provider records/measurements extracted from
            # source files or registers, even when original files are absent.
            sources[sid]["provider_asset_redistributed"] = (
                urlsplit(url).hostname == "www.horizonmarine.com" and "/loop-current-eddies" in url
                or urlsplit(url).hostname == "coastwatch.noaa.gov" and "MUNSTER_v1_eddyident_" in url
                or urlsplit(url).hostname == "ocean.weather.gov" and "/gulf_stream_text.php" in url
                or urlsplit(url).hostname == "www.ncei.noaa.gov" and "/satellite_analysis/nafreddy.zip" in url
                or urlsplit(url).hostname == "coastwatch.noaa.gov" and "/rads/sla/" in url)
            review = source_use_reviews.get(url)
            if review:
                assert review["material_use_class"] == sources[sid]["material_use_class"]
                assert not sources[sid]["provider_asset_redistributed"]
                sources[sid]["rights_status"] = review["rights_review_status"]
                sources[sid]["rights_policy_url"] = review["policy_reference_url"]
                sources[sid]["rights_review_date"] = review.get("review_date", data["source_use_reviews"]["review_date"])
        override = override_by_url.get(url) if kind == "external" else None
        if override:
            sources[sid].update({key: override[key] for key in
                                 ("title", "publisher", "publication_date", "source_update_date", "product_date", "credit_text", "preferred_citation", "license_url", "metadata_evidence_url", "metadata_note", "source_file_sha256", "source_file_url", "source_file_retrieved_date", "metadata_response_sha256", "doi")
                                 if key in override})
            sources[sid]["metadata_status"] = "source-page bibliographic metadata; rights pending"
            sources[sid]["label"] = override["title"]
        nasa_metadata = nasa_svs_by_url.get(url) if kind == "external" else None
        if kind == "external" and not nasa_metadata and not override and urlsplit(url).fragment:
            base_url = urlsplit(url)._replace(fragment="").geturl()
            nasa_metadata = nasa_svs_by_url.get(base_url)
        if nasa_metadata:
            fragment = urlsplit(url).fragment
            title = nasa_metadata["title"] + (" — " + fragment.replace("_", " ") if fragment else "")
            sources[sid].update({"title": title,
                                 "publisher": "NASA Scientific Visualization Studio",
                                 "publication_date": nasa_metadata["release_date"][:10],
                                 "source_update_date": nasa_metadata["update_date"],
                                 "source_credits": nasa_metadata["credits"],
                                 "metadata_api_url": nasa_metadata["api_url"],
                                 "metadata_response_sha256": nasa_metadata["response_sha256"],
                                 "metadata_status": "NASA SVS API bibliographic metadata; media rights pending"})
            sources[sid]["label"] = title
        if kind == "external" and urlsplit(url).hostname == "coastwatch.noaa.gov":
            filename = Path(urlsplit(url).path).name
            match = re.fullmatch(r"MUNSTER_v1_eddyident_multi_global_daily_s(\d{8})_e(\d{8})\.nc", filename)
            if match:
                assert match.group(1) == match.group(2), filename
                stamp = match.group(1)
                date = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
                sources[sid].update({
                    "title": f"MUNSTER v1 daily eddy identification, {date}",
                    "publisher": "NOAA CoastWatch / NOAA NESDIS STAR",
                    "product_date": date,
                    "product_version": "MUNSTER v1.0",
                    "credit_text": "Data courtesy of NOAA; Sentinel Data courtesy of Copernicus Program; Generated using AVISO+ Products",
                    "metadata_evidence_url": "https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html",
                    "metadata_status": "NOAA product-page and filename metadata; upstream data terms pending",
                })
                sources[sid]["label"] = sources[sid]["title"]
        parsed = urlsplit(url)
        if kind == "external" and parsed.netloc.lower() in {"doi.org", "www.doi.org", "dx.doi.org"}:
            doi = unquote(parsed.path.lstrip("/"))
            metadata = crossref_by_doi.get(doi.casefold())
            if metadata and metadata["status"] == "matched":
                sources[sid].update({"doi": doi, "title": metadata["title"],
                                     "authors": metadata["authors"], "publisher": metadata["publisher"],
                                     "publication_date_parts": metadata["publication_date_parts"],
                                     "metadata_api_url": metadata["api_url"],
                                     "metadata_response_sha256": metadata["response_sha256"],
                                     "metadata_status": "Crossref deposited bibliographic metadata; rights pending"})
                if not label and metadata.get("title"):
                    sources[sid]["label"] = metadata["title"]
        elif kind == "external" and sources[sid].get("doi"):
            metadata = crossref_by_doi.get(sources[sid]["doi"].casefold())
            if metadata and metadata["status"] == "matched":
                for key in ("title", "authors", "publisher", "publication_date_parts"):
                    if not sources[sid].get(key) and metadata.get(key):
                        sources[sid][key] = metadata[key]
                sources[sid]["citation_metadata_api_url"] = metadata["api_url"]
                sources[sid]["citation_metadata_response_sha256"] = metadata["response_sha256"]
        if label:
            sources[sid]["label"] = label
        if kind == "external" and url in source_use_reviews:
            sources[sid]["metadata_status"] = sources[sid].get("metadata_status", "bibliographic metadata not yet captured").replace(
                "rights pending", "current-use terms reviewed")
        return sid

    ledger_source = {
        key: add_source("research/" + filename, "OSW source ledger")
        for key, filename in INPUTS.items()
    }
    snapshot_ledger_source = {filename: add_source("research/" + filename, "OSW source ledger")
                              for filename in snapshot_inputs}
    current_source_urls = data["currents"]["sources"]
    release_urls = {item["id"]: item["url"] for item in data["nasa_objects"]["releases"]}
    for release in data["nasa_objects"]["releases"]:
        release_source = sources[add_source(release["url"], label="NASA " + release["title"])]
        release_source.setdefault("title", release["title"])
        release_source.setdefault("publisher", "NASA Scientific Visualization Studio")
        release_source.setdefault("metadata_status", "NASA release title in OSW source audit; item rights pending")
    entities: list[dict] = []
    names: list[dict] = []
    measurements: list[dict] = []
    length_assessments: list[dict] = []
    relations: list[dict] = []
    media: list[dict] = []
    geometries: list[dict] = []
    tiles: list[dict] = []
    tile_state_relations: list[dict] = []
    observation_sets: list[dict] = []
    named_eddy_source_observations: list[dict] = []
    named_current_source_observations: list[dict] = []
    operational_eddy_state_observations: list[dict] = []
    diagnosed_current_path_observations: list[dict] = []
    for (receipt, snapshot), filename in zip(snapshots, snapshot_inputs):
        assert snapshot["date"] == receipt["date"]
        assert snapshot["source_sha256"] == receipt["source_sha256"]
        assert len(snapshot["entries"]) == receipt["detection_count"]
        assert set(snapshot["states"]) == set(state_matrix)
        state_counts = {code: {"contained": len(groups["contained"]),
                               "intersected": len(groups["intersected"])}
                        for code, groups in snapshot["states"].items()}
        assert sum(counts["contained"] for counts in state_counts.values()) == receipt["contained_relation_count"]
        assert sum(counts["intersected"] for counts in state_counts.values()) == receipt["intersected_relation_count"]
        observation_sets.append({"id": "observation_set:" + receipt["date"], "date": receipt["date"],
                                 "product": snapshot["source_product"],
                                 "detection_count": receipt["detection_count"],
                                 "contained_relation_count": receipt["contained_relation_count"],
                                 "intersected_relation_count": receipt["intersected_relation_count"],
                                 "weekly_track_join": receipt["weekly_track_join"],
                                 "source_id": add_source(receipt["source_url"]),
                                 "source_response_sha256": receipt["source_sha256"],
                                 "source_snapshot_id": snapshot_ledger_source[filename],
                                 "observation_file": "observations/" + receipt["date"] + ".csv.gz",
                                 "state_counts": state_counts,
                                 "identity_limit": snapshot["identity_limit"],
                                 "coverage_limit": snapshot["coverage_limit"]})
    tile_source = add_source(data["nasa_tiles"]["source"])
    for tile in nasa_tiles:
        tiles.append({"id": "tile:" + tile["id"], "tile_id": tile["id"], "zoom": tile["zoom"],
                      "url": tile["url"], "picker_box_px": tile["picker_box_px"],
                      "latitude_range": tile["latitude_range"],
                      "longitude_range_unwrapped": tile["longitude_range_unwrapped"],
                      "spatial_role": "NASA regional movie crop", "source_id": tile_source})
    assert set(data["nasa_state_tiles"]["states"]) == set(state_matrix)
    known_tile_ids = {tile["id"] for tile in nasa_tiles}
    for code, state in data["nasa_state_tiles"]["states"].items():
        for match in state["matches"]:
            assert match["tile_id"] in known_tile_ids
            tile_state_relations.append({"id": f"tile_state:{code}:{match['tile_id']}",
                                         "tile_id": match["tile_id"], "state_id": "state:" + code,
                                         "predicate": "display_overlap",
                                         "display_coverage_fraction": match["display_coverage_fraction"],
                                         "evidence_class": "atlas_geometry",
                                         "physical_relation": "unresolved",
                                         "source_id": ledger_source["nasa_state_tiles"]})

    def name(entity_id: str, label: str, sid: str, preferred: bool) -> None:
        names.append({"id": f"name:{len(names)+1:04d}", "entity_id": entity_id,
                      "label": label, "preferred": preferred, "source_id": sid})

    ranked_lengths = sorted((item["length_km"] for item in lengths.values() if item["rank_eligible"]), reverse=True)
    arrow_source_id = add_source(data["illustrated_spans"]["source_layer"])
    for current in currents:
        current_id = current["id"]
        estimate = lengths[current_id]
        illustration = spans[current_id]
        source_url = estimate.get("length_source_url")
        length_assessments.append({
            "id": "length_assessment:" + current_id,
            "entity_id": "current:" + current_id,
            "evidence_status": estimate["status"],
            "rank_eligible": estimate["rank_eligible"],
            "published_rank": (ranked_lengths.index(estimate["length_km"]) + 1)
                              if estimate["rank_eligible"] else None,
            "published_length_km": estimate["length_km"],
            "lower_bound_km": estimate["lower_bound_km"],
            "gate_distance_sensitivity": gate_distances[current_id]["gate_distance_sensitivity"]
                                         if current_id in gate_distances else None,
            "gate_distance_method_source_id": ledger_source["gate_distances"]
                                               if current_id in gate_distances else None,
            "proposed_system_length_km": estimate["hypothesized_length_km"],
            "scope": estimate.get("scope"),
            "length_source_locator": estimate.get("length_source_locator"),
            "length_source_id": add_source(source_url) if source_url else None,
            "illustrated_span_km": illustration.get("longest_arrow_span_km"),
            "illustrated_span_rank": illustration.get("illustrated_span_rank"),
            "illustration_source_id": arrow_source_id if illustration["map_coverage"] == "source_arrow" else None,
            "illustration_limit": "Drawn map-arrow span, not a physical current length or lower bound",
            "source_id": ledger_source["lengths"],
            "illustration_ledger_source_id": ledger_source["illustrated_spans"],
        })

    deferred_geographic_floors = []
    deferred_reported_lengths = []
    deferred_admission_geometries = []
    deferred_admission_media = []
    deferred_admission_names = []
    deferred_admission_relations = []
    for current in currents:
        cid = "current:" + current["id"]
        name_url = current_source_urls.get(current.get("name_source")) or current.get("name_source_url")
        sid = add_source(name_url) if name_url else ledger_source["currents"]
        entities.append({"id": cid, "type": "named_current", "label": current["name"],
                         "identity_level": current_atlas_index[current["id"]]["identity_level"],
                         "source_kind": current.get("kind"),
                         "setting": current_atlas_index[current["id"]]["setting"],
                         "time_behavior": current_atlas_index[current["id"]]["time_behavior"],
                         "basin": current.get("basin"),
                         "source_id": sid, "source_record_id": current["id"],
                         "almanac_url": f"index.html#current-{current['id']}"})
        if current["id"] == "antarctic-slope":
            deferred_admission_names.append((cid, current["name"], sid))
            entities[-1]["identity_scope_note"] = current["identity_scope_note"]
        else:
            name(cid, current["name"], sid, True)
        for locator in current_atlas_index[current["id"]]["locators"]:
            (deferred_admission_geometries if current["id"] == "antarctic-slope" else geometries).append({"id": f"geometry:{len(geometries)+1:04d}", "entity_id": cid,
                               "role": "editorial_locator", "coordinate_reference_system": "OGC:CRS84",
                               "method": current_atlas_index[current["id"]].get("locator_basis") or data["current_atlas_index"]["method"],
                               "positional_uncertainty": "not quantified; no observed current core or path",
                               "geometry": {"type": "Point", "coordinates": locator},
                               "source_id": ledger_source["current_atlas_index"]})
        for alias in current.get("aliases", []):
            if isinstance(alias, str):
                alias_url = current_source_urls.get(current.get("alias_source"))
                name(cid, alias, add_source(alias_url) if alias_url else ledger_source["currents"], False)
        estimate = lengths[current["id"]]
        if estimate.get("length_km") is not None:
            length_url = estimate.get("length_source_url") or current_source_urls.get(current.get("length_source"))
            reported_length = {"id": f"measurement:{len(measurements)+1:04d}", "entity_id": cid,
                                 "quantity": "reported_length", "value": estimate["length_km"], "unit": "km",
                                 "scope": estimate.get("scope") or current.get("length_scope"),
                                 "evidence_status": estimate["status"], "rank_eligible": estimate["rank_eligible"],
                                 "source_locator": estimate.get("length_source_locator"),
                                 "source_id": add_source(length_url) if length_url else ledger_source["lengths"]}
            if current["id"] == "antarctic-slope":
                reported_length["method"] = "Source review's approximate system-span statement, retained with its Antarctic Peninsula continuity limit; no route digitization or instantaneous path measurement"
            if current["id"] == "falkland":
                reported_length["method"] = "Source-reported conference-abstract loop extent; no centerline digitization, endpoint coordinates, depth-defined length or error interval is supplied"
            if current["id"] in {"alaska-coastal-gulf", "antarctic-slope", "falkland"}:
                # New admissions follow all existing measurements, including
                # dated eddy observations and the previously appended floors.
                deferred_reported_lengths.append(reported_length)
            else:
                measurements.append(reported_length)
        if estimate.get("lower_bound_km") is not None:
            lower_source_url = estimate.get("length_source_url") or current_source_urls.get(current.get("length_source"))
            receipt = gate_distances.get(current["id"])
            if receipt:
                assert receipt["admitted_rounded_geographic_floor_km"] == estimate["lower_bound_km"]
            lower_bound_measurement = {"id": f"measurement:{len(measurements)+1:04d}", "entity_id": cid,
                                 "quantity": "length_lower_bound", "value": estimate["lower_bound_km"],
                                 "unit": "km", "scope": estimate.get("scope"), "evidence_status": estimate["status"],
                                 "source_locator": estimate.get("length_source_locator"),
                                 "rank_eligible": False,
                                 "source_id": add_source(lower_source_url) if lower_source_url else ledger_source["lengths"],
                                 "method_source_id": ledger_source["gate_distances"] if receipt else None,
                                 "direct_gate_distance_km": receipt["direct_gate_distance_km"] if receipt else None,
                                 "gate_type": receipt["gate_type"] if receipt else None}
            if current["id"] in {"benguela", "brazil", "deep-western-boundary"}:
                # Append newly admitted floors after existing measurements so
                # published claim IDs and prior review decisions remain stable.
                deferred_geographic_floors.append(lower_bound_measurement)
            else:
                measurements.append(lower_bound_measurement)
        if estimate.get("hypothesized_length_km") is not None:
            hypothesis_url = current_source_urls.get(current.get("hypothesis_source"))
            measurements.append({"id": f"measurement:{len(measurements)+1:04d}", "entity_id": cid,
                                 "quantity": "proposed_system_length", "value": estimate["hypothesized_length_km"],
                                 "unit": "km", "scope": estimate.get("scope"), "evidence_status": estimate["status"],
                                 "source_locator": estimate.get("length_source_locator"),
                                 "rank_eligible": False,
                                 "source_id": add_source(hypothesis_url) if hypothesis_url else ledger_source["lengths"]})
        for variant in estimate.get("source_reported_length_variants", []):
            if variant.get("length_km_approx") is None:
                continue
            variant_url = variant.get("source_url") or current_source_urls.get(variant.get("source"))
            measurements.append({"id": f"measurement:{len(measurements)+1:04d}", "entity_id": cid,
                                 "quantity": "alternate_reported_length", "value": variant["length_km_approx"],
                                 "unit": "km", "scope": variant.get("scope"), "evidence_status": "source_specific_variant",
                                 "source_locator": variant.get("source_locator"),
                                 "rank_eligible": False,
                                 "source_id": add_source(variant_url) if variant_url else ledger_source["lengths"]})
        for observation in estimate.get("other_observations", []):
            observation_url = observation.get("source_url")
            for field, quantity in (("alongflow_km_approx", "sampled_alongflow_reach"),
                                    ("cross_stream_width_km", "section_cross_stream_width")):
                if observation.get(field) is None:
                    continue
                measurements.append({"id": f"measurement:{len(measurements)+1:04d}", "entity_id": cid,
                                     "quantity": quantity, "value": observation[field], "unit": "km",
                                     "scope": observation.get("type"), "evidence_status": "section_or_sample_only",
                                     "source_locator": observation.get("source_locator"),
                                     "rank_eligible": False,
                                     "source_id": add_source(observation_url) if observation_url else ledger_source["lengths"]})
        entry = crosswalk[current["id"]]
        for relation in entry.get("object_relations", []):
            nid = relation["nasa_object_id"]
            assert nid in nasa_ids
            evidence = "source_identified" if entry["status"] == "nasa_named_or_described" else "source_associated"
            urls = relation.get("source_urls", [])
            for url in urls:
                add_source(url)
            nasa_object = next(item for item in nasa if item["id"] == nid)
            narrated_locator = (f"Narration transcript {nasa_object['narrated_start_s']}–"
                                f"{nasa_object['narrated_end_s']} seconds, named current"
                                if entry["status"] == "nasa_named_or_described" and
                                nasa_object.get("narrated_start_s") is not None and
                                any("script_" in url for url in urls) else None)
            relations.append({"id": f"relation:{len(relations)+1:06d}", "subject_id": cid,
                              "predicate": relation["relation"], "object_id": "nasa:" + nid,
                              "evidence_class": evidence, "source_id": add_source(urls[0]) if urls else ledger_source["nasa_crosswalk"],
                              "source_urls": urls, "source_locator": narrated_locator or relation.get("source_locator")})
        movie = entry.get("regional_movie")
        if movie and movie.get("url"):
            (deferred_admission_media if current["id"] == "antarctic-slope" else media).append({"id": f"media:{len(media)+1:04d}", "entity_id": cid,
                          "url": movie["url"], "tile_id": movie.get("tile_id"),
                          "relation": movie.get("relation", "geographic_crop_navigation_only"),
                          "source_id": ledger_source["nasa_crosswalk"]})

    for current in currents:
        parent_id = current.get("part_of_current_id")
        if parent_id:
            assert parent_id in current_ids and parent_id != current["id"]
            relations.append({"id": f"relation:{len(relations)+1:06d}",
                              "subject_id": "current:" + current["id"],
                              "predicate": "named_regional_segment_of",
                              "object_id": "current:" + parent_id,
                              "evidence_class": "source_associated",
                              "interpretation": "OSW classification of a source-described regional segment; no path or length equivalence is inferred",
                              "source_locator": current.get("part_of_current_source_locator"),
                              "source_id": add_source(current_source_urls[current["name_source"]])})

    for item in eddies:
        eid = "eddy:" + item["id"]
        sid = add_source(item["source_url"], label="Horizon Marine Loop Current eddies" if item["source_collection"] == "horizon_loop_current" else None)
        entities.append({"id": eid, "type": "named_eddy", "label": item["name"],
                         "identity_level": item["identity_level"], "basin": item.get("basin"),
                         "setting": "gulf_of_mexico" if item["source_collection"] in {"horizon_loop_current", "published_loop_current"} else "regional",
                         "time_behavior": "transient" if item["identity_level"] == "individual_eddy" else "recurrent" if item["identity_level"] == "recurrent_eddy_region" else "unresolved",
                         "source_id": sid, "source_record_id": item["source_record_id"],
                         "almanac_url": item["atlas_anchor"] if item["atlas_anchor"].startswith("object.html?") else "index.html" + item["atlas_anchor"]})
        name(eid, item["name"], sid, True)
        for field, quantity, unit in (("reported_travel_km_lower_bound", "travel_lower_bound", "km"),
                                      ("reported_lifetime_years_approx", "reported_lifetime", "years")):
            if item.get(field) is not None:
                measurements.append({"id": f"measurement:{len(measurements)+1:04d}", "entity_id": eid,
                                     "quantity": quantity, "value": item[field], "unit": unit,
                                     "scope": "source-specific individual eddy", "evidence_status": "source_reported",
                                     "source_locator": item.get("reported_motion_source_locator"),
                                     "rank_eligible": False, "source_id": sid})
        for state in item.get("state_locator_candidates", []):
            assert state in state_matrix, (eid, state)
            reported_center = (item.get("published_observed_position")
                               if item["source_collection"] == "published_loop_current" else None)
            relations.append({"id": f"relation:{len(relations)+1:06d}", "subject_id": eid,
                              "predicate": item.get("state_relation") or "state_locator_candidate",
                              "object_id": "state:" + state,
                              "evidence_class": ("figure_digitized" if item["id"] == kraken_figure_candidate["id"] else
                                                 "source_reported_point_projected_to_atlas" if reported_center else "atlas_geometry"),
                              "source_id": (add_source(item["source_url"]) if reported_center else ledger_source["eddies"]),
                              "source_locator": reported_center["source_locator"] if reported_center else None,
                              "physical_relation": ("red_curve_pixel_locations_not_whole_ring_containment" if item["id"] == kraken_figure_candidate["id"] else
                                                    "observed_center_point_not_whole_eddy_containment" if reported_center else "unresolved")})
        if item.get("nasa_movie_url"):
            media.append({"id": f"media:{len(media)+1:04d}", "entity_id": eid,
                          "url": item["nasa_movie_url"], "tile_id": None,
                          "relation": item.get("movie_relation") or "regional_context_only",
                          "source_id": ledger_source["eddies"]})

    eddies_by_id = {item["id"]: item for item in eddies}
    assert len(eddies_by_id) == len(eddies)
    for item in published_named_eddy_observations:
        eddy_id = item["eddy_id"]
        assert eddy_id in eddies_by_id and item["name"] == eddies_by_id[eddy_id]["name"]
        assert item["observation_start"] <= item["observation_end"]
        named_eddy_source_observations.append({
            "id": f"named_eddy_source_observation:{len(named_eddy_source_observations)+1:03d}",
            "entity_id": "eddy:" + eddy_id,
            "observation_start": item["observation_start"],
            "observation_end": item["observation_end"],
            "evidence_type": item["evidence_type"],
            "name_origin": item.get("name_origin"),
            "observed_center": item.get("observed_center"),
            "near_center_mooring": item.get("near_center_mooring"),
            "source_locator": item["source_locator"],
            "reported_measure": item["reported_measure"],
            "interpretation": item["interpretation"],
            "geometry_status": ("figure_red_pixels_georeferenced_no_closed_boundary"
                                if eddy_id == kraken_figure_candidate["id"] else
                                "published_figure_not_digitized"),
            "physical_state_relation": "unresolved_without_reusable_dated_geometry",
            "source_id": add_source(item["source_url"]),
            "source_snapshot_id": ledger_source["named_eddy_published_observations"],
        })
        for event in item.get("independent_event_observations", []):
            assert item["observation_start"] <= event["observation_date"] <= item["observation_end"]
            named_eddy_source_observations.append({
                "id": f"named_eddy_source_observation:{len(named_eddy_source_observations)+1:03d}",
                "entity_id": "eddy:" + eddy_id,
                "observation_start": event["observation_date"],
                "observation_end": event["observation_date"],
                "event_stage": event["event_stage"],
                "evidence_type": "independent_published_dated_event",
                "source_locator": event["source_locator"],
                "reported_measure": None,
                "interpretation": event["interpretation"],
                "geometry_status": "source_reported_event_no_named_eddy_footprint",
                "physical_state_relation": "unresolved_without_reusable_dated_geometry",
                "source_id": add_source(event["source_url"]),
                "source_snapshot_id": ledger_source["named_eddy_published_observations"],
            })

    for item in nasa:
        nid = "nasa:" + item["id"]
        urls = [release_urls[key] for key in item.get("nasa_sources", []) if key in release_urls]
        for url in urls:
            add_source(url)
        sid = add_source(urls[0]) if urls else ledger_source["nasa_objects"]
        entities.append({"id": nid, "type": "nasa_described_motion", "label": item["name"],
                         "identity_level": item.get("support"), "basin": None,
                         "motion_form": nasa_motion_forms[item["id"]],
                         "source_id": sid, "source_record_id": item["id"], "almanac_url": None})
        name(nid, item["name"], sid, True)
        if item.get("almanac_current_id") in current_ids:
            relations.append({"id": f"relation:{len(relations)+1:06d}", "subject_id": nid,
                              "predicate": "almanac_current_crosswalk", "object_id": "current:" + item["almanac_current_id"],
                              "evidence_class": "source_associated", "source_id": ledger_source["nasa_objects"]})
        locator = item.get("locator")
        if isinstance(locator, list) and len(locator) == 2:
            geometries.append({"id": f"geometry:{len(geometries)+1:04d}", "entity_id": nid,
                               "role": "editorial_locator", "coordinate_reference_system": "OGC:CRS84",
                               "method": "OSW editorial regional locator copied from the NASA object ledger",
                               "positional_uncertainty": "not quantified; no observed footprint",
                               "geometry": {"type": "Point", "coordinates": locator},
                               "source_id": ledger_source["nasa_objects"]})
        movie = catalog.get(item["id"], {}).get("regional_movie")
        if movie and movie.get("url"):
            media.append({"id": f"media:{len(media)+1:04d}", "entity_id": nid,
                          "url": movie["url"], "tile_id": movie.get("tile_id"),
                          "relation": "regional_movie_context", "source_id": ledger_source["nasa_catalog"]})

    for code, state in state_matrix.items():
        sid = "state:" + code
        entities.append({"id": sid, "type": "osw_state", "label": state["name"],
                         "identity_level": "atlas_region", "basin": None,
                         "source_id": ledger_source["states"], "source_record_id": code,
                         "almanac_url": "index.html?state=" + code})
        name(sid, state["name"], ledger_source["states"], True)
        assert set(state["currents"]) == current_ids
        for current_id, decision in state["currents"].items():
            status = decision["atlas_relation"]
            arrow_ids = decision.get("cartographic_source_arrow_ids", {})
            relation = {"id": f"relation:{len(relations)+1:06d}", "subject_id": "current:" + current_id,
                        "predicate": status, "object_id": sid,
                        "evidence_class": "unresolved" if status == "unresolved" else "atlas_geometry",
                        "physical_relation": decision.get("physical_relation"),
                        "evidence_kinds": decision.get("evidence_kinds", []),
                        "cartographic_source_arrow_ids": arrow_ids,
                        "source_id": ledger_source["states"]}
            (deferred_admission_relations if current_id == "antarctic-slope" else relations).append(relation)

    deferred_current_presence_relations = []
    appended_current_presence_relations = []
    for observation in published_named_current_observations:
        assert observation["current_id"] in current_ids
        assert observation["state_code"] in state_matrix
        assert observation["observation_start"] <= observation["observation_end"]
        source = add_source(observation["source_url"])
        observation_id = f"current_source_observation:{len(named_current_source_observations)+1:04d}"
        named_current_source_observations.append({
            "id": observation_id,
            "entity_id": "current:" + observation["current_id"],
            "state_id": "state:" + observation["state_code"],
            "observation_event_id": observation["observation_event_id"],
            "reported_locality": observation["reported_locality"],
            "observation_start": observation["observation_start"],
            "observation_end": observation["observation_end"],
            "observation_type": observation["observation_type"],
            "time_detail": observation["time_detail"],
            "source_locator": observation["source_locator"],
            "source_url": observation["source_url"],
            "spatial_basis": observation["spatial_basis"],
            "state_assignment_method": observation["state_assignment_method"],
            "state_boundary_limit": observation["state_boundary_limit"],
            "reported_section_endpoints_lon_lat": observation.get("reported_section_endpoints_lon_lat"),
            "geometry_status": observation["geometry_status"],
            "physical_relation": observation["physical_relation"],
            "source_id": source,
            "source_snapshot_id": ledger_source["named_current_published_observations"],
        })
        if observation.get("reported_observation_points_lon_lat"):
            named_current_source_observations[-1].update({key: observation[key] for key in
                ("reported_observation_points_lon_lat", "observation_time_precision", "observation_depth_note")})
        presence_relation = {
            "id": f"relation:{len(relations)+1:06d}",
            "subject_id": "current:" + observation["current_id"],
            "object_id": "state:" + observation["state_code"],
            "predicate": "source_reported_local_current_presence",
            "evidence_class": "source_associated",
            "physical_relation": observation["physical_relation"],
            "observation_start": observation["observation_start"],
            "observation_end": observation["observation_end"],
            "reported_locality": observation["reported_locality"],
            "state_assignment_method": observation["state_assignment_method"],
            "geometry_status": observation["geometry_status"],
            "observation_event_id": observation["observation_event_id"],
            "source_locator": observation["source_locator"],
            "observation_id": observation_id,
            "source_id": source,
            "source_snapshot_id": ledger_source["named_current_published_observations"],
        }
        if observation.get("reported_observation_points_lon_lat"):
            appended_current_presence_relations.append(presence_relation)
        elif observation["current_id"] == "alaska-coastal-gulf":
            # Preserve prior relation claim IDs when appending local evidence.
            deferred_current_presence_relations.append(presence_relation)
        else:
            relations.append(presence_relation)

    operational_eddy_receipt = data["navo_operational_eddies"]
    operational_eddy_join = data["navo_operational_eddy_states"]
    assert operational_eddy_receipt["source_zip_sha256"] == operational_eddy_join["source_zip_sha256"]
    assert operational_eddy_receipt["observation_date"] == operational_eddy_join["observation_date"]
    assert {row["provider_code"] for row in operational_eddy_receipt["eddies"]} == {
        row["provider_code"] for row in operational_eddy_join["features"]}
    operational_source_id = add_source(operational_eddy_receipt["source_url"],
                                       label="NAVO FREDDIES North Atlantic operational eddies")
    sources[operational_source_id].update({
        "title": "NAVO FREDDIES North Atlantic fronts and eddies, 2026-09-25",
        "publisher": "Naval Oceanographic Office via NOAA NCEI",
        "product_date": operational_eddy_receipt["observation_date"],
        "source_file_sha256": operational_eddy_receipt["source_zip_sha256"],
        "metadata_evidence_url": operational_eddy_receipt["source_landing_page"],
        "metadata_status": "Source package contains an approved-for-public-release statement; exact reuse terms still pending review",
    })
    for feature in operational_eddy_join["features"]:
        for state_relation in feature["state_relations"]:
            assert state_relation["state_code"] in state_matrix
            operational_eddy_state_observations.append({
                "id": "operational_eddy_state_observation:" + feature["provider_code"] + ":" + state_relation["state_code"],
                "operational_eddy_id": feature["id"],
                "provider_code": feature["provider_code"],
                "provider_type": feature["provider_type"],
                "provider_rotation": feature["provider_rotation"],
                "observation_date": operational_eddy_receipt["observation_date"],
                "state_id": "state:" + state_relation["state_code"],
                "relation": state_relation["relation"],
                "display_projection_polygon_area_fraction": state_relation["display_projection_polygon_area_fraction"],
                "provider_center_lon_lat": feature["provider_center_lon_lat"],
                "source_zip_sha256": operational_eddy_receipt["source_zip_sha256"],
                "source_locator": (operational_eddy_receipt["source_shapefile"] +
                                   ".shp/.dbf, provider code " + feature["provider_code"]),
                "identity_limit": operational_eddy_receipt["identity_limit"],
                "relation_limit": operational_eddy_join["relation_limit"],
                "source_id": operational_source_id,
                "source_snapshot_id": ledger_source["navo_operational_eddies"],
                "state_join_id": ledger_source["navo_operational_eddy_states"],
            })

    geostrophic_source = data["lsa_geostrophic_source"]
    diagnosed_path = data["gulf_stream_geostrophic_path"]
    assert diagnosed_path["source_response_sha256"] == geostrophic_source["source_response_sha256"]
    assert diagnosed_path["source_subset_sha256"] == digest(RESEARCH / INPUTS["lsa_geostrophic_source"])
    assert diagnosed_path["current_id"] == "gulf-stream-system"
    assert diagnosed_path["representative"]["stop_reason"] == "downstream_longitude_gate"
    lsa_source_id = add_source(geostrophic_source["source_url"], label="NOAA LSA daily geostrophic velocity, 2026-09-25")
    sources[lsa_source_id].update({
        "title": "NOAA LSA daily sea level anomaly and geostrophic currents, 2026-09-25",
        "publisher": "NOAA/NESDIS Laboratory for Satellite Altimetry via NOAA CoastWatch",
        "product_date": "2026-09-25",
        "source_file_sha256": geostrophic_source["source_response_sha256"],
        "metadata_evidence_url": geostrophic_source["product_page"],
        "credit_text": geostrophic_source["attribution"],
        "metadata_status": "Source NetCDF and NOAA product-page metadata; reuse attribution recorded, source review pending",
    })
    path_geometry_id = f"geometry:{len(geometries)+1:04d}"
    path_coordinates = diagnosed_path["representative"]["coordinates_lon_lat"]
    geometries.append({
        "id": path_geometry_id,
        "entity_id": "current:gulf-stream-system",
        "role": "dated_partial_geostrophic_streamline",
        "observation_date": diagnosed_path["observation_date"],
        "coordinate_reference_system": "OGC:CRS84",
        "method": diagnosed_path["integration_method"],
        "positional_uncertainty": "0.25-degree source analysis; seed sensitivity and velocity-field error are not a formal positional uncertainty",
        "diagnosed_reach_length_km": diagnosed_path["representative"]["segment_length_km"],
        "length_interpretation": diagnosed_path["length_role"],
        "geometry": {"type": "LineString", "coordinates": path_coordinates},
        "source_id": lsa_source_id,
        "source_snapshot_id": ledger_source["gulf_stream_geostrophic_path"],
    })
    diagnosed_current_path_observations.append({
        "id": "diagnosed_current_path:2026-09-25:gulf-stream-western-north-atlantic-reach",
        "entity_id": "current:gulf-stream-system",
        "observation_date": diagnosed_path["observation_date"],
        "source_field": diagnosed_path["field"],
        "source_locator": "NetCDF ugos/vgos[time=0], 2026-09-25 daily field; see pinned subset and integration method",
        "source_product_status": geostrophic_source["source_product_status"],
        "seed_gate": diagnosed_path["seed_gate"],
        "downstream_gate_longitude": diagnosed_path["downstream_gate_longitude"],
        "stop_reason": diagnosed_path["representative"]["stop_reason"],
        "reach_length_km": diagnosed_path["representative"]["segment_length_km"],
        "rank_eligible": False,
        "adjacent_seed_sensitivity": diagnosed_path["adjacent_seed_sensitivity"],
        "step_size_sensitivity": diagnosed_path["step_size_sensitivity"],
        "physical_limit": diagnosed_path["physical_limit"],
        "geometry_id": path_geometry_id,
        "source_id": lsa_source_id,
        "source_snapshot_id": ledger_source["gulf_stream_geostrophic_path"],
        "field_subset_id": ledger_source["lsa_geostrophic_source"],
    })
    measurements.append({
        "id": f"measurement:{len(measurements)+1:04d}",
        "entity_id": "current:gulf-stream-system",
        "quantity": "dated_geostrophic_streamline_reach",
        "value": diagnosed_path["representative"]["segment_length_km"],
        "unit": "km",
        "evidence_status": "dated_diagnosed_partial_reach",
        "rank_eligible": False,
        "scope": diagnosed_path["length_role"],
        "observation_date": diagnosed_path["observation_date"],
        "geometry_id": path_geometry_id,
        "source_id": lsa_source_id,
        "source_snapshot_id": ledger_source["gulf_stream_geostrophic_path"],
        "source_locator": "NetCDF ugos/vgos[time=0], 2026-09-25 daily field; see pinned subset and integration method",
    })
    for state_relation in diagnosed_path["state_relations"]:
        assert state_relation["state_code"] in state_matrix
        relations.append({
            "id": f"relation:{len(relations)+1:06d}",
            "subject_id": "current:gulf-stream-system",
            "object_id": "state:" + state_relation["state_code"],
            "predicate": state_relation["predicate"],
            "evidence_class": "derived_field",
            "physical_relation": "dated_partial_geostrophic_streamline_intersects_state_whole_current_passage_unresolved",
            "observation_date": diagnosed_path["observation_date"],
            "diagnosed_segment_length_km": state_relation["intersection_length_km"],
            "geometry_id": path_geometry_id,
            "source_id": lsa_source_id,
            "source_snapshot_id": ledger_source["gulf_stream_geostrophic_path"],
            "source_locator": "NetCDF ugos/vgos[time=0], 2026-09-25 daily field; see pinned subset and integration method",
        })

    front_source_id = add_source(front_receipt["source_url"])
    front_geometry_ids = {}
    for side, front in front_receipt["fronts"].items():
        geometry_id = f"geometry:{len(geometries)+1:04d}"
        front_geometry_ids[side] = geometry_id
        geometries.append({"id": geometry_id, "entity_id": "current:gulf-stream-system",
                           "role": "dated_analyzed_surface_front", "front_side": side,
                           "observation_date": front_receipt["date"],
                           "coordinate_reference_system": "OGC:CRS84",
                           "method": front_receipt["source_method_note"],
                           "positional_uncertainty": "0.1 degree reported coordinates; observation age and local effects not quantified",
                           "observed_front_length_km": front_states["front_lengths_km"][side],
                           "length_interpretation": front_states["length_limit"],
                           "geometry": front["geometry"], "source_id": front_source_id,
                           "source_snapshot_id": ledger_source["gulf_stream_front"]})
    for code, state in front_states["states"].items():
        for side, intersection_class in state["front_observations"].items():
            relations.append({"id": f"relation:{len(relations)+1:06d}",
                              "subject_id": "current:gulf-stream-system", "object_id": "state:" + code,
                              "predicate": "dated_surface_front_intersection",
                              "evidence_class": "observed_geometry",
                              "physical_relation": "observed_front_intersects_approximate_state_current_passage_unresolved",
                              "front_side": side, "intersection_class": intersection_class,
                              "observed_front_segment_length_km": state["front_intersection_lengths_km"][side],
                              "length_interpretation": front_states["length_limit"],
                              "observation_date": front_receipt["date"],
                              "geometry_id": front_geometry_ids[side],
                              "source_locator": ("2026-09-28 NAVO frontal bulletin, " +
                                                 side.replace("_", " ") + " coordinate list"),
                              "source_id": front_source_id,
                              "source_snapshot_id": ledger_source["gulf_stream_front_states"]})

    named_eddy_state_assessments = []
    for item in eddies:
        primary_states = set(item["state_locator_candidates"])
        additional_states = {code for point in item.get("additional_observed_position_joins", [])
                             for code in point.get("state_center_candidates", [])}
        assert primary_states | additional_states <= set(state_matrix)
        for code in sorted(state_matrix):
            point_evidence = []
            if code in primary_states:
                point_evidence.append(item["locator_evidence_type"])
            point_evidence.extend(point["evidence_type"] for point in
                                  item.get("additional_observed_position_joins", [])
                                  if code in point.get("state_center_candidates", []))
            candidate_type = ("figure_derived_red_curve_candidate" if item["id"] == kraken_figure_candidate["id"] and code == kraken_figure_candidate["state_code"] else
                              "figure_derived_dated_ssh_contour_candidate" if item["id"] == kraken_ssh_candidate["id"] and code == "CARB" else
                              "published_observed_center_point_candidate" if code in primary_states and item["source_collection"] == "published_loop_current" and item.get("published_observed_position") else
                              "shared_source_region_gateway" if code in primary_states and
                              item["state_relation"] == "shared_source_region_gateway_only" else
                              "point_or_region_locator" if code in primary_states else
                              "additional_observed_point" if point_evidence else "unresolved")
            named_eddy_state_assessments.append({
                "id": f"named_eddy_state:eddy:{item['id']}:state:{code}",
                "eddy_id": "eddy:" + item["id"], "state_id": "state:" + code,
                "evidence_status": candidate_type, "point_evidence_types": point_evidence,
                "physical_relation": ("observed_center_point_not_whole_eddy_containment"
                                      if candidate_type == "published_observed_center_point_candidate" else
                                      "dated_ssh_proxy_intersection_candidate_whole_eddy_relation_unresolved"
                                      if item["id"] == kraken_ssh_candidate["id"] and
                                      code in kraken_ssh_candidate["sensitivity_state_codes"] else
                                      "unknown_no_dated_eddy_footprint"),
                "source_id": (ledger_source["kraken_figure"] if candidate_type in {"figure_derived_red_curve_candidate", "figure_derived_dated_ssh_contour_candidate"}
                              else add_source(item["source_url"]) if candidate_type == "published_observed_center_point_candidate"
                              else ledger_source["eddies"]),
                "source_record_id": item["source_record_id"],
                "source_locator": (item["published_observed_position"]["source_locator"]
                                   if candidate_type == "published_observed_center_point_candidate" else None),
                "reported_center_lon_lat": (item["published_observed_position"]["coordinate_lon_lat"]
                                            if candidate_type == "published_observed_center_point_candidate" else None),
                "observed_center_date": (item["published_observed_position"]["date"]
                                         if candidate_type == "published_observed_center_point_candidate" else None),
                "figure_observation_dates": (kraken_figure_candidate["observation_dates"]
                                             if candidate_type == "figure_derived_red_curve_candidate" else None),
                "figure_axis_sensitivity_fraction": (
                    kraken_figure_candidate["minimum_axis_sensitivity_red_pixel_fraction_in_state"]
                    if candidate_type == "figure_derived_red_curve_candidate" else None),
                "dated_ssh_contour_observation_date": (
                    kraken_ssh_candidate["observation_date"]
                    if item["id"] == kraken_ssh_candidate["id"] and
                    code in kraken_ssh_candidate["sensitivity_state_codes"] else None),
                "dated_ssh_contour_assessment": (
                    ("robust_figure_intersection_candidate" if code == "CAMR" else
                     "axis_sensitive_figure_intersection_candidate")
                    if item["id"] == kraken_ssh_candidate["id"] and
                    code in kraken_ssh_candidate["sensitivity_state_codes"] else None),
                "dated_ssh_contour_nominal_area_fraction": (
                    kraken_ssh_candidate["segmentation_sensitivity_cases"][1]["nominal_footprint_area_fraction_by_state"].get(code, 0)
                    if item["id"] == kraken_ssh_candidate["id"] and
                    code in kraken_ssh_candidate["sensitivity_state_codes"] else None),
                "dated_ssh_contour_area_fraction_range": (
                    [min(case[f"{code.lower()}_footprint_area_fraction_range"][0]
                         for case in kraken_ssh_candidate["segmentation_sensitivity_cases"]),
                     max(case[f"{code.lower()}_footprint_area_fraction_range"][1]
                         for case in kraken_ssh_candidate["segmentation_sensitivity_cases"])]
                    if item["id"] == kraken_ssh_candidate["id"] and
                    code in kraken_ssh_candidate["sensitivity_state_codes"] else None),
            })
    assert len(named_eddy_state_assessments) == len(eddies) * len(state_matrix)

    for relation in deferred_current_presence_relations:
        relation["id"] = f"relation:{len(relations)+1:06d}"
        relations.append(relation)
    for floor in deferred_geographic_floors:
        floor["id"] = f"measurement:{len(measurements)+1:04d}"
        measurements.append(floor)
    for measurement in sorted(deferred_reported_lengths, key=lambda row: {"current:alaska-coastal-gulf": 0, "current:antarctic-slope": 1, "current:falkland": 2}[row["entity_id"]]):
        measurement["id"] = f"measurement:{len(measurements)+1:04d}"
        measurements.append(measurement)
    # Append dated detections after the existing collections to preserve IDs.
    # A provider designation identifies this receipt/date, not a named eddy track.
    operational_receipt_by_code = {row["provider_code"]: row
                                   for row in operational_eddy_receipt["eddies"]}
    for feature in operational_eddy_join["features"]:
        receipt = operational_receipt_by_code[feature["provider_code"]]
        entity_id = feature["id"]
        entities.append({
            "id": entity_id, "type": "operational_eddy_detection",
            "label": f"NAVO {feature['provider_code']} — {operational_eddy_receipt['observation_date']}",
            "identity_level": "dated_detection", "setting": "regional",
            "time_behavior": "unresolved", "vertical_setting": "unresolved", "basin": "North Atlantic",
            "observation_date": operational_eddy_receipt["observation_date"],
            "provider_code": feature["provider_code"],
            "provider_type": feature["provider_type"],
            "provider_rotation": feature["provider_rotation"],
            "identity_limit": operational_eddy_receipt["identity_limit"],
            "source_id": operational_source_id, "source_record_id": feature["provider_code"],
            "source_snapshot_id": ledger_source["navo_operational_eddies"],
        })
        name(entity_id, feature["provider_code"], operational_source_id, True)
        geometry_id = f"geometry:{len(geometries)+1:04d}"
        geometries.append({
            "id": geometry_id, "entity_id": entity_id,
            "role": "dated_operational_eddy_polygon",
            "observation_date": operational_eddy_receipt["observation_date"],
            "coordinate_reference_system": "unspecified_datum_lon_lat_degrees",
            "coordinate_reference_status": operational_eddy_receipt["coordinate_reference_status"],
            "method": "Unmodified source shapefile polygon coordinates from the pinned NAVO receipt; longitude/latitude interpretation, exact datum unspecified",
            "positional_uncertainty": "Provider positional uncertainty and exact datum are not specified in this receipt",
            "geometry": {"type": "Polygon", "coordinates": [receipt["source_polygon_lon_lat"]]},
            "source_id": operational_source_id,
            "source_snapshot_id": ledger_source["navo_operational_eddies"],
            "source_zip_sha256": operational_eddy_receipt["source_zip_sha256"],
        })
        for observation in operational_eddy_state_observations:
            if observation["operational_eddy_id"] == entity_id:
                observation["geometry_id"] = geometry_id
    for geometry in deferred_admission_geometries:
        geometry["id"] = f"geometry:{len(geometries)+1:04d}"
        geometries.append(geometry)
    for row in deferred_admission_media:
        row["id"] = f"media:{len(media)+1:04d}"
        media.append(row)
    for cid, label, sid in deferred_admission_names:
        name(cid, label, sid, True)
    for relation in deferred_admission_relations:
        relation["id"] = f"relation:{len(relations)+1:06d}"
        relations.append(relation)
    asc_source = add_source(current_source_urls["antarctic_slope_review"])
    for target in ("current:acc", "current:antarctic-coastal"):
        relations.append({"id": f"relation:{len(relations)+1:06d}",
                          "subject_id": "current:antarctic-slope", "object_id": target,
                          "predicate": "source_distinguished_current", "evidence_class": "source_associated",
                          "source_locator": "Section 1.1 ASC Characteristics; Figure 2 caption and circumpolar-continuity discussion",
                          "method": "OSW source-text comparison of separately named slope, coastal and circumpolar current systems; no geometric separation or dated identity measurement",
                          "source_id": asc_source})
    for relation in appended_current_presence_relations:
        relation["id"] = f"relation:{len(relations)+1:06d}"
        relations.append(relation)
    proxy_geometry, proxy_candidate = build_kraken_proxy(data["kraken_figure"],
        f"geometry:{len(geometries)+1:04d}",
        add_source("https://www.nature.com/articles/s41598-018-29582-5"), ledger_source["kraken_figure"])
    geometries.append(proxy_geometry)
    footprint_candidates = [proxy_candidate]
    footprint_movie_context = build_footprint_context(footprint_candidates, geometries, tiles,
        data["nasa_tiles"]["model_period"], ledger_source["nasa_tiles"])
    classification_vocabularies = []
    for vocabulary in data["taxonomy"].get("source_scoped_regime_vocabularies", []):
        row = {key: value for key, value in vocabulary.items() if key != "source_url"}
        row["source_id"] = add_source(vocabulary["source_url"])
        assert row["assignments"] == [] and row["assignment_status"] == "vocabulary_only_no_osw_state_assignments"
        classification_vocabularies.append(row)
    record_collections = {"entities": entities, "names": names, "measurements": measurements,
                   "classification_vocabularies": classification_vocabularies,
                   "named_eddy_footprint_candidates": footprint_candidates,
                   "footprint_movie_context": footprint_movie_context,
                   "length_assessments": length_assessments,
                   "relations": relations, "media": media, "geometries": geometries,
                   "tiles": tiles, "tile_state_relations": tile_state_relations,
                   "named_eddy_state_assessments": named_eddy_state_assessments,
                   "named_eddy_source_observations": named_eddy_source_observations,
                   "named_current_source_observations": named_current_source_observations,
                   "operational_eddy_state_observations": operational_eddy_state_observations,
                   "diagnosed_current_path_observations": diagnosed_current_path_observations,
                   "observation_sets": observation_sets}
    for source in sources.values():
        usage = {key: sum(row.get("source_id") == source["id"] or
                          row.get("illustration_source_id") == source["id"] for row in rows)
                 for key, rows in record_collections.items()}
        source["record_count"] = sum(usage.values())
        source["derived_detection_count"] = sum(
            row["detection_count"] for row in observation_sets if row["source_id"] == source["id"])
        source["total_packaged_row_count"] = source["record_count"] + source["derived_detection_count"]
        source["used_in_collections"] = [key for key, count in usage.items() if count]
    internal_locators = {}
    state_ledger_path = sources[ledger_source["states"]]["path"]
    for relation in relations:
        if (relation["source_id"] == ledger_source["states"] and
                relation["subject_id"].startswith("current:") and
                relation["object_id"].startswith("state:")):
            current_key = relation["subject_id"].removeprefix("current:")
            state_key = relation["object_id"].removeprefix("state:")
            internal_locators[relation["id"]] = (
                f"{state_ledger_path}#/states/{state_key}/currents/{current_key}")
    assert len(internal_locators) == data["states"]["pair_count"]
    tile_ledger_path = sources[ledger_source["nasa_state_tiles"]]["path"]
    for state_key, state in data["nasa_state_tiles"]["states"].items():
        for index, match in enumerate(state["matches"]):
            internal_locators[f"tile_state:{state_key}:{match['tile_id']}"] = (
                f"{tile_ledger_path}#/states/{state_key}/matches/{index}")
    assert len(internal_locators) == data["states"]["pair_count"] + len(tile_state_relations)
    eddy_ledger_path = sources[ledger_source["eddies"]]["path"]
    eddy_record_index = {"eddy:" + item["id"]: index for index, item in enumerate(eddies)}
    for relation in relations:
        if relation["source_id"] == ledger_source["eddies"] and relation["subject_id"] in eddy_record_index:
            internal_locators[relation["id"]] = (
                f"{eddy_ledger_path}#/entries/{eddy_record_index[relation['subject_id']]}")
    for assessment in named_eddy_state_assessments:
        if assessment["evidence_status"] in {"figure_derived_red_curve_candidate", "figure_derived_dated_ssh_contour_candidate"}:
            internal_locators[assessment["id"]] = (
                f"{sources[ledger_source['kraken_figure']]['path']}#/" +
                ("state_candidate" if assessment["evidence_status"] == "figure_derived_red_curve_candidate"
                 else "dated_ssh_footprint_candidate"))
        else:
            internal_locators[assessment["id"]] = (
                f"{eddy_ledger_path}#/entries/{eddy_record_index[assessment['eddy_id']]}")
    nasa_ledger_path = sources[ledger_source["nasa_objects"]]["path"]
    nasa_record_index = {"nasa:" + item["id"]: index for index, item in enumerate(nasa)}
    for relation in relations:
        if relation["source_id"] == ledger_source["nasa_objects"] and relation["subject_id"] in nasa_record_index:
            internal_locators[relation["id"]] = (
                f"{nasa_ledger_path}#/objects/{nasa_record_index[relation['subject_id']]}")
    internal_record_relations = sum(relation["id"] in internal_locators and
                                    relation["source_id"] in {ledger_source["eddies"], ledger_source["nasa_objects"]}
                                    for relation in relations)
    assert internal_record_relations == 129
    assert len(internal_locators) == (data["states"]["pair_count"] +
                                      len(tile_state_relations) + len(named_eddy_state_assessments) +
                                      internal_record_relations)
    claims = build_claims(
        relations, measurements, tile_state_relations, named_eddy_state_assessments,
        named_eddy_source_observations, named_current_source_observations,
        operational_eddy_state_observations, diagnosed_current_path_observations, sources,
        {ledger_source["states"]: data["states"]["method"],
         ledger_source["nasa_state_tiles"]: data["nasa_state_tiles"]["method"]},
        internal_locators, classification_vocabularies=classification_vocabularies,
        footprint_candidates=footprint_candidates, footprint_movie_context=footprint_movie_context)
    apply_claim_reviews(claims, data["claim_reviews"])
    ranked_editorial = data["ranked_length_editorial_reviews"]
    assert ranked_editorial["schema"] == "osw.ocean-motion-ranked-length-editorial-reviews.v1"
    assert ranked_editorial["status"] == "source_passage_audit_only_not_scientific_claim_approval"
    ranked_claims = {row["claim_id"]: row for row in measurements if row.get("rank_eligible")}
    editorial_entries = {row["claim_id"]: row for row in ranked_editorial["entries"]}
    assert len(ranked_claims) == len(editorial_entries) == len(ranked_editorial["entries"]) == data["lengths"]["counts"]["published_estimate"], [(row["id"], row["subject_id"], row["review_fingerprint"]) for row in claims if row["id"] in ranked_claims]
    assert set(ranked_claims) == set(editorial_entries)
    claims_by_id = {row["id"]: row for row in claims}
    for claim_id, decision in editorial_entries.items():
        claim = claims_by_id[claim_id]
        measurement = ranked_claims[claim_id]
        assert decision["review_fingerprint"] == claim["review_fingerprint"]
        assert decision["subject_id"] == claim["subject_id"] == measurement["entity_id"]
        assert decision["reported_length_km"] == claim["value"] == measurement["value"]
        assert decision["scientific_review_status"] == claim["review_status"]
        assert decision["source_passage_assessment"] in {
            "quoted_number_supported_with_scope_limit", "quoted_number_supported_with_source_warning"}
        assert decision.get("emphasis") in {None, "scope_warning"}
        assert decision["editorial_note"].strip()
        for corroboration in decision.get("corroborating_sources", []):
            assert corroboration["url"].startswith("https://")
            assert corroboration["locator"].strip()
            assert corroboration["role"].endswith("_not_measured_axis")
    collections = {**record_collections, "claims": claims,
                   "sources": sorted(sources.values(), key=lambda row: row["id"])}
    entity_ids = {item["id"] for item in entities}
    source_ids = set(sources)
    assert len(entity_ids) == len(entities)
    taxonomy_axes = data["taxonomy"]["axes"]
    for entity in entities:
        if entity["type"] in {"named_current", "named_eddy", "operational_eddy_detection"}:
            assert entity["identity_level"] in taxonomy_axes["identity_level"], entity
            assert entity["setting"] in taxonomy_axes["setting"], entity
            assert entity["time_behavior"] in taxonomy_axes["time_behavior"], entity
        if entity["type"] == "nasa_described_motion":
            assert entity["motion_form"] in data["nasa_motion_forms"]["forms"], entity
    for collection_name, collection in collections.items():
        assert len({row["id"] for row in collection}) == len(collection)
        for row in collection:
            if "entity_id" in row:
                assert row["entity_id"] in entity_ids, row
            if "subject_id" in row and collection_name != "claims":
                assert row["subject_id"] in entity_ids and row["object_id"] in entity_ids, row
            if "source_id" in row:
                assert row["source_id"] in source_ids, row
    assert sum(row["subject_id"].startswith("current:") and row["object_id"].startswith("state:")
               and row["predicate"] not in {"dated_surface_front_intersection", "source_reported_local_current_presence", "dated_geostrophic_streamline_segment_intersection"}
               for row in relations) == data["states"]["pair_count"]
    tile_ids = {row["tile_id"] for row in tiles}
    assert len(tile_ids) == 70
    claim_subject_ids = entity_ids | {"tile:" + tile_id for tile_id in tile_ids}
    assert all(claim["subject_id"] in claim_subject_ids
               and (claim["object_id"] is None or claim["object_id"] in entity_ids)
               for claim in claims)
    assert all(row["tile_id"] in tile_ids for row in media if row.get("tile_id"))
    assert all(row["tile_id"] in tile_ids for row in tile_state_relations)
    assert sum(row["detection_count"] for row in observation_sets) == data["noaa_manifest"]["detection_count_sum"]
    assert set(source_use_reviews) <= {row["url"] for row in sources.values()
                                       if row["kind"] == "external" and row["record_count"] > 0}

    OUTPUT.mkdir(parents=True, exist_ok=True)
    written = []
    for key, rows in collections.items():
        path = OUTPUT / (key + ".json")
        write_json(path, rows)
        written.append(path)
        # CSV stores nested evidence values as JSON, preserving their structure.
        columns = sorted({column for row in rows for column in row})
        path = OUTPUT / (key + ".csv")
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (list, dict))
                                 else value for key, value in row.items()})
        written.append(path)
    path = OUTPUT / "ranked-length-editorial-reviews.json"
    write_json(path, ranked_editorial)
    written.append(path)
    locator_worklist = sorted((claim for claim in claims
                               if claim["source_locator_status"] == "source_only_no_precise_locator"),
                              key=lambda row: row["id"])
    path = OUTPUT / "source-locator-worklist.csv"
    worklist_columns = ("claim_id", "target_collection", "target_id", "subject_id", "predicate",
                        "value", "unit", "source_id", "source_url", "needed_action",
                        "resolution_status", "reviewer", "review_date")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=worklist_columns)
        writer.writeheader()
        for claim in locator_worklist:
            writer.writerow({"claim_id": claim["id"], "target_collection": claim["target_collection"],
                             "target_id": claim["target_id"], "subject_id": claim["subject_id"],
                             "predicate": claim["predicate"], "value": claim["value"], "unit": claim["unit"],
                             "source_id": claim["source_id"], "source_url": sources[claim["source_id"]].get("url"),
                             "needed_action": "Find a precise source passage or field; revise or remove unsupported assertion",
                             "resolution_status": "pending", "reviewer": None, "review_date": None})
    written.append(path)
    ranked_claim_ids = {row["claim_id"] for row in measurements if row.get("rank_eligible")}
    science_worklist = sorted((claim for claim in claims if claim["source_locator_status"] == "specific"),
                              key=lambda row: (0 if row["id"] in ranked_claim_ids else
                                               1 if row["evidence_class"] in {"source_identified", "source_associated"} else 2,
                                               row["id"]))
    path = OUTPUT / "claim-science-review-first-pass.csv"
    science_columns = ("priority", "claim_id", "review_fingerprint", "target_collection", "target_id",
                       "subject_id", "predicate", "value", "unit", "evidence_class", "source_url",
                       "source_locator", "review_status", "reviewer", "review_date", "review_note")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=science_columns)
        writer.writeheader()
        for claim in science_worklist:
            writer.writerow({"priority": ("ranked_length" if claim["id"] in ranked_claim_ids else
                                          "source_relation" if claim["evidence_class"] in {"source_identified", "source_associated"}
                                          else "other_external_claim"),
                             "claim_id": claim["id"], "review_fingerprint": claim["review_fingerprint"],
                             "target_collection": claim["target_collection"], "target_id": claim["target_id"],
                             "subject_id": claim["subject_id"], "predicate": claim["predicate"],
                             "value": claim["value"], "unit": claim["unit"],
                             "evidence_class": claim["evidence_class"],
                             "source_url": sources[claim["source_id"]].get("url"),
                             "source_locator": claim["source_locator"],
                             "review_status": claim["review_status"], "reviewer": claim["reviewer"],
                             "review_date": claim["review_date"], "review_note": claim["review_note"]})
    written.append(path)
    path = OUTPUT / "geometries.geojson"
    write_json(path, {"type": "FeatureCollection", "features": [
        {"type": "Feature", "id": row["id"], "geometry": row["geometry"],
         "properties": {key: value for key, value in row.items() if key != "geometry"}}
        for row in geometries if row["coordinate_reference_system"] == "OGC:CRS84"]})
    written.append(path)
    coverage = {"version": VERSION, "scope": "Declared source set; no global completeness claim",
                "counts": {key: len(rows) for key, rows in collections.items()},
                "geojson_excluded_unspecified_datum_geometry_ids": [row["id"] for row in geometries
                    if row["coordinate_reference_system"] != "OGC:CRS84"],
                "claim_locator_statuses": dict(Counter(row["source_locator_status"] for row in claims)),
                "claim_method_statuses": dict(Counter(row["method_status"] for row in claims)),
                "claim_review_statuses": dict(Counter(row["review_status"] for row in claims)),
                "entity_types": dict(Counter(row["type"] for row in entities)),
                "identity_levels": dict(Counter(row["identity_level"] for row in entities
                                                if row["type"] in {"named_current", "named_eddy"})),
                "settings": dict(Counter(row["setting"] for row in entities
                                         if row["type"] in {"named_current", "named_eddy"})),
                "nasa_motion_forms": dict(Counter(row["motion_form"] for row in entities
                                                  if row["type"] == "nasa_described_motion")),
                "evidence_classes": dict(Counter(row["evidence_class"] for row in relations)),
                "current_state_pairs": data["states"]["pair_count"],
                "current_state_atlas_links": data["states"]["atlas_linked_pair_count"],
                "dated_front_state_observations": sum(row["predicate"] == "dated_surface_front_intersection"
                                                      for row in relations),
                "named_eddy_state_pairs": len(named_eddy_state_assessments),
                "named_eddies_with_published_observations": len({row["entity_id"] for row in named_eddy_source_observations}),
                "named_currents_with_published_local_observations": len({row["entity_id"] for row in named_current_source_observations}),
                "dated_operational_eddies_with_source_polygons": len({row["operational_eddy_id"] for row in operational_eddy_state_observations}),
                "dated_diagnosed_current_path_observations": len(diagnosed_current_path_observations),
                "dated_diagnosed_current_state_intersections": sum(row["predicate"] == "dated_geostrophic_streamline_segment_intersection" for row in relations),
                "named_eddy_state_evidence_statuses": dict(Counter(
                    row["evidence_status"] for row in named_eddy_state_assessments)),
                "ranked_current_lengths": sum(row["rank_eligible"] for row in measurements),
                "dated_noaa_detections": sum(row["detection_count"] for row in observation_sets),
                "external_sources_pending_terms": sum(row["kind"] == "external" and row["record_count"] > 0
                                                      and row["rights_status"].startswith("pending")
                                                      for row in sources.values()),
                "external_sources_reviewed_for_current_use": sum(row["kind"] == "external" and row["record_count"] > 0
                    and row["rights_status"].startswith("reviewed") for row in sources.values()),
                "used_external_sources_with_titles": sum(row["kind"] == "external" and row["record_count"] > 0
                                                          and bool(row.get("title")) for row in sources.values()),
                "used_external_material_use_classes": dict(Counter(row["material_use_class"]
                    for row in sources.values() if row["kind"] == "external" and row["record_count"] > 0)),
                "known_limitations": ["State relations based on map symbols or locators do not establish physical passage.",
                                      "Named eddies are a source-set inventory, not every eddy visible in NASA footage.",
                                      "NASA crop links are geographic navigation unless a source explicitly identifies an object.",
                                      "NOAA dated eddy detections are separate observation records, not named eddy identities or a continuous census.",
                                      "NAVO Gulf Stream walls are one dated frontal analysis, not a complete current footprint or perennial passage claim.",
                                      "NAVO/NCEI operational eddy polygons are dated provider detections, not persistent named eddy identities.",
                                      "The NOAA LSA Gulf Stream geostrophic line is a seed-sensitive partial frozen-field streamline, not a whole-current length or parcel path."]}
    path = OUTPUT / "coverage.json"
    write_json(path, coverage)
    written.append(path)
    taxonomy = {"schema": "osw.ocean-motion-release-taxonomy.v1",
                "status": data["taxonomy"]["status"],
                "scope": data["taxonomy"]["scope"],
                "axes": taxonomy_axes,
                "admission_rules": data["taxonomy"]["admission_rules"],
                "nasa_motion_forms": data["nasa_motion_forms"]["forms"],
                "nasa_class_relations": data["nasa_motion_forms"]["class_relations"],
                "source_ids": [ledger_source["taxonomy"], ledger_source["nasa_motion_forms"],
                               ledger_source["current_atlas_index"]],
                "source_urls": data["taxonomy"]["sources"]}
    taxonomy["source_scoped_regime_vocabulary_ids"] = [row["id"] for row in classification_vocabularies]
    path = OUTPUT / "taxonomy.json"
    write_json(path, taxonomy)
    written.append(path)
    def source_family(url: str) -> tuple[str, str | None, str]:
        host = urlparse(url).netloc.lower()
        if host == "ocean.weather.gov" and "/gulf_stream_text.php" in url:
            return "NAVO frontal bulletin via NOAA OPC", "https://www.weather.gov/disclaimer/", "Confirm that NAVO-provided coordinates have no separate terms beyond NWS page guidance; credit both providers. The candidate redistributes 510 reported wall points."
        if host == "www.ncei.noaa.gov" and "/satellite_analysis/nafreddy.zip" in url:
            return "NAVO FREDDIES via NOAA NCEI", "https://www.ncei.noaa.gov/data-submission/data-licensing", "Confirm the NAVO polygon package's exact worldwide reuse status, attribution, citation, and CRS; the ZIP states approved for public release but includes no .prj or license file."
        if host == "coastwatch.noaa.gov" and "/rads/sla/" in url:
            return "NOAA LSA geostrophic currents", "https://coastwatch.noaa.gov/cwn/products/sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html", "Review the product's NOAA LSA and CoastWatch acknowledgement, derived subset redistribution, and source citation before deposition."
        if host == "coastwatch.noaa.gov" and "MUNSTER_v1_eddyident_" in url:
            return "NOAA MUNSTER", "https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html", "Confirm NOAA, Sentinel/Copernicus, and AVISO+ attribution and upstream data terms for this product."
        if host == "www.horizonmarine.com":
            return "Horizon register", None, "Verify register compilation terms and preferred citation."
        if host.endswith("svs.gsfc.nasa.gov") or host.endswith("nasa.gov"):
            return "NASA", "https://www.nasa.gov/nasa-brand-center/images-and-media/", "Check item exceptions and record NASA attribution."
        if host.endswith("noaa.gov"):
            return "NOAA", "https://oceanservice.noaa.gov/about/faq.html", "Check item credits and product citation."
        if host.endswith("marineregions.org"):
            return "Marine Regions", "https://www.marineregions.org/disclaimer.php", "Confirm the terms for this gazetteer record or service."
        if host.endswith("arcgis.com"):
            return "Cartographic service", None, "Layer credits four parties but states no reuse license; verify owner and geometry terms before any polygon redistribution."
        if host == "doi.org" or "/article" in url or url.lower().endswith(".pdf"):
            return "Research publication", None, "Verify bibliographic metadata and any copied-content terms."
        return "Other external source", None, "Record publisher, citation, and item-specific terms."

    review_queue = []
    for source in sources.values():
        if source["kind"] != "external" or not source["record_count"]:
            continue
        use_rows = [(key, row) for key, rows in record_collections.items()
                    for row in rows if row.get("source_id") == source["id"]]
        entity_ids_for_source = sorted({entity_id for _, row in use_rows for entity_id in
                                        (row.get("entity_id"), row.get("subject_id"), row.get("object_id"))
                                        if entity_id})
        family, policy_url, next_action = source_family(source["url"])
        review = source_use_reviews.get(source["url"])
        if review:
            policy_url = review["policy_reference_url"]
            next_action = review["next_action"]
        review_queue.append({"id": "review:" + source["id"], "source_id": source["id"],
                             "label": source["label"], "url": source["url"], "source_family": family,
                             "title": source.get("title"), "authors": source.get("authors"),
                             "doi": source.get("doi"),
                             "publisher": source.get("publisher"),
                             "publication_date_parts": source.get("publication_date_parts"),
                             "publication_date": source.get("publication_date"),
                             "product_date": source.get("product_date"),
                             "product_version": source.get("product_version"),
                             "source_update_date": source.get("source_update_date"),
                             "source_file_sha256": source.get("source_file_sha256"),
                             "preferred_citation": source.get("preferred_citation"),
                             "credit_text": source.get("credit_text"),
                             "metadata_status": source.get("metadata_status", "not yet captured"),
                             "material_use_class": source["material_use_class"],
                             "provider_asset_redistributed": source["provider_asset_redistributed"],
                             "record_count": source["record_count"],
                             "derived_detection_count": source["derived_detection_count"],
                             "total_packaged_row_count": source["total_packaged_row_count"],
                             "affected_entity_count": len(entity_ids_for_source),
                             "affected_entity_ids": entity_ids_for_source,
                             "used_in_collections": source["used_in_collections"],
                             "policy_reference_url": policy_url,
                             "rights_review_status": source["rights_status"],
                             "rights_review_date": source.get("rights_review_date"),
                             "rights_review_note": review["review_note"] if review else None,
                             "citation_review_status": review["citation_review_status"] if review else ("bibliography captured; citation review pending" if source.get("title") else "pending item-specific review"),
                             "next_action": next_action})
    review_queue.sort(key=lambda row: (-row["total_packaged_row_count"],
                                       -row["affected_entity_count"], row["source_id"]))
    path = OUTPUT / "source-review-queue.json"
    write_json(path, review_queue)
    written.append(path)
    path = OUTPUT / "source-review-queue.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        columns = list(review_queue[0])
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in review_queue:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value
                             for key, value in row.items()})
    written.append(path)
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "OSW ocean motion release collection row contracts",
        "definitions": {
            "footprint_movie_context": {"required": ["id", "entity_id", "footprint_candidate_id", "geometry_id", "geometry_sha256", "tile_id", "zoom", "url", "nominal_angular_overlap_fraction", "nominal_complete_view", "recommended", "observation_date", "movie_model_period", "temporal_alignment_status", "event_identity_status", "source_id", "source_snapshot_id", "figure_source_id", "support_claim_id", "source_locator", "method", "physical_limit", "claim_id"],
                "properties": {"nominal_angular_overlap_fraction": {"type": "number", "exclusiveMinimum": 0, "maximum": 1}, "recommended": {"type": "boolean"}, "nominal_complete_view": {"type": "boolean"}, "event_identity_status": {"const": "not_established"}, "temporal_alignment_status": {"enum": ["outside_declared_model_years", "year_in_range_event_alignment_unresolved"]}}},
            "named_eddy_footprint_candidates": {"required": ["id", "entity_id", "geometry_id", "geometry_sha256", "observation_date", "boundary_type", "source_id", "source_snapshot_id", "source_locator", "method", "physical_limit", "state_assessments", "claim_id"],
                "properties": {"boundary_type": {"const": "figure_digitized_instantaneous_ssh_contour_proxy"},
                    "geometry_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "state_assessments": {"type": "array", "minItems": 1, "items": {"type": "object",
                        "required": ["state_id", "intersection_assessment", "containment_assessment", "nominal_display_area_fraction", "display_area_fraction_range"],
                        "properties": {"state_id": {"type": "string", "pattern": "^state:"},
                            "intersection_assessment": {"enum": ["robust_across_tested_calibrations", "calibration_sensitive_candidate"]},
                            "containment_assessment": {"const": "unresolved"},
                            "nominal_display_area_fraction": {"type": "number", "minimum": 0, "maximum": 1},
                            "display_area_fraction_range": {"type": "array", "minItems": 2, "maxItems": 2, "items": {"type": "number", "minimum": 0, "maximum": 1}}}}}}},
            "classification_vocabularies": {"required": ["id", "entity_id", "label", "source_id", "source_locator", "scope", "terms", "method", "assignment_status", "assignments", "claim_id"],
                "properties": {"assignment_status": {"const": "vocabulary_only_no_osw_state_assignments"},
                               "assignments": {"type": "array", "maxItems": 0},
                               "terms": {"type": "array", "minItems": 1, "items": {
                                   "type": "object", "required": ["id", "source_label", "criterion_summary"],
                                   "properties": {"id": {"type": "string", "minLength": 1}, "source_label": {"type": "string", "minLength": 1}, "criterion_summary": {"type": "string", "minLength": 1}}}}}},
            "entities": {"required": ["id", "type", "label", "source_id", "source_record_id"],
                         "properties": {"id": {"type": "string", "pattern": "^(current|eddy|nasa|state|navo-freddies):"},
                                        "type": {"enum": ["named_current", "named_eddy", "nasa_described_motion", "osw_state", "operational_eddy_detection"]}}},
            "names": {"required": ["id", "entity_id", "label", "preferred", "source_id"]},
            "measurements": {"required": ["id", "entity_id", "quantity", "value", "unit", "rank_eligible", "source_id", "claim_id"]},
            "claims": {"required": ["id", "target_collection", "target_id", "subject_id", "predicate",
                                    "object_id", "value", "unit", "scope", "evidence_class", "assertion_status",
                                    "source_id", "source_snapshot_id", "source_locator", "source_locator_status",
                                    "method", "method_source_id", "method_status", "observation_time",
                                    "source_date", "reviewer", "review_date", "review_status", "review_note",
                                    "review_fingerprint", "support_claim_id"],
                       "properties": {"target_collection": {"enum": ["relations", "measurements", "tile_state_relations", "named_eddy_state_assessments", "named_eddy_source_observations", "named_current_source_observations", "operational_eddy_state_observations", "diagnosed_current_path_observations", "classification_vocabularies", "named_eddy_footprint_candidates", "footprint_movie_context"]},
                                      "source_locator_status": {"enum": ["specific", "internal_ledger_row", "internal_ledger_record", "source_only_no_precise_locator"]},
                                      "method_status": {"enum": ["described", "method_reference_only", "method_not_recorded"]},
                                      "review_status": {"enum": ["not_individually_reviewed", "verified",
                                                                "needs_revision", "rejected"]}}},
            "length_assessments": {"required": ["id", "entity_id", "evidence_status", "rank_eligible",
                                                 "published_rank", "published_length_km", "lower_bound_km",
                                                 "proposed_system_length_km", "illustrated_span_km",
                                                 "illustrated_span_rank", "source_id",
                                                 "illustration_ledger_source_id"]},
            "relations": {"required": ["id", "subject_id", "predicate", "object_id", "evidence_class", "source_id", "claim_id"],
                          "properties": {"evidence_class": {"enum": ["source_identified", "source_associated", "observed_geometry", "derived_field", "figure_digitized", "source_reported_point_projected_to_atlas", "atlas_geometry", "unresolved"]}}},
            "media": {"required": ["id", "entity_id", "url", "relation", "source_id"]},
            "geometries": {"required": ["id", "entity_id", "role", "coordinate_reference_system", "method",
                                        "positional_uncertainty", "geometry", "source_id"],
                           "properties": {"role": {"enum": ["editorial_locator", "dated_analyzed_surface_front", "dated_partial_geostrophic_streamline", "dated_operational_eddy_polygon", "dated_figure_ssh_contour_proxy"]}}},
            "tiles": {"required": ["id", "tile_id", "zoom", "url", "picker_box_px", "latitude_range",
                                    "longitude_range_unwrapped", "spatial_role", "source_id"]},
            "tile_state_relations": {"required": ["id", "tile_id", "state_id", "predicate",
                                                  "display_coverage_fraction", "evidence_class", "claim_id",
                                                  "physical_relation", "source_id"]},
            "named_eddy_state_assessments": {"required": ["id", "eddy_id", "state_id",
                "evidence_status", "point_evidence_types", "physical_relation", "source_id", "claim_id",
                "source_record_id"], "properties": {"evidence_status": {"enum": [
                    "shared_source_region_gateway", "point_or_region_locator",
                    "published_observed_center_point_candidate",
                    "additional_observed_point", "figure_derived_red_curve_candidate",
                    "figure_derived_dated_ssh_contour_candidate",
                    "unresolved"]}}},
            "named_eddy_source_observations": {"required": ["id", "entity_id",
                "observation_start", "observation_end", "evidence_type", "source_locator",
                "geometry_status", "physical_state_relation", "source_id", "source_snapshot_id", "claim_id"]},
            "named_current_source_observations": {"required": ["id", "entity_id", "state_id", "observation_event_id",
                "reported_locality", "observation_start", "observation_end", "observation_type",
                "source_locator", "source_url", "state_assignment_method", "state_boundary_limit",
                "geometry_status", "physical_relation", "source_id", "source_snapshot_id", "claim_id"]},
            "operational_eddy_state_observations": {"required": ["id", "operational_eddy_id",
                "provider_code", "provider_type", "provider_rotation", "observation_date",
                "state_id", "relation", "display_projection_polygon_area_fraction",
                "provider_center_lon_lat", "source_zip_sha256", "identity_limit",
                "relation_limit", "source_id", "source_snapshot_id", "state_join_id", "geometry_id", "claim_id"]},
            "diagnosed_current_path_observations": {"required": ["id", "entity_id",
                "observation_date", "source_field", "source_product_status", "seed_gate", "downstream_gate_longitude",
                "stop_reason", "reach_length_km", "rank_eligible", "adjacent_seed_sensitivity",
                "step_size_sensitivity", "physical_limit", "geometry_id", "source_id",
                "source_snapshot_id", "field_subset_id", "claim_id"]},
            "observation_sets": {"required": ["id", "date", "product", "detection_count", "state_counts",
                                              "source_id", "source_snapshot_id", "source_response_sha256",
                                              "observation_file", "identity_limit", "coverage_limit"]},
            "sources": {"required": ["id", "kind", "label", "rights_status", "record_count"]},
        },
    }
    common_properties = {
        "id": {"type": "string", "minLength": 1},
        "entity_id": {"type": "string", "minLength": 1},
        "subject_id": {"type": "string", "minLength": 1},
        "object_id": {"type": "string", "minLength": 1},
        "source_id": {"type": "string", "minLength": 1},
        "claim_id": {"type": "string", "pattern": "^claim:"},
        "label": {"type": "string", "minLength": 1},
        "url": {"type": ["string", "null"], "format": "uri"},
    }
    for definition in schema["definitions"].values():
        definition["type"] = "object"
        definition["properties"] = {**common_properties, **definition.get("properties", {})}
    schema["definitions"]["names"]["properties"]["preferred"] = {"type": "boolean"}
    schema["definitions"]["measurements"]["properties"].update({
        "value": {"type": "number", "exclusiveMinimum": 0},
        "unit": {"type": "string", "minLength": 1},
        "rank_eligible": {"type": "boolean"},
    })
    schema["definitions"]["claims"]["properties"].update({
        "id": {"type": "string", "pattern": "^claim:"},
        "target_id": {"type": "string", "minLength": 1},
        "predicate": {"type": "string", "minLength": 1},
        "object_id": {"type": ["string", "null"]},
        "value": {"type": ["number", "null"]},
        "unit": {"type": ["string", "null"]},
        "source_snapshot_id": {"type": ["string", "null"]},
        "source_locator": {"type": ["string", "null"]},
        "method": {"type": ["string", "null"]},
        "method_source_id": {"type": ["string", "null"]},
        "support_claim_id": {"type": ["string", "null"]},
        "source_date": {"type": ["string", "null"]},
        "observation_time": {"oneOf": [{"type": "null"}, {"type": "string"},
                                         {"type": "object", "required": ["start", "end"],
                                          "properties": {"start": {"type": "string"},
                                                         "end": {"type": "string"}}}]},
        "reviewer": {"type": ["string", "null"]},
        "review_date": {"type": ["string", "null"], "format": "date"},
        "review_note": {"type": ["string", "null"]},
        "review_fingerprint": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    })
    schema["definitions"]["length_assessments"]["properties"].update({
        "evidence_status": {"enum": list(data["lengths"]["status_definitions"])},
        "rank_eligible": {"type": "boolean"},
        "published_rank": {"type": ["integer", "null"], "minimum": 1},
        "published_length_km": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "lower_bound_km": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "gate_distance_sensitivity": {"oneOf": [
            {"type": "null"},
            {"type": "object", "required": ["interpretation", "perturbation_basis", "perturbation_degrees", "scenario_count", "scenario_min_km", "scenario_max_km", "geographic_span_rank_best", "geographic_span_rank_worst", "geographic_span_rank_count", "rank_interpretation"],
             "properties": {
                 "perturbation_degrees": {"const": 0.5},
                 "scenario_count": {"enum": [9, 81]},
                 "scenario_min_km": {"type": "number", "exclusiveMinimum": 0},
                 "scenario_max_km": {"type": "number", "exclusiveMinimum": 0},
                 "geographic_span_rank_best": {"type": "integer", "minimum": 1, "maximum": 7},
                 "geographic_span_rank_worst": {"type": "integer", "minimum": 1, "maximum": 7},
                 "geographic_span_rank_count": {"const": 7},
             }},
        ]},
        "proposed_system_length_km": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "illustrated_span_km": {"type": ["number", "null"], "exclusiveMinimum": 0},
        "illustrated_span_rank": {"type": ["integer", "null"], "minimum": 1},
    })
    schema["definitions"]["geometries"]["properties"].update({
        "coordinate_reference_system": {"enum": ["OGC:CRS84", "unspecified_datum_lon_lat_degrees", "figure_axis_lon_lat_degrees_unspecified_datum"]},
        "geometry": {"oneOf": [
            {"type": "object", "required": ["type", "coordinates"],
             "properties": {"type": {"const": "Point"},
                            "coordinates": {"type": "array", "minItems": 2, "maxItems": 2,
                                            "prefixItems": [{"type": "number", "minimum": -180, "maximum": 180},
                                                            {"type": "number", "minimum": -90, "maximum": 90}]}}},
            {"type": "object", "required": ["type", "coordinates"],
             "properties": {"type": {"const": "LineString"},
                            "coordinates": {"type": "array", "minItems": 2,
                                            "items": {"type": "array", "minItems": 2, "maxItems": 2,
                                                      "prefixItems": [{"type": "number", "minimum": -180, "maximum": 180},
                                                                      {"type": "number", "minimum": -90, "maximum": 90}]}}}},
            {"type": "object", "required": ["type", "coordinates"],
             "properties": {"type": {"const": "Polygon"},
                            "coordinates": {"type": "array", "minItems": 1, "maxItems": 1,
                                            "items": {"type": "array", "minItems": 4,
                                                      "items": {"type": "array", "minItems": 2, "maxItems": 2,
                                                                "prefixItems": [{"type": "number", "minimum": -180, "maximum": 180},
                                                                                {"type": "number", "minimum": -90, "maximum": 90}]}}}}},
        ]},
    })
    schema["definitions"]["tiles"]["properties"].update({
        "zoom": {"type": "integer", "minimum": 0},
        "tile_id": {"type": "string", "minLength": 1},
        "latitude_range": {"type": "array", "minItems": 2, "maxItems": 2,
                           "items": {"type": "number", "minimum": -90, "maximum": 90}},
        "longitude_range_unwrapped": {"type": "array", "minItems": 2, "maxItems": 2,
                                      "items": {"type": "number", "minimum": -540, "maximum": 540}},
    })
    schema["definitions"]["tile_state_relations"]["properties"].update({
        "predicate": {"const": "display_overlap"},
        "display_coverage_fraction": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence_class": {"const": "atlas_geometry"},
        "physical_relation": {"const": "unresolved"},
    })
    schema["definitions"]["sources"]["properties"].update({
        "kind": {"enum": ["external", "OSW source ledger"]},
        "rights_status": {"type": "string", "minLength": 1},
        "record_count": {"type": "integer", "minimum": 0},
        "derived_detection_count": {"type": "integer", "minimum": 0},
        "total_packaged_row_count": {"type": "integer", "minimum": 0},
        "material_use_class": {"enum": ["compiled_name_and_date_records", "derived_dated_observations",
                                         "derived_cartographic_measurements", "gazetteer_name_crosswalk",
                                         "media_navigation_and_source_description", "source_scoped_factual_claim",
                                         "figure_derived_measurement_and_factual_claim"]},
        "provider_asset_redistributed": {"type": "boolean"},
    })
    schema["definitions"]["observation_sets"]["properties"].update({
        "detection_count": {"type": "integer", "minimum": 1},
        "contained_relation_count": {"type": "integer", "minimum": 0},
        "intersected_relation_count": {"type": "integer", "minimum": 0},
        "weekly_track_join": {"type": "boolean"},
    })
    path = OUTPUT / "schema.json"
    write_json(path, schema)
    written.append(path)
    observation_dir = OUTPUT / "observations"
    observation_dir.mkdir(exist_ok=True)
    observation_columns = ("id", "observation_set_id", "date", "source_ordinal", "polarity",
                           "center_lon", "center_lat", "radius_km", "area_km2", "amplitude_cm",
                           "contained_states", "intersected_states", "persistent_track_id", "source_id")
    for receipt, snapshot in snapshots:
        path = observation_dir / (receipt["date"] + ".csv.gz")
        with path.open("wb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
                with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=observation_columns)
                    writer.writeheader()
                    seen = set()
                    for entry in snapshot["entries"]:
                        assert entry["id"] not in seen
                        seen.add(entry["id"])
                        assert set(entry["contained_states"] + entry["intersected_states"]) <= set(state_matrix)
                        writer.writerow({"id": "observation:" + entry["id"],
                                         "observation_set_id": "observation_set:" + receipt["date"],
                                         "date": receipt["date"], "source_ordinal": entry["source_ordinal"],
                                         "polarity": entry["polarity"],
                                         "center_lon": entry["center"][0], "center_lat": entry["center"][1],
                                         "radius_km": entry["radius_km"], "area_km2": entry["area_km2"],
                                         "amplitude_cm": entry["amplitude_cm"],
                                         "contained_states": json.dumps(entry["contained_states"]),
                                         "intersected_states": json.dumps(entry["intersected_states"]),
                                         "persistent_track_id": entry.get("persistent_track_id"),
                                         "source_id": next(row["source_id"] for row in observation_sets if row["date"] == receipt["date"])})
        written.append(path)
    source_dir = OUTPUT / "source-ledgers"
    source_dir.mkdir(exist_ok=True)
    for filename in list(INPUTS.values()) + snapshot_inputs:
        path = source_dir / filename
        shutil.copyfile(RESEARCH / filename, path)
        written.append(path)
    for filename in RELEASE_DOCUMENTS:
        path = OUTPUT / filename
        shutil.copyfile(ROOT / "almanac" / "release" / filename, path)
        written.append(path)
    manifest = {"schema": "osw.ocean-motion-release.v1", "version": VERSION,
                "status": "release_candidate_not_published", "inputs": [
                    {"path": "research/" + filename, "sha256": digest(RESEARCH / filename)}
                    for filename in list(INPUTS.values()) + snapshot_inputs] + [
                    {"path": "figures/osw-province-atlas-interactive.svg",
                     "sha256": digest(ROOT / "figures" / "osw-province-atlas-interactive.svg")}] + [
                    {"path": "almanac/release/" + filename,
                     "sha256": digest(ROOT / "almanac" / "release" / filename)}
                    for filename in RELEASE_DOCUMENTS],
                "code_files": [{"path": path.as_posix(), "sha256": digest(ROOT / path)} for path in (
                    Path("analysis/build_ocean_motion_release.py"),
                    Path("analysis/build_loop_eddy_name_date_conflict_audit.py"),
                    Path("analysis/build_ocean_motion_claims.py"),
                    Path("analysis/test_ocean_motion_claim_reviews.py"),
                    Path("analysis/check_ocean_motion_release.py"),
                    Path("analysis/build_navo_freddies_eddy_state_join.py"),
                    Path("analysis/build_published_kraken_figure_state_join.py"),
                    Path("analysis/build_kraken_footprint_candidate.py"),
                    Path("analysis/build_footprint_movie_context.py"),
                    Path("analysis/fetch_navo_freddies_eddy_snapshot.py"),
                    Path("analysis/fetch_noaa_lsa_geostrophic_snapshot.py"),
                    Path("analysis/build_gulf_stream_geostrophic_path.py"),
                    Path("analysis/test_gulf_stream_geostrophic_path.py"),
                    Path("analysis/fetch_ocean_motion_crossref_metadata.py"),
                    Path("analysis/fetch_ocean_motion_nasa_svs_metadata.py"),
                    Path("analysis/fetch_gulf_stream_navo_front_snapshot.py"),
                    Path("analysis/build_gulf_stream_navo_state_snapshot.py"),
                    Path("analysis/build_motion_state_join.py"),
                    Path("analysis/build_cartographic_current_state_join.py"),
                    Path("almanac/screened-atlas/footprint-view.js"),
                    Path("almanac/object.js"), Path("almanac/object.html"),
                    Path("almanac/app.js"), Path("almanac/index.html"), Path("almanac/styles.css"),
                    Path("almanac/movies.js"), Path("almanac/movies.html"))],
                "files": [{"path": path.relative_to(OUTPUT).as_posix(), "sha256": digest(path)} for path in written]}
    write_json(OUTPUT / "manifest.json", manifest)
    print(json.dumps(coverage["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
