"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const dynamics = JSON.parse(fs.readFileSync(path.join(root, "research/ocean-state-intra-state-dynamics-synthesis-sant-2018.json"), "utf8"));

function element() {
  return {
    children: [],
    listeners: {},
    textContent: "",
    append(child) { this.children.push(child); },
    replaceChildren() { this.children = []; },
    addEventListener(type, callback) { this.listeners[type] = callback; },
  };
}

const select = element(), body = element(), cutoffResult = element(), repeatBody = element(), ensembleBody = element(), ensembleResult = element();
select.value = "27_0_to_27_5";
const document = {
  querySelector(selector) { return selector === "#interior-density-bin" ? select : selector === "#interior-density-monthly-body" ? body : selector === "#interior-cutoff-result" ? cutoffResult : selector === "#interior-july-repeat-body" ? repeatBody : selector === "#interior-july-ensemble-body" ? ensembleBody : selector === "#interior-july-ensemble-result" ? ensembleResult : null; },
  createElement() { return element(); },
};
const context = vm.createContext({ window: { OSW_INTRA_STATE_DYNAMICS: dynamics }, document });
vm.runInContext(fs.readFileSync(path.join(root, "exchange/interior-stage.js"), "utf8"), context);
vm.runInContext("renderDensityMonthTable()", context);
assert.equal(body.children.length, 12);
assert.equal(body.children[6].children[5].textContent, "Same sign");
assert.equal(body.children[7].children[5].textContent, "Changes sign");
assert.equal(body.children[7].children[2].textContent, "+0.048");
assert.equal(body.children[7].children[1].textContent, "15.78%");

select.value = "below_26_5";
select.listeners.change();
assert.equal(body.children.length, 12);
assert.equal(body.children[7].children[2].textContent, "0.000");
assert.equal(body.children[7].children[5].textContent, "Near zero");
vm.runInContext("renderCutoffSummary()", context);
assert.match(cutoffResult.textContent, /July's middle-high bin stays outward/);
assert.match(cutoffResult.textContent, /August's primary baseline sign changes/);
vm.runInContext("renderJulyRepeatTable()", context);
assert.equal(repeatBody.children.length, 3);
assert.equal(repeatBody.children[1].children[4].textContent, "Fail");
assert.match(repeatBody.children[1].children[3].textContent, /-0\.021 \(east control, baseline, upstream\)/);
vm.runInContext("renderJulyEnsembleTable()", context);
assert.equal(ensembleBody.children.length, 5);
assert.equal(ensembleBody.children[0].children[0].textContent, "opa0");
assert.match(ensembleResult.textContent, /members pass the strict four-box sign rule/);
console.log("interior density table interaction passed");
