"use strict";
// Transport only: Rust still validates and queries the complete logical bundle.
async function assembleQueryPacket(rootBytes, fetchBytes, digestBytes, pins) {
  const packet=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(rootBytes));
  if(packet.schema==='osw.query-bundle.v1')return rootBytes;
  const limit=16*1024*1024,hex=/^[0-9a-f]{64}$/;
  if(packet.schema!=='osw.query-packet.v1'||packet.logical_schema!=='osw.query-bundle.v1'||packet.hash_algorithm!=='sha256'
    ||packet.part_byte_limit!==limit||!hex.test(packet.logical_sha256)||!Number.isSafeInteger(packet.logical_byte_length)
    ||packet.logical_byte_length<=0||!Array.isArray(packet.parts)||packet.parts.length!==Math.ceil(packet.logical_byte_length/limit))throw Error('Invalid query packet');
  packet.parts.forEach((part,index)=>{
    if(part.index!==index||!hex.test(part.sha256)||part.path!==`query-parts/${String(index).padStart(6,'0')}-${part.sha256}.bin`
      ||part.byte_length!==Math.min(limit,packet.logical_byte_length-index*limit)
      ||pins['almanac/'+part.path]!==part.sha256)throw Error('Invalid or unpinned query packet part');
  });
  const result=new Uint8Array(packet.logical_byte_length);
  for(const part of packet.parts){
    const chunk=await fetchBytes(part.path);
    if(chunk.byteLength!==part.byte_length||await digestBytes(chunk)!==part.sha256)throw Error('Changed query packet part: '+part.path);
    result.set(new Uint8Array(chunk),part.index*limit);
  }
  if(await digestBytes(result)!==packet.logical_sha256)throw Error('Changed logical query bundle');
  // Decode only after joining bytes: a UTF-8 character may cross a part boundary.
  if(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result)).schema!==packet.logical_schema)throw Error('Wrong logical query schema');
  return result.buffer;
}
