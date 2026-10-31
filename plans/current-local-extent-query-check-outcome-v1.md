# Scoped local extent queries: verified runtime outcome

Run40131603572, attempt2, job120984471547 completed successfully from
469b25bdeaa57ef93706fe524ce0df4191852cba. The initial queued attempt was
terminally cancelled with zero jobs; attempt2 ran after the shared queue cleared.
The build-only request is disabled again.

Cloud execution used one actual CPU, nice15, one Cargo job/test thread and one
numerical worker. Six cloud-control tests passed in0.171s. Seven native tests
passed in0.11s, followed by native CLI compilation, WASM compilation and ten
native/WASM query comparisons. Compiler:rustc1.95.0; Node:v24.21.0.

Verified results on the835839-byte scalar snapshot:

- Twelve primary5km half-peak core extent rows remain queryable by month.
- Six primary10km missing-candidate cases remain explicit failures.
- Null physical-width selection returns864 attempts; zero-width selection
  returns zero. Pagination preserves all records.
- Record inspection resolves the original source seed case.
- Unsupported physical joins and unknown fields are rejected.
- A failed reload clears the scoped store; recovery requires a successful load.

The exact compact parity and source-gate reports are retained under research.
All83 executed scientific inputs and14 compiled query inputs remained unchanged.
The complete atlas was not loaded at runtime, and no provider source was
reacquired or processed. Installed data, query worker/UI and main were unchanged.

## Delivery size finding

The general engine compiles to59201757bytes. Its artifact is9030795bytes
compressed, with the exact checksums in the execution review. It remains remote;
only1623bytes of compact archive metadata were transferred for this readback.
Successful query parity does not by itself make this an appropriate lightweight
browser delivery artifact.

Next produce a dedicated smaller WASM target using the shared scalar-query
semantics. Retain this exact general-engine artifact as a reference for parity.
Compare the dedicated engine against the same snapshot, query results, record
resolution and failed-reload behavior, then connect the existing worker/UI to
the small dataset explicitly. Keep all original physical width/rank/state-join
admission fields unchanged. Use sequential cloud checks; local compilation,
browser automation and full index loads remain deferred.

No full-atlas regression, installed UI coverage or new physical measurements
are claimed by this scoped runtime result. The broader current/eddy dimensions,
seasonal uncertainty and atlas joins remain active work.
