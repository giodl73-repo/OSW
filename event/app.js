(function () {
  "use strict";
  const api = window.OSWEventScenes;
  const tabs = Array.from(document.querySelectorAll("[data-scene-tab]"));
  const panels = Array.from(document.querySelectorAll("[data-scene-panel]"));
  const tablist = document.querySelector(".scene-tabs");
  const status = document.getElementById("journey-status");
  const image = document.getElementById("scene-image");
  const imageCaption = document.getElementById("scene-image-caption");
  const stage = document.getElementById("interactive-stage");
  const cache = {};
  const requestedScene = new URL(location.href).searchParams.get("scene");
  const requestedSceneIsValid = api.SCENES.some(function (scene) { return scene.id === requestedScene; });
  let active = api.sceneById(requestedScene);

  function keepCanvasAligned() {
    const scroller = document.scrollingElement;
    if (scroller && scroller.scrollLeft !== 0) scroller.scrollLeft = 0;
  }

  tablist.setAttribute("role", "tablist");
  tabs.forEach(function (tab) {
    tab.setAttribute("role", "tab");
    tab.setAttribute("aria-controls", "static-" + tab.dataset.sceneTab);
  });
  panels.forEach(function (panel) {
    panel.setAttribute("role", "tabpanel");
    panel.tabIndex = 0;
  });

  function announce(message) { status.textContent = message; }
  function sourceMap(scene) {
    return Promise.all(scene.sources.map(function (source) {
      if (cache[source[0]]) return cache[source[0]];
      cache[source[0]] = fetch(source[1]).then(function (response) {
        if (!response.ok) throw new Error("Could not load " + source[0] + " (" + response.status + ")");
        return response.json();
      });
      return cache[source[0]];
    })).then(function (values) {
      return scene.sources.reduce(function (result, source, index) { result[source[0]] = values[index]; return result; }, {});
    });
  }

  function updateUrl(scene, replace) {
    const url = new URL(location.href); url.searchParams.set("scene", scene.id);
    history[replace ? "replaceState" : "pushState"]({ scene: scene.id }, "", url);
  }

  function activate(id, options) {
    const scene = api.sceneById(id); active = scene;
    keepCanvasAligned();
    tabs.forEach(function (tab) { const yes = tab.dataset.sceneTab === scene.id; tab.setAttribute("aria-selected", String(yes)); tab.tabIndex = yes ? 0 : -1; });
    panels.forEach(function (panel) { panel.hidden = panel.dataset.scenePanel !== scene.id; });
    stage.dataset.state = "loading"; image.removeAttribute("src");
    announce("Loading " + scene.label + " evidence.");
    if (!options || options.url !== false) updateUrl(scene, options && options.replace);
    sourceMap(scene).then(function (payloads) {
      const view = api.model(scene, payloads);
      document.getElementById("scene-kicker").textContent = scene.number + " / 05 · " + scene.label;
      document.getElementById("scene-question").textContent = scene.question;
      const badge = document.getElementById("scene-evidence"); badge.textContent = scene.evidence; badge.dataset.evidence = scene.evidenceKey;
      document.getElementById("scene-time").textContent = view.time;
      document.getElementById("scene-finding").textContent = view.finding;
      document.getElementById("scene-secondary").textContent = view.secondary || "";
      document.getElementById("scene-secondary").hidden = !view.secondary;
      document.getElementById("scene-variable").textContent = scene.facts.variable;
      document.getElementById("scene-depth").textContent = scene.facts.depth;
      document.getElementById("scene-space").textContent = scene.facts.space;
      document.getElementById("scene-limitation").textContent = view.limitation;
      document.getElementById("scene-stats").replaceChildren.apply(document.getElementById("scene-stats"), view.stats.map(function (stat) {
        const item = document.createElement("div"); const dt = document.createElement("dt"); const dd = document.createElement("dd");
        dt.textContent = stat.label; dd.textContent = stat.value; item.append(dt, dd); return item;
      }));
      document.getElementById("receipt-link").href = scene.receipt;
      document.getElementById("figure-link").href = scene.figure;
      const onward = document.getElementById("onward-link"); onward.hidden = !scene.onward; if (scene.onward) onward.href = scene.onward;
      image.alt = scene.figureAlt;
      image.onload = keepCanvasAligned;
      image.src = scene.figure;
      imageCaption.textContent = scene.figureAlt;
      const index = api.SCENES.indexOf(scene);
      document.getElementById("previous-scene").disabled = index === 0;
      document.getElementById("next-scene").disabled = index === api.SCENES.length - 1;
      stage.dataset.state = "ready"; announce(scene.label + " evidence loaded. " + view.stats.length + " values shown with limitation.");
    }).catch(function (error) {
      stage.dataset.state = "error";
      document.getElementById("scene-finding").textContent = "This scene could not be rendered from its committed evidence.";
      document.getElementById("scene-limitation").textContent = error.message + ". No substitute value has been shown.";
      document.getElementById("receipt-link").href = scene.receipt;
      announce(scene.label + " evidence error. " + error.message);
    });
  }

  tabs.forEach(function (tab, index) {
    tab.addEventListener("click", function () { activate(tab.dataset.sceneTab); });
    tab.addEventListener("keydown", function (event) {
      if (!(["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key))) return;
      event.preventDefault();
      let target = index + (event.key === "ArrowRight" ? 1 : -1);
      if (event.key === "Home") target = 0; if (event.key === "End") target = tabs.length - 1;
      target = (target + tabs.length) % tabs.length; tabs[target].focus({ preventScroll: true }); activate(tabs[target].dataset.sceneTab);
    });
  });
  document.getElementById("previous-scene").addEventListener("click", function () { const i = api.SCENES.indexOf(active); if (i > 0) activate(api.SCENES[i - 1].id); });
  document.getElementById("next-scene").addEventListener("click", function () { const i = api.SCENES.indexOf(active); if (i < api.SCENES.length - 1) activate(api.SCENES[i + 1].id); });
  document.getElementById("reset-journey").addEventListener("click", function () { activate("event"); });
  addEventListener("popstate", function () { activate(new URL(location.href).searchParams.get("scene"), { url: false }); });
  document.documentElement.classList.add("enhanced");
  activate(active.id, { replace: !requestedSceneIsValid });
})();
