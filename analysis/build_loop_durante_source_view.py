"""Native composite fields and separate source clocks; no inferred routes."""
from datetime import datetime,timedelta
import json,math
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from acquire_loop_durante_2026 import ROOT,DIRECTORY,OPERATOR,PROTOCOL,verify,sha,write

VIEW_PROTOCOL='plans/loop-durante-2026-source-view-protocol-v1.md'
VIEW_PROTOCOL_SHA='546deb7b6d26c55afd39f73ceffa7c8202e1b8ba9c336e90d5b40f2bb10e7e80'
GENERATOR='analysis/build_loop_durante_source_view.py'
REPORT='research/loop-durante-2026-source-view.json'
FIGURE='research/loop-durante-2026-source-view-figure.json'
STEM='figures/loop-durante-2026-source-view'


def calendar(v):return datetime.fromordinal(int(v))-timedelta(days=366)+timedelta(days=float(v)%1)


def blocks(values):
    values=np.asarray(values).reshape(-1);result=[];start=None
    def append(end):
        result.append({'first_source_index':start,'last_source_index':end,'source_records':end-start+1,
                       'start_calendar':calendar(values[start]).isoformat(),'end_calendar':calendar(values[end]).isoformat()})
    for i,value in enumerate(values):
        if not np.isfinite(value):
            if start is not None:append(i-1);start=None
            continue
        if start is not None and value-values[i-1]!=1:append(i-1);start=None
        if start is None:start=i
    if start is not None:append(len(values)-1)
    return result


def numbers(values):
    array=np.asarray(values)
    if array.ndim:return [numbers(v) for v in array]
    return float(array) if np.isfinite(array) else None


def build():
    if sha(ROOT/VIEW_PROTOCOL)!=VIEW_PROTOCOL_SHA:raise ValueError('Changed source view protocol')
    receipt,quality,arrays=verify()
    pins={PROTOCOL:sha(ROOT/PROTOCOL),VIEW_PROTOCOL:VIEW_PROTOCOL_SHA,GENERATOR:sha(ROOT/GENERATOR),OPERATOR:sha(ROOT/OPERATOR)}
    for name,entry in receipt['files'].items():pins[(DIRECTORY/name).relative_to(ROOT).as_posix()]=entry['sha256']
    pins[(DIRECTORY/'acquisition.json').relative_to(ROOT).as_posix()]=sha(DIRECTORY/'acquisition.json')
    phases=[]
    for label,suffix,axis,indices in [('Positive','max','CurAxisPositive','inmax_lc'),('Negative','min','CurAxisNegative','inmin_lc')]:
        speed,u,v=[arrays[prefix+suffix] for prefix in ['C','U','V']]
        x,y=arrays['xduf'],arrays['yduf']
        if any(a.shape!=x.shape for a in [y,speed,u,v]):raise ValueError('Changed composite/grid association')
        phases.append({'label':label,'speed_field':'C'+suffix,'eastward_field':'U'+suffix,'northward_field':'V'+suffix,
                       'speed_m_s':numbers(speed),'eastward_m_s':numbers(u),'northward_m_s':numbers(v),
                       'coordinate_field':axis,'unjoined_source_coordinate_points':numbers(arrays[axis]),
                       'axis_selection_indices_field':indices,'axis_selection_indices':quality['source_phase_indices'][indices]['original_indices'],
                       'axis_selection_index_basis':'one_based_MATLAB',
                       'axis_mean_member_support_available':False,'surface_composite_member_support_available':False})
    clocks={name:{'source_serial_days':numbers(arrays[name].reshape(-1)),'daily_blocks':blocks(arrays[name]),
                  'timezone':None,'source_position_index_basis':'zero_based_native_position','nonfinite_source_indices':np.flatnonzero(~np.isfinite(arrays[name].reshape(-1))).tolist()}
            for name in ['tid','tisp','htimef']}
    record={'schema':'osw.loop-durante-2026-source-view.v1','source_doi':'10.5281/zenodo.22652650','source_version':'0',
            'source_data_kind':'author_processed_conditional_composites_not_daily_loop_paths',
            'input_sha256':pins,'longitude':numbers(arrays['xduf']),'latitude':numbers(arrays['yduf']),
            'phases':phases,'clocks':clocks,
            'source_scalar_series':{name:{'source_field':name,'time_field':'tid','source_values':numbers(arrays[name].reshape(-1)),
                'unit_evidence':'Author plotting code multiplies by1e-5 and labels area in1e5km2; values here are unscaled.',
                'physical_enclosure_definition_verified':False,'source_polygon_supplied':False,
                'length_or_width_derived_from_area':False} for name in ['area_loop','AMR_loop']},
            'glyph_stride':4,'source_axes_are_complete_loop_paths':False,
            'source_axis_points_are_connected':False,'current_length_admitted':False,'width_measurement_admitted':False,
            'annual_physical_range_admitted':False,'current_footprints_admitted':False,
            'nonfinite_plot_values':'null; exact native IEEE values remain in the pinned MAT source',
            'clock_dates_are_composite_observation_dates':False,'coordinate_grid_is_effective_observation_resolution':False}
    (ROOT/REPORT).write_bytes((json.dumps(record,separators=(',',':'),allow_nan=False)+'\n').encode())
    return record,arrays


def figure():
    record,arrays=build();plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'osw-loop-durante-source-v1'})
    fig=plt.figure(figsize=(15,10),layout='constrained');fig.get_layout_engine().set(rect=(0,.09,1,.91))
    gs=fig.add_gridspec(2,2,height_ratios=[3,1]);axes=[fig.add_subplot(gs[0,i]) for i in range(2)]
    x,y=arrays['xduf'],arrays['yduf'];aspect=1/math.cos(math.radians(float((np.nanmin(y)+np.nanmax(y))/2)))
    maximum=max(float(np.nanmax(arrays[name])) for name in ['Cmax','Cmin']);cmap=plt.colormaps['viridis'].copy();cmap.set_bad('#ccd2d8')
    sample=(slice(None,None,4),slice(None,None,4))
    for ax,phase,suffix in zip(axes,record['phases'],['max','min']):
        speed,u,v=[arrays[prefix+suffix] for prefix in ['C','U','V']]
        image=ax.pcolormesh(x,y,np.ma.masked_invalid(speed),cmap=cmap,vmin=0,vmax=maximum,shading='nearest',rasterized=True)
        norm=np.hypot(u,v);valid=np.isfinite(u)&np.isfinite(v)&(norm>0)
        east=np.divide(u,norm,out=np.zeros_like(u),where=valid)/np.cos(np.deg2rad(y))
        north=np.divide(v,norm,out=np.zeros_like(v),where=valid)
        ax.quiver(x[sample],y[sample],np.ma.masked_where(~valid,east)[sample],np.ma.masked_where(~valid,north)[sample],
                  angles='xy',scale_units='xy',scale=4,width=.0014,color='white',pivot='mid')
        points=arrays[phase['coordinate_field']];paired=np.isfinite(points).all(axis=1)
        ax.scatter(points[paired,0],points[paired,1],s=4,c='#111',label='Unjoined source-axis points')
        ax.set(xlim=(float(x.min()),float(x.max())),ylim=(float(y.min()),float(y.max())),xlabel='Longitude °E',ylabel='Latitude °N')
        ax.set_aspect(aspect);ax.set_title(phase['label']+' author surface composite\n'+phase['coordinate_field']+': '+str(int(paired.sum()))+' unjoined points',fontsize=11)
        ax.legend(loc='upper left',fontsize=8);ax.grid(alpha=.12)
    fig.colorbar(image,ax=axes,location='bottom',label='Author composite geostrophic speed (m/s); common scale',shrink=.8,pad=.06)
    temporal=fig.add_subplot(gs[1,:]);colors=['#166b84','#c65816','#6c4c9c']
    for row,((name,clock),color) in enumerate(zip(record['clocks'].items(),colors)):
        for block in clock['daily_blocks']:
            lo=mdates.date2num(datetime.fromisoformat(block['start_calendar']));hi=mdates.date2num(datetime.fromisoformat(block['end_calendar']))
            if hi==lo:temporal.plot([lo],[row],'|',color=color,markersize=12)
            else:temporal.broken_barh([(lo,hi-lo)],(row-.15,.3),facecolors=color)
    temporal.set_yticks(range(3),[name+' · '+str(len(clock['source_serial_days']))+' source entries' for name,clock in record['clocks'].items()])
    temporal.set_ylim(-.5,2.5);temporal.invert_yaxis();temporal.xaxis.set_major_locator(mdates.YearLocator(5));temporal.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    temporal.grid(axis='x',alpha=.2);temporal.set_xlabel('Source calendar (timezone unspecified); gaps and missing timestamps are not filled')
    temporal.set_title('Three distinct source clocks · tisp time missing at OSW position3462 (MATLAB index3463)',fontsize=11)
    fig.suptitle('Loop Current archive · author surface composites and source coverage\n'
                 'Full supplied grid and all coordinate points; conditional composites are not dated paths or seasons',fontsize=15)
    fig.text(.5,.055,'Black points are the archived coordinate means, extending south of Yucatan; they do not trace a complete Loop Current. No connecting line or length inferred.\n'
             'Gray = missing source speed, not a coastline. Arrows = mean direction at fixed stride4. Native lon/lat cells, local aspect; no effective-resolution claim.\n'
             'Durante2026, Zenodo10.5281/zenodo.22652650 v0; CMEMS10.48670/moi-00148; Canek v4 Zenodo17887342. Source API license CC BY4.0; source notes retain metadata disagreements.',
             ha='center',va='center',fontsize=8)
    assets={}
    for extension in ['png','svg']:
        path=ROOT/(STEM+'.'+extension);fig.savefig(path,dpi=160,metadata={'Date':None} if extension=='svg' else {})
        if extension=='svg':
            ET.register_namespace('','http://www.w3.org/2000/svg');tree=ET.parse(path);svg=tree.getroot();svg.set('role','img');svg.set('aria-labelledby','loop-source-title loop-source-desc')
            title=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'loop-source-title'});title.text='Durante2026 processed source composites and three distinct source clocks'
            desc=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'loop-source-desc'});desc.text='Two full native-grid surface geostrophic-speed composites with direction-only arrows and all248unjoined source coordinate means each. Supplied coordinate means extend into the Caribbean and are not a complete Loop Current axis. Three separate source clocks preserve11902extended-calendar entries and4111entries each for tid and tisp, including a missing tisp timestamp at zero-based OSW position3462, MATLAB index3463. No clock filling, route length, width, current footprint or annual extrema are inferred. Exact plot inputs and masks are in loop-durante-2026-source-view.json.'
            svg.insert(0,title);svg.insert(1,desc);tree.write(path,encoding='utf8',xml_declaration=True)
        assets[path.relative_to(ROOT).as_posix()]=sha(path)
    plt.close(fig)
    result={'schema':'osw.loop-durante-2026-source-view-figure.v1','generator_file':GENERATOR,'generator_sha256':sha(ROOT/GENERATOR),
            'source_view_file':REPORT,'source_view_sha256':sha(ROOT/REPORT),'figures':assets,
            'current_length_admitted':False,'width_measurement_admitted':False,'source_axes_are_complete_loop_paths':False}
    write(ROOT/FIGURE,result);return result


if __name__=='__main__':print(json.dumps(figure(),indent=2))
