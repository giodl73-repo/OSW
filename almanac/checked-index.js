"use strict";
// Keep the checked store alive for seasonal selections and source-scoped queries.
(() => {
  const worker = new Worker("index-worker.js?v=checked-index-1");
  const pending = new Map();
  let serial = 0, failed = null;
  function fail(error) {
    failed = error;
    for (const item of pending.values()) {clearTimeout(item.timer); item.reject(error);}
    pending.clear(); worker.terminate();
  }
  worker.onerror = () => fail(Error("Checked index worker failed"));
  worker.onmessage = ({data}) => {
    const item = pending.get(data.id);
    if (!item) return;
    pending.delete(data.id); clearTimeout(item.timer);
    if (!data.result.ok) item.reject(Error(data.result.error));
    else item.resolve(data.result);
  };
  function request(action, value) {
    if (failed) return Promise.reject(failed);
    return new Promise((resolve, reject) => {
      const id = ++serial;
      const timer = setTimeout(() => fail(Error("Checked index request timed out")), 90000);
      pending.set(id, {resolve, reject, timer});
      worker.postMessage({id, action, value});
    });
  }
  window.oswCheckedIndexReady = (async () => {
    const metadata = await request("load");
    const {binary} = await request("cartography_binary");
    const cartography = await window.createOswCartography(binary);
    window.oswIndexCartography = cartography;
    window.oswIndexMetadata = metadata;
    return metadata;
  })();
  // Requests await one shared load. No raw-source fallback on missing/changed data.
  window.oswIndexDocument = async path => {
    await window.oswCheckedIndexReady;
    const url = new URL(path, window.location.href);
    const projectRoot = new URL("../", window.location.href).pathname;
    if (url.origin !== window.location.origin || url.search || url.hash)
      throw Error("Unsupported index source address");
    if (!url.pathname.startsWith(projectRoot)) throw Error("Index source outside project");
    return (await request("document", {document: decodeURIComponent(url.pathname.slice(projectRoot.length))})).value;
  };
  window.oswIndexQuery = async value => {
    await window.oswCheckedIndexReady;
    return request("query", value);
  };
  window.oswIndexCurrents = async value => {
    await window.oswCheckedIndexReady;
    return request("currents", value);
  };
  window.oswIndexEddies = async value => {
    await window.oswCheckedIndexReady;
    return request("eddies", value);
  };
  window.oswIndexNasa = async value => {
    await window.oswCheckedIndexReady;
    return request("nasa", value);
  };
  window.oswIndexReleaseMedia = async () => {
    await window.oswCheckedIndexReady;
    return request("release_media", {});
  };
  window.oswIndexStateMemberships = async value => {
    await window.oswCheckedIndexReady;
    return request("state_memberships", value);
  };
  window.oswIndexStateContext = async value => {
    await window.oswCheckedIndexReady;
    return request("state_context", value);
  };
  window.oswIndexNoaaState = async value => {
    await window.oswCheckedIndexReady;
    return request("noaa_state", value);
  };
  window.oswIndexNoaaTrack = async value => {
    await window.oswCheckedIndexReady;
    return request("noaa_track", value);
  };
  window.oswIndexSupport = async value => {
    await window.oswCheckedIndexReady;
    return request("support", value);
  };
  window.oswIndexMap = async () => {
    await window.oswCheckedIndexReady;
    return request("map", {});
  };
})();
