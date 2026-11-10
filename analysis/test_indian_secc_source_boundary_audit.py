"""Check censoring semantics separately from reported threshold crossing."""
from decimal import Decimal

from indian_secc_source_boundary_audit import outside_sides, threshold_relation


def test_corner_and_boundary_equality():
    bounds = dict(west=75, east=85, south=-12, north=0)
    assert outside_sides([0, 75, 0], bounds) == []
    assert outside_sides([0, 74.9, 0.1], bounds) == ['west', 'north']
    assert outside_sides(None, bounds) == []


def test_serialized_decimal_threshold_does_not_add_float_roundoff():
    row = [None] * 6
    row[5] = 0.3
    assert threshold_relation(row, Decimal('0.6') * Decimal('0.5')) == 'equal'
    assert threshold_relation(row, '0.30000000000000000001') == 'below'
    assert threshold_relation(row, '0.29999999999999999999') == 'above'


def test_missing_values_are_not_below_threshold():
    assert threshold_relation(None, '0.3') == 'unavailable'
    assert threshold_relation([None] * 6, '0.3') == 'unavailable'
    assert threshold_relation([0] * 6, None) == 'unavailable'
