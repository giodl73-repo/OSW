"""Geographic candidate paths and normal sections with all failed seeds visible."""
import calendar
import json
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import numpy as np
from indian_secc_local_normals import ROOT, REPORT, FIGURE, MANIFEST, SOURCE, build, encoded, digest

OPERATOR='analysis/build_indian_secc_local_normal_figure.py'
ALT='Twelve 2013 monthly maps of local Indian SECC candidate paths, source eastward velocities, original seeds and paired velocity-normal diagnostic spans. All five station checks pass in only one 10 km case and no seed passes at both 5 km and 10 km. Failed or partial candidates remain dashed; there is no admitted named-current axis or width.'


def main():
    d=json.loads((ROOT/REPORT).read_bytes())
    if encoded(d)!=encoded(build()):raise ValueError('Changed local normal report')
    source=json.loads((ROOT/SOURCE).read_bytes());lon,lat=np.meshgrid(source['longitude_degrees_east'],source['latitude_degrees_north'])
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-secc-local-normals-v1'})
    fig,axes=plt.subplots(4,3,figsize=(17,21));fig.subplots_adjust(left=.05,right=.98,top=.89,bottom=.16,hspace=.38,wspace=.22)
    fig.suptitle('Indian SECC investigation · local velocity-normal sections',x=.05,y=.98,ha='left',fontsize=19)
    fig.text(.05,.956,'2013 OSCAR monthly means · nominal 15 m · five station checks over a 200 km mean-field candidate segment',fontsize=12)
    fig.text(.05,.933,f"144 attempts · {d['counts']['central_paired_half_peak_sections']} central paired diagnostic spans · no seed passes all five checks at both 5 km and 10 km sampling",fontsize=12)
    colors={'indian-secc-80p333e':'#111111','indian-secc-80p667e':'#006335'}
    halo=[effects.Stroke(linewidth=3,foreground='white'),effects.Normal()]
    for ax,frame in zip(axes.flat,source['months']):
        ax.set_facecolor('#dddddd')
        image=ax.pcolormesh(lon,lat,np.array(frame['eastward_m_s'],dtype=float),cmap='RdBu_r',norm=Normalize(-.4,.4),shading='nearest',rasterized=True,alpha=.7)
        ax.axhspan(2,3,color='#dddddd');ax.axhspan(-11,-10,color='#dddddd');ax.axhline(0,color='#555555',linewidth=.6,linestyle=':')
        rows=[c for c in d['cases'] if c['month']==frame['month'] and c['primary_seed'] and c['normal_sample_step_km']==5]
        paired=0
        for c in rows:
            color=colors[c['section_id']]
            seed=c.get('original_seed_lon_lat')
            if seed:ax.plot(*seed,'o',color=color,markersize=4,markeredgecolor='white',markeredgewidth=.7)
            for path in c['paths']:
                points=np.array(path['vertices_lon_lat'])
                ax.plot(points[:,0],points[:,1],color=color,linewidth=1.3,linestyle='-' if c['all_five_local_axis_checks_pass'] else '--',path_effects=halo)
            for station in c['stations']:
                case=station['threshold_cases'][1];point=station['origin_lon_lat']
                if case['status']=='paired_sampled_edges':
                    paired+=1;ends=[e['point'] for e in case['edges'].values()]
                    ax.plot([p[0] for p in ends],[p[1] for p in ends],color=color,linewidth=1.0,
                            linestyle='-' if station['local_candidate_axis_check'] else ':',path_effects=halo)
                    ax.scatter([p[0] for p in ends],[p[1] for p in ends],s=7,facecolors='white',edgecolors=color,linewidths=.7,zorder=5)
                else:ax.plot(*point,'x',color=color,markersize=5)
            if c['refined_seed_lon_lat']:ax.plot(*c['refined_seed_lon_lat'],'^',color=color,markersize=4,markeredgecolor='white',markeredgewidth=.6)
        ax.set_xlim(74,87);ax.set_ylim(-11,3);ax.set_aspect('equal')
        ax.set_xticks([75,80,85]);ax.set_yticks([-10,-6,-2,2]);ax.tick_params(labelsize=8)
        ax.set_title(f"{calendar.month_name[frame['month']]} · {paired} paired station spans at 5 km",loc='left',fontsize=10)
    cax=fig.add_axes([.27,.105,.46,.012]);fig.colorbar(image,cax=cax,orientation='horizontal',extend='both')
    fig.text(.5,.129,'Monthly mean eastward velocity (m/s) · shared scale; values outside ±0.4 clipped',ha='center',fontsize=11)
    handles=[Line2D([],[],color=c,label=name) for c,name in [('#111111','80⅓E seed'),('#006335','80⅔E seed')]]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.073),ncol=2,frameon=False,fontsize=11)
    fig.text(.05,.066,'Circles: original seeds; triangles: refined seeds. Dashed paths: failed/partial five-station candidates. Bars: paired 50%-peak diagnostic spans.',fontsize=10)
    fig.text(.05,.048,'Solid/dotted bars: local check passes/fails; crosses: no paired span. Gray: outside source support. Maps show 5 km cases; all 5/10 km cases remain in data.',fontsize=10)
    fig.text(.05,.030,'Only one 10 km November case passes all five checks; it fails at 5 km. No robust axis, whole-current width/length or physical seasonal range is admitted.',fontsize=10)
    fig.text(.05,.012,'Equirectangular degree view. OSCAR 2017.0 / Earth & Space Research / NOAA OceanWatch. Fine sampling does not improve the native one-third-degree resolution.',fontsize=9)
    assets={}
    for suffix in ['svg','png']:
        path=FIGURE[:-3]+suffix;metadata={'Date':None,'Creator':'OSW'} if suffix=='svg' else {'Software':'OSW'}
        fig.savefig(ROOT/path,dpi=140,facecolor='white',metadata=metadata)
        if suffix=='svg':
            # Standalone SVG has its own accessible name; query tables supply the data equivalent.
            raw=(ROOT/path).read_text(encoding='utf-8');position=raw.index('>',raw.index('<svg'))+1
            import html
            raw=raw[:position]+'\n<title id="secc-normal-title">Indian SECC local velocity-normal diagnostics</title>\n<desc id="secc-normal-desc">'+html.escape(ALT)+'</desc>'+raw[position:]
            raw=raw.replace('<svg ','<svg role="img" aria-labelledby="secc-normal-title secc-normal-desc" ',1)
            (ROOT/path).write_bytes(raw.encode());ET.parse(ROOT/path)
        assets[suffix]={'file':path,'sha256':digest(path),'bytes':(ROOT/path).stat().st_size}
    plt.close(fig)
    manifest={'schema':'osw.indian-secc-local-axis-normal-figure.v1','source_file':REPORT,'source_sha256':digest(REPORT),
              'generator_file':OPERATOR,'generator_sha256':digest(OPERATOR),'figures':assets,'alt':ALT,
              'current_geometry_admitted':False,'source_image_redistributed':False}
    (ROOT/MANIFEST).write_bytes((json.dumps(manifest,indent=2)+'\n').encode());print(json.dumps(assets))


if __name__=='__main__':main()
