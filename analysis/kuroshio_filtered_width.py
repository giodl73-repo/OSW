"""Bind published filtered-width readings and their derived figure to queries."""
from pathlib import Path
import hashlib,json
from build_kuroshio_filtered_width_series import ROOT,OUTPUT,verify

ID='diagnostic:kuroshio-filtered-width'
FIGURE='research/kuroshio-ecs-filtered-width-time-series-figure.json'

def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def verify_inputs():
 document=verify();figure=json.loads((ROOT/FIGURE).read_bytes())
 if figure['source_file']!=OUTPUT or figure['source_sha256']!=digest(OUTPUT):raise ValueError('Stale filtered-width figure source')
 if figure['samples_are_raw_monthly_means'] or figure['source_uncertainty_inferred'] or figure['physical_edges_rendered'] or figure['annual_extrema_inferred']:
  raise ValueError('Promoted filtered-width figure')
 inputs={**document['input_sha256'],OUTPUT:digest(OUTPUT),FIGURE:digest(FIGURE),
  document['generator_file']:document['generator_sha256'],figure['generator_file']:figure['generator_sha256'],
  Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__).relative_to(ROOT))}
 for asset in figure['figures'].values():inputs[asset['file']]=asset['sha256']
 for path,pin in inputs.items():
  if digest(path)!=pin:raise ValueError('Changed filtered-width input: '+str(path))
 return document,figure,inputs

def record(document):
 return {'id':ID,'label':'Kuroshio filtered regional width curve readings','entity_id':'current:kuroshio','current_id':'kuroshio',
  'status':document['status'],'rank_eligible':False,'source_file':OUTPUT,'source_file_sha256':digest(OUTPUT),
  'source_json':(ROOT/OUTPUT).read_bytes().decode('utf8'),'document':document}
