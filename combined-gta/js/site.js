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

	// Only the main menu speaks on entry. Firing on all 11 sections turns a
	// nice moment into background noise, so the rest stay quiet.
	// ponytail: sound is off on purpose. Browsers block audio until the user
	// has clicked something, so an entry notification is silent no matter what
	// we pass. Pages that notify after a click (notifications.html) keep sound.
	if (section === "main") {
		GTASA.notification({
			message: "Welcome back~n~~n~Grand Theft Auto: San Andreas",
			position: "bottom right",
			time: 5000,
			enableSound: false
		});
	}
})();
