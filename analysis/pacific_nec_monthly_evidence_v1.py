"""Lossless metadata compaction; never calculates or changes measurements."""
import copy


def compact(report, original_sha256):
    body=copy.deepcopy(report);profiles={}
    for row in body['section_spans']:
        key=str(row['month'])+':'+str(row['longitude_east'])
        profile=row.pop('profile')
        if key in profiles and profiles[key]!=profile:
            raise ValueError('Threshold cases contain different source profiles')
        profiles[key]=profile;row['profile_ref_v1']=key
    return {'schema':'osw.pacific-nec-monthly-evidence.v1',
            'original_report_sha256':original_sha256,
            'compaction':'Repeated identical section profiles stored once; no measurement values changed.',
            'report':body,'section_profiles':profiles}


def expand(evidence):
    if evidence['schema']!='osw.pacific-nec-monthly-evidence.v1':raise ValueError('Unknown evidence format')
    result=copy.deepcopy(evidence['report']);used=set()
    for row in result['section_spans']:
        key=row.pop('profile_ref_v1')
        if key!=str(row['month'])+':'+str(row['longitude_east']):raise ValueError('Wrong profile association')
        row['profile']=copy.deepcopy(evidence['section_profiles'][key]);used.add(key)
    if used!=set(evidence['section_profiles']):raise ValueError('Unreferenced source profiles')
    return result
