/*
 * NearbyGo map helpers (SRS 4.4).
 *
 * Uses Leaflet with OpenStreetMap tiles. If Leaflet or the tiles cannot load,
 * a message is shown and the rest of the page keeps working (FR-MP-06, NFR-PE-05).
 * Data is read from <script type="application/json"> blocks produced by
 * Django's json_script filter, and popups are built with DOM methods so place
 * text is never interpreted as HTML.
 */
(function () {
  "use strict";

  var TILE_TIMEOUT_MS = 8000;

  function readJSON(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  function showStatus(statusId, text) {
    var el = document.getElementById(statusId);
    if (!el) return;
    el.textContent = text;
    el.hidden = false;
  }

  function createMap(elementId, config, statusId, fallbackText) {
    var el = document.getElementById(elementId);
    if (!el || !config) return null;
    if (typeof window.L === "undefined") {
      el.classList.add("map-unavailable");
      showStatus(statusId, "The map could not be loaded. " + fallbackText);
      return null;
    }

    var map = L.map(el, { scrollWheelZoom: false, keyboard: true });
    map.setView(config.center, config.zoom);
    // Let people scroll the page past the map; zoom with the wheel only after they click the map.
    map.once("focus", function () { map.scrollWheelZoom.enable(); });
    map.on("click", function () { map.scrollWheelZoom.enable(); });

    var tiles = L.tileLayer(config.tileUrl, {
      maxZoom: 19,
      attribution: config.attribution // FR-MP-05, OR-03
    }).addTo(map);

    var loaded = false;
    var warned = false;
    function warn() {
      if (warned || loaded) return;
      warned = true;
      showStatus(statusId, "Map images could not be loaded right now. " + fallbackText);
    }
    tiles.on("tileload", function () { loaded = true; });
    var errors = 0;
    tiles.on("tileerror", function () { errors += 1; if (errors >= 3) warn(); });
    window.setTimeout(warn, TILE_TIMEOUT_MS);
    return map;
  }

  function markerIcon(colour, label, extraClass) {
    var span = document.createElement("span");
    span.className = "ng-pin" + (extraClass ? " " + extraClass : "");
    span.style.setProperty("--pin", colour || "#0e6a73");
    if (label) span.textContent = label;
    return L.divIcon({
      className: "ng-marker",
      html: span.outerHTML,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -14]
    });
  }

  function popupContent(m, prefix) {
    var box = document.createElement("div");
    box.className = "ng-popup";
    var title = document.createElement("strong");
    title.textContent = (prefix || "") + m.name;
    var meta = document.createElement("span");
    meta.className = "ng-popup-meta";
    meta.textContent = m.category + (typeof m.distance === "number" ? ", " + m.distance.toFixed(1) + " km" : "");
    var link = document.createElement("a");
    link.href = m.url;
    link.textContent = "View details";
    box.appendChild(title);
    box.appendChild(meta);
    box.appendChild(link);
    return box;
  }

  function addMarker(map, m, label, extraClass, prefix) {
    var marker = L.marker([m.lat, m.lng], {
      icon: markerIcon(m.colour, label, extraClass),
      title: m.name,
      keyboard: true,
      riseOnHover: true
    }).addTo(map);
    marker.bindPopup(popupContent(m, prefix));
    var el = marker.getElement();
    if (el) {
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", (prefix || "") + m.name + ", " + m.category);
    }
    return marker;
  }

  function fit(map, markers, singleZoom) {
    if (!markers.length) return;
    if (markers.length === 1) {
      map.setView(markers[0].getLatLng(), singleZoom || 14);
    } else {
      map.fitBounds(L.featureGroup(markers).getBounds(), { padding: [36, 36], maxZoom: 15 });
    }
  }

  window.NearbyGoMaps = {
    /* One place on its details page. */
    single: function (elementId, markerId, configId, statusId) {
      var data = readJSON(markerId);
      var map = createMap(elementId, readJSON(configId), statusId, "The address details on this page still apply.");
      if (!map || !data) return;
      var marker = addMarker(map, data, "", "");
      fit(map, [marker], 14);
    },

    /* Every place on the map page (FR-MP-01 to FR-MP-04). */
    many: function (elementId, markersId, configId, statusId) {
      var data = readJSON(markersId) || [];
      var map = createMap(elementId, readJSON(configId), statusId, "The list of places below still works.");
      if (!map) return;
      var markers = data.map(function (m) {
        return addMarker(map, m, "", m.inPlan ? "is-planned" : "");
      });
      fit(map, markers, 13);
    },

    /* Plan stops numbered in visit order. No route is drawn: version 1.0 has no routing (BR-06). */
    plan: function (elementId, markersId, configId, statusId) {
      var data = readJSON(markersId) || [];
      var map = createMap(elementId, readJSON(configId), statusId, "Your plan list still works.");
      if (!map) return;
      var markers = data.map(function (m) {
        return addMarker(map, m, String(m.order), "is-numbered", m.order + ". ");
      });
      fit(map, markers, 13);
    }
  };
})();
