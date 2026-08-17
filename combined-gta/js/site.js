/* Shared layer for the combined GTA site.
 *
 * Each page tags itself with <body data-section="..."> and loads the
 * notification library from gtasa-notification.js. That library appends its own
 * fixed-position containers to <body> and its CSS is fully namespaced under
 * .gtasa-notification*, which is why it can run on top of any page here without
 * disturbing that page's own styles.
 *
 * Sections in use:
 *   main, hud, stats, map, notifications,
 *   game, options, language, loadgame, deletegame, quitgame
 *
 * GTASA.notification(messageOrOptions, position, time)
 *   message   string, "~n~" becomes a line break
 *   position  "top left" | "top right" | "bottom left" | "bottom right"
 *   time      milliseconds on screen (last 20% is the fade)
 *   options form also takes { enableSound: bool, soundUrl: string }
 */

(function () {
	var section = document.body.dataset.section;
	if (!section || typeof GTASA === "undefined") return;

	// The game announces the area you have just walked into. The second line is
	// the visitor's own clock read through GTA's EXTRASUNNY_LA weather preset,
	// the same keyframes sky.js interpolates for the horizon strip, so the
	// greeting matches the colour at the top of the page instead of contradicting
	// it. "Clear" is not decoration: that preset has no other weather in it.
	function skyState(hour) {
		if (hour < 5) return "clear night";
		if (hour < 8) return "sunrise";
		if (hour < 12) return "clear morning";
		if (hour < 17) return "clear afternoon";
		if (hour < 20) return "sunset";
		return "clear night";
	}

	function clock(now) {
		var h = now.getHours();
		var m = now.getMinutes();
		return (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m;
	}

	// 11th, 12th and 13th are the exceptions every naive version of this gets
	// wrong, so they are checked before the last digit is looked at.
	function ordinal(n) {
		var label = n.toLocaleString();
		var tens = n % 100;
		if (tens >= 11 && tens <= 13) return label + "th";
		switch (n % 10) {
			case 1: return label + "st";
			case 2: return label + "nd";
			case 3: return label + "rd";
			default: return label + "th";
		}
	}

	// A static site cannot count its own visitors, so the tally lives on a free
	// keyless counter. /hit/ increments and returns the new value; /get/ only
	// reads, which is what local development uses so that reloading this page
	// fifty times while working on it does not inflate the real number.
	var COUNTER = "https://abacus.jasoncameron.dev/";
	var LOCAL = location.hostname === "localhost" ||
		location.hostname === "127.0.0.1" ||
		location.protocol === "file:";

	// Only the main menu speaks on entry. Firing on all 11 sections turns a
	// nice moment into background noise, so the rest stay quiet.
	// ponytail: sound is off on purpose. Browsers block audio until the user
	// has clicked something, so an entry notification is silent no matter what
	// we pass. Pages that notify after a click (notifications.html) keep sound.
	if (section !== "main") return;

	var now = new Date();
	var announced = false;

	function announce(count) {
		if (announced) return;
		announced = true;
		var message = "You have entered Chambana~n~~n~" +
			clock(now) + " - " + skyState(now.getHours());
		// The greeting has to stand on its own. If the counter is slow, down or
		// blocked, the visitor still gets the same welcome minus one line,
		// rather than an apology or a zero presented as a real tally.
		if (count > 0) message += "~n~You are the " + ordinal(count) + " visitor";
		GTASA.notification({
			message: message,
			position: "bottom right",
			time: 6000,
			enableSound: false
		});
	}

	setTimeout(function () { announce(0); }, 2500);

	fetch(COUNTER + (LOCAL ? "get" : "hit") + "/janimaharsh.com/home")
		.then(function (r) { return r.ok ? r.json() : null; })
		.then(function (d) { announce(d && d.value ? d.value : 0); })
		.catch(function () { announce(0); });
})();
