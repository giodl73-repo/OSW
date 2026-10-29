# Preserve ranked lengths while admitting unmeasured basin identities

Run40796833828 attempt2 compiled natively and passed271 Rust tests, including complete taxonomy validation. Loading the full candidate then failed at the Norwegian Atlantic Slope Current validator because the shared expected-length table did not include the five new basin assessments. No native query, WASM comparison, browser check or installation completed.

Repair `length_assessment_overlays::expected` once, for every existing complete-table consumer. Append the five exact assessments only after the compiled basin contract validates. Preserve every historical row and rank and reject duplicate assessment IDs/owners and any promotion of unknown length or rank. Do not recompute ranks or copy family lengths into basin members.

The scientific v3 identity contract and candidate data remain unchanged. Before compilation, require the candidate logical digest and source-catalog digest to equal the saved inputs from the failed v3 engine run. Version the runtime source, compiler scope and dispatch controls; retain the exact failure evidence and disable its request.

Three new Rust tests cover exact append/order/rank preservation, duplicate/promoted assessment rejection, and legacy/partial-receipt behavior. The next cloud run must pass274 Rust tests,195 main-query and73 source-query comparisons, three global and seven object API comparisons, plus the same desktop/narrow browser checks and individual visual review. Only one job may run in the shared queue with one CPU and single workers. No local build, installed packet/index load or browser automation runs.

No physical length, width, uncertainty range, observation, geometry or publication is added by this repair. Installation, main merge and local bulk synchronization remain disabled.
