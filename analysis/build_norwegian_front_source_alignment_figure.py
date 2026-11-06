"""Plot source positions and alignment without inferring current boundaries."""
import json
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]
def main():
    doc=json.loads((ROOT/'research/norwegian-front-glider-source-alignment.json').read_bytes())
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'osw-norwegian-source-alignment-v1'})
    fig,axes=plt.subplots(1,3,figsize=(15,5));projection=Transformer.from_crs(4326,3413,always_xy=True)
    for mission,color in zip(doc['missions'],['#087a91','#ba6716']):
        positions=mission['profile_positions'];x,y=projection.transform([p['longitude'] for p in positions],[p['latitude'] for p in positions])
        axes[0].scatter([v/1000 for v in x],[v/1000 for v in y],s=3,color=color,label=mission['file'].split('_')[1])
        records=mission['coordinate_comparisons'];axes[1].scatter([datetime.fromisoformat(r['time']) for r in records],[r['offset_km']*1000 for r in records],s=3,color=color)
        records=[r for r in mission['DAC_records'] if r['vector_magnitude_m_s'] is not None];axes[2].scatter([datetime.fromisoformat(r['time']) for r in records],[r['vector_magnitude_m_s'] for r in records],s=3,color=color)
    axes[0].set(title='Observed profile positions',xlabel='EPSG:3413 easting (km)',ylabel='EPSG:3413 northing (km)');axes[0].set_aspect('equal');axes[0].legend()
    axes[1].set(title='Internal position alignment',ylabel='DAC vs interpolated profile position (m)')
    axes[2].set(title='Recorded depth-average current magnitude',ylabel='Vector magnitude (m/s)')
    for ax in axes[1:]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'));ax.tick_params(axis='x',rotation=30)
        cutoff=datetime.fromisoformat('2017-08-01T00:00:00+00:00')
        ax.axvline(cutoff,color='#657680',linestyle='--',linewidth=1)
        ax.text(cutoff,.98,' Paper ends Jul 2017',transform=ax.get_xaxis_transform(),ha='left',va='top',fontsize=8)
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Norwegian front-current source investigation / two PROVOLO glider missions')
    fig.text(.025,.02,'Bosse & Fer / University of Bergen / NMDC, CC BY 4.0. Source alignment only; no current width, axis or occupied footprint.\nInternal agreement does not verify the corrected paper methodology. DAC_U metadata conflict retained; direction not validated.',fontsize=10)
    fig.tight_layout(rect=(0,.12,1,.94))
    path=ROOT/'figures/norwegian-front-glider-source-alignment.svg';fig.savefig(path,metadata={'Date':None});fig.savefig(ROOT/'figures/norwegian-front-glider-source-alignment-review.png',dpi=120)
    svg=path.read_text(encoding='utf-8').replace('<svg ','<svg role="img" aria-labelledby="source-audit-title source-audit-desc" ',1);i=svg.index('>',svg.index('<svg '))+1
    svg=svg[:i]+'\n<title id="source-audit-title">PROVOLO source coordinates and current magnitudes</title><desc id="source-audit-desc">Two mission tracks, internal coordinate offsets and recorded depth-average current magnitudes. Positions are glider samples, not current boundaries. Exact values are retained in the source alignment JSON.</desc>'+svg[i:]
    path.write_bytes(('\n'.join(line.rstrip() for line in svg.splitlines())+'\n').encode());plt.close(fig)
if __name__=='__main__':main()
