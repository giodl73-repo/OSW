"use strict";
// Reuse the worker-verified binary for synchronous, stateless display calculations.
window.createOswCartography = async function(binary) {
  const {instance}=await WebAssembly.instantiate(binary,{}),engine=instance.exports;
  if(typeof engine.osw_cartography!=='function')throw Error('Rust cartography export unavailable');
  const encoder=new TextEncoder(),decoder=new TextDecoder(),cache=new Map();
  return request=>{
    const key=JSON.stringify(request);if(cache.has(key))return cache.get(key);
    const bytes=encoder.encode(key),ptr=engine.osw_alloc(bytes.length);
    try {
      new Uint8Array(engine.memory.buffer,ptr,bytes.length).set(bytes);
      engine.osw_cartography(ptr,bytes.length);
      const result=JSON.parse(decoder.decode(new Uint8Array(engine.memory.buffer,engine.osw_result_ptr(),engine.osw_result_len())));
      if(!result.ok)throw Error(result.error);
      if(cache.size>=4096)cache.clear();cache.set(key,result);return result;
    } finally {engine.osw_dealloc(ptr,bytes.length);}
  };
};
