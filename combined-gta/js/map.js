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

	var STYLE = "https://api.maptiler.com/maps/2b36665a-5454-4b57-9676-ff47dc5d11cc/style.json?key=V8DFSo7qMSgAu0JLPgjH";

	// Champaign-Urbana, from the styled map's own share link.
	var FALLBACK = { lng: -88.22906, lat: 40.11088, zoom: 15.05 };

	var status = document.querySelector(".site-map-status");

	function say(text) {
		if (status) status.textContent = text;
	}

	var map = new maplibregl.Map({
		container: "map",
		style: STYLE,
		center: [FALLBACK.lng, FALLBACK.lat],
		zoom: FALLBACK.zoom,
		attributionControl: { compact: true }
	});

	map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
	map.addControl(new maplibregl.ScaleControl({ unit: "imperial" }), "bottom-left");

	say("Champaign - Urbana, Illinois");

	/* Personal markers. Only meaningful over Champaign, so they are added once
	   and simply sit off-screen if the viewer is somewhere else. */
	function addPlaces() {
		fetch("./data/places.json").then(function (r) {
			if (!r.ok) throw new Error(r.status);
			return r.json();
		}).then(function (data) {
			data.places.forEach(function (p) {
				var img = document.createElement("img");
				img.src = "./assets/game/hud/" + p.icon;
				img.className = "site-marker";
				img.alt = p.name;
				new maplibregl.Marker({ element: img })
					.setLngLat([p.lon, p.lat])
					.setPopup(new maplibregl.Popup({ offset: 16, closeButton: false })
						.setHTML("<b>" + p.name + "</b><br>" + p.detail))
					.addTo(map);
			});
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
