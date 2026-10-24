"use strict";
// This worker has no atlas packet, spatial index, or workspace dependency.
const files = {
  engine: {url: 'local-extents-engine.wasm', bytes: 278034, sha256: '5758d51eb754b14b0b0660c6d5f7c2137f0f4f56b9e8b0ea133ca5ec8c21e8cc'},
  data: {url: '../research/eacc-local-extent-evidence-bundle-v1.json', bytes: 835839, sha256: 'e4ca7c532c39d22efc2d6600a89424f48558669fe6e6682b1c6ec9442d00cdf8'}
};
const encoder = new TextEncoder(), decoder = new TextDecoder('utf-8', {fatal: true});
let engine = null, metadata = null, queue = Promise.resolve();
async function fetchExact(file) {
  const response = await fetch(file.url, {cache: 'no-store'});
  if (!response.ok) throw Error(`Evidence asset unavailable (HTTP ${response.status}).`);
  const reader = response.body.getReader(), chunks = [];
  let count = 0;
  try {
    for (;;) {
      const {done, value} = await reader.read();
      if (done) break;
      count += value.length;
      if (count > file.bytes) throw Error('Evidence asset exceeded its reviewed size.');
      chunks.push(value);
    }
  } finally { await reader.cancel(); }
  if (count !== file.bytes) throw Error('Evidence asset size does not match the reviewed version.');
  const bytes = new Uint8Array(count);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
    .map(byte => byte.toString(16).padStart(2, '0')).join('');
  if (digest !== file.sha256) throw Error('Evidence asset hash does not match the reviewed version.');
  return bytes;
}
function checkMemory() {
  if (engine.memory.buffer.byteLength > 64 * 1024 * 1024) throw Error('Evidence engine exceeded its memory budget.');
}
function invoke(name, value) {
  const bytes = value instanceof Uint8Array ? value : encoder.encode(JSON.stringify(value));
  if (name !== 'osw_local_extents_load' && bytes.length > 20000) throw Error('Query exceeds 20,000 bytes.');
  const pointer = engine.osw_alloc(bytes.length);
  try {
    new Uint8Array(engine.memory.buffer, pointer, bytes.length).set(bytes);
    engine[name](pointer, bytes.length);
    checkMemory();
    const length = engine.osw_result_len();
    if (length > 2 * 1024 * 1024) throw Error('Evidence response exceeded its size budget.');
    return JSON.parse(decoder.decode(new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length)));
  } finally { engine.osw_dealloc(pointer, bytes.length); }
}
async function load() {
  engine = null; metadata = null;
  try {
    const binary = await fetchExact(files.engine);
    const result = await WebAssembly.instantiate(binary, {});
    engine = result.instance.exports;
    const data = await fetchExact(files.data);
    metadata = invoke('osw_local_extents_load', data);
    if (!metadata.ok) throw Error(metadata.error);
    if (metadata.dataset !== 'current-local-extents-v1' || metadata.bundle_sha256 !== files.data.sha256
        || metadata.workspace_available !== false || metadata.complete_atlas_loaded !== false
        || metadata.physical_width_inventory_increment !== 0) throw Error('Unexpected evidence scope.');
    return metadata;
  } catch (error) { engine = null; metadata = null; throw error; }
}
self.onmessage = event => {
  const {id, action, value} = event.data;
  queue = queue.then(async () => {
    try {
      let result;
      if (action === 'load') result = await load();
      else {
        if (!engine || !metadata) throw Error('Load the evidence snapshot before querying.');
        if (action === 'query') result = invoke('osw_local_extents_query', value);
        else if (action === 'record') result = invoke('osw_local_extents_record', value);
        else throw Error('Unsupported evidence action.');
      }
      self.postMessage({id, result});
    } catch (error) { self.postMessage({id, result: {ok: false, error: String(error.message || error)}}); }
  });
};
