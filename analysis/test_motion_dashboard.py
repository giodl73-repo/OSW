"""Ensure provenance updates and observation dates preserve their meaning."""
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from build_motion_dashboard import ROOT, build, build_ground, latest_observation_date


class DashboardEvidenceTests(unittest.TestCase):
    def test_kuroshio_counts_four_profiles_without_double_counting_prose(self):
        row=next(r for r in build()['entries'] if r['id']=='current:kuroshio')
        self.assertEqual(row['capabilities']['scoped_width'],3)
        self.assertEqual(row['capabilities']['time_samples'],4)
        self.assertEqual(row['series'][0]['evidence_role'],'seasonal_width_profile_plot_extraction')
        self.assertEqual(row['series'][0]['frames'],4)
        self.assertIsNone(row['latest_observation_date'])

    def test_leeuwin_width_months_count_as_records_without_single_year_dates(self):
        current=next(row for row in build()['entries'] if row['id']=='current:leeuwin')
        self.assertEqual(current['capabilities']['scoped_width'],2)
        self.assertEqual(current['capabilities']['time_samples'],12)
        self.assertEqual(current['series'][0]['frames'],12)
        self.assertEqual(current['series'][0]['evidence_role'],'monthly_fitted_width_plot_extraction')
        self.assertIsNone(current['latest_observation_date'])
        self.assertNotEqual(current['latest_observation_date'],'2008-04-01')

    def test_necc_monthly_diagnostic_is_pinned_and_not_admitted_width(self):
        current=next(row for row in build()['entries'] if row['id']=='current:pacific-north-equatorial-countercurrent')
        self.assertEqual(current['capabilities']['scoped_width'],1)
        self.assertEqual(current['capabilities']['reported_length'],0)
        self.assertEqual(current['capabilities']['time_samples'],12)
        series=next(s for s in current['series'] if s['evidence_role']=='monthly_mean_section_width_candidate')
        self.assertEqual(series['frames'],12)
        path=ROOT/'research/pacific-necc-oscar-2013-section-diagnostic.json'
        original=Path.read_bytes;altered=json.loads(original(path));altered['annual_width_range_km']=[210,640]
        def read_bytes(candidate):return json.dumps(altered).encode() if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',read_bytes),self.assertRaises(ValueError):build()

    def test_tsuchiya_general_width_counts_scoped_records_without_seasonal_support(self):
        snapshot=build()
        for side in ['north','south']:
            current=next(row for row in snapshot['entries'] if row['id']==f'current:pacific-{side}-subsurface-countercurrent')
            self.assertEqual(current['capabilities']['scoped_width'],1)
            self.assertEqual(current['capabilities']['reported_length'],0)

    def test_red_sea_reach_and_channels_do_not_become_ranked_length_or_current_width(self):
        current=next(row for row in build()['entries'] if row['id']=='current:red-sea-saline-overflow')
        self.assertEqual(current['capabilities']['scoped_width'],0)
        self.assertEqual(current['capabilities']['reference_route'],0)
        self.assertEqual(current['capabilities']['reported_length'],0)
        self.assertEqual(current['scope_audits'][0]['reported_reach']['approximate_length_km'],130)
        self.assertEqual(len(current['scope_audits'][0]['branches']),3)

    def test_persian_gulf_core_records_are_scoped_widths_without_route_admission(self):
        current=next(row for row in build()['entries'] if row['id']=='current:persian-gulf-saline-overflow')
        self.assertEqual(current['capabilities']['scoped_width'],6)
        self.assertEqual(current['capabilities']['reference_route'],0)
        self.assertEqual(len(current['scope_audits'][0]['reported_local_core_widths']),6)
        self.assertEqual(current['scope_audits'][0]['reported_section_distances']['rows'][-1]['distance_km'],920)

    def test_observed_section_content_changes_only_its_current_time_fingerprint(self):
        before={row['id']:row for row in build()['entries']}
        path=ROOT/'research/antilles-ab0505-400m-section-diagnostic.json'
        original=Path.read_bytes;data=json.loads(original(path))
        data['sections'][1]['half_peak_diagnostic']['offshore_span_km']+=.01
        def altered(candidate):return json.dumps(data).encode() if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',altered):after={row['id']:row for row in build()['entries']}
        self.assertNotEqual(before['current:antilles']['section_fingerprints']['time_evidence'],after['current:antilles']['section_fingerprints']['time_evidence'])
        self.assertEqual([ident for ident in before if before[ident]['fingerprint']!=after[ident]['fingerprint']],['current:antilles'])

    def test_antilles_section_series_preserves_pending_measurement_and_checksum(self):
        current=next(row for row in build()['entries'] if row['id']=='current:antilles')
        self.assertEqual(current['series'][0]['frames'],2)
        self.assertEqual(current['capabilities']['scoped_width'],0)
        self.assertEqual(current['capabilities']['reference_route'],0)
        path=ROOT/'research/antilles-ab0505-400m-section-diagnostic.json'
        original=Path.read_bytes
        for key,value in [('inventory_sha256','wrong'),('whole_current_width_km',74),('width_rank_eligible',True),('seasonal_playback_eligible',True),('geographic_role','current_axis')]:
            data=json.loads(original(path));data[key]=value
            def altered(candidate):return json.dumps(data).encode() if candidate==path else original(candidate)
            with self.subTest(key=key),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):build()
        data=json.loads(original(path));data['sections'][1]['half_peak_diagnostic']['full_width_km']=74
        def altered(candidate):return json.dumps(data).encode() if candidate==path else original(candidate)
        with patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):build()

    def test_pending_scope_links_resolve_without_canonical_admission(self):
        rows = {row['id']: row for row in build()['entries']}
        aleutian = rows['current:aleutian']
        self.assertEqual(aleutian['scope_notes'][0]['related_proposed_currents'], [
            {'id':'alaskan-stream','name':'Alaskan Stream'},
            {'id':'aleutian-north-slope','name':'Aleutian North Slope Current'}])
        self.assertEqual(aleutian['capabilities']['reference_route'],0)
        self.assertEqual(aleutian['capabilities']['scoped_width'],0)
        self.assertNotIn('current:aleutian-north-slope',rows)
        notes_path=ROOT/'research/ocean-current-scope-notes.json'
        notes=json.loads(notes_path.read_bytes())
        note=next(n for n in notes['entries'] if n['current_id']=='aleutian')
        original=Path.read_bytes
        def altered(path):
            return json.dumps(notes).encode() if path==notes_path else original(path)
        for invalid in ['alaskan-stream',['aleutian'],['missing'],['alaskan-stream','alaskan-stream'],[{}]]:
            note['related_proposed_current_ids']=invalid
            with self.subTest(invalid=invalid),patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):
                build()

    def test_supporting_scope_sources_preserve_access_and_reject_missing_limits(self):
        rows = {row['id']: row for row in build()['entries']}
        current = rows['current:west-australian']
        self.assertEqual(current['capabilities']['reference_route'], 0)
        self.assertEqual(current['capabilities']['scoped_width'], 0)
        self.assertIsNone(current['latest_observation_date'])
        note = current['scope_notes'][0]
        self.assertEqual(note['related_current_ids'], ['leeuwin'])
        self.assertEqual(len(note['supporting_sources']), 2)
        self.assertIn('full paper unavailable', note['supporting_sources'][0]['access'])
        notes_path = ROOT / 'research/ocean-current-scope-notes.json'
        notes = json.loads(notes_path.read_bytes())
        source = next(n for n in notes['entries'] if n['current_id'] == 'west-australian')['supporting_sources'][0]
        original = Path.read_bytes
        def altered(path):
            return json.dumps(notes).encode() if path == notes_path else original(path)
        for key, invalid in [('access', ''), ('locator', None), ('url', 'javascript:alert(1)')]:
            with self.subTest(key=key):
                saved = source[key]
                source[key] = invalid
                with patch.object(Path, 'read_bytes', altered), self.assertRaises(ValueError):
                    build()
                source[key] = saved

    def test_guiana_local_continuity_review_does_not_borrow_north_brazil_route(self):
        rows={row['id']:row for row in build()['entries']}
        guiana=rows['current:guiana']
        self.assertEqual(guiana['capabilities']['scope_notes'],1)
        self.assertEqual(guiana['capabilities']['reference_route'],0)
        self.assertEqual(guiana['capabilities']['scoped_width'],1)
        self.assertEqual(rows['current:north-brazil']['capabilities']['scoped_width'],2)
        self.assertEqual(guiana['capabilities']['time_samples'],0)
        self.assertEqual(guiana['latest_observation_date'],'2004-02-18')
        self.assertEqual(guiana['scope_notes'][0]['related_current_ids'],['north-brazil'])
        self.assertEqual(rows['current:north-brazil']['capabilities']['reference_route'],1)
        audit=json.loads((ROOT/guiana['scope_notes'][0]['audit_file']).read_text(encoding='utf-8'))
        self.assertFalse(audit['continuity_assessment']['local_non_detection_implies_global_absence'])
        self.assertFalse(audit['continuity_assessment']['annual_geometry_playback_eligible'])
        self.assertFalse(audit['continuity_assessment']['ring_translation_is_current_axis'])
        self.assertIsNone(audit['whole_current_length_km'])
        self.assertIsNone(audit['whole_current_width_km'])

    def test_dated_lines_preserve_identity_date_and_receipt(self):
        rows={r['id']:r for r in build()['entries']}
        system=rows['current:gulf-stream-system']
        dated=[f for f in system['map_features'] if f['role'] in {'dated_partial_geostrophic_streamline','dated_analyzed_surface_front'}]
        self.assertEqual(len(dated),3)
        geometry={g['id']:g for g in json.loads((ROOT/'almanac/release/v0.1.0/geometries.json').read_text(encoding='utf-8'))}
        for feature in dated:
            original=geometry[feature['geometry_id']]
            self.assertEqual(feature['geometry'],original['geometry'])
            self.assertEqual(feature['observation_date'],original['observation_date'])
            self.assertEqual(feature['front_side'],original.get('front_side'))
            self.assertTrue(feature['receipt_file'].startswith('research/'))
            self.assertTrue(feature['source_url'].startswith('https://'))
        self.assertEqual({f['observation_date'] for f in dated},{'2026-09-25','2026-09-28'})
        self.assertEqual(rows['current:gulf-stream']['capabilities']['geometry'],0)
        self.assertEqual(system['capabilities']['reference_route'],0)

    def test_ground_serializes_valid_svg_with_namespaced_atlas_layers(self):
        # Imported source layers carry namespaces; manually adding xmlns duplicates
        # the serializer's declaration after route modules register SVG defaults.
        build_ground()
        svg=ET.parse(ROOT/'figures/ocean-motion-dashboard-ground.svg').getroot()
        self.assertEqual(svg.tag,'{http://www.w3.org/2000/svg}svg')
        self.assertEqual(svg.get('viewBox'),'60 90 1480 740')
        self.assertTrue(any(e.get('class')=='province-field' for e in svg))
        self.assertTrue(any(e.get('class')=='province-labels' for e in svg))

    def test_scope_note_does_not_turn_integration_span_into_width(self):
        rows = {row['id']: row for row in build()['entries']}
        antilles = rows['current:antilles']
        self.assertEqual(antilles['capabilities']['scope_notes'], 1)
        self.assertEqual(antilles['capabilities']['scoped_width'], 0)
        self.assertEqual(antilles['capabilities']['reference_route'], 0)
        self.assertEqual(antilles['latest_observation_date'], '2015-11-23')
        self.assertIn('Modern observations', antilles['scope_notes'][0]['summary'])

    def test_profile_composite_does_not_invent_an_observation_endpoint(self):
        row=next(r for r in build()['entries'] if r['id']=='current:north-cape')
        self.assertEqual(row['capabilities']['scoped_width'],1)
        self.assertEqual(row['capabilities']['scope_notes'],1)
        self.assertEqual(row['capabilities']['time_samples'],1)
        self.assertIsNone(row['latest_observation_date'])
        self.assertEqual(row['capabilities']['reference_route'],1)

    def test_typed_links_do_not_supply_metrics_or_observation_dates(self):
        result = build()
        self.assertEqual(len(result['connections']), 5)
        self.assertEqual({c['predicate'] for c in result['connections']}, {'source_described_downstream_continuation', 'source_described_feeding_relation', 'source_described_branching_relation'})
        rows = {row['id']: row for row in result['entries']}
        self.assertEqual(rows['current:aleutian']['capabilities']['source_connectivity'], 3)
        self.assertEqual(rows['current:aleutian']['capabilities']['reference_route'], 0)
        self.assertIsNone(rows['current:aleutian']['latest_observation_date'])
        self.assertNotIn('current:alaskan-stream', rows)
        for connection in result['connections']:
            self.assertIsNone(connection['junction_coordinate'])
            self.assertIsNone(connection['transport_sv'])
            self.assertIs(connection['canonical_admission'], False)

    def test_naming_review_does_not_transfer_neighbor_dimensions_or_dates(self):
        rows={row['id']:row for row in build()['entries']}
        for ident in ['norwegian','spitsbergen-atlantic']:
            row=rows['current:'+ident]
            self.assertEqual(row['capabilities']['scope_notes'],1)
            self.assertEqual(row['capabilities']['reference_route'],0)
            self.assertEqual(row['capabilities']['scoped_width'],0)
            self.assertIsNone(row['latest_observation_date'])
        notes_path=ROOT/'research/ocean-current-scope-notes.json'
        notes=json.loads(notes_path.read_bytes())
        next(n for n in notes['entries'] if n['current_id']=='norwegian')['related_current_ids']=['unreleased-current']
        original=Path.read_bytes
        def altered(path):return json.dumps(notes).encode() if path==notes_path else original(path)
        with patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):build()

    def test_map_preserves_gateway_and_geometry_roles(self):
        rows = build()['entries']
        self.assertTrue(all(row['map_features'] for row in rows))
        shared = [f for row in rows for f in row['map_features'] if f['role'] == 'shared_regional_gateway']
        self.assertGreaterEqual(len(shared), 96)
        self.assertEqual({tuple(f['geometry']['coordinates']) for f in shared}, {(-93, 25)})
        self.assertTrue(all(f['group'] == 'Gulf of Mexico regional gateway' for f in shared))
        portugal = next(row for row in rows if row['id'] == 'current:portugal')
        self.assertTrue(any(f['role'] == 'editorial_reference_route' for f in portugal['map_features']))
        self.assertEqual(portugal['capabilities']['geometry'], 0)
        self.assertTrue(all(f['note'] for row in rows for f in row['map_features']))

    def test_only_valid_explicit_observation_dates_count(self):
        self.assertEqual(latest_observation_date([None,'winter','2026','2026-02-30',{'start':'1993-05-01','end':'1994-03-01'},'2024-12-15T12:00:00Z']), '2024-12-15')
        self.assertIsNone(latest_observation_date([{'publication_date':'2026-10-03','retrieved_at':'2026-10-03'},'2026-13-01']))

    def test_source_review_change_highlights_only_affected_records(self):
        before=build()
        sources_path=ROOT/'almanac/release/v0.1.0/sources.json'
        sources=json.loads(sources_path.read_bytes())
        entity=json.loads((ROOT/'almanac/release/v0.1.0/entities.json').read_bytes())[0]
        target=next(s for s in sources if s['id']==entity['source_id'])
        target['rights_review_date']='2099-01-01'  # Synthetic metadata, never written.
        original=Path.read_bytes
        def altered(path):
            return json.dumps(sources).encode() if path==sources_path else original(path)
        with patch.object(Path,'read_bytes',altered):
            after=build()
        old={r['id']:r for r in before['entries']}
        changed=[r for r in after['entries'] if r['fingerprint']!=old[r['id']]['fingerprint']]
        self.assertIn(entity['id'],[r['id'] for r in changed])
        self.assertLess(len(changed),240)
        for row in changed:
            self.assertNotEqual(row['section_fingerprints']['sources'],old[row['id']]['section_fingerprints']['sources'])
            self.assertEqual(row['capabilities'],old[row['id']]['capabilities'])
            self.assertEqual(row['latest_observation_date'],old[row['id']]['latest_observation_date'])


if __name__=='__main__': unittest.main()
