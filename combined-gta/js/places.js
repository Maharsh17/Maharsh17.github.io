/* Overlays Maharsh's own places onto the generated Champaign-Urbana map.
 *
 * The base map is assets/map/champaign-urbana.svg, built by
 * scripts/build-cu-map.py from real WGS84 coordinates. These pins use the same
 * bounding box and the same projection, so a pin lands where the place
 * actually is rather than where it looked about right.
 *
 * The SVG viewBox is 1000x720 with the map panel occupying the left 700px, so
 * a panel-relative position has to be rescaled against the full viewBox before
 * it becomes a CSS percentage. */
(function () {
	var host = document.querySelector(".site-map-pins");
	if (!host) return;

	// Must match scripts/build-cu-map.py.
	var VIEW_W = 1000, VIEW_H = 720, MAP_W = 700, PAD = 12;

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;");
	}

	function project(lon, lat, bbox) {
		var x = (lon - bbox.lonW) / (bbox.lonE - bbox.lonW) * (MAP_W - 2 * PAD) + PAD;
		var y = (bbox.latN - lat) / (bbox.latN - bbox.latS) * (VIEW_H - 2 * PAD) + PAD;
		return { x: (x / VIEW_W) * 100, y: (y / VIEW_H) * 100 };
	}

	fetch("./data/places.json").then(function (r) {
		if (!r.ok) throw new Error(r.status);
		return r.json();
	}).then(function (data) {
		var bbox = data.bbox;
		var frag = document.createDocumentFragment();
		var i, p, pos, pin;
		for (i = 0; i < data.places.length; i++) {
			p = data.places[i];
			pos = project(p.lon, p.lat, bbox);
			pin = document.createElement("div");
			pin.className = "site-pin";
			pin.style.left = pos.x.toFixed(2) + "%";
			pin.style.top = pos.y.toFixed(2) + "%";
			pin.innerHTML =
				'<img src="./assets/game/hud/' + esc(p.icon) + '" alt="" class="site-pin-icon">' +
				'<span class="site-pin-label"><b>' + esc(p.name) + '</b><br>' +
				esc(p.detail) + '</span>';
			frag.appendChild(pin);
		}
		host.appendChild(frag);
	}).catch(function () {
		// Base map still renders without the personal pins.
	});
})();
