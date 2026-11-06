// Keep the engine's JSON bytes intact across JavaScript fixture transport.
// Parsed values are suitable for status checks, never preservation evidence.
import assert from 'node:assert/strict';
export function readResponseJson(engine, limit) {
  const length = engine.osw_result_len();
  assert(Number.isSafeInteger(length) && length > 0 && length <= limit);
  return new TextDecoder('utf-8', {fatal: true}).decode(
    new Uint8Array(engine.memory.buffer, engine.osw_result_ptr(), length));
}
export function invokeJson(engine, name, bytes, limit) {
  const pointer = engine.osw_alloc(bytes.length);
  try {
    new Uint8Array(engine.memory.buffer, pointer, bytes.length).set(bytes);
    engine[name](pointer, bytes.length);
    return readResponseJson(engine, limit);
  } finally {
    engine.osw_dealloc(pointer, bytes.length);
  }
}
export function captureJson(rawResponseJson) {
  assert.equal(typeof rawResponseJson, 'string');
  JSON.parse(rawResponseJson); // Validate syntax without re-encoding the response.
  return {raw_response_json: rawResponseJson};
}
export function assertSameJsonBytes(actual, expected) {
  assert.equal(typeof actual, 'string');
  assert.equal(typeof expected, 'string');
  assert.equal(actual, expected, 'Exact engine JSON differs');
}
