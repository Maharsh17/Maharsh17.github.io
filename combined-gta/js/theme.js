/* Main-menu theme music.
 *
 * Three constraints drove the design:
 *
 * 1. Browsers block audio until a real user gesture, so this can never start
 *    on load. It always begins as a click.
 * 2. This is a multi-page site, so an <audio> element dies on every
 *    navigation. Music running sitewide would restart or stutter on each page
 *    change. Playing only on the main menu sidesteps that entirely, and is
 *    also what the game does: menu music stops when you load in.
 * 3. A portfolio should not play music at someone reading it. Silence is the
 *    default and the visitor opts in.
 *
 * The preference is remembered, and playback position is kept for the session,
 * so returning to the menu resumes rather than restarting a six-minute track.
 */
(function () {
	var btn = document.getElementById("theme-toggle");
	if (!btn) return;

	var PREF = "gta-theme-on";
	var POS = "gta-theme-pos";

	var audio = new Audio("./assets/audio/theme.mp3");
	audio.loop = true;
	audio.volume = 0.45;
	audio.preload = "none";

	function paint(on) {
		btn.textContent = on ? "▶ theme" : "■ theme";
		btn.setAttribute("aria-pressed", on ? "true" : "false");
		btn.classList.toggle("is-on", on);
	}

	function remember() {
		try { sessionStorage.setItem(POS, String(audio.currentTime)); } catch (e) {}
	}

	function start() {
		var at = 0;
		try { at = parseFloat(sessionStorage.getItem(POS)) || 0; } catch (e) {}
		if (at && isFinite(at)) audio.currentTime = at;
		return audio.play().then(function () {
			paint(true);
			try { localStorage.setItem(PREF, "1"); } catch (e) {}
		});
	}

	function stop() {
		remember();
		audio.pause();
		paint(false);
		try { localStorage.setItem(PREF, "0"); } catch (e) {}
	}

	btn.addEventListener("click", function () {
		if (audio.paused) {
			start().catch(function () { paint(false); });
		} else {
			stop();
		}
	});

	window.addEventListener("pagehide", remember);
	setInterval(function () { if (!audio.paused) remember(); }, 2000);

	paint(false);

	/* If they turned it on earlier, try to resume. A fresh page load is a fresh
	   autoplay decision, so this succeeds only once the browser trusts the
	   origin. When it is refused we simply stay off and wait for a click. */
	var wanted = "0";
	try { wanted = localStorage.getItem(PREF) || "0"; } catch (e) {}
	if (wanted === "1") {
		start().catch(function () { paint(false); });
	}
})();
