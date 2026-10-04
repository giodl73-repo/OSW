import copy
import json
import unittest
from unittest.mock import patch
import build_current_reference_path_catalog as catalog
from pathlib import Path
from check_current_measurement_protocol import validate_record, validate_route_topology

class ProtocolAuditTests(unittest.TestCase):
    def test_frontal_anchor_role_dates_and_vertex_support_remain_explicit(self):
        row=json.loads((Path(__file__).resolve().parents[1]/'research/south-pacific-eastern-front-reach-reference-path-candidate.json').read_text(encoding='utf-8'))
        validate_record(row)
        for key,value in [('geometry_role','observed_current_axis'),('time_precision','day'),('longitude_latitude',[-104,-33.8]),('source_locator',''),('observed_period',{'start':'1994-04','end':'1994-02'}),('observed_period',{'start':'1994-13','end':'1995-01'}),('observed_period',{'start':'0000-02','end':'0000-04'})]:
            invalid=copy.deepcopy(row);invalid['source_anchor_observations'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_record(invalid)
        invalid=copy.deepcopy(row);invalid['source_anchor_observations'][1]['id']=invalid['source_anchor_observations'][0]['id']
        with self.assertRaises(ValueError):validate_record(invalid)
    def test_source_seasons_preserve_windows_without_annual_geometry(self):
        row=copy.deepcopy(self.row)
        convention={'label_basis':'boreal','role':'source_observation_labels_only','months_by_label':{'summer':[7,8,9]},'source_locator':'Source table footnote','supports_annual_route_geometry':False}
        row['source_season_convention']=convention
        validate_record(row)
        for key,value in [('label_basis','geographic_latitude_inference'),('role','annual_geometry'),('supports_annual_route_geometry',True),('source_locator',''),('months_by_label',{}),('months_by_label',{'summer':[0,7]}),('months_by_label',{'summer':[True]}),('months_by_label',{'summer':[7,7]}),('months_by_label',{'summer':[13]})]:
            invalid=copy.deepcopy(row);invalid['source_season_convention'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_record(invalid)

    def test_closed_circuit_rejects_open_reversed_and_independent_endpoints(self):
        row={'route_topology':'closed_circuit','circuit_direction':'counterclockwise',
             'circuit_anchor_role':'arbitrary_repeat_vertex_not_origin',
             'endpoint_latitude_offsets_degrees':[0],
             'coordinates_lon_lat':[[29,42],[32,41],[40,42],[36,44],[29,42]]}
        validate_route_topology(row)
        for key,value in [('coordinates_lon_lat',row['coordinates_lon_lat'][:-1]),
                          ('circuit_direction','clockwise'),
                          ('circuit_anchor_role','observed_origin'),
                          ('endpoint_latitude_offsets_degrees',[-.1,0,.1]),
                          ('coordinates_lon_lat',[[29,42],[40,44],[29,44],[40,42],[29,42]])]:
            invalid=copy.deepcopy(row);invalid[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_route_topology(invalid)
    def setUp(self):
        self.row = json.loads((Path(__file__).resolve().parents[1] / "research/guinea-reference-path-candidate.json").read_text(encoding="utf-8"))

    def test_catalog_gate_preserves_output_on_rejection(self):
        with patch("check_current_measurement_protocol.main", side_effect=ValueError("protocol rejected")) as audit, patch.object(catalog, "OUTPUT") as output:
            with self.assertRaisesRegex(ValueError, "protocol rejected"):
                catalog.main()
            audit.assert_called_once()
            output.write_text.assert_not_called()

    def test_rejects_missing_provenance_and_admission_changes(self):
        for field, value in (("source_retrieved_date", ""), ("scope", ""), ("rank_eligible_published_estimates", True), ("remaining_gates", [])):
            row = copy.deepcopy(self.row)
            row[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_record(row)

    def test_rejects_truncated_or_duplicated_grid(self):
        row = copy.deepcopy(self.row)
        row["scenarios"].pop()
        row["scenario_count"] -= 1
        with self.assertRaisesRegex(ValueError, "truncated"):
            validate_record(row)
        row = copy.deepcopy(self.row)
        row["scenarios"][-1] = copy.deepcopy(row["scenarios"][0])
        with self.assertRaisesRegex(ValueError, "declared grid"):
            validate_record(row)

    def test_rejects_nonfinite_numbers_and_invalid_date(self):
        for value in [float("nan"), float("inf"), -float("inf")]:
            row = copy.deepcopy(self.row)
            row["scenarios"][0]["length_km"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_record(row)
        row = copy.deepcopy(self.row)
        row["source_retrieved_date"] = "2026-02-30"
        with self.assertRaisesRegex(ValueError, "calendar date"):
            validate_record(row)

    def test_rejects_distance_and_envelope_corruption(self):
        row = copy.deepcopy(self.row)
        row["scenarios"][0]["length_km"] += 1
        with self.assertRaises(ValueError):
            validate_record(row)
        row = copy.deepcopy(self.row)
        row["reported_scenario_range_km"][0] += 100
        with self.assertRaises(ValueError):
            validate_record(row)

if __name__ == "__main__":
    unittest.main()
