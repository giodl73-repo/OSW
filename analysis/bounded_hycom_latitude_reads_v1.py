"""Exact fixed-latitude hyperslab retries using the frozen target-budget ledger."""
import numpy as np
from bounded_hycom_component_reads_v1 import BoundedComponentReads


class BoundedLatitudeReads(BoundedComponentReads):
    def receipt(self):
        result=super().receipt()
        result.update(schema='osw.bounded-hycom-latitude-reads.v1',geometry='fixed_native_latitude_contiguous_native_longitudes')
        return result

    def read(self,variable,time_index,y_index,x0,x1):
        values=40*(x1-x0+1)
        if not 3<=x1-x0+1<=150:raise ValueError('Bounded native longitude profile count required')
        for attempt in range(1,self.maximum_attempts+1):
            if attempt>1:
                if self.base_values+self.extra_values+values>self.max_values or 8*(self.base_values+self.extra_values+values)>self.max_bytes:
                    self.requests.append({'variable':variable.name,'attempt':attempt,'status':'retry_denied_before_read_by_full_target_budget'})
                    self.save();raise ValueError('Retry would consume budget reserved for original target')
                self.extra_values+=values
            if self.requested_values+values>self.max_values:raise ValueError('Actual request-value budget exceeded before read')
            entry={'variable':variable.name,'source_time_index':time_index,'latitude_index':y_index,
                'longitude_indices_inclusive':[x0,x1],'depth_indices_inclusive':[0,39],'attempt':attempt,'requested_component_values':values}
            self.requested_values+=values
            try:
                result=np.ma.filled(variable[time_index,:,y_index:y_index+1,x0:x1+1],np.nan)[:,0,:]
            except RuntimeError as error:
                if 'NetCDF: I/O failure' not in str(error):
                    entry['status']='non_transport_error_not_retried';self.requests.append(entry);self.save();raise
                entry['status']='provider_io_failure';self.requests.append(entry);self.save()
                if attempt==self.maximum_attempts:raise
                self.sleep([2,5][attempt-1]);continue
            if result.shape!=(40,x1-x0+1):
                entry['status']='shape_mismatch_not_retried';self.requests.append(entry);self.save();raise ValueError('Native source hyperslab shape changed')
            entry['status']='success';entry['actual_returned_array_bytes']=int(result.nbytes)
            self.returned_values+=int(result.size);self.requests.append(entry);self.save();return result
