/* Paints the HUD page's sky using GTA San Andreas' real colour grading.
 *
 * data/timecyc.json holds the 8 EXTRASUNNY_LA keyframes straight out of the
 * game's timecyc.dat. We interpolate between them by the visitor's local hour,
 * so at 3am the page is the game's midnight sky and at noon it is its midday
 * blue. Wraps around midnight, hence the modular distance below. */
(function () {
	// Paint the body itself rather than a layer behind it. A fixed element at
	// z-index -1 under a body that has its own background colour is fragile
	// stacking; the body has no such ambiguity.
	var host = document.querySelector(".site-hud-page");
	if (!host) return;

	function lerp(a, b, t) { return Math.round(a + (b - a) * t); }

	function rgb(c) { return "rgb(" + c[0] + "," + c[1] + "," + c[2] + ")"; }

	function mix(c1, c2, t) {
		return [lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t)];
	}

	function paint(keys) {
		var now = new Date();
		var hour = now.getHours() + now.getMinutes() / 60;

		// Find the keyframe at or before `hour`, wrapping past the last one.
		var lo = keys[keys.length - 1];
		var hi = keys[0];
		for (var i = 0; i < keys.length; i++) {
			if (keys[i].hour <= hour) {
				lo = keys[i];
				hi = keys[i + 1] || keys[0];
			}
		}

		// Modular span so the 22:00 -> 00:00 wrap interpolates over 2 hours,
		// not backwards over 22.
		var span = (hi.hour - lo.hour + 24) % 24 || 24;
		var into = (hour - lo.hour + 24) % 24;
		var t = Math.min(into / span, 1);

		var top = mix(lo.top, hi.top, t);
		var bottom = mix(lo.bottom, hi.bottom, t);
		host.style.background = "linear-gradient(" + rgb(top) + " 0%, " + rgb(bottom) + " 100%)";

		var label = document.querySelector(".site-sky-label");
		if (label) {
			label.textContent = "San Andreas sky at your local " +
				(now.getHours() < 10 ? "0" : "") + now.getHours() +
				(now.getMinutes() < 10 ? ":0" : ":") + now.getMinutes();
		}
	}

	fetch("./data/timecyc.json").then(function (r) {
		if (!r.ok) throw new Error(r.status);
		return r.json();
	}).then(function (data) {
		paint(data.keys);
		// Repaint every minute so a page left open follows the clock.
		setInterval(function () { paint(data.keys); }, 60000);
	}).catch(function () {
		// Leave the CSS fallback background in place.
	});
})();
