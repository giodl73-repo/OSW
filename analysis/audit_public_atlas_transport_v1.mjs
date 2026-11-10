// Inspect byte sizes of the existing Rust UI export. No field diagnostics or builds.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { performance } from 'node:perf_hooks';

if (process.env.GITHUB_ACTIONS !== 'true' || process.env.OSW_PUBLIC_ATLAS_TRANSPORT_V1 !== '1') {
  throw Error('Scoped cloud UI transport audit only');
}
const began = performance.now();
const emit = (phase, extra = {}) => fs.writeSync(1, JSON.stringify({ phase, elapsed_ms: performance.now() - began, ...extra }) + '\n');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = path => fs.readFileSync(path);
const packet = JSON.parse(read('almanac/query-data.json'));
const manifest = JSON.parse(read('almanac/query-engine.manifest.json'));
if (packet.schema !== 'osw.query-packet.v1') throw Error('Expected the installed packet, not a replacement dataset');
const binary = read('almanac/query-engine.wasm');
if (hash(binary) !== manifest.sha256['almanac/query-engine.wasm']) throw Error('Changed installed engine');
const parts = [];
for (const part of packet.parts) {
  const bytes = read('almanac/' + part.path);
  if (bytes.length !== part.byte_length || hash(bytes) !== part.sha256 || manifest.sha256['almanac/' + part.path] !== part.sha256) throw Error('Changed packet part');
  parts.push(bytes);
}
const logical = Buffer.concat(parts);
if (logical.length !== packet.logical_byte_length || hash(logical) !== packet.logical_sha256) throw Error('Changed logical corpus');
emit('verified-input-bytes', { binary_bytes: binary.length, corpus_bytes: logical.length });
const { instance } = await WebAssembly.instantiate(binary, {});
const engine = instance.exports;
emit('instantiated');
const pointer = engine.osw_alloc(logical.length);
new Uint8Array(engine.memory.buffer, pointer, logical.length).set(logical);
engine.osw_load(pointer, logical.length);
engine.osw_dealloc(pointer, logical.length);
const result = () => {
  const length = engine.osw_result_len();
  if (length > 32_000_000) throw Error('UI export exceeds the 32 MB inspection ceiling: ' + length);
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length)));
};
const loaded = result();
if (!loaded.ok) throw Error('Existing Rust store rejected input: ' + String(loaded.error));
emit('store-loaded', { collection_count: loaded.collections?.length });
engine.osw_atlas();
emit('atlas-exported', { result_bytes: engine.osw_result_len() });
const atlas = result();
if (!atlas.ok) throw Error('Atlas export failed: ' + String(atlas.error));
const size = value => Buffer.byteLength(JSON.stringify(value), 'utf8');
const sources = Object.entries(atlas.sources_json || {}).map(([path, raw]) => ({ path, bytes: Buffer.byteLength(raw, 'utf8'), sha256: hash(raw) }));
const fields = Object.entries(atlas).filter(([key]) => key !== 'sources_json').map(([key, value]) => ({ key, bytes: size(value) }));
engine.osw_dashboard();
const dashboard = result();
if (!dashboard.ok) throw Error('Dashboard export failed: ' + String(dashboard.error));
const report = {
  schema: 'osw.public-atlas-transport-audit.v1', status: 'PASS_METADATA_AUDIT_ONLY',
  source_commit: process.env.GITHUB_SHA, engine_sha256: hash(binary), logical_sha256: packet.logical_sha256,
  independent_question: 'Byte inventory of current Rust UI exports for progressive delivery; no scientific values extracted',
  prior_question_charges: { numeric_tokens: 0, json_bytes: 0, active_seconds: 0 },
  binary_bytes: binary.length, logical_corpus_bytes: logical.length,
  checked_index_gzip_bytes: fs.statSync('almanac/index-data.json.gz').size,
  atlas_export_bytes: size(atlas), source_document_count: sources.length,
  source_documents: sources.sort((a, b) => b.bytes - a.bytes),
  atlas_fields: fields.sort((a, b) => b.bytes - a.bytes),
  dashboard_export_bytes: size(dashboard),
  active_seconds: (performance.now() - began) / 1000,
  rebuilt: false, scientific_field_processing: false, publication_approved: false,
};
fs.writeFileSync('.pytest_cache/public-atlas-transport-v1/result.json', JSON.stringify(report, null, 2) + '\n');
emit('complete', { atlas_export_bytes: report.atlas_export_bytes, source_document_count: sources.length });
