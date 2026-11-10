"""Verify retained graph trace pixels against the pinned original source PDF.

Read-only original-PDF analysis on one low-priority CPU; no engine/field data.
Requires PyMuPDF. The source PDF is supplied explicitly and is never downloaded.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def constrain():
    if os.name=='nt':
        k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p
        k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
        k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
        assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1)
        assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
    else:
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
        if os.getpriority(os.PRIO_PROCESS,0)<15:os.nice(15-os.getpriority(os.PRIO_PROCESS,0))


def verify(pdf,batch_path):
    constrain()
    import pymupdf
    from build_eddy_measurement_register_v1 import validate_plot_estimate
    raw=batch_path.read_bytes();batch=json.loads(raw)
    source=batch['sources']['dwde-2020-plots']['original']
    assert pdf.stat().st_size==source['bytes']<35000000
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==source['sha256']
    checked=[]
    with pymupdf.open(pdf) as document:
        assert len(document)==source['pages']
        for record in batch['records']:
            plot=record['source_plot_estimate'];ref=plot['source_raster']
            assert ref['xref'] in [r[0] for r in document[plot['pdf_page']-1].get_images(full=True)]
            encoded=document.extract_image(ref['xref'])
            assert hashlib.sha256(encoded['image']).hexdigest()==ref['sha256']
            pix=pymupdf.Pixmap(document,ref['xref']);assert pix.n==3
            assert (pix.width,pix.height)==(ref['width'],ref['height'])
            pixels=pix.samples;roi=plot['roi_xyxy_inclusive'];columns=[]
            for x in range(roi[0],roi[2]+1):
                ys=[]
                for y in range(roi[1],roi[3]+1):
                    offset=(y*pix.width+x)*3;r,g,b=pixels[offset:offset+3]
                    if {'blue':b>180 and r<100 and g<100,'red':r>180 and g<100 and b<100,'green':g>180 and r<100 and b<100,'black':max(r,g,b)<80}[plot['trace_color']]:ys.append(y)
                if ys:columns.append([x,min(ys),max(ys)])
            assert columns==plot['column_y_extents'],record['id']
            validate_plot_estimate(plot,record['range_value'])
            checked.append({'id':record['id'],'verified_source_columns':len(columns),'range_km':record['range_value']})
    return {'schema':'osw.eddy-plot-source-verification.v1','status':'PASS','original_pdf_sha256':source['sha256'],'batch_sha256':hashlib.sha256(raw).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':checked,'source_pixels_verified':True,'runtime_changed':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',type=Path,required=True)
    parser.add_argument('--batch',type=Path,default=ROOT/'research/eddy-measurement-register-additions-v8.json')
    parser.add_argument('--result',type=Path)
    args=parser.parse_args();result=verify(args.pdf,args.batch)
    if args.result:args.result.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps(result))
