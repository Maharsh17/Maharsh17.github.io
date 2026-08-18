/* Cheat codes. Type a real San Andreas code anywhere on the site.
 *
 * Loaded on every page. Keeps a rolling buffer of the last N letters typed and
 * matches it against the codes below. Every code does the same thing: the
 * game's own wording from american.gxt, and every stat bar on the page filled.
 *
 * Deliberately undiscoverable: nothing on the site advertises this. A visitor
 * who knows GTA finds it; everyone else sees a clean site. */
(function () {
	if (typeof GTASA === "undefined") return;

	var BUFFER_MAX = 0;
	var buffer = "";

	// Absolute, because a cheat can be typed on any page and the pages sit at
	// three different depths.
	var HERE = (document.currentScript && document.currentScript.src) || location.href;
	var AWSHI = new Audio(new URL("../audio/awshi.mp3", HERE).href);
	// Fetched up front so the clip is ready the instant HESOYAM is typed.
	AWSHI.preload = "auto";
	// The vendor default soundUrl is relative and wrong for this layout, so the
	// notification sound only fires if we hand it an absolute one.
	var NOTIFY_WAV = new URL("../vendor/notify/sounds/notification.wav", HERE).href;

	/* HESOYAM plays the tone and then the sound bite, one after the other. The
	   library only fires its clip and forgets it, with no hook for the end, so
	   HESOYAM owns its own tone and chains off that instead. */
	var TONE = new Audio(NOTIFY_WAV);
	TONE.preload = "auto";

	function playAwshi() {
		AWSHI.currentTime = 0;
		// A blocked or missing clip just stays quiet.
		AWSHI.play().catch(function () {});
	}

	TONE.addEventListener("ended", playAwshi);

	/* Fill every stat bar, hold, then restore. Works on the stats page and the
	   weapons page, both of which render .gtasa-stats-bar--progress or
	   .site-wbar-fill children. */
	function maxBars() {
		var fills = document.querySelectorAll(
			".gtasa-stats-bar--progress > div, .site-wbar-fill");
		if (!fills.length) return;
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
	}

	// Code to the line the game prints when you enter it. Every code behaves
	// identically, so this is a table rather than thirteen copies of HESOYAM.
	var CODES = {
		HESOYAM: "$250,000, full health, full armour",
		BAGUVIX: "Infinite health",
		LXGIWYL: "Weapon set 1",
		PROFESSIONALSKIT: "Weapon set 2",
		FULLCLIP: "Infinite ammo, no reload",
		ROCKETMAN: "Jetpack",
		JUMPJET: "Spawn Hydra",
		OHDUDE: "Spawn Hunter",
		AIWPRTON: "Spawn Rhino",
		CHITTYCHITTYBANGBANG: "Cars can fly",
		AEZAKMI: "Never wanted",
		BRINGITON: "Six star wanted level",
		STATEOFEMERGENCY: "Riot mode"
	};

	// Longest code decides how much history we need to keep.
	for (var code in CODES) {
		if (Object.prototype.hasOwnProperty.call(CODES, code)) {
			BUFFER_MAX = Math.max(BUFFER_MAX, code.length);
		}
	}

	function activate(code) {
		var hesoyam = code === "HESOYAM";
		GTASA.notification({
			message: "Cheat activated~n~~n~" + CODES[code],
			position: "bottom right",
			time: 4000,
			// Every other code lets the library play the tone. HESOYAM plays
			// its own below, so it can follow it with the sound bite.
			enableSound: !hesoyam,
			soundUrl: NOTIFY_WAV
		});
		maxBars();
		if (!hesoyam) return;
		// Rewound so a second HESOYAM restarts the run instead of no-opping.
		// If the tone cannot play at all, go straight to the sound bite rather
		// than losing it to a silent first half.
		TONE.currentTime = 0;
		TONE.play().catch(playAwshi);
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
				activate(code);
				return;
			}
		}
	});
})();
