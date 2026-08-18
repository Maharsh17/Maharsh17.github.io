/* Shared layer for the combined GTA site.
 *
 * Each page tags itself with <body data-section="..."> and loads the
 * notification library from gtasa-notification.js. That library appends its own
 * fixed-position containers to <body> and its CSS is fully namespaced under
 * .gtasa-notification*, which is why it can run on top of any page here without
 * disturbing that page's own styles.
 *
 * Sections in use:
 *   main, brief, missions, loadgame, options, map, quitgame, wasted
 *
 * GTASA.notification(messageOrOptions, position, time)
 *   message   string, "~n~" becomes a line break
 *   position  "top left" | "top right" | "bottom left" | "bottom right"
 *   time      milliseconds on screen (last 20% is the fade)
 *   options form also takes { enableSound: bool, soundUrl: string }
 */

(function () {
	// Only the main menu speaks on entry. Firing on every section turns a nice
	// moment into background noise, so the rest never run this at all.
	if (document.body.dataset.section !== "main" ||
		typeof GTASA === "undefined") return;

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

	// ponytail: sound is off on purpose. Browsers block audio until the user
	// has clicked something, so an entry notification is silent no matter what
	// we pass.

	// This file re-runs on every client-side swap, so returning to the main
	// menu would otherwise greet and re-count the visitor each time. The flag
	// lives on window because the swap re-executes this whole closure.
	if (window.__gtaGreeted) return;
	window.__gtaGreeted = true;

	// The tally is a first-visit moment. A returning visitor gets the greeting
	// alone and does not re-increment the counter, so the number stays a count
	// of people rather than of page loads. localStorage can throw when storage
	// is blocked, in which case every visit reads as the first one.
	var SEEN = "gta-viewer-count-seen";
	var seen = false;
	try { seen = localStorage.getItem(SEEN) === "1"; } catch (e) {}

	var announced = false;

	function announce(count) {
		if (announced) return;
		announced = true;
		var message = "Welcome CJ";
		// The greeting has to stand on its own. If the counter is slow, down or
		// blocked, the visitor still gets the same welcome minus one line,
		// rather than an apology or a zero presented as a real tally.
		if (count > 0) {
			message += "~n~~n~You're the " + ordinal(count) + " viewer";
			// Marked only once the tally is actually on screen, so a counter
			// outage does not silently spend the visitor's one shot at it.
			try { localStorage.setItem(SEEN, "1"); } catch (e) {}
		}
		GTASA.notification({
			message: message,
			position: "bottom right",
			time: 6000,
			enableSound: false
		});
	}

	setTimeout(function () { announce(0); }, 2500);

	if (seen) return;

	fetch(COUNTER + (LOCAL ? "get" : "hit") + "/janimaharsh.com/home")
		.then(function (r) { return r.ok ? r.json() : null; })
		.then(function (d) { announce(d && d.value ? d.value : 0); })
		.catch(function () { announce(0); });
})();
