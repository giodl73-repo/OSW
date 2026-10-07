(() => {
  const byId = id => document.getElementById(id);
  const link = (label, href, external = false) => {
    const a = document.createElement('a');
    a.textContent = label;
    a.href = href;
    if (external) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  };
  const textCell = (row, value) => {
    const cell = row.insertCell();
    cell.textContent = value;
    return cell;
  };
  const controls=['movie-query','movie-zoom','movie-state'];
  controls.forEach(id=>byId(id).disabled=true);
  const worker=new Worker('query-worker.js?v=movies-1');
  let generation=1,ready=false;
  const timer=setTimeout(()=>fail('Movie data request timed out'),90000);
  function fail(message){clearTimeout(timer);worker.terminate();controls.forEach(id=>byId(id).disabled=true);byId('movie-error').textContent=message;byId('movie-error').hidden=false;byId('movie-count').textContent='Unavailable';}
  function request(){
    const query=byId('movie-query').value,zoom=byId('movie-zoom').value,state=byId('movie-state').value;
    worker.postMessage({id:++generation,action:'movies',value:{query,zoom:zoom==='all'?null:Number(zoom),state_id:state==='all'?null:state}});
  }
  worker.onerror=()=>fail('Rust movie data worker failed');
  worker.onmessage=event=>{
    const {id,result}=event.data;if(id!==generation)return;
    if(!result.ok){fail(result.error);return;}
    if(id===1){ready=true;request();return;}
    clearTimeout(timer);window.oswMovieView=result;
    const states=result.states;
    if(byId('movie-state').options.length===1){
    states.forEach(state => {
      const option = document.createElement('option');
      option.value = state.id;
      option.textContent = state.label;
      byId('movie-state').append(option);
    });
    }
    controls.forEach(id=>byId(id).disabled=false);
    const body=byId('movie-rows');body.replaceChildren();
    result.rows.forEach(({tile,states:stateList,objects})=>{
        const row = body.insertRow();
        row.id = `movie-${tile.tile_id}`;
        textCell(row, `${tile.tile_id} · level ${tile.zoom}`);
        row.insertCell().append(link('Watch at NASA', tile.url, true));
        const stateCell = row.insertCell();
        const stateDetails = document.createElement('details');
        const stateSummary = document.createElement('summary');
        stateSummary.textContent = `${stateList.length} display overlaps`;
        stateDetails.append(stateSummary);
        const stateLinks = document.createElement('ul');
        stateList.forEach(({relation:item,entity:stateEntity}) => {
          const li = document.createElement('li');
          li.append(link(stateEntity?.label || item.state_id, `object.html?id=${encodeURIComponent(item.state_id)}`));
          li.append(` · ${(100 * item.display_coverage_fraction).toFixed(1)}% of state's display area`);
          stateLinks.append(li);
        });
        stateDetails.append(stateLinks);
        stateCell.append(stateDetails);
        const objectCell = row.insertCell();
        const objectIds = objects.map(item=>item.id);
        if (!objectIds.length) { objectCell.textContent = 'No linked motion record'; return; }
        const objectDetails = document.createElement('details');
        const objectSummary = document.createElement('summary');
        objectSummary.textContent = `${objectIds.length} geographic links`;
        objectDetails.append(objectSummary);
        const objectLinks = document.createElement('ul');
        objects.forEach(entity => {
          const id=entity.id;
          const li = document.createElement('li');
          li.append(link(entity.label || id, `object.html?id=${encodeURIComponent(id)}`));
          objectLinks.append(li);
        });
        objectDetails.append(objectLinks);
        objectCell.append(objectDetails);
      });
    byId('movie-count').textContent=`${result.matched} of ${result.total} crops`;
  };
  controls.forEach(id=>byId(id).addEventListener(id==='movie-query'?'input':'change',()=>{if(ready)request();}));
  worker.postMessage({id:1,action:'load'});
})();
