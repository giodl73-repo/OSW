"""Check offshore component interpretation and original-data reproducibility."""
import json, unittest
from unittest.mock import patch
from build_west_australian_oscar_spans import CONFIG,OUTPUT,CACHE,build,profiles,source_urls
from build_basin_surface_section_spans import diagnostic_matches

class OffshoreTests(unittest.TestCase):
    def test_exact_source_and_recomputed_months(self):
        actual=build();saved=json.loads(OUTPUT.read_bytes())
        self.assertTrue(diagnostic_matches(saved,actual))
        self.assertEqual(actual['counts'],{'source_times':72,'cells_per_time':169,'missing_vector_pairs':144})
        self.assertEqual([m['approximate_section_span_km'] for m in actual['months']],[120,190,100,150,90,90,100,90,120,110,120,90])
        self.assertEqual(sum(m['nominal']['resolution_review_required'] for m in actual['months']),10)
        self.assertTrue(all(m['all_thresholds_resolved'] for m in actual['months']))
        self.assertFalse(actual['current_association_verified'])
        self.assertIsNone(actual['annual_width_range_km'])

    def test_missing_u_cannot_contribute_to_mean_v(self):
        rows=[{'coordinate':x,'longitude':x,'latitude':-32,'eastward_m_s':0.,'northward_m_s':v} for x,v in [(80,0.),(81,.1),(82,.2),(83,.1),(84,0.)]]
        frames=[{'time':f'2013-{m:02d}-{day:02d}T00:00:00Z','samples':[dict(r) for r in rows]} for m in range(1,13) for day in [1,6,11,16,21,26]]
        frames[0]['samples'][2].update(eastward_m_s=None,northward_m_s=100.)
        section={'fixed_axis':'latitude','fixed_coordinate':-32,'varying_axis':'longitude','domain':[80,84],'peak_search':[80,84],'component':'northward'}
        result=profiles(frames,section)
        self.assertAlmostEqual(result[0]['profile'][2]['component_m_s'],.2)
        self.assertEqual(result[0]['profile'][2]['paired_source_samples'],5)
        frames[1]['samples'][2]['eastward_m_s']=None
        result=profiles(frames,section)
        self.assertIsNone(result[0]['profile'][2]['component_m_s'])
        self.assertEqual(result[0]['nominal']['status'],'unresolved_full_span')

    def test_changed_component_and_domain_rejected(self):
        cfg=json.loads(CONFIG.read_bytes())
        for changed in [dict(cfg,component='southward'),dict(cfg,domain=[80,105]),dict(cfg,current_association_verified=True)]:
            with self.subTest(changed=changed),self.assertRaises(ValueError):source_urls(changed)

    def test_provider_bytes_cannot_bypass_pin(self):
        path=CACHE/'section.csv';original=path.read_bytes()
        from pathlib import Path
        read=Path.read_bytes
        def changed(p):return original+b'\n' if p==path else read(p)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'provider bytes'):build()

if __name__=='__main__':unittest.main()
