"""Optional MATLAB/ASCII probe. Does not replace scientific inputs.

Requires scipy1.17.1/numpy2.4.1; the default section builder/tests do not.
"""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/source-data/redsox-lower-nc-2001'
RECEIPT_SHA='f0cc0d599b9ae5262ec05183211611ffa1b483eeef313ad845ba3d035d6e11ac'


def verify():
    import scipy.io
    import numpy as np
    from build_redsox_ladcp_source_inventory import parse_gpl
    raw_receipt=(SOURCE/'alternate-format-acquisition.json').read_bytes()
    if hashlib.sha256(raw_receipt).hexdigest()!=RECEIPT_SHA:raise ValueError('Changed frozen alternate-format acquisition')
    receipt=json.loads(raw_receipt);results=[]
    with zipfile.ZipFile(ROOT/'research/source-data/ncei-redsox-2001/ladcp-ascii-originals.zip') as z:
        for key,name in [('cast10mat.mat','RSX1/rsx1010.downup.hr.ladcpp.asc'),('cast34mat.mat','RSX2/rsx2034.downup.hr.ladcpp.asc')]:
            raw=(SOURCE/key).read_bytes();pin=receipt[key]
            if len(raw)!=pin['bytes'] or hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('Changed alternate original')
            mat=scipy.io.loadmat(SOURCE/key,simplify_cells=True);header,rows,_=parse_gpl(z.read(name))
            observed=np.array(rows,dtype=float)
            equivalent=False
            differences=None
            if len(observed)==len(mat['hz']):
                original=np.column_stack([mat[k] for k in ['hz','zz','ur','vr']])
                differences=np.nanmax(abs(observed-original),axis=0).tolist()
                equivalent=bool(np.allclose(observed,original,rtol=1e-5,atol=1e-5,equal_nan=True))
            results.append({'ASCII_file':name,'ASCII_samples':len(observed),'MATLAB_samples':len(mat['hz']),
                'ASCII_sequence':header['sequence'],'MATLAB_sequence':mat['gpl_HDR']['sequence'],
                'ASCII_reference':header['reference'],'MATLAB_reference':mat['gpl_HDR']['reference'],
                'same_rows_and_numerically_equivalent_at_ASCII_rounding':equivalent,
                'max_column_differences_when_shapes_match':differences})
    if any(r['same_rows_and_numerically_equivalent_at_ASCII_rounding'] for r in results):raise ValueError('Changed alternate-format finding')
    return results


if __name__=='__main__':print(json.dumps(verify(),indent=2))
