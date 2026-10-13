"""Pinned original-source ring radii; source disagreements never become ranges."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH='research/agulhas-guerra-2022-ring-radius-scope-audit.json'
SOURCE='research/source-data/guerra-agulhas-2022/journal-article.pdf'
SHA='150734e346134f4a252d7f76b46229a9f30dfd1e5bdaa2f53f039dcaae84dff1'
ACQ='research/source-data/guerra-agulhas-2022/acquisition.json'
PROTOCOL='plans/agulhas-ring-radius-protocol-v1.md'
GENERATOR='analysis/build_agulhas_ring_radius_audit.py'
URL='https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.958733/full'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def claim(value,period,locator,panel=None):
    return {'value_km':value,'reported_period':period,'source_locator':locator,'figure_panel_time_label':panel}

def build():
    if (ROOT/SOURCE).stat().st_size!=16034257 or digest(SOURCE)!=SHA:
        raise ValueError('Changed original Agulhas radius source')
    acquisition=json.loads((ROOT/ACQ).read_bytes())
    if acquisition['sha256']!=SHA or acquisition['bytes']!=16034257:
        raise ValueError('Changed Agulhas radius acquisition')
    entities={}
    slots={
        'ana-2004': [('may-2005','May 2005','2005-05',67,False,[claim(67,'25-26 May 2005 XBT context','Figure 8 caption, printed p11; section 3.1.1, printed p10','25-26 / May / 2005')])],
        'eliza-2007': [
            ('feb-2009','Feb 2009','2009-02',None,False,[claim(88,'Feb/09','Table 1, printed p16, Eliza Feb/09 L column'),claim(93,'February 2009','Figure 10 caption, printed p12, older-to-younger ordering','14-Feb-2009')]),
            ('jul-2009','Jul 2009','2009-07',95,False,[claim(95,'Jul/09','Table 1, printed p16, Eliza Jul/09 L column'),claim(95,'July 2009','Figure 10 caption, printed p12, middle section','20-Jul-2009')]),
            ('january-section','Jan 2010 / 2019',None,None,True,[claim(93,'Jan/10','Table 1, printed p16, Eliza Jan/10 L column'),claim(88,'January 2019','Figure 10 caption, printed p12, younger section','31-Jan-2010')]),
        ],
        'jeannette-2012': [
            ('may-2013','May 2013','2013-05',74,False,[claim(74,'May/13','Table 1, printed p16, Jeannette May/13 L column'),claim(74,'May/2013','Figure 13 caption, printed p14, Cape Basin section','25-May-2013')]),
            ('nov-2015','Nov 2015','2015-11',72,False,[claim(72,'Nov/15','Table 1, printed p16, Jeannette Nov/15 L column'),claim(72,'Nov/2015','Figure 13 caption, printed p14, western basin section','29-Nov-2015')]),
        ],
    }
    for owner,sections in slots.items():
        name='Agulhas Ring '+owner.split('-')[0].title()
        rows=[]
        for key,label,month,value,date_conflict,claims in sections:
            rows.append({'id':owner+'-'+key+'-radius','entity_id':'eddy:geography:'+owner,'name':name,
                'metric':'author_reported_altimetric_area_equivalent_radius','value_km':value,
                'period_label':label,'period_month':month,'period_precision':'source_section_month' if month else 'unresolved_source_year_conflict',
                'source_claims':claims,'radius_conflict':len({c['value_km'] for c in claims})>1,'date_conflict':date_conflict,
                'conflict_resolution':None,'definition':'Source-described area-equivalent circle radius from altimetry; L is the ring radius in the two-layer diagnostic model. Not a mapped occupied perimeter.',
                'layer':'Altimetric surface geometry; no full-depth radius layer or occupied volume inferred.',
                'observation_date':None,'observed_period':None,'reported_uncertainty_km':None,'radius_range_km':None,'geometry':None,
                'annual_extrema_eligible':False,'seasonal_playback_eligible':False,'footprint_inference_eligible':False,
                'diameter_inference_eligible':False,'area_inference_eligible':False,'rank_eligible':False,
                'evidence_kind':'published_altimetric_radius_source_claims_not_canonical','source_url':URL})
        entities[owner]={'entity_id':'eddy:geography:'+owner,'name':name,'measurements':rows,'closed_footprint':None,'annual_radius_range_km':None}
    return {'schema':'osw.agulhas-ring-radius-scope-audit.v1','as_of':'2026-10-08','status':'editorial_original_extraction_scientific_review_pending',
        'source_document_file':SOURCE,'source_document_bytes':16034257,'source_document_sha256':SHA,
        'acquisition_file':ACQ,'acquisition_sha256':digest(ACQ),'protocol_file':PROTOCOL,'protocol_sha256':digest(PROTOCOL),
        'generator_file':GENERATOR,'generator_sha256':digest(GENERATOR),'source_url':URL,'source_doi':'10.3389/fmars.2022.958733',
        'source_citation':'Guerra, Mill and Paiva (2022), Observing the spread of Agulhas Leakage into the Western South Atlantic by tracking mode waters within ocean rings, Frontiers in Marine Science 9:958733.',
        'source_access':'Original publisher PDF retained unchanged; methods, captions, panels and Table 1 reviewed; printed pages 11, 12, 14 and 16 visually inspected.',
        'source_license':'CC BY, stated on printed p1','method_locator':'Sections 2.1 and 2.4; Table 1 caption and discussion on printed p16.',
        'method_limit':'Source-described maximum radial velocity terminology retained. XBT sections and thermocline fitting errors do not supply radius uncertainty or contour coordinates.',
        'date_conflict_note':'Figure 10 caption says January 2019; Table 1, section 3.1.2 and panel label support January 2010. Preserve the disagreement without inventing a corrected measurement date.',
        'radius_conflict_note':'Figure 10 older-to-younger radii 93/95/88 km conflict with Table 1 February/July/January radii 88/95/93 km. No midpoint, range or preferred value selected for the first and last slots.',
        'counts':{'entities':3,'section_slots':6,'source_claims':11,'slots_with_consistent_radius':4,'slots_with_radius_conflict':2,'slots_with_date_conflict':1},
        'entities':entities,'nasa_individual_identity_claim':False,
        'remaining_gates':['Resolve original caption/table conflicts before a single radius/date for Eliza February and January slots.','Recover dated contour coordinates and boundary convention before occupied footprint or state intersection.','Obtain compatible repeats before annual extrema or seasons; independent scientific and canonical admission.']}

def validate(doc,geography=None):
    if doc!=build():raise ValueError('Agulhas radius source or unresolved scope mismatch')
    if geography is not None:
        for owner,evidence in doc['entities'].items():
            row=next(r for r in geography['entries'] if r['id']==owner)
            if row.get('published_ring_radius_evidence')!=evidence['measurements'] or row.get('ring_radius_audit_file')!=PATH or row.get('ring_radius_audit_sha256')!=digest(PATH):
                raise ValueError('Agulhas geography radius evidence differs from source audit')

if __name__=='__main__':
    (ROOT/PATH).write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Built 6 ring-radius source slots for 3 named rings; 2 unresolved radii')
