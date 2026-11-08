"use strict";
(() => {
  async function verified(path, expected) {
    let target=path;if(expected){const url=new URL(path,location.href);url.searchParams.set('v',expected);target=url.href;}const response=await fetch(target,{cache:expected?'force-cache':'no-cache'});if(!response.ok)throw Error(`Could not load atlas record (HTTP ${response.status})`);
    const bytes=await response.arrayBuffer();if(bytes.byteLength>2400000)throw Error('Atlas record exceeds its expected size');
    if(expected){const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==expected)throw Error('Atlas record does not match this snapshot');}
    let value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
    if(value.schema==='osw.preview-json-envelope.v1'){
      if(value.encoding!=='gzip+base64'||!Number.isInteger(value.decoded_bytes)||value.decoded_bytes<0||value.decoded_bytes>=2500000)throw Error('Invalid preview record envelope');
      if(typeof DecompressionStream==='undefined')throw Error('This preview needs a browser with gzip decompression support');
      const compressed=Uint8Array.from(atob(value.payload),c=>c.charCodeAt(0)),reader=new Blob([compressed]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();
      const chunks=[];let size=0;try{while(true){const next=await reader.read();if(next.done)break;size+=next.value.length;if(size>value.decoded_bytes)throw Error('Preview record exceeds its declared decoded size');chunks.push(next.value);}}finally{await reader.cancel();}
      if(size!==value.decoded_bytes)throw Error('Incomplete preview record');const decoded=new Uint8Array(size);let offset=0;for(const chunk of chunks){decoded.set(chunk,offset);offset+=chunk.length;}
      const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',decoded))].map(n=>n.toString(16).padStart(2,'0')).join('');if(hash!==value.decoded_sha256)throw Error('Preview record decoded checksum mismatch');
      value=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(decoded));
    }
    return value;
  }
  const root='preview-data-screened-v1', records=new Map();let editionPromise=null;
  const repo='https://github.com/giodl73-repo/OSW/blob/4de9653df054c1db32fcb56149d28e1d58c0502a/';
  function sourceURL(value){if(typeof value!=='string'||!value.trim())return null;try{const u=new URL(value,location.href);if(!['http:','https:'].includes(u.protocol))return null;if(u.origin===location.origin){const match=u.pathname.match(/\/(research|plans|analysis)\/(.+)$/);return match?repo+match[1]+'/'+match[2]+u.hash:null;}return u.href;}catch{return null;}}
  async function edition(){if(!editionPromise)editionPromise=(async()=>{
    const review=await verified('preview-review-v1/screened-manifest.json');
    const build=await verified(root+'/build.json',review.data_build_sha256);
    if(build.status!=='PASS_SCOPED_DATA_PACKAGE_NOT_PUBLICATION'||build.counts.named_current!==111)throw Error('Unsupported preview edition');
    async function part(path){const pin=build.files.find(f=>f.path===path);if(!pin)throw Error('Unlisted edition file: '+path);return verified(root+'/'+path,pin.sha256);}
    const index=await part('index.json');if(index.schema!=='osw.preview-display-index.v1'||index.counts.named_current!==111)throw Error('Incomplete preview inventory');
    const original=await part('depth-contexts.json'),extraPin=review.files.find(f=>f.path==='contexts.json');if(!extraPin)throw Error('Missing context receipt');
    const extra=await verified('preview-review-v1/contexts.json',extraPin.sha256);if(extra.candidate_build_sha256!==review.candidate_build_sha256)throw Error('Context edition mismatch');
    const contexts={...original.contexts};for(const[id,row]of Object.entries(extra.contexts)){if(!Object.hasOwn(contexts,id)||Object.keys(contexts[id]).length)throw Error('Context supplement would replace evidence');contexts[id]=row;}
    async function record(entry){if(!records.has(entry.id))records.set(entry.id,(async()=>{const doc=await part(entry.record.path);if(doc.id!==entry.id||doc.object.id!==entry.id)throw Error('Record identity mismatch');return doc;})());try{return await records.get(entry.id);}catch(e){records.delete(entry.id);throw e;}}
    return {build,index,contexts,part,record,review,buildSha:review.data_build_sha256};
  })().catch(error=>{editionPromise=null;throw error;});return editionPromise;}
  function download(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  window.OSWPreview=Object.freeze({read:verified,edition,sourceURL,download});
})();
