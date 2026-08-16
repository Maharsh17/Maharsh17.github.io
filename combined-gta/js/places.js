/* Pins real places onto the San Andreas map.
 *
 * The map image is Los Santos and the places are in Illinois. That mismatch is
 * the point: it is a deliberate conceit, not a mislabelled map. The legend
 * says so explicitly so it reads as a joke rather than an error.
 *
 * Icons are authentic radar sprites decoded from the game's hud.txd. */
(function () {
	var host = document.querySelector(".menu-content--map");
	if (!host) return;

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;");
	}

	fetch("./data/places.json").then(function (r) {
		if (!r.ok) throw new Error(r.status);
		return r.json();
	}).then(function (data) {
		var frag = document.createDocumentFragment();
		var i, p, pin;
		for (i = 0; i < data.places.length; i++) {
			p = data.places[i];
			pin = document.createElement("div");
			pin.className = "site-pin";
			pin.style.left = p.x + "%";
			pin.style.top = p.y + "%";
			pin.innerHTML =
				'<img src="./assets/game/hud/' + esc(p.icon) + '" alt="" class="site-pin-icon">' +
				'<span class="site-pin-label"><b>' + esc(p.name) + '</b><br>' +
				esc(p.detail) + '</span>';
			frag.appendChild(pin);
		}
		host.appendChild(frag);
	}).catch(function () {
		// Map still renders without pins.
	});
})();
