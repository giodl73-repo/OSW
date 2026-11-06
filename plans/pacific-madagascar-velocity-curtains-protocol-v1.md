# Pacific and Madagascar pre-tag native depth contours

All40original retained cases:California16,Alaska12,SouthernEastMadagascar12.
37interior and3unresolved. ExactJan15/July15,2022individual00Z snapshots,not
seasonalmeans orannualrange. California/Alaska primary.05m/s andsurfacegate.02;
Madagascar primary.1m/s andsurfacegate.05. Alaska0degree northward,others180south.

Originalpre-tagcollectorformat has no fixed_axis insectiondefinition,no mixed
geometrytag and no native_source_latitude repeatedincolumns. Do not rewrite or
addfields to source. First frozen acquire_three_current_depth_sections_v1
component/diagnosis validator,then scopedgeometryaudit matching exact original
operator sectiondefinition,40levels0..5000m,3..150nativecolumns,fullhyperslab,
timeindex,contiguous increasinglongitudes,fixedlatitude/index andgates. Offset
must EXACTLY reproduce originalGEOD.inv(-45,requested,-45,native)/1000,within
original tolerance. No nearest-row assumption/0meridian substitution.

Reuse validatedv2 source-threshold component,runs,frozenconnected_layer math;
look up primarylayer byvalue,notindex1. Everycandidate/selection/core/layer and
originalseedrunboundary reproduces. Strictfour-native-axis-neighbors,nodiagonal/
missingbridge,reselection orinterpolation. Separateverticalruns andfinitecrossings,
missing/domain/lateralcensors preserved;surfaceconnectivitytopologyonly.

Regional componentflow canincludeotherflows/eddies/coastalmasks;no independent
namedaxis/body/watermass/physicalbottom,annualrange,whole-routeprofile,width/area/
volume orduplicate scalarrefs. Missingnotzero,bed,absence;nativebracketsnot
uncertainty. Cloud-only sequentialoneidleCPU tests/build,zero retrieval/replay/
sourceedits/capchanges. Localstaticediting/AST,metadata/hash/exactretentiononly.
