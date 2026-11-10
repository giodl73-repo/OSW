import unittest
import inspect_chen_indian_sec_coordinates_v1 as subject


class Array:
    def __init__(self, row, shape=None):
        self.row = row
        self.shape = shape or (1, len(row))
    def tolist(self):
        return [self.row]


def coordinates():
    return {'lat': Array([-20 + i / 3 for i in range(76)]),
            'lon': Array([40 + i / 3 for i in range(212)]),
            'time_year': Array(list(range(1993, 2017)))}


class CoordinateGuards(unittest.TestCase):
    def test_only_coordinates_requested_and_values_retained(self):
        def loader(path, **options):
            self.assertEqual(options, {'variable_names':['lat','lon','time_year'], 'squeeze_me':False})
            return coordinates()
        result = subject.inspect_coordinates('synthetic', loader)
        self.assertTrue(result['provider_year_range_matches'])
        self.assertEqual(result['time_year']['values'], list(range(1993, 2017)))

    def test_unexpected_fields_or_missing_coordinates_refused(self):
        for content in [dict(coordinates(), uyear=Array([1])), {'lat':Array([1])}]:
            with self.assertRaises(ValueError):
                subject.inspect_coordinates('synthetic', lambda *a,**k:content)

    def test_shape_change_refused(self):
        content = coordinates();content['lat'].shape=(76,1)
        with self.assertRaisesRegex(ValueError, 'shape'):
            subject.inspect_coordinates('synthetic', lambda *a,**k:content)

    def test_invalid_coordinates_refused(self):
        for name, values in [('lat',[100]*76), ('lon',[float('nan')]*212), ('time_year',[1993]*24)]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                subject.summarize(values,name)

    def test_decreasing_axis_is_explicit_and_preserved(self):
        values=list(reversed(range(76)))
        result=subject.summarize(values,'lat')
        self.assertEqual(result['order'],'decreasing')
        self.assertEqual(result['values'],values)

    def test_period_mismatch_is_retained_without_relabeling(self):
        content=coordinates();content['time_year']=Array(list(range(1992,2016)))
        result=subject.inspect_coordinates('synthetic',lambda *a,**k:content)
        self.assertFalse(result['provider_year_range_matches'])
        self.assertEqual(result['time_year']['minimum'],1992)


if __name__ == '__main__':
    unittest.main()
