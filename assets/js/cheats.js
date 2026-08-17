/* Cheat codes. Type a real San Andreas code anywhere on the site.
 *
 * Loaded on every page. Keeps a rolling buffer of the last N letters typed and
 * matches it against the codes below. Effects are per-page where one makes
 * sense, and every message uses the game's own wording from american.gxt.
 *
 * Deliberately undiscoverable: nothing on the site advertises this. A visitor
 * who knows GTA finds it; everyone else sees a clean site. */
(function () {
	if (typeof GTASA === "undefined") return;

	var BUFFER_MAX = 16;
	var buffer = "";

	// Absolute, because a cheat can be typed on any page and the pages sit at
	// three different depths.
	var HERE = (document.currentScript && document.currentScript.src) || location.href;
	var MAP = new URL("../../map/", HERE).href;
	var WASTED = new URL("../../404.html", HERE).href;
	var AWSHI = new Audio(new URL("../audio/awshi.mp3", HERE).href);

	function notify(message, position) {
		GTASA.notification({
			message: message,
			position: position || "bottom right",
			time: 4000,
			enableSound: true
		});
	}

	/* Fill every stat bar, hold, then restore. Works on the stats page and the
	   weapons page, both of which render .gtasa-stats-bar--progress or
	   .site-wbar-fill children. */
	function maxBars() {
		var fills = document.querySelectorAll(
			".gtasa-stats-bar--progress > div, .site-wbar-fill");
		if (!fills.length) return false;
		var previous = [];
		var i;
		for (i = 0; i < fills.length; i++) {
			previous.push(fills[i].style.width);
			fills[i].style.transition = "width .4s ease";
			fills[i].style.width = "100%";
		}
		setTimeout(function () {
			for (var j = 0; j < fills.length; j++) {
				fills[j].style.width = previous[j];
			}
		}, 6000);
		return true;
	}

	function flash(color) {
		var el = document.createElement("div");
		el.style.cssText = "position:fixed;inset:0;z-index:9998;pointer-events:none;" +
			"background:" + color + ";opacity:.55;transition:opacity 1.2s ease";
		document.body.appendChild(el);
		requestAnimationFrame(function () { el.style.opacity = "0"; });
		setTimeout(function () {
			if (el.parentNode) el.parentNode.removeChild(el);
		}, 1400);
	}

	var CODES = {
		// Health, armour and money. The one everybody remembers.
		HESOYAM: function () {
			notify("Cheat activated~n~~n~$250,000, full health, full armour");
			maxBars();
			// Rewind so a second HESOYAM restarts the clip instead of no-opping.
			AWSHI.currentTime = 0;
			AWSHI.play();
		},
		// Infinite health.
		BAGUVIX: function () {
			notify("Cheat activated~n~~n~Infinite health", "top left");
			flash("#306C26");
		},
		// Weapon set. The weapons page is gone, so this is message only now.
		PROFESSIONALSKIT: function () {
			notify("Cheat activated~n~~n~Weapon set 2", "top right");
			flash("#C2A22B");
		},
		// Jetpack. Takes you to the map, the only page that is a place.
		ROCKETMAN: function () {
			notify("Cheat activated~n~~n~Jetpack", "top right");
			setTimeout(function () { window.location.href = MAP; }, 900);
		},
		// Riot mode. Just a colour and a message.
		STATEOFEMERGENCY: function () {
			notify("Cheat activated~n~~n~Riot mode", "bottom left");
			flash("#BF242A");
		},
		// Wanted level. Fires the death screen.
		BRINGITON: function () {
			notify("Cheat activated~n~~n~Six star wanted level", "top left");
			setTimeout(function () { window.location.href = WASTED; }, 900);
		}
	};

	// Longest code decides how much history we need to keep.
	for (var code in CODES) {
		if (Object.prototype.hasOwnProperty.call(CODES, code)) {
			BUFFER_MAX = Math.max(BUFFER_MAX, code.length);
		}
	}

	document.addEventListener("keydown", function (e) {
		// Ignore typing in a field, and ignore modified keys.
		var tag = (e.target && e.target.tagName) || "";
		if (tag === "INPUT" || tag === "TEXTAREA" || e.ctrlKey || e.metaKey) return;
		if (!/^[a-zA-Z]$/.test(e.key)) return;

		buffer = (buffer + e.key.toUpperCase()).slice(-BUFFER_MAX);

		for (var code in CODES) {
			if (!Object.prototype.hasOwnProperty.call(CODES, code)) continue;
			if (buffer.slice(-code.length) === code) {
				buffer = "";
				CODES[code]();
				return;
			}
		}
	});
})();
