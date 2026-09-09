const legacyZones = [
  { id: "indo-pacific-warm-pool", n: 1, name: "Indo-Pacific Warm Pool", kind: "reservoir", label: "Heat continent", role: "persistent reservoir", depth: "surface / upper ocean", clock: "persistent; seasonally breathing", evidence: "conceptual · O18", x: 85, y: 42.4, families: ["heatmass", "oceanbelts"], summary: "The largest persistent expanse of very warm surface water: a continent-like reservoir whose edge moves with threshold, season, and dataset.", boundary: "A warm surface footprint is not a full-depth heat-content integral, and its diagnostic boundary is not a material wall.", source: "https://www.climate.gov/news-features/featured-images/warm-pool-indo-pacific-ocean-has-almost-doubled-size-changing-global" },
  { id: "western-hemisphere-warm-pool", n: 2, name: "Western Hemisphere Warm Pool", kind: "reservoir", label: "Seasonal heat continent", role: "seasonal reservoir", depth: "surface / upper ocean", clock: "seasonal expansion", evidence: "conceptual · O19", x: 31.3, y: 41, families: ["heatmass"], summary: "A seasonally connected warm-water province spanning parts of the tropical eastern Pacific, Gulf of Mexico, Caribbean, and western tropical Atlantic.", boundary: "Central America divides the ocean basins even when a temperature threshold visually joins the warm regions.", source: "https://www.aoml.noaa.gov/phod/research/tav/awp/" },
  { id: "northeast-pacific-blob", n: 3, name: "Northeast Pacific Blob", kind: "transient", label: "Heat blob", role: "marine heatwave anomaly", depth: "surface with subsurface remnant", clock: "episodic / multi-year", evidence: "observational · O20–O21", x: 12.8, y: 27.1, families: ["heatmass"], summary: "A named marine heatwave demonstrates why a heat blob is an event relative to a baseline—not a permanent ocean province.", boundary: "Its surface expression does not determine its full-depth energy or prove a single cause.", source: "https://doi.org/10.1002/2016GL071039" },
  { id: "el-nino-tongue", n: 4, name: "El Niño Tongue", kind: "transient", label: "Heat tongue", role: "basin-scale anomaly", depth: "surface / thermocline coupled", clock: "interannual", evidence: "conceptual", x: 18.1, y: 44.8, families: ["heatmass", "oceanbelts"], summary: "An eastward-reaching equatorial anomaly: a tongue because its geometry and evolution matter as much as its peak temperature.", boundary: "The atlas shape is schematic and is not an event declaration or an ENSO index.", source: "../SOURCE-REGISTER.md" },
  { id: "gulf-stream", n: 5, name: "Gulf Stream", kind: "pathway", label: "Heat river", role: "western boundary current", depth: "surface intensified; deep structure", clock: "persistent and variable", evidence: "conceptual · O2", x: 33.8, y: 30, families: ["oceanrealms", "oceanbelts"], summary: "A narrow, fast pathway that exports warm water poleward and sheds moving rings into the surrounding ocean.", boundary: "Current speed and water temperature do not, by themselves, give heat transport across a section.", source: "https://www.whoi.edu/ocean-learning-hub/ocean-topics/how-the-ocean-works/ocean-circulation/currents-gyres-eddies/" },
  { id: "kuroshio", n: 6, name: "Kuroshio", kind: "pathway", label: "Heat river", role: "western boundary current", depth: "surface intensified; deep structure", clock: "persistent and variable", evidence: "conceptual · O2", x: 87.2, y: 30.5, families: ["oceanrealms", "oceanbelts"], summary: "The North Pacific counterpart in the map grammar: a swift boundary current, extension, and ring-forming system.", boundary: "The analogy to the Gulf Stream is structural, not an assertion of identical forcing, geometry, or transport.", source: "https://www.whoi.edu/ocean-learning-hub/ocean-topics/how-the-ocean-works/ocean-circulation/currents-gyres-eddies/" },
  { id: "agulhas", n: 7, name: "Agulhas System", kind: "pathway", label: "River and moving islands", role: "boundary current / leakage", depth: "upper ocean to intermediate", clock: "persistent with episodic rings", evidence: "conceptual", x: 56.6, y: 59.5, families: ["oceanrealms"], summary: "A current system whose retroflection and rings make exchange look less like a pipe and more like parcels escaping a moving border.", boundary: "The schematic shape does not quantify leakage or attribute downstream climate effects.", source: "../SOURCE-REGISTER.md" },
  { id: "antarctic-circumpolar-current", n: 8, name: "Antarctic Circumpolar Current", kind: "pathway", label: "Circumpolar belt", role: "fronted zonal current", depth: "deep-reaching fronts", clock: "persistent and meandering", evidence: "observational · O4, O8–O9", x: 78.8, y: 67, families: ["oceanrealms", "oceanbelts"], summary: "Earth's clearest ocean belt: a deep-reaching, eastward current whose fronts inhibit exchange while eddies and regional pathways leak heat across them.", boundary: "The ACC is not a solid cold wall and Drake Passage is not a thermal plug.", source: "https://doi.org/10.1175/JPO-D-19-0266.1" },
  { id: "circumpolar-deep-water", n: 9, name: "Circumpolar Deep Water", kind: "buried", label: "Buried heat continent", role: "subsurface reservoir / source water", depth: "intermediate to deep; region dependent", clock: "persistent with changing access", evidence: "synthesis · O10, O14", x: 49.4, y: 66.7, families: ["heatmass", "oceanrealms"], summary: "Relatively warm subsurface water can approach Antarctic margins beneath a cold surface, making vertical structure central to ice-shelf exposure.", boundary: "Offshore presence does not equal delivery to a cavity; fronts, shelf breaks, troughs, mixing, and winds intervene.", source: "https://doi.org/10.1029/2018RG000624" },
  { id: "atlantic-water-arctic", n: 10, name: "Atlantic Water in the Arctic", kind: "buried", label: "Buried heat continent", role: "subsurface inflow and reservoir", depth: "below the cold, fresh halocline", clock: "persistent and variable", evidence: "observational synthesis · O22", x: 57.5, y: 16.2, families: ["heatmass", "oceanrealms"], summary: "Warm Atlantic-origin water can sit beneath a colder, fresher lid: the Arctic example of why the surface can conceal a large thermal contrast.", boundary: "Subsurface temperature does not determine when, where, or how much heat reaches sea ice or the atmosphere.", source: "https://doi.org/10.3389/fmars.2019.00416" },
  { id: "drake-passage", n: 11, name: "Drake Passage", kind: "gate", label: "Heat gate", role: "circumpolar transport section", depth: "full water column", clock: "persistent geometry; variable flow", evidence: "observational / modeled · O4–O7", x: 33.1, y: 66.1, families: ["oceanrealms", "oceanbelts"], summary: "The narrowest major gate on the circumpolar route. It makes ACC transport measurable and exposes how geometry reorganizes global circulation.", boundary: "Closing the gate in a model changes many coupled circulations; it is not equivalent to simply sending warm water south.", source: "https://doi.org/10.1175/JCLI-D-15-0554.1" },
  { id: "indonesian-throughflow", n: 12, name: "Indonesian Throughflow", kind: "gate", label: "Archipelagic heat gate", role: "inter-basin exchange", depth: "multiple constrained passages", clock: "persistent and variable", evidence: "conceptual", x: 80.5, y: 46.2, families: ["oceanrealms"], summary: "A branching tropical gate where land geometry constrains exchange between the Pacific and Indian oceans.", boundary: "The schematic shape simplifies multiple straits, vertical structure, tides, mixing, and seasonal reversals.", source: "../SOURCE-REGISTER.md" }
];

const lensForLegacy = {
  reservoir: "waters", buried: "waters", pathway: "flows", gate: "edges", transient: "events"
};
const depthClassForLegacy = { reservoir: "upper", buried: "deep", pathway: "full-column", gate: "full-column", transient: "surface" };
const propertyForLegacy = { reservoir: ["warm"], buried: ["warm"], pathway: ["dynamic"], gate: ["dynamic"], transient: ["warm"] };
const clockForLegacy = { reservoir: "seasonal", buried: "persistent", pathway: "persistent", gate: "persistent", transient: "episodic" };
const zones = legacyZones.map(zone => ({
  ...zone,
  lens: lensForLegacy[zone.kind],
  depthClass: depthClassForLegacy[zone.kind],
  properties: propertyForLegacy[zone.kind],
  clockClass: clockForLegacy[zone.kind],
  basis: zone.role,
  sourceId: zone.evidence.includes("·") ? zone.evidence.split("·").at(-1).trim() : "REGISTER",
  legacyFamilies: zone.families
})).concat([
  { id: "antarctic-bottom-water", n: 13, name: "Antarctic Bottom Water", kind: "water-mass", label: "Cold bottom water", role: "dense abyssal water mass", depth: "bottom; formed around Antarctica", depthClass: "bottom", clock: "persistent", lens: "waters", properties: ["cold", "salty"], evidence: "synthesis · OG01", basis: "Very cold, dense water formed around Antarctic shelves and margins that spreads into abyssal basins.", x: 47, y: 75, families: ["waters"], legacyFamilies: [], summary: "The coldest major water mass occupies the deepest layer of much of the world ocean—an immense geography hidden from surface maps.", boundary: "The schematic extent is not a measured boundary or a claim of uniform properties across every abyssal basin.", sourceId: "OG01", source: "https://divediscover.whoi.edu/polar-regions/antarctic-ocean-circulation/" },
  { id: "north-atlantic-deep-water", n: 14, name: "North Atlantic Deep Water", kind: "water-mass", label: "Deep water mass", role: "deep overturning water", depth: "deep Atlantic; spreads southward", depthClass: "deep", clock: "persistent", lens: "waters", properties: ["cold", "salty"], evidence: "synthesis · OG02", basis: "Relatively salty deep water assembled from northern-source waters and traced by hydrographic properties.", x: 42, y: 39, families: ["waters"], legacyFamilies: [], summary: "A basin-spanning deep water mass demonstrates that major ocean countries can lie kilometers below the visible surface.", boundary: "Its hydrographic core is modified by mixing and does not define a sealed or uniformly moving parcel.", sourceId: "OG02", source: "https://www.whoi.edu/science/PO/people/jprice/class/miscart/Stewart2006.pdf" },
  { id: "antarctic-intermediate-water", n: 15, name: "Antarctic Intermediate Water", kind: "water-mass", label: "Fresh intermediate water", role: "intermediate water mass", depth: "roughly 600–1000 m; basin dependent", depthClass: "intermediate", clock: "persistent", lens: "waters", properties: ["cold", "fresh"], evidence: "synthesis · OG03", basis: "Cool, relatively fresh Southern Ocean water subducted north of the polar domain and traced at intermediate depth.", x: 38, y: 61, families: ["waters"], legacyFamilies: [], summary: "A cool, fresh intermediate layer spreads northward beneath warmer surface waters in several basins.", boundary: "The schematic shape cannot show its branching cores, mixing, or basin-specific definitions.", sourceId: "OG03", source: "https://divediscover.whoi.edu/polar-regions/antarctic-ocean-circulation/" },
  { id: "subantarctic-mode-water", n: 16, name: "Subantarctic Mode Water", kind: "water-mass", label: "Mode-water belt", role: "ventilated thermocline water", depth: "deep winter mixed layer / upper thermocline", depthClass: "upper", clock: "seasonal", lens: "waters", properties: ["cold", "fresh"], evidence: "synthesis · OG04", basis: "Thick, weakly stratified water formed by winter mixing north of the Subantarctic Front.", x: 68, y: 62, families: ["waters"], legacyFamilies: [], summary: "A broad Southern Hemisphere mode-water family ventilates the thermocline rather than forming a surface continent.", boundary: "Formation properties and geographic definitions vary by basin and year.", sourceId: "OG04", source: "https://www.gfdl.noaa.gov/bibliography/related_files/jls0401.pdf" },
  { id: "north-pacific-intermediate-water", n: 17, name: "North Pacific Intermediate Water", kind: "water-mass", label: "Fresh intermediate water", role: "North Pacific ventilation layer", depth: "intermediate North Pacific", depthClass: "intermediate", clock: "persistent", lens: "waters", properties: ["cold", "fresh"], evidence: "synthesis · OG05", basis: "A North Pacific salinity-minimum layer formed and transformed in the subpolar–subtropical transition.", x: 88, y: 25, families: ["waters"], legacyFamilies: [], summary: "The North Pacific contains a recognizable intermediate layer even where the surface belongs to a warm gyre.", boundary: "The salinity-minimum core is not a fixed-edged body or a direct velocity measurement.", sourceId: "OG05", source: "https://www.gfdl.noaa.gov/bibliography/related_files/jls0401.pdf" },
  { id: "labrador-sea-water", n: 18, name: "Labrador Sea Water", kind: "water-mass", label: "Ventilated deep water", role: "subpolar mode / deep water", depth: "intermediate to deep North Atlantic", depthClass: "deep", clock: "seasonal", lens: "waters", properties: ["cold", "fresh"], evidence: "synthesis · OG06", basis: "Weakly stratified water renewed by variable deep winter convection in the Labrador Sea.", x: 37, y: 19, families: ["waters"], legacyFamilies: [], summary: "A named subpolar water mass records formation history and ventilation below the surface.", boundary: "The schematic shape does not show variable formation extent or downstream pathways.", sourceId: "OG06", source: "https://www.whoi.edu/science/PO/people/jprice/class/miscart/Stewart2006.pdf" },
  { id: "mediterranean-outflow-water", n: 19, name: "Mediterranean Outflow Water", kind: "water-mass", label: "Salty outflow layer", role: "marginal-sea source water", depth: "intermediate eastern North Atlantic", depthClass: "intermediate", clock: "persistent", lens: "waters", properties: ["warm", "salty"], evidence: "synthesis · OG07", basis: "Warm, saline Mediterranean-origin water exits Gibraltar and forms an intermediate salinity maximum.", x: 48, y: 32, families: ["waters"], legacyFamilies: [], summary: "A narrow gate seeds a much larger salty subsurface signature in the Atlantic.", boundary: "The schematic shape does not show mixing, meddies, or a measured outflow transport.", sourceId: "OG07", source: "https://www.gfdl.noaa.gov/ocean-mesoscale-eddies/" },
  { id: "red-sea-water", n: 20, name: "Red Sea Water", kind: "water-mass", label: "Warm salty source water", role: "marginal-sea outflow water", depth: "intermediate western Indian Ocean", depthClass: "intermediate", clock: "persistent", lens: "waters", properties: ["warm", "salty"], evidence: "synthesis · OG08", basis: "Warm, highly saline water formed by strong evaporation and exported through Bab el-Mandeb.", x: 56, y: 40, families: ["waters"], legacyFamilies: [], summary: "A small marginal sea leaves a traceable intermediate-water signature far beyond its gate.", boundary: "The schematic shape is not the full outflow plume or a transport estimate.", sourceId: "OG08", source: "https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/" },
  { id: "north-pacific-subtropical-gyre", n: 21, name: "North Pacific Subtropical Gyre", kind: "gyre", label: "Rotating current system", role: "subtropical gyre", depth: "surface-intensified circulation", depthClass: "upper", clock: "persistent", lens: "flows", properties: ["dynamic"], evidence: "conceptual · OG09", basis: "A basin-scale wind-driven system of rotating currents surrounding the subtropical interior.", x: 8, y: 35, families: ["flows"], legacyFamilies: [], summary: "The largest gyre makes an enormous moving province out of water that a heat-only atlas leaves blank.", boundary: "A gyre is a current system, not homogeneous water or a plastic island.", sourceId: "OG09", source: "https://oceanservice.noaa.gov/facts/gyre.html" },
  { id: "south-pacific-subtropical-gyre", n: 22, name: "South Pacific Subtropical Gyre", kind: "gyre", label: "Rotating current system", role: "subtropical gyre", depth: "surface-intensified circulation", depthClass: "upper", clock: "persistent", lens: "flows", properties: ["dynamic"], evidence: "conceptual · OG10", basis: "A Southern Hemisphere wind-driven current circuit around the subtropical Pacific interior.", x: 14, y: 59, families: ["flows"], legacyFamilies: [], summary: "A vast circulation realm occupies the South Pacific even without a famous thermal nickname.", boundary: "Its edges shift and do not define a uniform water mass.", sourceId: "OG10", source: "https://oceanservice.noaa.gov/facts/gyre.html" },
  { id: "north-atlantic-subtropical-gyre", n: 23, name: "North Atlantic Subtropical Gyre", kind: "gyre", label: "Rotating current system", role: "subtropical gyre", depth: "surface-intensified circulation", depthClass: "upper", clock: "persistent", lens: "flows", properties: ["dynamic"], evidence: "conceptual · OG11", basis: "A wind-driven current circuit containing the Sargasso Sea and bounded by major currents.", x: 42, y: 33, families: ["flows"], legacyFamilies: [], summary: "Currents organize the North Atlantic interior into a recognizable rotating realm.", boundary: "The schematic shape is not a fixed gyre center or edge.", sourceId: "OG11", source: "https://oceanservice.noaa.gov/facts/gyre.html" },
  { id: "south-atlantic-subtropical-gyre", n: 24, name: "South Atlantic Subtropical Gyre", kind: "gyre", label: "Rotating current system", role: "subtropical gyre", depth: "surface-intensified circulation", depthClass: "upper", clock: "persistent", lens: "flows", properties: ["dynamic"], evidence: "conceptual · OG12", basis: "A wind-driven clockwise current circuit spanning the subtropical South Atlantic.", x: 43, y: 57, families: ["flows"], legacyFamilies: [], summary: "The basin interior belongs to a circulation system even where no single current line dominates the map.", boundary: "The gyre is variable and internally heterogeneous.", sourceId: "OG12", source: "https://oceanservice.noaa.gov/facts/gyre.html" },
  { id: "indian-ocean-subtropical-gyre", n: 25, name: "Indian Ocean Subtropical Gyre", kind: "gyre", label: "Rotating current system", role: "subtropical gyre", depth: "surface-intensified circulation", depthClass: "upper", clock: "persistent", lens: "flows", properties: ["dynamic"], evidence: "conceptual · OG13", basis: "A Southern Hemisphere wind-driven current circuit shaped by the Indian basin and monsoon influence.", x: 68, y: 58, families: ["flows"], legacyFamilies: [], summary: "A fifth major subtropical gyre fills much of the Indian Ocean's apparently unlabeled interior.", boundary: "Seasonal monsoon circulation complicates any static outline.", sourceId: "OG13", source: "https://oceanservice.noaa.gov/facts/gyre.html" },
  { id: "antarctic-polar-front", n: 26, name: "Antarctic Polar Front", kind: "front", label: "Water-mass boundary", role: "deep-reaching ACC front", depth: "surface expression and deep structure", depthClass: "full-column", clock: "persistent", lens: "edges", properties: ["dynamic", "cold"], evidence: "observational · OG14", basis: "A circumpolar hydrographic front separating Antarctic and subantarctic waters, with multiple diagnostic definitions.", x: 61, y: 68, families: ["edges"], legacyFamilies: [], summary: "A front gives the Southern Ocean an edge, but it meanders, branches, and leaks rather than forming a wall.", boundary: "The schematic line cannot represent the front's changing circumpolar path.", sourceId: "OG14", source: "https://doi.org/10.5194/essd-8-191-2016" },
  { id: "subantarctic-front", n: 27, name: "Subantarctic Front", kind: "front", label: "Water-mass boundary", role: "northern major ACC front", depth: "surface expression and deep structure", depthClass: "full-column", clock: "persistent", lens: "edges", properties: ["dynamic"], evidence: "observational · OG15", basis: "A major ACC-associated front bounding the Polar Frontal Zone to the north.", x: 78, y: 63, families: ["edges"], legacyFamilies: [], summary: "Another circumpolar edge shows why the Southern Ocean is a stack of belts rather than one cold ring.", boundary: "Its surface expression can be weak and its position varies regionally.", sourceId: "OG15", source: "https://www.aoml.noaa.gov/phod/goos/xbtscience/ax25_acc.php" },
  { id: "equatorial-pacific-divergence", n: 28, name: "Equatorial Pacific Divergence", kind: "upwelling", label: "Cold nutrient-rich seam", role: "equatorial upwelling zone", depth: "surface / upper thermocline", depthClass: "upper", clock: "persistent", lens: "edges", properties: ["cold", "nutrient-rich", "dynamic"], evidence: "synthesis · OG16", basis: "Wind-driven divergence draws cooler, nutrient-rich subsurface water toward the equatorial surface.", x: 11, y: 49, families: ["edges"], legacyFamilies: [], summary: "Some ocean geography is a seam where water rises, not a mass sitting still.", boundary: "The schematic shape does not diagnose upwelling rate or the changing cold-tongue footprint.", sourceId: "OG16", source: "https://oceanservice.noaa.gov/facts/upwelling.html" },
  { id: "mid-atlantic-ridge", n: 29, name: "Mid-Atlantic Ridge", kind: "seafloor", label: "Submerged mountain range", role: "divergent plate boundary", depth: "seabed", depthClass: "seabed", clock: "geologic", lens: "floor", properties: ["relief"], evidence: "observational · OG17", basis: "A long volcanic ridge formed at a divergent plate boundary along the Atlantic basin floor.", x: 48, y: 48, families: ["floor"], legacyFamilies: [], summary: "The Atlantic has a mountain spine beneath the water that helps organize basins and deep pathways.", boundary: "A single point cannot show ridge segmentation, transform faults, or water-column effects.", sourceId: "OG17", source: "https://prod-01-alb-www-noaa.woc.noaa.gov/education/resource-collections/ocean-coasts/ocean-floor-features" },
  { id: "east-pacific-rise", n: 30, name: "East Pacific Rise", kind: "seafloor", label: "Fast-spreading ridge", role: "divergent plate boundary", depth: "seabed", depthClass: "seabed", clock: "geologic", lens: "floor", properties: ["relief"], evidence: "observational · OG18", basis: "A fast-spreading mid-ocean ridge system forming new Pacific seafloor.", x: 24, y: 57, families: ["floor"], legacyFamilies: [], summary: "A second submerged mountain system gives the Pacific a hidden structural spine.", boundary: "The point is only an index to a long segmented ridge system.", sourceId: "OG18", source: "https://prod-01-alb-www-noaa.woc.noaa.gov/education/resource-collections/ocean-coasts/ocean-floor-features" },
  { id: "mariana-trench", n: 31, name: "Mariana Trench", kind: "seafloor", label: "Ocean trench", role: "subduction trench", depth: "seabed / hadal", depthClass: "seabed", clock: "geologic", lens: "floor", properties: ["relief"], evidence: "observational · OG19", basis: "A very deep, narrow depression formed where one tectonic plate subducts beneath another.", x: 89, y: 39, families: ["floor"], legacyFamilies: [], summary: "The deepest ocean geography is a hadal trench—not a surface color or current.", boundary: "The schematic shape does not represent the trench's full arc or habitat variability.", sourceId: "OG19", source: "https://prod-01-alb-www.noaa.woc.noaa.gov/education/resource-collections/ocean-coasts/ocean-floor-features" },
  { id: "kerguelen-plateau", n: 32, name: "Kerguelen Plateau", kind: "seafloor", label: "Submerged plateau", role: "large igneous province / bathymetric obstacle", depth: "seabed; rises into deep water column", depthClass: "seabed", clock: "geologic", lens: "floor", properties: ["relief"], evidence: "synthesis · OG20", basis: "A broad elevated seafloor province in the southern Indian Ocean that steers deep and circumpolar flows.", x: 69, y: 68, families: ["floor"], legacyFamilies: [], summary: "Submerged plateaus can redirect fronts and currents even though they are invisible at the surface.", boundary: "The point does not quantify bathymetric steering or delimit the plateau.", sourceId: "OG20", source: "https://prod-01-alb-www-noaa.woc.noaa.gov/education/resource-collections/ocean-coasts/ocean-floor-features" },
  { id: "etnp-oxygen-minimum-zone", n: 33, name: "Eastern Tropical North Pacific OMZ", kind: "biogeochemical", label: "Low-oxygen layer", role: "oxygen-minimum zone", depth: "roughly 100–1500 m; regional", depthClass: "intermediate", clock: "persistent", lens: "life", properties: ["low-oxygen"], evidence: "observational synthesis · OG21", basis: "A persistent subsurface region where oxygen consumption and weak ventilation maintain low concentrations.", x: 19, y: 43, families: ["life"], legacyFamilies: [], summary: "A vast subsurface oxygen geography exists beneath tropical surface waters.", boundary: "The schematic shape is not a hypoxia threshold contour, habitat forecast, or current measurement.", sourceId: "OG21", source: "https://oceanexplorer.noaa.gov/ocean-fact/omz/" },
  { id: "etsp-oxygen-minimum-zone", n: 34, name: "Eastern Tropical South Pacific OMZ", kind: "biogeochemical", label: "Low-oxygen layer", role: "oxygen-minimum zone", depth: "subsurface eastern tropical Pacific", depthClass: "intermediate", clock: "persistent", lens: "life", properties: ["low-oxygen"], evidence: "observational synthesis · OG22", basis: "Low ventilation and biogeochemical oxygen consumption sustain a major eastern tropical subsurface minimum.", x: 24, y: 54, families: ["life"], legacyFamilies: [], summary: "The southeast Pacific contains a major low-oxygen province layered beneath productive surface waters.", boundary: "The schematic shape does not encode oxygen concentration, threshold, or vertical extent.", sourceId: "OG22", source: "https://repository.library.noaa.gov/view/noaa/26936" },
  { id: "arabian-sea-oxygen-minimum-zone", n: 35, name: "Arabian Sea OMZ", kind: "biogeochemical", label: "Low-oxygen layer", role: "oxygen-minimum zone", depth: "subsurface Arabian Sea", depthClass: "intermediate", clock: "persistent", lens: "life", properties: ["low-oxygen"], evidence: "observational synthesis · OG23", basis: "High productivity, respiration, stratification, and circulation combine to maintain low subsurface oxygen.", x: 62, y: 40, families: ["life"], legacyFamilies: [], summary: "The Arabian Sea is a named chemical province as well as a geographic sea.", boundary: "The point is not an oxygen contour and does not imply uniform ecological effects.", sourceId: "OG23", source: "https://oceanexplorer.noaa.gov/ocean-fact/omz/" },
  { id: "sargasso-sea", n: 36, name: "Sargasso Sea", kind: "biogeochemical", label: "Oligotrophic gyre province", role: "low-nutrient open-ocean ecosystem", depth: "surface / upper ocean", depthClass: "upper", clock: "persistent", lens: "life", properties: ["nutrient-poor"], evidence: "observational synthesis · OG24", basis: "A clear, nutrient-limited ecosystem within the North Atlantic subtropical gyre, bounded by currents rather than land.", x: 44, y: 31, families: ["life"], legacyFamilies: [], summary: "The Sargasso Sea proves that an ocean sea can be geographically real without a coastline.", boundary: "The schematic shape does not delimit a fixed ecosystem boundary or uniform productivity.", sourceId: "OG24", source: "https://prod-01-alb-www.noaa.woc.noaa.gov/gc-international-section/marine-protected-areas-mpas-sargasso-sea" }
]).map(zone => ({ ...zone, clockClass: zone.clockClass || zone.clock }));

const count = document.querySelector("#visible-count");
const fields = Object.fromEntries(["index", "name", "kind", "summary", "lens", "role", "basis", "property", "depth", "clock", "evidence", "boundary", "source"].map(key => [key, document.querySelector(`#zone-${key}`)]));
let selectedZone = zones[0];
let currentLens = "waters";
let currentMode = "conceptual";
let currentConceptualView = "water-first";
let selectedProvinceCode = null;
let provinceView = null;
let featureView = null;
let requestedProvinceCode = new URLSearchParams(window.location.search).get("province");
let requestedFeatureId = new URLSearchParams(window.location.search).get("feature");
let zoomInvoker = null;
let probeCell = null;
let ringLatitude = 64;
let currentArgoPressure = 700;
const RELATION_METHOD = Object.freeze({ version: "rendered-overlap-1", coarsePathStep: 6, coarseGridStep: 12, finePathStep: 3, fineGridStep: 6 });
let provinceGroups = [];
let featureGroups = [];
let relationMatrix = new Map();
let relationMatrixBuilding = false;
const featureSampleCache = new WeakMap();
const featureGridCache = new WeakMap();
let relationSubject = "feature";
let provinceSvgSha256 = "pending";
let featureSvgSha256 = "pending";
// These observation globals and their oceanlines.* schema IDs are versioned
// data interfaces. Keep them stable across the OSW human-facing rebrand.
const argoLayers = {
  10: window.OCEANLINES_ARGO_TEMPERATURE_ANOMALY_10DBAR,
  300: window.OCEANLINES_ARGO_TEMPERATURE_ANOMALY_300DBAR,
  700: window.OCEANLINES_ARGO_TEMPERATURE_ANOMALY_700DBAR,
  1000: window.OCEANLINES_ARGO_TEMPERATURE_ANOMALY_1000DBAR
};

function selectZone(zone) {
  selectedZone = zone;
  relationSubject = "feature";
  document.querySelectorAll("#feature-shape-host .feature-shape").forEach(shape => shape.classList.toggle("selected", shape.dataset.id === zone.id));
  fields.index.textContent = `ZONE ${String(zone.n).padStart(2, "0")} · ${zone.label.toUpperCase()}`;
  fields.name.textContent = zone.name;
  fields.kind.textContent = zone.families.map(name => name.toUpperCase()).join(" · ");
  fields.lens.textContent = zone.lens.toUpperCase();
  fields.basis.textContent = zone.basis;
  fields.property.textContent = zone.properties.join(" · ").toUpperCase();
  for (const key of ["summary", "role", "depth", "clock", "evidence", "boundary"]) fields[key].textContent = zone[key];
  fields.source.href = zone.source;
  fields.source.textContent = zone.source.startsWith("../") ? "Open the source register →" : "Open primary source →";
  const badge = document.querySelector("#evidence-badge");
  const evidence = evidenceClass(zone).toLowerCase().replace("/", "-");
  badge.dataset.evidence = evidence;
  badge.textContent = evidenceClass(zone);
  document.querySelector("#feature-zoom").disabled = !featureGroups.some(group => group.dataset.id === zone.id);
  renderFeatureLabels();
  renderFeatureRelations(zone);
}

function colorFromStops(value, stops) {
  const bounded = Math.max(stops[0][0], Math.min(stops.at(-1)[0], value));
  let upper = stops.findIndex(stop => stop[0] >= bounded);
  if (upper < 1) upper = 1;
  const [lowValue, lowColor] = stops[upper - 1];
  const [highValue, highColor] = stops[upper];
  const mix = (bounded - lowValue) / (highValue - lowValue);
  const color = lowColor.map((channel, index) => Math.round(channel + (highColor[index] - channel) * mix));
  return `rgb(${color.join(",")})`;
}

function temperatureColor(value) {
  return colorFromStops(value, [
    [-2, [216, 244, 255]], [0, [141, 211, 232]], [8, [43, 156, 189]],
    [16, [56, 182, 138]], [22, [242, 207, 91]], [28, [240, 120, 66]], [32, [185, 39, 53]]
  ]);
}

function anomalyColor(value) {
  return colorFromStops(value, [
    [-5, [35, 59, 131]], [-3, [61, 119, 184]], [-1, [155, 203, 225]],
    [0, [238, 233, 216]], [1, [241, 187, 120]], [3, [207, 91, 71]], [5, [124, 35, 69]]
  ]);
}

function errorColor(value) {
  return colorFromStops(value, [
    [0.1, [244, 241, 222]], [0.2, [184, 216, 186]], [0.3, [110, 182, 167]],
    [0.4, [223, 179, 92]], [0.5, [184, 76, 76]], [0.6, [99, 44, 85]]
  ]);
}

function renderObservedField(data, colorFunction) {
  const canvas = document.querySelector("#sst-canvas");
  const context = canvas.getContext("2d");
  const [rows, columns] = data.shape;
  const cellWidth = Math.abs(data.longitude.step) / 360 * canvas.width;
  const cellHeight = Math.abs(data.latitude.step) / 180 * canvas.height;
  context.fillStyle = "#30454b";
  context.fillRect(0, 0, canvas.width, canvas.height);
  const domainNorth = data.latitude.start + (rows - 1) * data.latitude.step + Math.abs(data.latitude.step) / 2;
  const domainSouth = data.latitude.start - Math.abs(data.latitude.step) / 2;
  context.fillStyle = "#c8bda5";
  context.fillRect(0, (90 - domainNorth) / 180 * canvas.height, canvas.width, (domainNorth - domainSouth) / 180 * canvas.height);
  data.values_c_hundredths.forEach((encoded, index) => {
    if (encoded === null) return;
    const row = Math.floor(index / columns);
    const column = index % columns;
    const longitude = normalizedLongitude(data.longitude.start + column * data.longitude.step);
    const latitude = data.latitude.start + row * data.latitude.step;
    const x = (longitude + 180) / 360 * canvas.width - cellWidth / 2;
    const y = (90 - latitude) / 180 * canvas.height - cellHeight / 2;
    context.fillStyle = colorFunction(encoded / 100);
    context.fillRect(x, y, Math.ceil(cellWidth), Math.ceil(cellHeight));
    if (x < 0) context.fillRect(x + canvas.width, y, Math.ceil(cellWidth), Math.ceil(cellHeight));
    if (x + cellWidth > canvas.width) context.fillRect(x - canvas.width, y, Math.ceil(cellWidth), Math.ceil(cellHeight));
  });
  context.strokeStyle = "rgba(255,255,255,.24)";
  context.lineWidth = 1;
  for (let longitude = 60; longitude < 360; longitude += 60) {
    context.beginPath(); context.moveTo(longitude / 360 * canvas.width, 0); context.lineTo(longitude / 360 * canvas.width, canvas.height); context.stroke();
  }
  for (let latitude = 30; latitude < 180; latitude += 30) {
    context.beginPath(); context.moveTo(0, latitude / 180 * canvas.height); context.lineTo(canvas.width, latitude / 180 * canvas.height); context.stroke();
  }
  if (data.schema === "oceanlines.oisst.snapshot.v2") {
    const rings = pairedRingRows(ringLatitude, data);
    for (const [ring, color] of [[rings.north, "#5ee2d6"], [rings.south, "#ff6f61"]]) {
      const y = (90 - ring.latitude) / 180 * canvas.height;
      context.beginPath(); context.moveTo(0, y); context.lineTo(canvas.width, y);
      context.strokeStyle = "#071b22"; context.lineWidth = 5; context.stroke();
      context.beginPath(); context.moveTo(0, y); context.lineTo(canvas.width, y);
      context.strokeStyle = color; context.lineWidth = 2; context.setLineDash([8, 5]); context.stroke();
      context.setLineDash([]);
    }
  }
  if (probeCell) {
    const displayProbe = probeCellFromCoordinates(probeCell.latitude, probeCell.longitude, data);
    const x = (displayProbe.longitude + 180) / 360 * canvas.width;
    const y = (90 - displayProbe.latitude) / 180 * canvas.height;
    context.beginPath();
    context.arc(x, y, 7, 0, Math.PI * 2);
    context.strokeStyle = "#071b22";
    context.lineWidth = 5;
    context.stroke();
    context.beginPath();
    context.moveTo(x - 10, y); context.lineTo(x + 10, y);
    context.moveTo(x, y - 10); context.lineTo(x, y + 10);
    context.strokeStyle = "#ffffff";
    context.lineWidth = 2;
    context.stroke();
  }
}

function showObservedMetadata(data, mode) {
  const valid = data.values_c_hundredths.filter(value => value !== null);
  const summary = data.summary || {
    valid_ocean_cells: valid.length,
    minimum_c: Math.min(...valid) / 100,
    maximum_c: Math.max(...valid) / 100
  };
  const anomaly = mode === "anomaly";
  const subsurface = mode === "argo700";
  const error = mode === "error";
  const fieldClass = anomaly || subsurface ? "REFERENCE-BASED" : error ? "UNCERTAINTY" : "ABSOLUTE";
  fields.index.textContent = `ATLAS 10 · ${fieldClass} ${subsurface ? "PRESSURE-LAYER" : "SURFACE"} FIELD`;
  fields.name.textContent = subsurface ? `${data.pressure_dbar.toFixed(0)} dbar Temperature Anomaly` : anomaly ? "SST Anomaly" : error ? "Estimated SST Analysis Error" : "Sea Surface Temperature";
  fields.kind.textContent = subsurface ? `SCRIPPS RG ARGO · ${data.month}` : `NOAA OISST V2.1 · ${data.date}`;
  fields.summary.textContent = subsurface
    ? `Objectively mapped potential-temperature anomaly at ${data.pressure_dbar.toFixed(0)} dbar across ${summary.valid_ocean_cells.toLocaleString()} displayed cells. Range: ${summary.minimum_c.toFixed(2)}–${summary.maximum_c.toFixed(2)}°C.`
    : anomaly
    ? `Departure from NOAA's 1971–2000 daily climatology across ${summary.valid_ocean_cells.toLocaleString()} displayed ocean cells. Range: ${summary.minimum_c.toFixed(1)}–${summary.maximum_c.toFixed(1)}°C.`
    : error
      ? `Time-matched estimated analysis error across ${summary.valid_ocean_cells.toLocaleString()} displayed ocean cells. Range: ${summary.minimum_c.toFixed(2)}–${summary.maximum_c.toFixed(2)}°C.`
    : `Absolute surface temperature across ${summary.valid_ocean_cells.toLocaleString()} displayed ocean cells. Range: ${summary.minimum_c.toFixed(1)}–${summary.maximum_c.toFixed(1)}°C.`;
  fields.role.textContent = subsurface ? "subsurface departure from climatology" : anomaly ? "surface departure from climatology" : error ? "estimated surface analysis uncertainty" : "absolute surface thermal field";
  fields.depth.textContent = subsurface ? `${data.pressure_dbar.toFixed(0)} dbar pressure surface · not a fixed geometric depth` : "sea surface · 0 m product level";
  fields.clock.textContent = subsurface ? `monthly extension · ${data.month}` : `one day · ${data.date}`;
  fields.evidence.textContent = subsurface ? "Argo-only objective analysis · D2" : "observational analysis · D1";
  fields.boundary.textContent = data.boundary;
  fields.source.href = subsurface ? data.query_url : data.doi;
  fields.source.textContent = subsurface ? "Open the fixed Scripps product →" : "Open NOAA dataset record →";
  document.querySelector("#map-insight").textContent = subsurface
    ? `This depth-ladder view shows July 2026 departure from the RG seasonal climatology at ${data.pressure_dbar.toFixed(0)} dbar. Switch pressure levels to test whether a mapped anomaly is shallow or persists deeper; no level alone gives absolute warmth, water-column heat content, circulation, or delivery onto the Antarctic shelf.`
    : anomaly
    ? "This one-day surface map shows where temperature departed from the 1971–2000 daily baseline. It shows the pattern, not why it occurred or how much heat is stored below the surface."
    : error
      ? "This layer shows where the surface analysis carries higher or lower estimated error. It qualifies the mapped product; it is not forecast error or full-budget uncertainty."
      : "This one-day surface map shows the familiar warm tropics and cold poles, plus regional structure. Absolute surface temperature is not an anomaly, full-depth heat content, or heat transport.";
}

const latitudeBands = [
  ["Arctic", 60, 90],
  ["Northern midlatitudes", 30, 60],
  ["Tropics", -30, 30],
  ["Southern midlatitudes", -60, -30],
  ["Southern Ocean", -90, -60]
];

function valuePhrase(value, mode, includeSign = false) {
  if (mode === "anomaly" || mode === "argo700") {
    const sign = value > 0 ? "+" : value < 0 ? "−" : "";
    const direction = value > 0 ? "warmer" : value < 0 ? "cooler" : "at baseline";
    return `${sign}${Math.abs(value).toFixed(2)}°C ${direction}`;
  }
  const precision = mode === "error" ? 2 : 1;
  return `${includeSign && value > 0 ? "+" : ""}${value.toFixed(precision)}°C`;
}

function renderTextSummary(data, mode) {
  const [rows, columns] = data.shape;
  const table = document.querySelector("#summary-body");
  table.replaceChildren();
  for (const [name, south, north] of latitudeBands) {
    const values = [];
    for (let row = 0; row < rows; row += 1) {
      const latitude = data.latitude.start + row * data.latitude.step;
      const inBand = latitude >= south && (north === 90 ? latitude <= north : latitude < north);
      if (!inBand) continue;
      for (let column = 0; column < columns; column += 1) {
        const encoded = data.values_c_hundredths[row * columns + column];
        if (encoded !== null) values.push(encoded / 100);
      }
    }
    const mean = values.reduce((total, value) => total + value, 0) / values.length;
    const row = document.createElement("tr");
    const cells = [name, valuePhrase(mean, mode), `${valuePhrase(Math.min(...values), mode)} to ${valuePhrase(Math.max(...values), mode)}`, values.length.toLocaleString()];
    cells.forEach((content, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) cell.scope = "row";
      cell.textContent = content;
      row.append(cell);
    });
    table.append(row);
  }
  const fieldName = mode === "argo700" ? `${data.pressure_dbar.toFixed(0)} dbar potential-temperature anomaly relative to the RG 2019 climatology` : mode === "anomaly" ? "SST anomaly relative to 1971–2000" : mode === "error" ? "estimated SST analysis error" : "absolute sea surface temperature";
  document.querySelector("#map-a11y-summary").textContent = `Text equivalent for ${fieldName} on ${data.date || data.month}: five latitude-band rows report mean, range, and valid-cell count. Missing and land cells are excluded.`;
  document.querySelector("#summary-caption").textContent = `Latitude-band statistics for ${fieldName}; values are not area-weighted.`;
}

function normalizedLongitude(longitude) {
  return ((longitude + 180) % 360 + 360) % 360 - 180;
}

function probeCellFromCoordinates(latitude, longitude, data = window.OCEANLINES_OISST) {
  const [rows, columns] = data.shape;
  const boundedLatitude = Math.max(-90, Math.min(90, latitude));
  const longitude360 = (normalizedLongitude(longitude) + 360) % 360;
  const row = Math.max(0, Math.min(rows - 1, Math.round((boundedLatitude - data.latitude.start) / data.latitude.step)));
  const rawColumn = Math.round((longitude360 - data.longitude.start) / data.longitude.step);
  const column = ((rawColumn % columns) + columns) % columns;
  return {
    row,
    column,
    latitude: data.latitude.start + row * data.latitude.step,
    longitude: normalizedLongitude(data.longitude.start + column * data.longitude.step)
  };
}

function pairedRingRows(magnitude, data = window.OCEANLINES_OISST) {
  const bounded = Math.max(0, Math.min(89, Math.abs(magnitude)));
  const north = probeCellFromCoordinates(bounded, 0, data);
  const south = probeCellFromCoordinates(-bounded, 0, data);
  return { requested: bounded, north: { row: north.row, latitude: north.latitude }, south: { row: south.row, latitude: south.latitude } };
}

function longestCyclicRun(flags) {
  if (flags.every(Boolean)) return flags.length;
  let longest = 0;
  let current = 0;
  for (let index = 0; index < flags.length * 2; index += 1) {
    current = flags[index % flags.length] ? Math.min(current + 1, flags.length) : 0;
    longest = Math.max(longest, current);
  }
  return longest;
}

function ringStatistics(data, ring, geometryData = window.OCEANLINES_OISST) {
  const columns = data.shape[1];
  const encoded = data.values_c_hundredths.slice(ring.row * columns, (ring.row + 1) * columns);
  const geometryEncoded = geometryData.values_c_hundredths.slice(ring.row * columns, (ring.row + 1) * columns);
  const ocean = geometryEncoded.map(value => value !== null);
  const values = encoded.filter(value => value !== null).map(value => value / 100);
  const arcs = ocean.every(Boolean) ? 1 : ocean.reduce((count, value, index) => count + (value && !ocean[(index - 1 + columns) % columns] ? 1 : 0), 0);
  const mean = values.length ? values.reduce((total, value) => total + value, 0) / values.length : null;
  return {
    encoded,
    valid: values.length,
    coverage: values.length / columns * 100,
    arcs,
    longestDegrees: longestCyclicRun(ocean) * Math.abs(data.longitude.step),
    mean,
    minimum: values.length ? Math.min(...values) : null,
    maximum: values.length ? Math.max(...values) : null
  };
}

function renderRingStrip(canvas, data, statistics, colorFunction) {
  const context = canvas.getContext("2d");
  const columns = data.shape[1];
  const width = canvas.width / columns;
  context.fillStyle = "#c8bda5";
  context.fillRect(0, 0, canvas.width, canvas.height);
  statistics.encoded.forEach((value, column) => {
    if (value === null) return;
    const longitude = normalizedLongitude(data.longitude.start + column * data.longitude.step);
    const x = (longitude + 180) / 360 * canvas.width - width / 2;
    context.fillStyle = colorFunction(value / 100);
    context.fillRect(x, 0, Math.ceil(width), canvas.height);
    if (x < 0) context.fillRect(x + canvas.width, 0, Math.ceil(width), canvas.height);
    if (x + width > canvas.width) context.fillRect(x - canvas.width, 0, Math.ceil(width), canvas.height);
  });
  context.strokeStyle = "rgba(255,255,255,.45)";
  for (let longitude = 60; longitude < 360; longitude += 60) {
    context.beginPath(); context.moveTo(longitude / 360 * canvas.width, 0); context.lineTo(longitude / 360 * canvas.width, canvas.height); context.stroke();
  }
}

function renderRingComparison(data, mode, colorFunction) {
  const rings = pairedRingRows(ringLatitude, data);
  const specifications = [
    ["north", "Northern", rings.north, document.querySelector("#north-ring")],
    ["south", "Southern", rings.south, document.querySelector("#south-ring")]
  ];
  const body = document.querySelector("#ring-body");
  body.replaceChildren();
  const summaries = [];
  for (const [id, name, ring, canvas] of specifications) {
    const statistics = ringStatistics(data, ring);
    renderRingStrip(canvas, data, statistics, colorFunction);
    const coordinate = coordinatePhrase(ring.latitude, "N", "S");
    document.querySelector(`#${id}-ring-label`).textContent = `${name} ring · ${coordinate}`;
    canvas.setAttribute("aria-label", `${name} longitude strip at ${coordinate}; land-or-missing gaps use beige and the displayed field uses the active map scale.`);
    const row = document.createElement("tr");
    const range = statistics.mean === null ? "No ocean values" : `${valuePhrase(statistics.mean, mode)} mean; ${valuePhrase(statistics.minimum, mode)} to ${valuePhrase(statistics.maximum, mode)}`;
    const cells = [`${name} · ${coordinate}`, `${statistics.valid}/${data.shape[1]} cells · ${statistics.coverage.toFixed(1)}%`, String(statistics.arcs), `${statistics.longestDegrees.toFixed(0)}° longitude`, range];
    cells.forEach((content, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) cell.scope = "row";
      cell.textContent = content;
      row.append(cell);
    });
    body.append(row);
    summaries.push(`${name} ${coordinate}: ${statistics.coverage.toFixed(1)}% analyzed-water coverage in ${statistics.arcs} arc${statistics.arcs === 1 ? "" : "s"}; longest ${statistics.longestDegrees.toFixed(0)}°`);
  }
  const fieldName = mode === "anomaly" ? "SST anomaly" : mode === "error" ? "estimated analysis error" : "absolute SST";
  document.querySelector("#ring-summary").textContent = `${summaries.join(". ")}. Display-grid geometry with ${fieldName}; not a current, barrier strength, heat-content, or transport measurement.`;
  document.querySelector("#ring-caption").textContent = `Latitude-ring geometry and ${fieldName} statistics; values are not area-weighted.`;
  renderPolarMirrors(data, mode, colorFunction);
  renderLatitudeLadder();
}

function renderPolarMirror(canvas, data, colorFunction, hemisphere) {
  const context = canvas.getContext("2d");
  const size = canvas.width;
  const center = size / 2;
  const radius = center - 10;
  const capLatitude = 40;
  const image = context.createImageData(size, size);
  const colorCache = new Map();
  const [rows, columns] = data.shape;
  const background = [6, 23, 28];
  const missing = [200, 189, 165];
  const colorFor = encoded => {
    if (encoded === null) return missing;
    if (!colorCache.has(encoded)) colorCache.set(encoded, colorFunction(encoded / 100).match(/\d+/g).map(Number));
    return colorCache.get(encoded);
  };
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const dx = x + 0.5 - center;
      const dy = y + 0.5 - center;
      const distance = Math.hypot(dx, dy);
      let color = background;
      if (distance <= radius) {
        const magnitude = 90 - distance / radius * (90 - capLatitude);
        const latitude = hemisphere === "north" ? magnitude : -magnitude;
        const longitude = Math.atan2(dx, -dy) * 180 / Math.PI;
        const cell = probeCellFromCoordinates(latitude, longitude, data);
        color = colorFor(data.values_c_hundredths[cell.row * columns + cell.column]);
      }
      const offset = (y * size + x) * 4;
      image.data[offset] = color[0];
      image.data[offset + 1] = color[1];
      image.data[offset + 2] = color[2];
      image.data[offset + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);
  context.strokeStyle = "rgba(255,255,255,.35)";
  context.lineWidth = 1;
  for (const latitude of [40, 60, 80]) {
    const ringRadius = (90 - latitude) / (90 - capLatitude) * radius;
    context.beginPath(); context.arc(center, center, ringRadius, 0, Math.PI * 2); context.stroke();
  }
  for (let longitude = 0; longitude < 360; longitude += 90) {
    const angle = longitude * Math.PI / 180;
    context.beginPath(); context.moveTo(center, center);
    context.lineTo(center + Math.sin(angle) * radius, center - Math.cos(angle) * radius); context.stroke();
  }
  const selected = pairedRingRows(ringLatitude, data)[hemisphere];
  const selectedMagnitude = Math.abs(selected.latitude);
  const selectedVisible = selectedMagnitude >= capLatitude;
  if (selectedVisible) {
    const selectedRadius = (90 - selectedMagnitude) / (90 - capLatitude) * radius;
    context.beginPath(); context.arc(center, center, selectedRadius, 0, Math.PI * 2);
    context.strokeStyle = "#071b22"; context.lineWidth = 6; context.stroke();
    context.beginPath(); context.arc(center, center, selectedRadius, 0, Math.PI * 2);
    context.strokeStyle = "#ffb250"; context.lineWidth = 2; context.setLineDash([9, 6]); context.stroke();
    context.setLineDash([]);
  }
  return { selected, selectedVisible };
}

function renderPolarMirrors(data, mode, colorFunction) {
  const northCanvas = document.querySelector("#north-polar");
  const southCanvas = document.querySelector("#south-polar");
  const north = renderPolarMirror(northCanvas, data, colorFunction, "north");
  const south = renderPolarMirror(southCanvas, data, colorFunction, "south");
  const fieldName = mode === "anomaly" ? "SST anomaly" : mode === "error" ? "estimated analysis error" : "absolute SST";
  const selectedText = north.selectedVisible && south.selectedVisible
    ? `Amber circles mark sampled ${coordinatePhrase(north.selected.latitude, "N", "S")} and ${coordinatePhrase(south.selected.latitude, "N", "S")}.`
    : `The selected ${ringLatitude.toFixed(1)}° request lies outside at least one 40–90° cap, so no out-of-domain circle is drawn.`;
  const orientation = "Both caps place 0° longitude at top and 90°E at right; the south is an intentional comparison mirror.";
  document.querySelector("#polar-summary").textContent = `${fieldName} on ${data.date}. ${selectedText} ${orientation} Surface display only; not bathymetry, sea ice, circulation, or heat transport.`;
  northCanvas.setAttribute("aria-label", `Northern 40–90° polar cap showing ${fieldName}. ${selectedText} ${orientation}`);
  southCanvas.setAttribute("aria-label", `Southern 40–90° polar comparison mirror showing ${fieldName}. ${selectedText} ${orientation}`);
}

function latitudeLadder(data = window.OCEANLINES_OISST) {
  const ladder = [];
  for (let magnitude = 0; magnitude <= 88; magnitude += 2) {
    const rings = pairedRingRows(magnitude, data);
    ladder.push({
      magnitude,
      north: { ...rings.north, ...ringStatistics(data, rings.north, data) },
      south: { ...rings.south, ...ringStatistics(data, rings.south, data) }
    });
  }
  return ladder;
}

function renderLatitudeLadder() {
  const data = window.OCEANLINES_OISST;
  const ladder = latitudeLadder(data);
  const canvas = document.querySelector("#continuity-chart");
  const context = canvas.getContext("2d");
  const margin = { left: 54, right: 20, top: 20, bottom: 42 };
  const width = canvas.width - margin.left - margin.right;
  const height = canvas.height - margin.top - margin.bottom;
  const xFor = magnitude => margin.left + Math.min(88, magnitude) / 88 * width;
  const yFor = coverage => margin.top + (100 - coverage) / 100 * height;
  context.fillStyle = "#06171c";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.font = "11px ui-monospace, monospace";
  context.textAlign = "right";
  context.textBaseline = "middle";
  for (const coverage of [0, 25, 50, 75, 100]) {
    const y = yFor(coverage);
    context.beginPath(); context.moveTo(margin.left, y); context.lineTo(canvas.width - margin.right, y);
    context.strokeStyle = "rgba(146,170,169,.25)"; context.lineWidth = 1; context.stroke();
    context.fillStyle = "#92aaa9"; context.fillText(`${coverage}%`, margin.left - 8, y);
  }
  context.textAlign = "center";
  context.textBaseline = "top";
  for (const magnitude of [0, 30, 60, 88]) {
    const x = xFor(magnitude);
    context.beginPath(); context.moveTo(x, margin.top); context.lineTo(x, canvas.height - margin.bottom);
    context.strokeStyle = "rgba(146,170,169,.14)"; context.stroke();
    context.fillStyle = "#92aaa9"; context.fillText(`${magnitude}°`, x, canvas.height - margin.bottom + 10);
  }
  const drawSeries = (hemisphere, color, dashed) => {
    context.beginPath();
    ladder.forEach((point, index) => {
      const x = xFor(point.magnitude);
      const y = yFor(point[hemisphere].coverage);
      if (index === 0) context.moveTo(x, y); else context.lineTo(x, y);
    });
    context.strokeStyle = "#071b22"; context.lineWidth = 7; context.setLineDash([]); context.stroke();
    context.strokeStyle = color; context.lineWidth = 3; context.setLineDash(dashed ? [10, 7] : []); context.stroke();
    context.setLineDash([]);
  };
  drawSeries("north", "#5ee2d6", false);
  drawSeries("south", "#ff6f61", true);
  const selected = pairedRingRows(ringLatitude, data);
  const selectedNorth = ringStatistics(data, selected.north, data);
  const selectedSouth = ringStatistics(data, selected.south, data);
  const selectedX = xFor(ringLatitude);
  context.beginPath(); context.moveTo(selectedX, margin.top); context.lineTo(selectedX, canvas.height - margin.bottom);
  context.strokeStyle = "#ffb250"; context.lineWidth = 2; context.stroke();
  for (const [statistics, color] of [[selectedNorth, "#5ee2d6"], [selectedSouth, "#ff6f61"]]) {
    context.beginPath(); context.arc(selectedX, yFor(statistics.coverage), 6, 0, Math.PI * 2);
    context.fillStyle = color; context.fill(); context.strokeStyle = "#071b22"; context.lineWidth = 3; context.stroke();
  }
  const body = document.querySelector("#continuity-body");
  body.replaceChildren();
  ladder.forEach(point => {
    const row = document.createElement("tr");
    const cells = [
      `${point.magnitude}°`,
      coordinatePhrase(point.north.latitude, "N", "S"),
      `${point.north.valid}/${data.shape[1]} · ${point.north.coverage.toFixed(1)}%`,
      `${point.north.arcs} / ${point.north.longestDegrees.toFixed(0)}°`,
      coordinatePhrase(point.south.latitude, "N", "S"),
      `${point.south.valid}/${data.shape[1]} · ${point.south.coverage.toFixed(1)}%`,
      `${point.south.arcs} / ${point.south.longestDegrees.toFixed(0)}°`
    ];
    cells.forEach((content, index) => {
      const cell = document.createElement(index === 0 ? "th" : "td");
      if (index === 0) cell.scope = "row";
      cell.textContent = content;
      row.append(cell);
    });
    body.append(row);
  });
  const nearCircumpolar = hemisphere => ladder.find(point => point[hemisphere].coverage >= 95 && point[hemisphere].longestDegrees >= 300);
  const northThreshold = nearCircumpolar("north");
  const southThreshold = nearCircumpolar("south");
  const selectedText = `Selected ${ringLatitude.toFixed(1)}° request: north ${selectedNorth.coverage.toFixed(1)}%, south ${selectedSouth.coverage.toFixed(1)}%.`;
  const thresholdText = `First scan rows meeting the declared ≥95% coverage and ≥300° longest-arc threshold: south ${southThreshold.magnitude}° request (${coordinatePhrase(southThreshold.south.latitude, "N", "S")}); north ${northThreshold.magnitude}° request (${coordinatePhrase(northThreshold.north.latitude, "N", "S")}).`;
  document.querySelector("#continuity-summary").textContent = `${thresholdText} ${selectedText} Product-mask topology only; not a circulation boundary.`;
  canvas.setAttribute("aria-label", `Latitude continuity ladder. Northern coverage is a solid line and southern coverage is dashed. ${thresholdText} ${selectedText}`);
}

function coordinatePhrase(value, positive, negative) {
  if (Math.abs(value) < 0.005) return "0.00°";
  return `${Math.abs(value).toFixed(2)}°${value > 0 ? positive : negative}`;
}

function probeValue(data, latitude, longitude, mode) {
  const halfStep = Math.abs(data.latitude.step) / 2;
  const domainSouth = data.latitude.start - halfStep;
  const domainNorth = data.latitude.start + (data.shape[0] - 1) * data.latitude.step + halfStep;
  if (latitude < domainSouth || latitude > domainNorth) return "outside source domain";
  const cell = probeCellFromCoordinates(latitude, longitude, data);
  const encoded = data.values_c_hundredths[cell.row * data.shape[1] + cell.column];
  if (encoded === null) return "land or missing";
  return valuePhrase(encoded / 100, mode);
}

function activeObservedField() {
  if (currentMode === "argo700") return [argoLayers[currentArgoPressure], anomalyColor];
  if (currentMode === "anomaly") return [window.OCEANLINES_OISST_ANOMALY, anomalyColor];
  if (currentMode === "error") return [window.OCEANLINES_OISST_ERROR, errorColor];
  return [window.OCEANLINES_OISST, temperatureColor];
}

function updateAtlasUrl() {
  const url = new URL(window.location.href);
  if (currentMode === "conceptual") {
    url.searchParams.delete("mode");
    url.searchParams.delete("lat");
    url.searchParams.delete("lon");
    url.searchParams.delete("ring");
    url.searchParams.delete("pressure");
    if (currentConceptualView === "reference") url.searchParams.delete("view");
    else url.searchParams.set("view", currentConceptualView);
    if (currentLens !== "waters") url.searchParams.set("lens", currentLens); else url.searchParams.delete("lens");
    for (const [parameter, selector] of [["depth", "#filter-depth"], ["property", "#filter-property"], ["clock", "#filter-clock"]]) {
      const value = document.querySelector(selector).value;
      if (value === "all") url.searchParams.delete(parameter); else url.searchParams.set(parameter, value);
    }
  } else {
    url.searchParams.set("mode", currentMode);
    url.searchParams.set("ring", ringLatitude.toFixed(3));
    if (probeCell) {
      url.searchParams.set("lat", probeCell.latitude.toFixed(3));
      url.searchParams.set("lon", probeCell.longitude.toFixed(3));
    }
    if (currentMode === "argo700") url.searchParams.set("pressure", String(currentArgoPressure));
    else url.searchParams.delete("pressure");
    url.searchParams.delete("view");
    for (const parameter of ["lens", "depth", "property", "clock"]) url.searchParams.delete(parameter);
  }
  if (selectedProvinceCode || requestedProvinceCode) url.searchParams.set("province", selectedProvinceCode || requestedProvinceCode);
  else url.searchParams.delete("province");
  if (featureView) url.searchParams.set("feature", selectedZone.id);
  else url.searchParams.delete("feature");
  window.history.replaceState({}, "", url);
}

function relationKey(provinceCode, featureId) {
  return `${provinceCode}::${featureId}`;
}

async function sha256Text(value) {
  if (!window.crypto?.subtle) return "unavailable";
  const bytes = new TextEncoder().encode(value);
  const digest = await window.crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}

function geometryChildren(group) {
  return [...group.querySelectorAll("path,ellipse,rect,circle,polygon,polyline")];
}

function boxesOverlap(a, b) {
  return a.x <= b.x + b.width && a.x + a.width >= b.x && a.y <= b.y + b.height && a.y + a.height >= b.y;
}

function featureContainsPoint(group, point) {
  return geometryChildren(group).some(element => {
    try {
      return Boolean(element.isPointInFill?.(point) || element.isPointInStroke?.(point));
    } catch (_) {
      return false;
    }
  });
}

function featurePathSamples(group, pathStep) {
  let byStep = featureSampleCache.get(group);
  if (!byStep) { byStep = new Map(); featureSampleCache.set(group, byStep); }
  if (byStep.has(pathStep)) return byStep.get(pathStep);
  const points = [];
  for (const element of geometryChildren(group)) {
    if (!element.getTotalLength || !element.getPointAtLength) continue;
    let length = 0;
    try { length = element.getTotalLength(); } catch (_) { continue; }
    const samples = Math.max(1, Math.ceil(length / pathStep));
    for (let index = 0; index <= samples; index += 1) {
      const point = element.getPointAtLength(length * index / samples);
      points.push(new DOMPoint(point.x, point.y));
    }
  }
  byStep.set(pathStep, points);
  return points;
}

function featureInteriorSamples(group, gridStep) {
  let byStep = featureGridCache.get(group);
  if (!byStep) { byStep = new Map(); featureGridCache.set(group, byStep); }
  if (byStep.has(gridStep)) return byStep.get(gridStep);
  const box = group.getBBox();
  const points = [];
  for (let y = box.y + gridStep / 2; y <= box.y + box.height; y += gridStep) {
    for (let x = box.x + gridStep / 2; x <= box.x + box.width; x += gridStep) {
      const point = new DOMPoint(x, y);
      if (featureContainsPoint(group, point)) points.push(point);
    }
  }
  byStep.set(gridStep, points);
  return points;
}

function sampledPairHit(provincePath, featureGroup, pathStep, gridStep) {
  const provinceBox = provincePath.getBBox();
  const featureBox = featureGroup.getBBox();
  if (!boxesOverlap(provinceBox, featureBox)) return false;
  for (const point of featurePathSamples(featureGroup, pathStep)) {
    if (provincePath.isPointInFill(point)) return true;
  }
  for (const point of featureInteriorSamples(featureGroup, gridStep)) {
    if (point.x < provinceBox.x || point.x > provinceBox.x + provinceBox.width || point.y < provinceBox.y || point.y > provinceBox.y + provinceBox.height) continue;
    if (provincePath.isPointInFill(point)) return true;
  }
  return false;
}

function classifyRenderedOverlap(provinceGroup, featureGroup) {
  const provincePath = provinceGroup.querySelector("path");
  if (!provincePath?.isPointInFill || !window.DOMPoint) return { relation: "none", hitMethod: "unsupported" };
  if (sampledPairHit(provincePath, featureGroup, RELATION_METHOD.coarsePathStep, RELATION_METHOD.coarseGridStep)) {
    return { relation: "overlap", hitMethod: "coarse-sampled-svg" };
  }
  if (sampledPairHit(provincePath, featureGroup, RELATION_METHOD.finePathStep, RELATION_METHOD.fineGridStep)) {
    return { relation: "near-contact", hitMethod: "fine-sampled-svg" };
  }
  return { relation: "none", hitMethod: "sampled-svg" };
}

function evidenceClass(zone) {
  const evidence = zone.evidence.toLowerCase();
  if (evidence.includes("modeled") || evidence.includes("modelled") || evidence.includes(" / ")) return "MODELED/MIXED";
  if (evidence.includes("observational")) return "OBSERVATIONAL";
  if (evidence.includes("synthesis")) return "SYNTHESIS";
  return "CONCEPTUAL";
}

function featureMapName(zone) {
  return zone.name
    .replace("Subtropical Gyre", "Gyre")
    .replace("Oxygen Minimum Zone", "OMZ")
    .replace("Eastern Tropical ", "E. Tropical ")
    .replace("Antarctic Circumpolar Current", "Antarctic Circumpolar")
    .replace("Continental Shelf Break", "Shelf Break");
}

function rectanglesMeet(a, b) {
  return a.x < b.x + b.width + 10 && a.x + a.width + 10 > b.x && a.y < b.y + b.height + 7 && a.y + a.height + 7 > b.y;
}

function pointFallsInOcean(x, y) {
  const point = new DOMPoint(x, y);
  return provinceGroups.some(group => {
    try { return group.querySelector("path")?.isPointInFill(point); } catch (_) { return false; }
  });
}

function renderFeatureLabels() {
  const svg = document.querySelector("#feature-shape-host > svg");
  if (!svg) return;
  svg.querySelector(".feature-label-layer")?.remove();
  const namespace = "http://www.w3.org/2000/svg";
  const layer = document.createElementNS(namespace, "g");
  layer.setAttribute("class", "feature-label-layer");
  layer.setAttribute("aria-hidden", "true");
  const occupied = [];
  const visible = zones.filter(zone => {
    const group = featureGroups.find(item => item.dataset.id === zone.id);
    return group && !group.hasAttribute("hidden") && (currentLens !== "all" || zone.id === selectedZone.id);
  });
  visible.sort((a, b) => Number(b.id === selectedZone.id) - Number(a.id === selectedZone.id) || a.n - b.n);
  for (const zone of visible) {
    // Curatorial anchors position labels only; they never participate in relation classification.
    const anchorX = zone.x * 16;
    const anchorY = zone.y * 10.5;
    const name = featureMapName(zone);
    const width = Math.min(310, Math.max(78, name.length * 9.2));
    const candidates = [[0, -28], [0, 28], [0, -58], [0, 58], [-90, -28], [90, -28], [-90, 28], [90, 28]];
    let placement = null;
    for (const [dx, dy] of candidates) {
      const seamMinimum = anchorX < 800 ? width / 2 + 12 : 800 + width / 2 + 12;
      const seamMaximum = anchorX < 800 ? 800 - width / 2 - 12 : 1600 - width / 2 - 12;
      const x = Math.max(seamMinimum, Math.min(seamMaximum, anchorX + dx));
      const y = Math.max(22, Math.min(1028, anchorY + dy));
      const box = { x: x - width / 2, y: y - 13, width, height: 26 };
      if (pointFallsInOcean(x, y) && !occupied.some(other => rectanglesMeet(box, other))) { placement = { x, y, box }; break; }
    }
    if (!placement) continue;
    occupied.push(placement.box);
    if (Math.hypot(placement.x - anchorX, placement.y - anchorY) > 35) {
      const leader = document.createElementNS(namespace, "path");
      leader.setAttribute("class", "feature-label-leader");
      leader.setAttribute("d", `M ${anchorX.toFixed(1)} ${anchorY.toFixed(1)} L ${placement.x.toFixed(1)} ${(placement.y + 5).toFixed(1)}`);
      layer.append(leader);
    }
    const label = document.createElementNS(namespace, "text");
    label.setAttribute("class", `feature-label${zone.id === selectedZone.id ? " selected" : ""}`);
    label.setAttribute("x", placement.x.toFixed(1));
    label.setAttribute("y", placement.y.toFixed(1));
    label.textContent = name;
    layer.append(label);
  }
  svg.append(layer);
}

function verifyRelationSmokeFixture() {
  const fixture = window.OSW_RELATION_SMOKE_FIXTURE || [];
  const failures = fixture.filter(expected => relationMatrix.get(relationKey(expected.provinceCode, expected.featureId))?.relation !== expected.relation);
  window.OSW_RELATION_SMOKE = Object.freeze({ passed: failures.length === 0, checked: fixture.length, failures });
  document.querySelector("#relation-panel").dataset.smoke = failures.length ? "failed" : "passed";
  if (failures.length) console.error("OSW relation smoke fixture failed", failures);
}

async function buildRelationMatrix() {
  if (relationMatrixBuilding || relationMatrix.size || provinceGroups.length !== 56 || featureGroups.length !== 36) return;
  relationMatrixBuilding = true;
  const hiddenFeatures = featureGroups.filter(group => group.hasAttribute("hidden"));
  hiddenFeatures.forEach(group => group.removeAttribute("hidden"));
  for (let provinceIndex = 0; provinceIndex < provinceGroups.length; provinceIndex += 1) {
    const province = provinceGroups[provinceIndex];
    for (const feature of featureGroups) {
      const classification = classifyRenderedOverlap(province, feature);
      relationMatrix.set(relationKey(province.dataset.code, feature.dataset.id), {
        provinceCode: province.dataset.code,
        featureId: feature.dataset.id,
        ...classification
      });
    }
    if (provinceIndex % 2 === 1) {
      document.querySelector("#relation-summary").textContent = `Building sampled rendered overlap… ${provinceIndex + 1} of 56 ocean states.`;
      await new Promise(resolve => window.setTimeout(resolve, 0));
    }
  }
  hiddenFeatures.forEach(group => group.setAttribute("hidden", ""));
  window.OSW_RELATION_MATRIX = relationMatrix;
  window.OSW_RELATION_METHOD = RELATION_METHOD;
  verifyRelationSmokeFixture();
  relationMatrixBuilding = false;
  document.querySelector("#relation-export").disabled = false;
  if (selectedProvinceCode) renderProvinceRelations(provinceGroups.find(group => group.dataset.code === selectedProvinceCode));
  else renderFeatureRelations(selectedZone);
}

function maybeBuildRelationMatrix() {
  if (provinceGroups.length === 56 && featureGroups.length === 36) window.requestAnimationFrame(buildRelationMatrix);
}

function recordsForProvince(code) {
  return zones.map(zone => ({ zone, record: relationMatrix.get(relationKey(code, zone.id)) })).filter(item => item.record);
}

function recordsForFeature(id) {
  return provinceGroups.map(province => ({ province, record: relationMatrix.get(relationKey(province.dataset.code, id)) })).filter(item => item.record);
}

function clearRelationClasses() {
  document.querySelectorAll("#feature-shape-host .feature-shape,#province-map-host .province").forEach(element => {
    element.classList.remove("related", "near-contact", "relation-muted");
  });
}

function renderRelationButtons(container, items, near = false) {
  container.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("span");
    empty.textContent = "None at the declared tolerance";
    container.append(empty);
    return;
  }
  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.classList.toggle("near", near);
    if (item.zone) {
      button.textContent = `${item.zone.name} · ${item.zone.lens}`;
      button.addEventListener("click", () => selectZone(item.zone));
    } else {
      button.textContent = `${item.province.dataset.code} · ${item.province.dataset.name}`;
      button.addEventListener("click", () => selectProvince(item.province));
    }
    container.append(button);
  }
}

function renderProvinceRelations(group) {
  if (!group || !relationMatrix.size) return;
  relationSubject = "province";
  clearRelationClasses();
  const records = recordsForProvince(group.dataset.code);
  const overlaps = records.filter(item => item.record.relation === "overlap");
  const near = records.filter(item => item.record.relation === "near-contact");
  const relatedIds = new Set(overlaps.map(item => item.zone.id));
  const nearIds = new Set(near.map(item => item.zone.id));
  featureGroups.forEach(feature => {
    feature.classList.toggle("related", relatedIds.has(feature.dataset.id));
    feature.classList.toggle("near-contact", nearIds.has(feature.dataset.id));
    feature.classList.toggle("relation-muted", !relatedIds.has(feature.dataset.id) && !nearIds.has(feature.dataset.id));
  });
  document.querySelector("#relation-title").textContent = `${group.dataset.code} · schematic rendered overlap`;
  document.querySelector("#relation-summary").textContent = `${overlaps.length} feature shapes overlap ${group.dataset.name}; ${near.length} additional pair${near.length === 1 ? " is" : "s are"} resolution-dependent near-contacts.`;
  renderRelationButtons(document.querySelector("#relation-overlaps"), overlaps);
  renderRelationButtons(document.querySelector("#relation-near"), near, true);
}

function renderFeatureRelations(zone) {
  if (!zone || !relationMatrix.size || relationSubject === "province" && selectedProvinceCode) return;
  relationSubject = "feature";
  clearRelationClasses();
  const records = recordsForFeature(zone.id);
  const overlaps = records.filter(item => item.record.relation === "overlap");
  const near = records.filter(item => item.record.relation === "near-contact");
  const relatedCodes = new Set(overlaps.map(item => item.province.dataset.code));
  const nearCodes = new Set(near.map(item => item.province.dataset.code));
  featureGroups.forEach(feature => feature.classList.toggle("relation-muted", feature.dataset.id !== zone.id));
  provinceGroups.forEach(province => {
    province.classList.toggle("related", relatedCodes.has(province.dataset.code));
    province.classList.toggle("near-contact", nearCodes.has(province.dataset.code));
    province.classList.toggle("relation-muted", !relatedCodes.has(province.dataset.code) && !nearCodes.has(province.dataset.code));
  });
  document.querySelector("#relation-title").textContent = `${zone.name} · schematic rendered overlap`;
  document.querySelector("#relation-summary").textContent = `${zone.name} overlaps ${overlaps.length} approximate ocean state${overlaps.length === 1 ? "" : "s"}; ${near.length} additional pair${near.length === 1 ? " is" : "s are"} resolution-dependent near-contacts.`;
  renderRelationButtons(document.querySelector("#relation-overlaps"), overlaps);
  renderRelationButtons(document.querySelector("#relation-near"), near, true);
}

function provinceFeatureMatches(group, relation = "overlap") {
  if (!relationMatrix.size) return [];
  return recordsForProvince(group.dataset.code).filter(item => item.record.relation === relation).map(item => item.zone);
}

function exportRelationMatrix() {
  if (relationMatrix.size !== 2016) return;
  const header = ["algorithm_version", "province_svg_sha256", "feature_svg_sha256", "province_edition", "catalog_version", "province_code", "feature_number", "feature_id", "evidence_class", "relation", "hit_method", "coarse_path_step", "coarse_grid_step", "fine_path_step", "fine_grid_step"];
  const quote = value => `"${String(value).replaceAll('"', '""')}"`;
  const rows = [header.map(quote).join(",")];
  [...provinceGroups].sort((a, b) => a.dataset.code.localeCompare(b.dataset.code)).forEach(province => {
    zones.forEach(zone => {
      const record = relationMatrix.get(relationKey(province.dataset.code, zone.id));
      rows.push([RELATION_METHOD.version, provinceSvgSha256, featureSvgSha256, "classic-56-approximate", "atlas-08", province.dataset.code, zone.n, zone.id, evidenceClass(zone), record.relation, record.hitMethod, RELATION_METHOD.coarsePathStep, RELATION_METHOD.coarseGridStep, RELATION_METHOD.finePathStep, RELATION_METHOD.fineGridStep].map(quote).join(","));
    });
  });
  const url = URL.createObjectURL(new Blob([`${rows.join("\n")}\n`], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "osw-schematic-rendered-overlap.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function clearRelationSpotlight() {
  relationSubject = null;
  clearRelationClasses();
  document.querySelector("#relation-title").textContent = "Schematic rendered overlap";
  document.querySelector("#relation-summary").textContent = "Spotlight cleared. Select a province or feature to inspect its sampled display relationships.";
  document.querySelector("#relation-overlaps").replaceChildren();
  document.querySelector("#relation-near").replaceChildren();
}

function applyMapZoom() {
  const viewport = document.querySelector("#map-viewport");
  const stage = document.querySelector("#map-stage");
  const view = featureView || provinceView;
  if (!view) {
    viewport.style.transform = "none";
    return;
  }
  const [x, y, width, height] = view;
  const scale = 1600 / width;
  const translateX = -x / 1600 * stage.clientWidth * scale;
  const translateY = -y / 1050 * stage.clientHeight * scale;
  viewport.style.transform = `matrix(${scale},0,0,${scale},${translateX},${translateY})`;
}

function expandedMapView(box, padding = 62) {
  const minimumX = box.x;
  const minimumY = box.y;
  const maximumX = box.x + box.width;
  const maximumY = box.y + box.height;
  let x = Math.max(0, minimumX - padding);
  let y = Math.max(0, minimumY - padding);
  let width = Math.min(1600 - x, maximumX - minimumX + padding * 2);
  let height = Math.min(1050 - y, maximumY - minimumY + padding * 2);
  const aspect = 1600 / 1050;
  if (width / height < aspect) {
    const expandedWidth = Math.min(1600, height * aspect);
    x = Math.max(0, Math.min(1600 - expandedWidth, x - (expandedWidth - width) / 2));
    width = expandedWidth;
  } else {
    const expandedHeight = Math.min(1050, width / aspect);
    y = Math.max(0, Math.min(1050 - expandedHeight, y - (expandedHeight - height) / 2));
    height = expandedHeight;
  }
  return [x, y, width, height];
}

function expandedProvinceView(group) {
  const [minimumX, minimumY, maximumX, maximumY] = group.dataset.viewbox.split(" ").map(Number);
  return expandedMapView({ x: minimumX, y: minimumY, width: maximumX - minimumX, height: maximumY - minimumY });
}

function selectProvince(group, updateUrl = true) {
  if (!group) return;
  relationSubject = "province";
  selectedProvinceCode = group.dataset.code;
  requestedProvinceCode = null;
  provinceView = expandedProvinceView(group);
  featureView = null;
  document.querySelectorAll("#province-map-host .province").forEach(item => item.classList.toggle("selected", item === group));
  document.querySelector("#province-select").value = selectedProvinceCode;
  document.querySelector("#province-reset").disabled = false;
  document.querySelector("#province-status").textContent = `${selectedProvinceCode} · ${group.dataset.name} · click another state or change any view.`;
  if (currentMode === "conceptual") {
    const related = provinceFeatureMatches(group);
    const near = provinceFeatureMatches(group, "near-contact");
    fields.index.textContent = `PROVINCE ${selectedProvinceCode} · ${group.dataset.biome.toUpperCase()}`;
    fields.name.textContent = group.dataset.name;
    fields.kind.textContent = `${group.dataset.basin.toUpperCase()} · CLASSIC 56`;
    fields.summary.textContent = `${related.length} curated feature shape${related.length === 1 ? " overlaps" : "s overlap"} this approximate state${near.length ? `, with ${near.length} resolution-dependent near-contact${near.length === 1 ? "" : "s"}` : ""}: ${related.length ? related.map(zone => zone.name).join(", ") : "none at the declared sampling tolerance"}. Switch lenses or observed fields without leaving the province.`;
    fields.lens.textContent = "ALL SIX LENSES + OBSERVED FIELDS";
    fields.role.textContent = "surface ecological reference province";
    fields.basis.textContent = "approximate geographic seed with its real Natural Earth coast edge";
    fields.property.textContent = group.dataset.biome.toUpperCase();
    fields.depth.textContent = "surface province identity; other atlas layers may be deeper";
    fields.clock.textContent = "mean reference; natural boundaries move";
    fields.evidence.textContent = "classic 56 vocabulary · schematic OSW geometry";
    fields.boundary.textContent = "The inherited coast is real context. Internal state boundaries and sampled shape overlaps are approximate display relationships, not published Longhurst geometry or observed ocean membership.";
    fields.source.href = "../research/longhurst-province-reference.csv";
    fields.source.textContent = "Open the 56-province directory →";
  }
  renderProvinceRelations(group);
  applyMapZoom();
  if (updateUrl) updateAtlasUrl();
}

function resetProvince(updateUrl = true) {
  selectedProvinceCode = null;
  requestedProvinceCode = null;
  provinceView = null;
  featureView = null;
  document.querySelectorAll("#province-map-host .province").forEach(item => item.classList.remove("selected"));
  document.querySelector("#province-select").value = "all";
  document.querySelector("#province-reset").disabled = true;
  document.querySelector("#province-reset").textContent = "Return to all 56";
  document.querySelector("#province-status").textContent = "Select a province to inspect and zoom.";
  applyMapZoom();
  if (currentMode === "conceptual") {
    relationSubject = "feature";
    selectZone(selectedZone);
  }
  if (updateUrl) updateAtlasUrl();
  if (zoomInvoker?.isConnected) zoomInvoker.focus();
  zoomInvoker = null;
}

function zoomToSelectedFeature(updateUrl = true, invoker = null) {
  const group = featureGroups.find(item => item.dataset.id === selectedZone.id);
  if (!group) return;
  selectedProvinceCode = null;
  requestedProvinceCode = null;
  provinceView = null;
  featureView = expandedMapView(group.getBBox(), 86);
  document.querySelectorAll("#province-map-host .province").forEach(item => item.classList.remove("selected"));
  document.querySelector("#province-select").value = "all";
  document.querySelector("#province-reset").disabled = false;
  document.querySelector("#province-reset").textContent = "Return to whole ocean";
  document.querySelector("#province-status").textContent = `${selectedZone.name} · feature anatomy view.`;
  applyMapZoom();
  if (updateUrl) updateAtlasUrl();
  if (invoker) {
    zoomInvoker = invoker;
    document.querySelector("#province-status").focus();
  }
}

async function loadProvinceMap() {
  const host = document.querySelector("#province-map-host");
  try {
    const response = await fetch("../figures/osw-province-atlas-interactive.svg");
    if (!response.ok) throw new Error(`Province map request failed: ${response.status}`);
    const svgText = await response.text();
    provinceSvgSha256 = await sha256Text(svgText);
    const documentSvg = new DOMParser().parseFromString(svgText, "image/svg+xml");
    const svg = documentSvg.documentElement;
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    host.replaceChildren(document.importNode(svg, true));
    const groups = [...host.querySelectorAll(".province")];
    provinceGroups = groups;
    const select = document.querySelector("#province-select");
    groups.sort((a, b) => a.dataset.code.localeCompare(b.dataset.code)).forEach(group => {
      const option = document.createElement("option");
      option.value = group.dataset.code;
      option.textContent = `${group.dataset.code} — ${group.dataset.name}`;
      select.append(option);
      group.addEventListener("click", () => selectProvince(group));
      group.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectProvince(group);
        }
      });
    });
    setConceptualView(currentConceptualView, false);
    renderFeatureLabels();
    if (requestedProvinceCode) selectProvince(groups.find(group => group.dataset.code === requestedProvinceCode), false);
    maybeBuildRelationMatrix();
  } catch (error) {
    document.querySelector("#province-status").textContent = "Static province map loaded; interactive zoom requires the local web preview.";
  }
}

async function loadFeatureShapes() {
  const host = document.querySelector("#feature-shape-host");
  try {
    const response = await fetch("../figures/osw-atlas-feature-shapes.svg");
    if (!response.ok) throw new Error(`Feature-shape request failed: ${response.status}`);
    const svgText = await response.text();
    featureSvgSha256 = await sha256Text(svgText);
    const documentSvg = new DOMParser().parseFromString(svgText, "image/svg+xml");
    const svg = documentSvg.documentElement;
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    host.replaceChildren(document.importNode(svg, true));
    featureGroups = [...host.querySelectorAll(".feature-shape")];
    featureGroups.forEach(shape => {
      const zone = zones.find(item => item.id === shape.dataset.id);
      if (!zone) return;
      shape.addEventListener("click", event => {
        event.stopPropagation();
        selectZone(zone);
      });
      shape.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          selectZone(zone);
        }
      });
    });
    applyGeographyFilters(false);
    const requestedZone = zones.find(zone => zone.id === requestedFeatureId);
    if (requestedZone) selectZone(requestedZone);
    else selectZone(selectedZone);
    if (requestedZone) zoomToSelectedFeature(false);
    maybeBuildRelationMatrix();
  } catch (error) {
    host.hidden = true;
    document.querySelector("#filter-status").textContent = "Feature shapes require the local web preview; use the complete text directory below the map.";
  }
}

function conceptualMapNote() {
  const view = currentConceptualView === "shape-first"
    ? "fluid shapes primary · ghost coastlines only · "
    : currentConceptualView === "water-first" ? "quiet province ground · " : "coast-owned province ground · ";
  return `<span></span> ${view}selectable feature shapes are schematic—not observed or fixed boundaries`;
}

function setConceptualView(view, updateUrl = true) {
  if (!['reference', 'water-first', 'shape-first'].includes(view)) return;
  currentConceptualView = view;
  const waterFirst = view === "water-first";
  const host = document.querySelector("#province-map-host");
  host.classList.toggle("quiet", waterFirst);
  host.classList.toggle("shape-only", view === "shape-first");
  host.querySelector(".province-labels")?.toggleAttribute("hidden", view === "shape-first");
  host.querySelectorAll(".province path").forEach(path => {
    if (view === "shape-first") {
      path.style.setProperty("fill", "#d7dfdc", "important");
      path.style.setProperty("stroke", "transparent", "important");
    } else {
      path.style.removeProperty("fill");
      path.style.removeProperty("stroke");
    }
  });
  document.querySelector("#full-size-conceptual-map").href = "../figures/osw-province-atlas-coastal-states.svg";
  document.querySelectorAll("#conceptual-views button").forEach(button => {
    button.setAttribute("aria-pressed", String(button.dataset.conceptualView === view));
  });
  if (currentMode === "conceptual") document.querySelector("#map-note").innerHTML = conceptualMapNote();
  renderFeatureLabels();
  if (updateUrl) updateAtlasUrl();
}

function setRingLatitude(latitude, updateUrl = true) {
  if (!Number.isFinite(latitude)) return;
  ringLatitude = Math.max(0, Math.min(89, Math.abs(latitude)));
  document.querySelector("#ring-lat").value = ringLatitude.toFixed(3);
  if (currentMode !== "conceptual") {
    const [data, colorFunction] = activeObservedField();
    renderObservedField(data, colorFunction);
    if (currentMode !== "argo700") renderRingComparison(data, currentMode, colorFunction);
  }
  if (updateUrl) updateAtlasUrl();
}

function inspectCoordinates(latitude, longitude, updateUrl = true) {
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;
  const [activeData] = activeObservedField();
  probeCell = probeCellFromCoordinates(latitude, longitude, activeData);
  document.querySelector("#probe-lat").value = probeCell.latitude.toFixed(3);
  document.querySelector("#probe-lon").value = probeCell.longitude.toFixed(3);
  const location = `${coordinatePhrase(probeCell.latitude, "N", "S")}, ${coordinatePhrase(probeCell.longitude, "E", "W")}`;
  const sst = probeValue(window.OCEANLINES_OISST, probeCell.latitude, probeCell.longitude, "sst");
  const anomaly = probeValue(window.OCEANLINES_OISST_ANOMALY, probeCell.latitude, probeCell.longitude, "anomaly");
  const error = probeValue(window.OCEANLINES_OISST_ERROR, probeCell.latitude, probeCell.longitude, "error");
  const argoProfile = Object.entries(argoLayers).map(([pressure, data]) => `${pressure} dbar: ${probeValue(data, probeCell.latitude, probeCell.longitude, "argo700")}`).join("; ");
  document.querySelector("#probe-result").textContent = `Nearest active display cell · ${location}. SST: ${sst}. SST anomaly: ${anomaly}. Estimated analysis error: ${error}. Argo anomaly profile — ${argoProfile}. Products are sampled on their own grids and baselines; none is heat content or transport.`;
  const [data, colorFunction] = activeObservedField();
  renderObservedField(data, colorFunction);
  if (updateUrl) updateAtlasUrl();
}

function setMapMode(mode) {
  if (mode === "observed") mode = "sst";
  const observed = mode !== "conceptual";
  const anomaly = mode === "anomaly";
  const subsurface = mode === "argo700";
  const error = mode === "error";
  currentMode = mode;
  const data = subsurface ? argoLayers[currentArgoPressure] : anomaly ? window.OCEANLINES_OISST_ANOMALY : error ? window.OCEANLINES_OISST_ERROR : window.OCEANLINES_OISST;
  document.querySelectorAll(".map-mode").forEach(button => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.querySelector("#province-map-host").classList.toggle("observed-overlay", observed);
  document.querySelector("#sst-canvas").hidden = !observed;
  document.querySelector("#observed-stamp").hidden = !observed;
  document.querySelector("#temperature-key").hidden = !observed;
  document.querySelector("#temperature-key").classList.toggle("anomaly", anomaly || subsurface);
  document.querySelector("#temperature-key").classList.toggle("error", error);
  document.querySelector("#ring-comparison").hidden = subsurface;
  document.querySelector("#argo-depths").hidden = !subsurface;
  document.querySelector("#map-data-summary").hidden = !observed;
  document.querySelector("#conceptual-actions").hidden = observed;
  document.querySelector("#conceptual-views").hidden = observed;
  document.querySelector("#map-reference-labels").hidden = !observed;
  document.querySelector("#ocean-basin-labels").hidden = observed;
  document.querySelector(".atlas-shell").classList.toggle("observed-mode", observed);
  document.querySelector("#feature-shape-host").hidden = observed;
  document.querySelector("#map-stage").classList.toggle("observed", observed);
  document.querySelectorAll(".lens").forEach(button => { button.disabled = observed; });
  document.querySelectorAll("#geography-filters select, #geography-filters button").forEach(control => { control.disabled = observed; });
  document.querySelector("#observed-title").textContent = subsurface ? `ARGO ANALYSIS · ${data.pressure_dbar.toFixed(0)} DBAR ANOMALY` : anomaly ? "OBSERVATIONAL · SURFACE ANOMALY" : error ? "OBSERVATIONAL · ESTIMATED ERROR" : "OBSERVATIONAL · ABSOLUTE SURFACE";
  document.querySelector("#observed-status").textContent = subsurface ? "SCRIPPS RG · JULY 2026 · 2004–2018 REFERENCE" : anomaly ? "NOAA OISST v2.1 · 1971–2000 BASELINE" : error ? "NOAA OISST v2.1 · TIME-MATCHED ERROR" : "NOAA OISST v2.1 · FINAL · 2026-08-01";
  document.querySelector("#scale-min").textContent = anomaly || subsurface ? "−5°C cooler" : error ? "0.1°C lower" : "−2°C";
  document.querySelector("#scale-mid").textContent = anomaly || subsurface ? "0°C baseline" : error ? "0.35°C" : "15°C";
  document.querySelector("#scale-max").textContent = anomaly || subsurface ? "+5°C warmer" : error ? "0.6°C higher" : "32°C";
  document.querySelector("#temperature-key").setAttribute("aria-label", subsurface ? `${data.pressure_dbar.toFixed(0)} dbar temperature anomaly scale from five degrees cooler to five degrees warmer than the RG baseline` : anomaly ? "SST anomaly scale from five degrees cooler to five degrees warmer than baseline" : error ? "Estimated analysis error scale from lower to higher error" : "Absolute sea surface temperature color scale");
  const canvas = document.querySelector("#sst-canvas");
  canvas.setAttribute("aria-label", subsurface ? `Scripps RG Argo potential-temperature anomaly at ${data.pressure_dbar.toFixed(0)} dbar for July 2026, displayed on a two-degree equirectangular grid from 64.5 degrees south to 79.5 degrees north.` : anomaly ? "NOAA OISST anomaly for 1 August 2026 relative to 1971 to 2000, displayed on a two-degree equirectangular grid." : error ? "NOAA OISST estimated analysis error for 1 August 2026, displayed on a two-degree equirectangular grid." : "NOAA OISST absolute sea surface temperature for 1 August 2026, displayed on a two-degree equirectangular grid.");
  document.querySelector("#map-note").innerHTML = observed
    ? `<span></span> ${subsurface ? `${data.pressure_dbar.toFixed(0)} dbar anomaly · RG 2019 seasonal reference · July 2026 · symmetric ±5°C display clamp · 64.5°S–79.5°N · slate outside source domain` : anomaly ? "SST anomaly · 1971–2000 reference · symmetric ±5°C display clamp" : error ? "estimated analysis error · 0.1–0.6°C display clamp" : "absolute SST"} · equirectangular · antimeridian seam · 2° display stride · province borders are approximate reference geometry`
    : conceptualMapNote();
  if (observed) {
    renderObservedField(data, anomaly || subsurface ? anomalyColor : error ? errorColor : temperatureColor);
    showObservedMetadata(data, mode);
    renderTextSummary(data, mode);
    if (!subsurface) renderRingComparison(data, mode, anomaly ? anomalyColor : error ? errorColor : temperatureColor);
    if (probeCell) inspectCoordinates(probeCell.latitude, probeCell.longitude, false);
  } else if (selectedProvinceCode) {
    const selected = [...document.querySelectorAll("#province-map-host .province")].find(group => group.dataset.code === selectedProvinceCode);
    if (selected) selectProvince(selected, false);
  } else selectZone(selectedZone);
  updateAtlasUrl();
}

function zoneMatches(zone, filters) {
  return (filters.lens === "all" || zone.lens === filters.lens)
    && (filters.depth === "all" || zone.depthClass === filters.depth)
    && (filters.property === "all" || zone.properties.includes(filters.property))
    && (filters.clock === "all" || zone.clockClass === filters.clock);
}

function activeGeographyFilters() {
  return {
    lens: currentLens,
    depth: document.querySelector("#filter-depth").value,
    property: document.querySelector("#filter-property").value,
    clock: document.querySelector("#filter-clock").value
  };
}

function rebuildDirectory(matching) {
  const list = document.querySelector("#zone-directory-list");
  list.replaceChildren();
  for (const zone of matching) {
  const item = document.createElement("li");
    item.dataset.lens = zone.lens;
  const directoryButton = document.createElement("button");
  directoryButton.type = "button";
    directoryButton.innerHTML = `<span>${String(zone.n).padStart(2, "0")} · ${zone.lens.toUpperCase()}</span> ${zone.name}<small>${evidenceClass(zone)}</small>`;
  directoryButton.addEventListener("click", () => {
    selectZone(zone);
    document.querySelector("#zone-panel").scrollIntoView({ block: "start" });
  });
  item.append(directoryButton);
    list.append(item);
  }
}

function applyGeographyFilters(updateUrl = true) {
  const filters = activeGeographyFilters();
  const matching = zones.filter(zone => zoneMatches(zone, filters));
  const matchingIds = new Set(matching.map(zone => zone.id));
  document.querySelectorAll("#feature-shape-host .feature-shape").forEach(shape => {
    const show = matchingIds.has(shape.dataset.id);
    shape.toggleAttribute("hidden", !show);
    shape.tabIndex = show ? 0 : -1;
  });
  count.textContent = matching.length;
  const lensName = currentLens === "all" ? "curated" : currentLens;
  const message = `${matching.length} matching ${lensName} feature${matching.length === 1 ? "" : "s"}. Shapes are schematic geographic indexes, not observed boundaries.`;
  document.querySelector("#filter-status").textContent = message;
  document.querySelector("#directory-summary").textContent = `Browse ${matching.length} matching features as text`;
  rebuildDirectory(matching);
  if (matching.length && !matchingIds.has(selectedZone.id) && !selectedProvinceCode) selectZone(matching[0]);
  else if (selectedProvinceCode) renderProvinceRelations(provinceGroups.find(group => group.dataset.code === selectedProvinceCode));
  renderFeatureLabels();
  if (updateUrl) updateAtlasUrl();
}

function setArgoPressure(pressure, updateUrl = true) {
  if (!argoLayers[pressure]) return;
  currentArgoPressure = Number(pressure);
  document.querySelectorAll("#argo-depths button").forEach(button => {
    button.setAttribute("aria-pressed", String(Number(button.dataset.pressure) === currentArgoPressure));
  });
  if (currentMode === "argo700") setMapMode("argo700");
  if (updateUrl) updateAtlasUrl();
}

document.querySelectorAll(".lens").forEach(button => {
  button.addEventListener("click", () => {
    currentLens = button.dataset.lens;
    document.querySelectorAll(".lens").forEach(item => {
      const active = item === button;
      item.classList.toggle("active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    applyGeographyFilters();
  });
});

document.querySelectorAll("#geography-filters select").forEach(select => select.addEventListener("change", () => applyGeographyFilters()));
document.querySelector("#geography-filters").addEventListener("reset", () => {
  setTimeout(() => {
    currentLens = "waters";
    document.querySelectorAll(".lens").forEach(button => {
      const active = button.dataset.lens === "waters";
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    applyGeographyFilters();
  });
});

document.querySelectorAll(".map-mode").forEach(button => button.addEventListener("click", () => setMapMode(button.dataset.mode)));
document.querySelectorAll("#argo-depths button").forEach(button => button.addEventListener("click", () => setArgoPressure(Number(button.dataset.pressure))));
document.querySelectorAll("#conceptual-views button").forEach(button => button.addEventListener("click", () => setConceptualView(button.dataset.conceptualView)));
document.querySelector("#feature-zoom").addEventListener("click", event => zoomToSelectedFeature(true, event.currentTarget));
document.querySelector("#province-select").addEventListener("change", event => {
  if (event.target.value === "all") resetProvince();
  else selectProvince([...document.querySelectorAll("#province-map-host .province")].find(group => group.dataset.code === event.target.value));
});
document.querySelector("#province-reset").addEventListener("click", () => resetProvince());
document.querySelector("#relation-clear").addEventListener("click", clearRelationSpotlight);
document.querySelector("#relation-export").addEventListener("click", exportRelationMatrix);
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && (provinceView || featureView)) resetProvince();
});
window.addEventListener("resize", applyMapZoom);
document.querySelector("#coordinate-probe").addEventListener("submit", event => {
  event.preventDefault();
  inspectCoordinates(Number(document.querySelector("#probe-lat").value), Number(document.querySelector("#probe-lon").value));
});
document.querySelector("#ring-form").addEventListener("submit", event => {
  event.preventDefault();
  setRingLatitude(Number(document.querySelector("#ring-lat").value));
});
document.querySelector("#sst-canvas").addEventListener("click", event => {
  const rectangle = event.currentTarget.getBoundingClientRect();
  const longitude = (event.clientX - rectangle.left) / rectangle.width * 360 - 180;
  const latitude = 90 - (event.clientY - rectangle.top) / rectangle.height * 180;
  inspectCoordinates(latitude, longitude);
});
const requestedParameters = new URLSearchParams(window.location.search);
const requestedMode = requestedParameters.get("mode");
if (["all", "waters", "flows", "edges", "floor", "life", "events"].includes(requestedParameters.get("lens"))) currentLens = requestedParameters.get("lens");
for (const [parameter, selector] of [["depth", "#filter-depth"], ["property", "#filter-property"], ["clock", "#filter-clock"]]) {
  const value = requestedParameters.get(parameter);
  if (value && [...document.querySelector(selector).options].some(option => option.value === value)) document.querySelector(selector).value = value;
}
document.querySelectorAll(".lens").forEach(button => {
  const active = button.dataset.lens === currentLens;
  button.classList.toggle("active", active);
  button.setAttribute("aria-pressed", String(active));
});
applyGeographyFilters(false);
selectZone(selectedZone);
setConceptualView(["reference", "water-first", "shape-first"].includes(requestedParameters.get("view")) ? requestedParameters.get("view") : "water-first", false);
if (requestedParameters.has("pressure")) setArgoPressure(Number(requestedParameters.get("pressure")), false);
if (requestedParameters.has("ring")) setRingLatitude(Number(requestedParameters.get("ring")), false);
if (["observed", "sst", "anomaly", "argo700", "error"].includes(requestedMode)) setMapMode(requestedMode);
if (currentMode !== "conceptual" && requestedParameters.has("lat") && requestedParameters.has("lon")) {
  inspectCoordinates(Number(requestedParameters.get("lat")), Number(requestedParameters.get("lon")));
}
loadProvinceMap();
loadFeatureShapes();
