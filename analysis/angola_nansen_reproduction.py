"""Delivery adapter for the frozen native-section compiler and its field files."""
from angola_nansen_native_sections import ROOT, calculate, encoded


def build():
    report,fields=calculate()
    for path,raw in fields.items():
        if (ROOT/path).read_bytes()!=raw:
            raise ValueError('Changed native Angola field bytes: '+path)
    return report
