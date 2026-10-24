from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from xml.etree import ElementTree as ET

matplotlib.rcParams['svg.hashsalt']='osw-indian-eof-feasibility-v1'

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
data=json.loads((ROOT/'research/indian-secc-eof-classification-feasibility.json').read_bytes())
fits=[f for f in data['fits'] if f['domain']==[-8,6]]
fig,axes=plt.subplots(2,3,figsize=(13,7.8),layout='constrained')
colors=['#007b83','#b74d14'];styles=['-','--']
bands=[(-6,-2.5,'#f4dba7'),(-2.5,3,'#cce5ed'),(3,5.5,'#e1d1ec')]
for mode in range(3):
 ax=axes[0,mode]
 for lo,hi,color in bands:ax.axvspan(lo,hi,color=color,alpha=.55,zorder=0)
 ax.axvspan(4.5,6,facecolor='#eeeeee',edgecolor='#999999',hatch='///',alpha=.7,zorder=.5)
 ax.axhline(0,color='#687780',linewidth=.7)
 for i,fit in enumerate(fits):
  item=fit['modes'][mode]
  ax.plot(fit['latitude_degrees'],item['spatial_loading'],color=colors[i],linestyle=styles[i],label=f"{fit['longitude']:.3f} E ({100*item['variance_fraction']:.1f}%)")
 edge=any(f['modes'][mode]['absolute_peak_at_retained_domain_edge'] for f in fits)
 ax.set(title=f'Mode {mode+1}: spatial loading'+(' (edge peak)' if edge else ''),xlabel='Latitude (degrees north)',ylabel='Unit-norm loading',xlim=(-8,6))
 ax.legend(fontsize=8,loc='best');ax.grid(alpha=.2)
 ax=axes[1,mode]
 for i,fit in enumerate(fits):
  item=fit['modes'][mode]
  ax.plot(range(1,13),item['monthly_pc_climatology_m_s'],color=colors[i],linestyle=styles[i],marker='o',markersize=3,
          label=f"annual {100*item['annual_harmonic_fraction']:.0f}% / semiannual {100*item['semiannual_harmonic_fraction']:.0f}%")
 ax.axhline(0,color='#687780',linewidth=.7)
 ax.set(title=f'Mode {mode+1}: monthly PC climatology',xlabel='Calendar month',ylabel='PC coefficient (m/s)',xticks=range(1,13))
 ax.legend(fontsize=8,loc='best');ax.grid(alpha=.2)
fig.suptitle('Indian near-equatorial current classification experiment\nOSCAR 2017.0 / 1995-2016 / two native columns, analyzed separately',fontsize=14)
fig.supxlabel('Bands left to right: SECC / Wyrtki jets / monsoon circulation frequency context; not current edges.\nHatching: incomplete northern support, not land. PC coefficients are not local current speeds.\nNo width or confirmed current identity admitted.',fontsize=10)
fig.savefig(OUT/'indian-secc-eof-feasibility.png',dpi=150)
target=OUT/'indian-secc-eof-feasibility.svg'
fig.savefig(target,metadata={'Date':None})
# Retain an explicit alternative independent of color and rendered text paths.
ET.register_namespace('','http://www.w3.org/2000/svg')
tree=ET.parse(target);root=tree.getroot()
root.set('role','img');root.set('aria-labelledby','eof-title eof-description')
title=ET.Element('{http://www.w3.org/2000/svg}title',id='eof-title')
title.text='Indian near-equatorial statistical current classification experiment'
description=ET.Element('{http://www.w3.org/2000/svg}desc',id='eof-description')
description.text=('Two native OSCAR columns over1995-2016 have three similar leading statistical patterns: '
    'an equatorial semiannual pattern, a northern annual pattern peaking at the retained data edge, '
    'and a southern annual pattern near5S. Solid and dashed lines identify the two columns. '
    'Northern hatching marks incomplete observations, not land. Colored latitude bands are source '
    'classification context, not physical current boundaries. Principal component coefficients are '
    'not local current speeds. Neither current identity nor physical width is admitted. '
    'Numerical values, fifteen fit comparisons and missing support are provided in the companion JSON and plan.')
root.insert(0,title);root.insert(1,description)
tree.write(target,encoding='utf-8',xml_declaration=True)
target.write_bytes(b'\n'.join(line.rstrip() for line in target.read_bytes().splitlines())+b'\n')
