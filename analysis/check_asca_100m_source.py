"""Verify exact ASCA source byte subsets; do not infer current boundaries."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'research/source-data/asca-2016-2018-100m'
ACQUISITION_SHA = '811666af518d1196a5b8a5e6dfee546f9a6cedcecca7cb046ec8585c3a89c828'
FIELDS = ('temp', 'sal', 'v', 'U')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(directory=DIRECTORY):
    directory = Path(directory)
    raw = (directory / 'acquisition.json').read_bytes()
    if digest(raw) != ACQUISITION_SHA:
        raise ValueError('Changed frozen ASCA subset acquisition')
    receipt = json.loads(raw)
    for item in [receipt['header'], receipt['provider_record']]:
        if digest((directory / item['file']).read_bytes()) != item['sha256']:
            raise ValueError('Changed ASCA header, coordinates or provider metadata')
    fields = {name: [None] * 931 for name in FIELDS}
    seen = set()
    for group in receipt['groups']:
        raw = (directory / 'raw-ranges' / group['file']).read_bytes()
        if len(raw) != group['bytes'] or digest(raw) != group['sha256']:
            raise ValueError('Changed retained ASCA HTTP response')
        expected = {(row['start'], row['end']): row for row in group['ranges']}
        pos = 0
        while True:
            match = re.search(rb'Content-Range: bytes (\d+)-(\d+)/(\d+)\r?\n\r?\n', raw[pos:])
            if match is None:
                break
            low, high, total = map(int, match.groups())
            if total != receipt['provider_file_bytes'] or (low, high) not in expected:
                raise ValueError('Unrequested ASCA source range')
            row = expected.pop((low, high))
            key = (row['variable'], row['time_index'])
            if key in seen or high - low + 1 != 2404:
                raise ValueError('Repeated or truncated ASCA profile')
            seen.add(key)
            first = pos + match.end()
            last = first + high - low + 1
            fields[key[0]][key[1]] = raw[first:last]
            pos = last
        if expected or b'EOSMULTIPARTBOUNDARY' not in raw[pos:]:
            raise ValueError('Incomplete ASCA multipart response')
    if len(seen) != 931 * 4:
        raise ValueError('Incomplete ASCA field/time coverage')
    arrays = {}
    for name, rows in fields.items():
        raw = b''.join(rows)
        if digest(raw) != receipt['source_bound_arrays'][name]['source_float_bytes_sha256']:
            raise ValueError('Changed original ASCA float bytes or order')
        arrays[name] = np.frombuffer(raw, dtype='>f4').reshape(931, 601)
        if np.isinf(arrays[name]).any():
            raise ValueError('Unexpected infinite source value')
    header = (directory / receipt['header']['file']).read_bytes()
    # Exact offsets in the pinned NETCDF3_CLASSIC header. Original big-endian
    # coordinates and float32 epoch seconds remain unchanged, including precision.
    coordinates = {name: np.frombuffer(header[low:high], dtype='>f4')
                   for name, low, high in [('dist',3980,6384),('z',6384,7288),('time',7288,11012)]}
    if coordinates['z'][5] != 100 or not np.array_equal(coordinates['dist'], np.arange(601)*500):
        raise ValueError('Changed ASCA depth selection or distance axis')
    return receipt, coordinates, arrays


def quality(directory=DIRECTORY):
    from netCDF4 import num2date
    receipt, coordinates, arrays = load(directory)
    times = coordinates['time'].astype('float64')
    units = 'seconds since 1970-01-01 00:00:00'
    dates = num2date(times, units)
    nominal = times[0] + np.arange(len(times)) * 72000
    nominal_dates = num2date(nominal, units)
    bins = {}
    for date in dates:
        key = f'{date.year:04d}-{date.month:02d}'
        bins[key] = bins.get(key, 0) + 1
    paired = np.isfinite(arrays['v']) & np.isfinite(arrays['U'])
    return {'times': len(times), 'distance_cells': len(coordinates['dist']), 'depth_m': 100,
            'scalar_values': sum(a.size for a in arrays.values()),
            'finite_values': {k: int(np.isfinite(a).sum()) for k,a in arrays.items()},
            'paired_vector_positions': int(paired.sum()),
            'unavailable_paired_vector_positions': int((~paired).sum()),
            'first_time_utc': str(dates[0]), 'last_time_utc': str(dates[-1]),
            'source_time_step_seconds': sorted(set(np.diff(times).tolist())),
            'deviation_from_nominal_twenty_hour_clock_seconds': sorted(set((times-nominal).tolist())),
            'calendar_bin_changes_under_nominal_clock': sum((a.year,a.month)!=(b.year,b.month)
                                                          for a,b in zip(dates,nominal_dates)),
            'source_timestamps_modified': False, 'month_counts': bins,
            'complete_file_checksum_verified': False, 'width_measurement_admitted': False}


def plot(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as dates
    from datetime import datetime, timezone
    _, coordinates, arrays = load()
    time = dates.date2num([datetime.fromtimestamp(float(t),timezone.utc) for t in coordinates['time']])
    distance = coordinates['dist']/1000
    fig, axes = plt.subplots(1,4,figsize=(16,8),sharey=True)
    fig.subplots_adjust(left=.08,right=.98,bottom=.22,top=.78,wspace=.12)
    specs = [('v','Across array velocity\nSouthwest negative','RdBu_r',-2.5,2.5,'m/s'),
             ('U','Along array velocity\nSoutheast positive','RdBu_r',-1.5,1.5,'m/s'),
             ('temp','Temperature','inferno',11,25,'degrees C'),
             ('sal','Practical salinity','viridis',34.8,35.7,'PSU')]
    for ax,(name,title,palette,low,high,unit) in zip(axes,specs):
        cmap=plt.get_cmap(palette).copy();cmap.set_bad('#c9cfd2')
        im=ax.pcolormesh(distance,time,np.ma.masked_invalid(arrays[name]),shading='nearest',
                         cmap=cmap,vmin=low,vmax=high,rasterized=True)
        ax.set_title(title,fontsize=12);ax.set_xlabel('Distance along array (km)')
        ax.set_xlim(0,300);ax.set_xticks([0,100,200,300])
        fig.colorbar(im,ax=ax,orientation='horizontal',pad=.11,shrink=.93,label=unit)
        ax.yaxis.set_major_locator(dates.MonthLocator(interval=3))
        ax.yaxis.set_major_formatter(dates.DateFormatter('%b %Y'))
    axes[0].set_ylabel('Source time (UTC)')
    fig.suptitle('Agulhas at 100 m · 931 source cross sections',fontsize=19)
    fig.text(.08,.89,'19 April 2016–3 June 2018 · source interpolation · gray marks unavailable values',fontsize=12)
    fig.text(.08,.07,'Source: Beal Lab / ASCA version 2 · DOI 10.5281/zenodo.20515068 · CC BY 4.0\n'
             '500 m output spacing is not independent instrument resolution. Along-array velocity is unavailable over much of the offshore section.\n'
             'Exact source byte subsets reviewed; complete 2 GB file checksum unverified. No current-width boundaries or seasonal extrema inferred.',
             fontsize=11,linespacing=1.6)
    fig.savefig(output,dpi=130,facecolor='white');plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure',type=Path)
    args=parser.parse_args()
    print(json.dumps(quality(),indent=2))
    if args.figure:
        plot(args.figure)
