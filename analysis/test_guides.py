import csv
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
PAGES = tuple(GUIDES / f"{number:02d}-{slug}.md" for number, slug in (
    (1, "WATER-MASSES-AND-LAYERS"),
    (2, "FRONTS-JETS-AND-BANDS"),
    (3, "EDDIES-FILAMENTS-AND-BARRIERS"),
    (4, "GATES-TRANSPORTS-AND-RELAYS"),
    (5, "TRANSFORMATION-AND-OVERTURNING"),
    (6, "PROVINCES-SEASCAPES-AND-HEATWAVES"),
    (7, "OCEANS-AND-GAS-GIANTS"),
    (8, "SEAFLOOR-COASTS-AND-TOPOGRAPHIC-STEERING"),
    (9, "WAVES-TIDES-AND-OSCILLATIONS"),
    (10, "PLUMES-UPWELLING-AND-VERTICAL-EXCHANGE"),
    (11, "SEA-ICE-POLYNYAS-AND-OCEAN-CAVITIES"),
    (12, "LIFE-OXYGEN-NUTRIENTS-AND-CARBON"),
    (13, "HOW-TO-NAME-AN-OCEAN-PATCH"),
    (14, "EVIDENCE-RECEIPTS"),
))
REGISTRY = ROOT / "research" / "ocean-object-classification.csv"
RELATIONS = ROOT / "research" / "ocean-object-relations.csv"

OBJECT_TYPES = {
    "material_body",
    "layer_interface",
    "gradient_boundary",
    "flow_structure",
    "connectivity_structure",
    "flux_budget_construct",
    "process",
    "event_classified_state",
    "reference_geography",
    "substrate_feature",
    "wave_oscillation",
    "phase_cover_object",
    "contact_boundary",
}

COVERAGE_VALUES = {"exhaustive", "partial", "event_only", "sparse", "construct_only"}
IDENTITY_TESTS = {
    "property_signature",
    "source_tracer",
    "vertical_structure",
    "vertical_gradient",
    "geographic_convention",
    "horizontal_gradient",
    "velocity_pattern",
    "vertical_velocity",
    "trajectory_coherence",
    "section_integral",
    "closed_budget",
    "transformation_rate",
    "streamfunction",
    "anomaly_threshold",
    "coupled_index",
    "ecological_classifier",
    "terrain_geometry",
    "spectral_phase",
    "phase_fraction",
    "vertical_displacement",
    "inventory_integral",
    "impact_classifier",
    "surface_flux",
    "absolute_threshold",
}
GEOMETRIES = {"curve", "event_field", "network", "pathway", "property_space", "surface", "volume"}
TIME_BEHAVIORS = {
    "instantaneous",
    "days_months",
    "seasonal",
    "interannual",
    "climatic_reference",
    "geological",
    "periodic",
    "user_declared",
    "hours_days",
}
MOBILITY_VALUES = {"advects", "evolves", "fixed", "oscillates", "propagates"}
STATUS_VALUES = {"established", "osw_construct"}
RELATION_PREDICATES = {
    "subtype_of",
    "often_coincides_with",
    "reshapes",
    "produced_by",
    "carried_by",
    "measured_across",
    "part_of",
    "bounds",
    "supports",
    "diagnosed_by",
    "transforms",
    "moves_across",
    "changes_membership_of",
    "changes_volume_of",
    "overlays",
    "steers",
    "channels",
    "drives",
    "transports_energy_through",
    "contains",
    "entrains",
    "opens_within",
}


def test_ocean_object_guide_contract() -> None:
    assert (GUIDES / "README.md").is_file()
    assert all(page.is_file() for page in PAGES)
    index = (GUIDES / "README.md").read_text(encoding="utf-8")
    for page in PAGES:
        assert page.name in index
        text = page.read_text(encoding="utf-8")
        assert "```text" in text
        assert "## Common mistakes" in text

    assert "## How to read these guides" in index
    for evidence_label in (
        "Concept",
        "Reference geography",
        "Field",
        "Detected state",
        "Integrated quantity",
        "Mechanism hypothesis",
    ):
        assert evidence_label in index

    gate_guide = PAGES[3].read_text(encoding="utf-8")
    assert "reference-dependent advective heat transport" in gate_guide
    assert "volume budget closes consistently" in gate_guide

    planetary_guide = PAGES[6].read_text(encoding="utf-8")
    assert "## A falsifiable comparison" in planetary_guide
    assert "What would count against it" in planetary_guide


def test_ocean_object_guide_links_resolve() -> None:
    for page in (GUIDES / "README.md",) + PAGES:
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#")):
                continue
            path = (page.parent / target.split("#", 1)[0]).resolve()
            assert path.exists(), f"broken link in {page.name}: {target}"


def test_ocean_object_classification_registry() -> None:
    with REGISTRY.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 110
    assert len({row["object_id"] for row in rows}) == len(rows)
    assert len({row["preferred_name"].casefold() for row in rows}) == len(rows)
    assert {row["object_type"] for row in rows} == OBJECT_TYPES
    assert {row["coverage"] for row in rows} <= COVERAGE_VALUES
    assert {row["identity_test"] for row in rows} <= IDENTITY_TESTS
    assert {row["geometry"] for row in rows} <= GEOMETRIES
    assert {row["time_behavior"] for row in rows} <= TIME_BEHAVIORS
    assert {row["mobility"] for row in rows} <= MOBILITY_VALUES
    assert {row["status"] for row in rows} <= STATUS_VALUES
    assert all(re.fullmatch(r"OBJ\d{3}", row["object_id"]) for row in rows)
    assert all(row["identity_test"] and row["geometry"] for row in rows)
    assert all(row["external_anchor"] and row["guide"] and row["status"] for row in rows)

    classification = (ROOT / "CLASSIFICATION.md").read_text(encoding="utf-8")
    normalized_classification = " ".join(classification.split())
    assert "110 core terms across 13 types" in classification
    assert REGISTRY.name in classification
    assert "not a claim that nature contains exactly 110" in normalized_classification

    with RELATIONS.open(encoding="utf-8", newline="") as handle:
        relations = list(csv.DictReader(handle))

    object_ids = {row["object_id"] for row in rows}
    assert len(relations) == 107
    assert len({row["relation_id"] for row in relations}) == len(relations)
    assert {row["predicate"] for row in relations} <= RELATION_PREDICATES
    assert all(row["subject_id"] in object_ids and row["object_id"] in object_ids for row in relations)
    assert all(row["subject_id"] != row["object_id"] for row in relations)
    assert all(row["qualification"] and row["status"] for row in relations)
    assert "107 explicit" in classification


def test_source_register_ids_are_unique() -> None:
    source_register = (ROOT / "SOURCE-REGISTER.md").read_text(encoding="utf-8")
    source_ids = re.findall(r"^\| ([A-Z]+\d+) \|", source_register, flags=re.MULTILINE)
    duplicates = sorted({source_id for source_id in source_ids if source_ids.count(source_id) > 1})
    assert not duplicates, f"duplicate source-register IDs: {duplicates}"
