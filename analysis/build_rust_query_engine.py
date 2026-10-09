"""Compile the same pinned Rust engine for local CLI and browser WASM."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='rust/osw-query/Cargo.toml'

def main():
    for args in [['cargo','fmt','--manifest-path',MANIFEST],
                 ['cargo','test','--offline','--locked','--manifest-path',MANIFEST],
                 ['cargo','build','--offline','--locked','--manifest-path',MANIFEST],
                 ['cargo','build','--offline','--locked','--release','--target','wasm32-unknown-unknown','--lib','--manifest-path',MANIFEST]]:
        subprocess.run(args,cwd=ROOT,check=True)
    target=ROOT/'almanac/query-engine.wasm'
    shutil.copyfile(ROOT/'rust/osw-query/target/wasm32-unknown-unknown/release/osw_query.wasm',target)
    paths=['rust/osw-query/Cargo.toml','rust/osw-query/Cargo.lock','rust/osw-query/src/lib.rs','rust/osw-query/src/map.rs','rust/osw-query/src/spatial.rs','rust/osw-query/src/workspace.rs','rust/osw-query/src/rebase.rs','rust/osw-query/src/main.rs',
           'rust/osw-query/src/svg.rs','rust/osw-query/src/temporal.rs','rust/osw-query/src/seasonal.rs','rust/osw-query/src/samples.rs','rust/osw-query/src/charts.rs','rust/osw-query/src/planning.rs','rust/osw-query/src/loop_diagnostics.rs','rust/osw-query/src/network.rs','rust/osw-query/src/taxonomy.rs','figures/ocean-motion-dashboard-ground.svg','almanac/query-engine.wasm','almanac/query-data.json']
    paths.append('rust/osw-query/src/dashboard.rs')
    paths.append('rust/osw-query/src/dashboard_map.rs')
    paths.append('rust/osw-query/src/dashboard_beck.rs')
    paths.append('rust/osw-query/src/seasons_data.rs')
    paths.append('rust/osw-query/src/object_view.rs')
    paths.append('rust/osw-query/src/eddy_recurrence.rs')
    paths.append('rust/osw-query/src/object_plot.rs')
    paths.append('rust/osw-query/src/atlas_data.rs')
    paths.append('rust/osw-query/src/atlantic_euc_sections.rs')
    paths.append('rust/osw-query/src/proposed_widths.rs')
    paths.append('rust/osw-query/src/stream_tube_widths.rs')
    paths.append('rust/osw-query/src/abstract_regional_widths.rs')
    paths.append('rust/osw-query/src/astrid_scales.rs')
    paths.append('rust/osw-query/src/ring_radii.rs')
    paths.append('rust/osw-query/src/somali_width.rs')
    paths.append('rust/osw-query/src/guinea_width.rs')
    paths.append('rust/osw-query/src/original_regional_widths.rs')
    paths.append('rust/osw-query/src/observed_sections.rs')
    paths.append('rust/osw-query/src/cartography.rs')
    paths.append('rust/osw-query/src/norkyst_data.rs')
    paths.append('rust/osw-query/src/movies.rs')
    paths.append('rust/osw-query/src/model_sections.rs')
    paths.append('rust/osw-query/src/loop_recorded.rs')
    paths.append('rust/osw-query/src/index_bifurcation.rs')
    paths.extend(['rust/osw-query/src/index_store.rs','rust/osw-query/src/index_noaa.rs','rust/osw-query/src/index_support.rs','rust/osw-query/src/index_map.rs','almanac/index-catalog.json','almanac/index-data.json.gz'])
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    rust=subprocess.check_output(['rustc','--version'],text=True).strip()
    (ROOT/'almanac/query-engine.manifest.json').write_text(json.dumps({'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1',
        'abi_version':1,'rustc':rust,'sha256':hashes},indent=2)+'\n',encoding='utf-8')
    print('Built WASM query engine:',target.stat().st_size,'bytes; bundle:',(ROOT/'almanac/query-data.json').stat().st_size,'bytes')

if __name__=='__main__':main()
