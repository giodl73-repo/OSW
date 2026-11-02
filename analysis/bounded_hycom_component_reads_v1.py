"""Budgeted exact-hyperslab retries; no field selection or numerical repair."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np


class BoundedComponentReads:
    def __init__(self,planned_pairs,operator,receipt_path,sleep=time.sleep):
        self.base_values=2*planned_pairs;self.extra_values=0;self.requested_values=0;self.returned_values=0
        self.max_values=2*operator['maximum_total_cell_pairs'];self.max_bytes=operator['maximum_total_decoded_velocity_bytes']
        self.maximum_attempts=operator['maximum_component_read_attempts'];self.receipt_path=Path(receipt_path);self.sleep=sleep;self.requests=[]
        if not 1<=self.maximum_attempts<=3 or self.base_values>self.max_values or self.base_values*8>self.max_bytes:raise ValueError('Full target and bounded retries must fit declared transport budget')
        self.save()

    def receipt(self):
        return {'schema':'osw.bounded-hycom-component-reads.v1','planned_successful_component_values':self.base_values,
            'additional_retry_component_values_reserved':self.extra_values,'actual_requested_component_values':self.requested_values,
            'successfully_returned_component_values':self.returned_values,'maximum_requested_component_values':self.max_values,
            'conservative_all_target_plus_retries_decoded_byte_bound':8*(self.base_values+self.extra_values),
            'maximum_decoded_byte_bound':self.max_bytes,'maximum_attempts_per_component':self.maximum_attempts,
            'requests':self.requests,'failed_request_wire_bytes_instrumented':False,'source_wire_hash_claimed':False,
            'counter_scope':'Requested values refer to exact requested hyperslab shapes,including failed reads. Buffer bound reserves all future first-attempt target reads plus allowed retries at8bytes/value;it is not observed wiretraffic or physical uncertainty.'}

    def save(self):
        self.receipt_path.parent.mkdir(parents=True,exist_ok=True)
        self.receipt_path.write_text(json.dumps(self.receipt(),indent=2,allow_nan=False)+'\n',encoding='utf8')

    def read(self,variable,time_index,y0,y1,x_index):
        values=40*(y1-y0+1)
        if not 3<=y1-y0+1<=150:raise ValueError('Bounded native latitude profile count required')
        for attempt in range(1,self.maximum_attempts+1):
            if attempt>1:
                if self.base_values+self.extra_values+values>self.max_values or 8*(self.base_values+self.extra_values+values)>self.max_bytes:
                    self.requests.append({'variable':variable.name,'attempt':attempt,'status':'retry_denied_before_read_by_full_target_budget'})
                    self.save();raise ValueError('Retry would consume budget reserved for original target')
                self.extra_values+=values
            if self.requested_values+values>self.max_values:raise ValueError('Actual request-value budget exceeded before read')
            entry={'variable':variable.name,'source_time_index':time_index,'latitude_indices_inclusive':[y0,y1],
                'longitude_index':x_index,'depth_indices_inclusive':[0,39],'attempt':attempt,'requested_component_values':values}
            self.requested_values+=values
            try:
                result=np.ma.filled(variable[time_index,:,y0:y1+1,x_index:x_index+1],np.nan)[:,:,0]
            except RuntimeError as error:
                if 'NetCDF: I/O failure' not in str(error):
                    entry['status']='non_transport_error_not_retried';self.requests.append(entry);self.save();raise
                entry['status']='provider_io_failure';self.requests.append(entry);self.save()
                if attempt==self.maximum_attempts:raise
                self.sleep([2,5][attempt-1]);continue
            if result.shape!=(40,y1-y0+1):
                entry['status']='shape_mismatch_not_retried';self.requests.append(entry);self.save();raise ValueError('Native source hyperslab shape changed')
            entry['status']='success';entry['actual_returned_array_bytes']=int(result.nbytes)
            self.returned_values+=int(result.size);self.requests.append(entry);self.save();return result

    def digest(self):return hashlib.sha256(self.receipt_path.read_bytes()).hexdigest()
