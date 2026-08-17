/* The menu blip on hover.
 *
 * Replaces assets/menu/js/gtasamenu.js, which bound a mouseenter handler to
 * every .menu-option present at the moment it ran. That had three problems
 * here:
 *
 *   - Rows rendered later never got one. projects.js fetches its data and
 *     builds the rows after that script has already finished, so the entire
 *     projects page was silent.
 *   - The sound path was relative, so it resolved against whatever URL the
 *     page happened to have. From a blog post one directory down it 404'd.
 *   - One shared Audio object: play() on an already-playing element does
 *     nothing, so hovering quickly down a list made a single blip.
 *
 * One delegated listener fixes all three. It covers rows that do not exist
 * yet, needs no rebinding after a client-side page swap, and cannot go stale.
 */
(function () {
	// Resolved against this file's own URL, so it is correct from any depth
	// and immune to the base URL changing under a client-side navigation.
	var here = document.currentScript && document.currentScript.src;
	var SRC = here
		? new URL("../assets/menu/sounds/button.wav", here).href
		: "./assets/menu/sounds/button.wav";

	var sound = new Audio(SRC);
	sound.preload = "auto";

	// mouseenter does not bubble, so delegation listens to mouseover and
	// tracks which option is current. Moving between children of the same row
	// fires mouseover repeatedly; only a change of row is an entry.
	var current = null;

	document.addEventListener("mouseover", function (e) {
		var option = e.target.closest ? e.target.closest(".menu-option") : null;
		if (option === current) return;
		current = option;
		if (!option) return;

		// Rewinding first is what lets a fast run down a list blip on every
		// row instead of once. Browsers refuse audio before the first click,
		// which is expected and silent.
		try { sound.currentTime = 0; } catch (err) { /* not seekable yet */ }
		sound.play().catch(function () {});
	});
})();
