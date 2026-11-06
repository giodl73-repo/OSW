# Mid-Norway paired depth sections

Declare two new editorial latitude cuts63N[4.5,9.5]E and63.75N[6,11.5]E.
Retain March/June/September/December15,2022 00Z snapshots. These extend sampling
northward from the existing61.5/62.25N cases; no prior gate or successful source
patch changes or repeats. The Albretsen2012doi10.1093/icesjms/fsr187 broader
northward low-salinity coastal-current context does not provide these exact gates,
observed axes or depths. They remain declared regional sampling conventions.

Use the unchanged validated NCCjoint numerical collector through a scoped wrapper
that sets only the new operator, two sections, output and journaling read class.
Preserve original native-axis/time matching, all-target preflight, north0degree
signed component,0-100m core/selection window, original integral selector, primary
component>0.1m/s,5/10/20cm/s sensitivities and practicalS<35test after velocitycore
selection. No fresher-core replacement or post-result retuning. All unresolved
axes, outside-class cores, missing/domain censoring and native brackets persist.

The same joint reader reserves all8cases and all3fields before fields: Nvelocity
pairs plusNsalinityscalars=2Nnativeunits,24Nconservativebytes. Retry extras count
against unchanged250000nativeunits/7MB with all future first reads reserved.
Keep40levels,3-150profiles,20000cells/patch and5kmnative-axis tolerances. Only
literalNetCDFIOfailure permits3identicalattempts after2/5s. Never replay success.

After each successful field read, save its exact decoded native values to an
exclusive-create journal before requesting the next field. No extra source read
for journaling. On success retain all24patch journals and their hashes alongside
the8combined sections and source ledger/report. Whole batch including journal
must remain below2.4MB; per-file/publication caps unchanged. The journal is decoded
native data, not a raw HTTPpayload or wire-byte hash. If a later field fails or
times out, upload the partial sections, ledger and successful journals. Do not
restart completed patches. Any future resume must verify archived fields and
consume only uncompleted targets under a separately reviewed plan.

Run frozen22transport/selection checks and new wrapper/journal tests sequentially
in cloud on one idleCPU before actual source collection. Separate collection-step
timeout20min from25min job timeout to leave time for always-uploading artifacts.
No local field numerics/imports/tests. No reference inventory admission, physical
currentbottom/thickness/width/area/volume, annual envelope or whole-route claim
from this acquisition. Main/runtime/UI/eddy data and previous methods unchanged.
