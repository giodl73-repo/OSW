"use strict";
// The index has a separate corpus; loading it does not load query-data.json.
let engine = null;
let checkedBinary = null;
const encoder = new TextEncoder(), decoder = new TextDecoder();
async function digest(bytes) {
  const hash = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return [...hash].map(b => b.toString(16).padStart(2, "0")).join("");
}
function invoke(name, value) {
  const bytes = value instanceof Uint8Array ? value : encoder.encode(JSON.stringify(value));
  const ptr = engine.osw_alloc(bytes.length);
  try {
    new Uint8Array(engine.memory.buffer, ptr, bytes.length).set(bytes);
    engine[name](ptr, bytes.length);
    return JSON.parse(decoder.decode(new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), engine.osw_result_len())));
  } finally {engine.osw_dealloc(ptr, bytes.length);}
}
async function fetchBytes(path) {
  const response = await fetch(path, {cache: "no-store"});
  if (!response.ok) throw Error(path + ": HTTP " + response.status);
  return response.arrayBuffer();
}
async function load() {
  if (typeof DecompressionStream !== "function") throw Error("This browser cannot decompress the checked index corpus");
  const manifest = JSON.parse(decoder.decode(await fetchBytes("query-engine.manifest.json")));
  if (manifest.schema !== "osw.query-engine-manifest.v1" || manifest.abi_version !== 1) throw Error("Unsupported index engine manifest");
  const [wasm, catalogBytes, compressed] = await Promise.all([
    fetchBytes("query-engine.wasm"), fetchBytes("index-catalog.json"), fetchBytes("index-data.json.gz")]);
  for (const [path, bytes] of [["almanac/query-engine.wasm", wasm], ["almanac/index-catalog.json", catalogBytes], ["almanac/index-data.json.gz", compressed]]) {
    if (await digest(bytes) !== manifest.sha256[path]) throw Error("Changed " + path);
  }
  const catalog = JSON.parse(decoder.decode(catalogBytes));
  if (catalog.schema !== "osw.almanac-index-catalog.v1") throw Error("Unsupported index source catalog");
  const bytes = new Uint8Array(await new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream("gzip"))).arrayBuffer());
  if (await digest(bytes) !== catalog.bundle_sha256) throw Error("Changed decompressed index corpus");
  const instance = await WebAssembly.instantiate(wasm, {});
  engine = instance.instance.exports;
  const result = invoke("osw_index_load", bytes);
  if (!result.ok) {engine = null; throw Error(result.error);}
  checkedBinary = wasm;
  return result;
}
self.onmessage = async event => {
  const {id, action, value} = event.data;
  try {
    let result;
    if (action === "load") result = await load();
    else if (!engine) throw Error("Index store not loaded");
    else if (action === "cartography_binary") result = {ok: true, binary: checkedBinary};
    else if (action === "query") result = invoke("osw_index_query", value);
    else if (action === "currents") result = invoke("osw_index_currents", value);
    else if (action === "eddies") result = invoke("osw_index_eddies", value);
    else if (action === "nasa") result = invoke("osw_index_nasa", value);
    else if (action === "release_media") result = invoke("osw_index_release_media", value);
    else if (action === "state_memberships") result = invoke("osw_index_state_memberships", value);
    else if (action === "state_context") result = invoke("osw_index_state_context", value);
    else if (action === "noaa_state") result = invoke("osw_index_noaa_state", value);
    else if (action === "noaa_track") result = invoke("osw_index_noaa_track", value);
    else if (action === "support") result = invoke("osw_index_support", value);
    else if (action === "map") result = invoke("osw_index_map", value);
    else if (action === "document") result = invoke("osw_index_document", value);
    else throw Error("Unknown index worker action");
    self.postMessage({id, result});
  } catch (error) {self.postMessage({id, result: {ok: false, error: error.message}});}
};
