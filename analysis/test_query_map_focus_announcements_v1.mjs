import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync('almanac/query.js','utf8');
const body=source.match(/function bindMapAnnouncement\(node,feature,layer\)\{[\s\S]*?\n  \}/)?.[0];
assert.ok(body,'Actual map announcement event binding is available');
const description={textContent:''},document={activeElement:null};
const bind=vm.runInNewContext(body+';bindMapAnnouncement',{$:()=>description,document});
class Mark {
  constructor(name){this.name=name;this.handlers=new Map();}
  getAttribute(name){assert.equal(name,'aria-label');return this.name;}
  addEventListener(type,handler){this.handlers.set(type,handler);}
  closest(selector){assert.equal(selector,'.query-map-mark');return this;}
  fire(type){this.handlers.get(type)();}
  focus(options){this.focusOptions=options;document.activeElement=this;this.fire('focus');}
}
const spring=new Mark('Spring route'),fall=new Mark('Fall route'),marks=new Set([spring,fall]);
const layer={contains:node=>marks.has(node)};
bind(spring,{note:'Spring scope'},layer);bind(fall,{note:'Fall scope'},layer);
spring.focus();fall.fire('pointerenter');
assert.equal(description.textContent,'Spring route — Spring scope');
fall.focus();spring.fire('pointerenter');
assert.equal(description.textContent,'Fall route — Fall scope');
assert.equal(document.activeElement,fall);
spring.fire('pointerdown');
assert.equal(document.activeElement,spring);
assert.equal(spring.focusOptions.preventScroll,true);
assert.equal(description.textContent,'Spring route — Spring scope');
document.activeElement=null;fall.fire('pointerenter');
assert.equal(description.textContent,'Fall route — Fall scope');
document.activeElement={closest:()=>null};spring.fire('pointerenter');
assert.equal(description.textContent,'Spring route — Spring scope');
assert.ok(source.includes("bindMapAnnouncement(node,feature,$('query-map-features'))"));
console.log('PASS actual map handlers: keyboard focus survives competing hover; pointer activation transfers focus; ordinary hover remains available');
