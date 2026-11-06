"""Independent actual-original/product checks; canonical delivery remains pending."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "research/eicc-wijesekera-2015-width-source-facts-v1.json"
REPORT = ROOT / "research/eicc-wijesekera-2015-width-evidence-v1.json"
FIGURE = ROOT / "figures/eicc-wijesekera-2015-width-evidence-v1.svg"


def test_actual_original_and_retained_facts_are_exact():
    facts = json.loads(FACTS.read_text())
    path = ROOT / facts["source"]["original_file"]
    assert path.stat().st_size == 14987904
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "56fababd833dfb08ab4ff606c778eed1268ee9e0d7bc5bbfcc0635b93130b7fc"
    receipt = json.loads((ROOT / facts["source"]["acquisition_receipt"]).read_text())
    assert receipt["sha256"] == facts["source"]["original_sha256"]
    assert facts["source"]["doi"] == "10.1002/2015JC010744"
    assert facts["source"]["whole_paper_scientifically_reviewed"] is False


def test_width_statement_support_and_nonpromotion_are_preserved():
    assert hashlib.sha256(REPORT.read_bytes()).hexdigest() == "4a452eeafa4c95a3afafac470bb6858819d748b81b1a4bb43219c8737175479b"
    report = json.loads(REPORT.read_text())
    facts = json.loads(FACTS.read_text())
    assert report["source_facts"] == facts
    assert report["source_statement_count"] == 3
    assert report["independent_observations_created"] == 0
    assert report["canonical_admission_verified"] is False
    transect, turning, discussion = facts["reported_widths"]
    assert [r["reported_width_km"] for r in (transect, turning, discussion)] == [100, 200, 250]
    assert transect["reported_time_window"] == ["2013-12-23", "2013-12-24"]
    assert transect["width_depth_level_m"] == 21
    assert turning["reported_time_window"] is discussion["reported_time_window"] is None
    assert turning["width_depth_level_m"] is discussion["width_depth_level_m"] is None
    assert turning["support_kind"] == "source_reported_observational_synthesis_context"
    assert discussion["support_kind"] == "source_reported_combined_observation_model_context"
    assert all(row["canonical_width_admitted"] is False for row in facts["reported_widths"])
    assert facts["eligibility"]["annual_width_min_km"] is None
    assert facts["eligibility"]["annual_width_max_km"] is None
    assert facts["eligibility"]["canonical_width_admissions"] == 0


def test_original_svg_has_separate_markers_accessible_context_and_source_link():
    assert hashlib.sha256(FIGURE.read_bytes()).hexdigest() == "63616a738d10e181afc4b04f33b9b082c9be2f6cdc44bc9d9a16f6298c37055e"
    root = ET.fromstring(FIGURE.read_bytes())
    ns = {"s": "http://www.w3.org/2000/svg"}
    assert root.attrib["role"] == "img"
    assert root.find("s:title", ns).text
    desc = root.find("s:desc", ns).text
    assert "not an annual range" in desc and "Canonical admission pending" in desc
    markers = root.findall(".//s:circle", ns)
    assert [float(x.attrib["cx"]) for x in markers] == [700, 810, 865]
    assert markers[2].attrib["fill"] != markers[0].attrib["fill"]
    assert not root.findall(".//s:polygon", ns) and not root.findall(".//s:polyline", ns)
    link = root.find(".//s:a", ns)
    assert link.attrib["href"] == "https://agupubs.onlinelibrary.wiley.com/doi/10.1002/2015JC010744"
    assert "doi:10.1002/2015JC010744" in "".join(link.itertext())
