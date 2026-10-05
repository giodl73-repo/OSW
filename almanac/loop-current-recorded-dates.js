(()=>{
'use strict';
const frames=JSON.parse(document.getElementById('recorded-frames').textContent);
const $=id=>document.getElementById(id),select=$('recorded-date');
let timer=null,index=0;
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
for(const frame of frames){const option=document.createElement('option');option.value=frame.date;option.textContent=frame.date;select.append(option);}
const requested=new URL(location.href).searchParams.get('date');
const found=frames.findIndex(frame=>frame.date===requested);if(found>=0)index=found;
function stop(){if(timer!==null){clearInterval(timer);timer=null;}$('play').textContent='Play recorded days';$('play').setAttribute('aria-pressed','false');}
function render(){
 const frame=frames[index];select.value=frame.date;$('map-title').textContent='Loop Current methods · '+frame.date;
 $('noaa-line').setAttribute('d',frame.noaa_path);$('noaa-line').classList.toggle('failed',!frame.noaa_connected);
 $('noaa-title').textContent='NOAA '+frame.date+': '+frame.noaa_stop;
 $('adt-line').setAttribute('d',frame.adt_path||'');$('adt-line').hidden=!frame.adt_path;
 $('adt-title').textContent='DUACS '+frame.date+': '+frame.adt_display;
 $('outcome').textContent=frame.date+' · NOAA '+frame.noaa_display+' ('+frame.noaa_stop+'); DUACS '+frame.adt_display+'. Failed NOAA scenarios: '+frame.failed_scenarios+'.'+(frame.difference===null?' Method difference unresolved.':' Method difference: '+frame.difference+' km.');
 for(const [id,key] of [['query-date','query_url'],['noaa-source','noaa_file'],['adt-source','adt_file']])$(id).href=frame[key];
 $('previous').disabled=index===0;$('next').disabled=index===frames.length-1;
 const url=new URL(location.href);url.searchParams.set('date',frame.date);history.replaceState(null,'',url);
}
select.addEventListener('change',()=>{stop();index=frames.findIndex(frame=>frame.date===select.value);render();});
$('previous').addEventListener('click',()=>{stop();index=Math.max(0,index-1);render();});
$('next').addEventListener('click',()=>{stop();index=Math.min(frames.length-1,index+1);render();});
$('play').addEventListener('click',()=>{if(timer!==null){stop();return;}if(index===frames.length-1)index=0;render();$('play').textContent='Pause';$('play').setAttribute('aria-pressed','true');timer=setInterval(()=>{if(index>=frames.length-1){stop();return;}index++;render();if(index===frames.length-1)stop();},1500);});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
function motionPreference(){if(reducedMotion.matches)stop();$('play').disabled=reducedMotion.matches;$('play').title=reducedMotion.matches?'Reduced motion enabled; use the date selector or Previous and Next.':'';}
reducedMotion.addEventListener('change',motionPreference);motionPreference();window.addEventListener('pagehide',stop);render();$('controls').hidden=false;
})();
