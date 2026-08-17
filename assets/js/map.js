/* Interactive map page, backed by the "GTA SA" MapTiler style.
 *
 * Centres on the viewer's own location when they allow it, and falls back to
 * Champaign-Urbana otherwise. The fallback is not an error path: most visitors
 * will decline or be on a browser that blocks the prompt, so Champaign is the
 * expected default rather than a consolation.
 *
 * Geolocation requires a secure context. It works on localhost and over HTTPS,
 * and silently fails on plain http from another host, which the catch handles.
 *
 * Maharsh's own places are added as markers using authentic radar sprites
 * decoded from the game's hud.txd. */
(function () {
	var el = document.getElementById("map");
	if (!el || typeof maplibregl === "undefined") return;

	// Resolved against this file, not the page, for the same reason as
	// projects.js: the map page is one level down but the script is shared.
	var HERE = (document.currentScript && document.currentScript.src) || location.href;
	function asset(rel) { return new URL(rel, HERE).href; }

	var STYLE = "https://api.maptiler.com/maps/2b36665a-5454-4b57-9676-ff47dc5d11cc/style.json?key=V8DFSo7qMSgAu0JLPgjH";

	// Champaign-Urbana, from the styled map's own share link.
	var FALLBACK = { lng: -88.22906, lat: 40.11088, zoom: 15.05 };

	var status = document.querySelector(".site-map-status");

	function say(text) {
		if (status) status.textContent = text;
	}

	// This file re-runs every time the map page is navigated to, and the old
	// container is gone by then. Left alone, each visit stranded a live Map
	// holding a WebGL context and an animation loop, which threw NotFoundError
	// trying to clean up DOM that no longer existed. Browsers cap WebGL
	// contexts, so enough visits would have stopped the map working at all.
	if (window.__map) {
		try { window.__map.remove(); } catch (e) { /* already torn down */ }
	}

	var map = new maplibregl.Map({
		container: "map",
		style: STYLE,
		center: [FALLBACK.lng, FALLBACK.lat],
		zoom: FALLBACK.zoom,
		attributionControl: { compact: true }
	});

	window.__map = map;

	map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
	map.addControl(new maplibregl.ScaleControl({ unit: "imperial" }), "bottom-left");

	// MapLibre measures its container once, at construction. The container is
	// sized by the page grid, which has not necessarily resolved by then, and
	// when the page arrives through a client-side swap it certainly has not.
	// A zero-height measurement puts the projection origin at the top edge, so
	// markers north of centre land at negative y and sit outside the frame:
	// the map looks empty even though every tile returned 200. Re-measuring
	// after layout settles is the fix.
	function fit() { try { map.resize(); } catch (e) { /* torn down */ } }
	requestAnimationFrame(fit);
	map.on("load", fit);
	window.addEventListener("resize", fit);

	say("Champaign - Urbana, Illinois");

	// Set once the viewer shares their location, so the fit below does not
	// yank the view back to Champaign after they have been taken to their own.
	var followingViewer = false;

	/* Personal markers. Only meaningful over Champaign, so they are added once
	   and simply sit off-screen if the viewer is somewhere else. */
	function addPlaces() {
		fetch(asset("../data/places.json")).then(function (r) {
			if (!r.ok) throw new Error(r.status);
			return r.json();
		}).then(function (data) {
			var bounds = new maplibregl.LngLatBounds();
			data.places.forEach(function (p) {
				var img = document.createElement("img");
				img.src = asset("../game/hud/" + p.icon);
				img.className = "site-marker";
				img.alt = p.name;
				new maplibregl.Marker({ element: img })
					.setLngLat([p.lon, p.lat])
					.setPopup(new maplibregl.Popup({ offset: 16, closeButton: false })
						.setHTML("<b>" + p.name + "</b><br>" + p.detail))
					.addTo(map);
				bounds.extend([p.lon, p.lat]);
			});

			// A fixed zoom cannot know how tall the frame is. At 15.05 the five
			// places spanned about 930px inside a 351px container, so four of
			// them sat outside the frame and the map read as empty even with
			// every tile loaded. Framing the places themselves works at any
			// size, which is the whole point of showing them.
			if (!followingViewer && !bounds.isEmpty()) {
				map.fitBounds(bounds, { padding: 70, maxZoom: 16, duration: 0 });
			}
		}).catch(function () {
			// Map is still useful without the personal pins.
		});
	}

	map.on("load", addPlaces);

	/* Try the viewer's location. Anything other than an explicit allow leaves
	   the Champaign default in place. */
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			function (pos) {
				var c = [pos.coords.longitude, pos.coords.latitude];
				followingViewer = true;
				map.flyTo({ center: c, zoom: FALLBACK.zoom, speed: 0.8 });
				new maplibregl.Marker({ color: "#bf242a" })
					.setLngLat(c)
					.setPopup(new maplibregl.Popup({ offset: 16, closeButton: false })
						.setHTML("<b>You are here</b>"))
					.addTo(map);
				say("Your location");
			},
			function () {
				say("Champaign - Urbana, Illinois (location not shared)");
			},
			{ enableHighAccuracy: false, timeout: 8000, maximumAge: 600000 }
		);
	}
})();
