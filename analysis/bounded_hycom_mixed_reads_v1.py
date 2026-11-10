"""One target reservation and ledger dispatching the unchanged two read methods."""
from bounded_hycom_component_reads_v1 import BoundedComponentReads
from bounded_hycom_latitude_reads_v1 import BoundedLatitudeReads


class BoundedMixedReads(BoundedComponentReads):
    read_longitude=BoundedComponentReads.read
    read_latitude=BoundedLatitudeReads.read

    def receipt(self):
        result=super().receipt()
        result.update(schema='osw.bounded-hycom-mixed-reads.v1',geometry='declared_fixed_axis_per_request_native_index_keys')
        return result
