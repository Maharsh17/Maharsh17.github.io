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

	// Only the main menu speaks on entry. Firing on all 11 sections turns a
	// nice moment into background noise, so the rest stay quiet.
	// ponytail: sound is off on purpose. Browsers block audio until the user
	// has clicked something, so an entry notification is silent no matter what
	// we pass. Pages that notify after a click (notifications.html) keep sound.
	if (section === "main") {
		var now = new Date();
		GTASA.notification({
			message: "You have entered Chambana~n~~n~" +
				clock(now) + " - " + skyState(now.getHours()),
			position: "bottom right",
			time: 5000,
			enableSound: false
		});
	}
})();
