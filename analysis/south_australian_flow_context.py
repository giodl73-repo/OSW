"""Compact checked query/map scene for the retained surrounding model field."""
import argparse
import json

import build_south_australian_flow_context as context

ROOT=context.ROOT
FILE='research/south-australian-hycom-2d-flow-context-scene.json'
HELPER='analysis/south_australian_flow_context.py'
ID='diagnostic:south-australian-hycom-2d-flow-context'
FIGURES=['research/south-australian-hycom-2d-source-figure.json','research/south-australian-hycom-2d-flow-context-figure.json']


def build():
    report=json.loads((ROOT/context.OUTPUT).read_bytes())
    if context.build()!=report:raise ValueError('Changed South Australian context corpus')
    receipt,arrays,quality=context.verify()
    if quality['cells_with_time_varying_pair_mask']!=0:raise ValueError('This source scene requires the checked constant paired mask')
    old_sections=json.loads((ROOT/context.ORIGINAL).read_bytes())
    pins={p:context.sha(ROOT/p) for p in [context.OUTPUT,HELPER,context.PROTOCOL,context.GENERATOR,context.ORIGINAL]}
    acquisition=(context.DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix()
    pins[acquisition]=context.SOURCE_ACQUISITION_SHA
    for name,entry in receipt['files'].items():pins[(context.DIRECTORY/name).relative_to(ROOT).as_posix()]=entry['sha256']
    for key in ['protocol','operator','npz_writer']:pins[receipt[key+'_file']]=receipt[key+'_sha256']
    figures=[]
    for path in FIGURES:
        figure=json.loads((ROOT/path).read_bytes());pins[path]=context.sha(ROOT/path)
        pins[figure['generator_file']]=figure['generator_sha256'];pins.update(figure['figures'])
        if figure['current_association_verified'] is not False or figure['width_measurement_admitted'] is not False:
            raise ValueError('Figure promoted source context to physical measurement')
        figures.append(next(p for p in figure['figures'] if p.endswith('.svg')))
    for path,pin in pins.items():
        if context.sha(ROOT/path)!=pin:raise ValueError('Changed South Australian context input: '+path)
    months=[]
    for original in report['months']:
        month={k:v for k,v in original.items() if k!='paired_counts_by_cell'}
        old=old_sections['months'][month['month']-1]['nominal']['boundaries']
        month['original_section_boundaries']=[old['low_coordinate']['coordinate'],old['high_coordinate']['coordinate']]
        u,v,counts,supported=context.monthly_vectors(arrays,month['source_indices'],month['minimum_required_pairs'])
        # Fixed native stride preserves every sampled supported/missing position.
        month['direction_samples']=[[y,x,float(u[y,x]) if supported[y,x] else None,
                                      float(v[y,x]) if supported[y,x] else None,int(counts[y,x])]
                                     for y in range(0,76,4) for x in range(0,51,4)]
        months.append(month)
    return {'schema':'osw.south-australian-flow-context-scene.v1','current_id':'south-australian',
            'entity_id':'current:south-australian','status':report['status'],'year':2012,'depth_m':100,
            'longitude':report['longitude'],'latitude':report['latitude'],'months':months,
            'source_paired_counts_by_cell':quality['paired_counts_by_cell'],
            'source_dates':366,'valid_paired_vectors':quality['paired_positions'],'original_scalar_overlap':55632,
            'raw_context_file':context.OUTPUT,'raw_context_sha256':pins[context.OUTPUT],
            'source_figure':figures[0],'context_figure':figures[1],'input_sha256':pins,
            'direction_sample_columns':['latitude_index','longitude_index','eastward_m_s','northward_m_s','paired_days'],
            'glyph_stride':4,'fractions':[.4,.5,.6],'adjacency':report['adjacency'],
            'scope_note':report['scope_note'],'current_association_verified':False,
            'width_measurement_admitted':False,'annual_range_admitted':False,'width_rank_eligible':False,
            'whole_current_width_km':None,'annual_width_range_km':None,'geographic_current_edges':None}


def verify_inputs():
    stored=json.loads((ROOT/FILE).read_bytes())
    if stored!=build():raise ValueError('Changed South Australian scene')
    return stored,{**stored['input_sha256'],FILE:context.sha(ROOT/FILE)}


def record(doc):
    return {'id':ID,'label':'South Australian monthly model-grid context; width unresolved',
            'entity_id':'current:south-australian','current_id':'south-australian','status':doc['status'],
            'rank_eligible':False,'source_file':FILE,'source_file_sha256':context.sha(ROOT/FILE),
            'source_json':(ROOT/FILE).read_bytes().decode('utf8'),'document':doc}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:doc,_=verify_inputs()
    else:
        doc=build();(ROOT/FILE).write_bytes((json.dumps(doc,separators=(',',':'),allow_nan=False)+'\n').encode())
    print(json.dumps({'months':len(doc['months']),'bytes':(ROOT/FILE).stat().st_size,'pins':len(doc['input_sha256'])}))
