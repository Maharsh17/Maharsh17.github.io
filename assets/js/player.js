/* The theme track, continued across pages.
 *
 * A multi-page site tears the <audio> element down on every navigation, so
 * "keep playing" has to mean "restart at the position it reached, on the next
 * page". Two values in localStorage carry that: whether it is on, and how far
 * in it got.
 *
 * Only the main menu has controls. Every other page runs this file purely to
 * pick the track back up, which is why the flag is written from the click
 * handler rather than from the audio element's own play/pause events: those
 * also fire when a document is torn down, and clearing the flag there would
 * stop the music at the first link the visitor clicked.
 *
 * Nothing here starts the track on a first visit. The stored flag only ever
 * becomes "1" inside a real click on the main menu.
 */
(function () {
	var KEY_ON = "gtasa.theme.on";
	var KEY_AT = "gtasa.theme.at";

	var audio = document.getElementById("theme");
	if (!audio) return;

	function read(k) {
		try { return localStorage.getItem(k); } catch (e) { return null; }
	}

	function store(k, v) {
		try { localStorage.setItem(k, v); } catch (e) { /* private mode */ }
	}

	// Controls exist on the main menu only.
	var root = document.getElementById("player");
	var playBtn = root && root.querySelector(".site-player-play");
	var bar = root && root.querySelector(".site-player-bar");
	var fill = root && root.querySelector(".site-player-fill");

	function paint() {
		if (!root || !playBtn) return;
		var playing = !audio.paused && !audio.ended;
		var glyph = root.querySelector(".site-player-glyph");
		if (glyph) glyph.innerHTML = playing ? "&#10074;&#10074;" : "&#9654;";
		playBtn.setAttribute("aria-label", playing ? "Pause theme" : "Play theme");
		root.classList.toggle("is-playing", playing);
	}

	function whenReady(fn) {
		// readyState 1 is HAVE_METADATA: duration is known, so currentTime can
		// be set. Seeking before that throws.
		if (audio.readyState >= 1) fn();
		else audio.addEventListener("loadedmetadata", fn, { once: true });
	}

	whenReady(function () {
		var at = parseFloat(read(KEY_AT));
		if (isFinite(at) && at > 0 && at < audio.duration) audio.currentTime = at;

		if (read(KEY_ON) !== "1") return;

		// Not the autoplay that was turned down: the visitor pressed play on
		// the main menu and this is the same track carrying across a link.
		// Browsers judge that per document and can still refuse, so a refusal
		// clears the flag rather than leaving the main menu claiming to play
		// something silent.
		audio.play().catch(function () {
			store(KEY_ON, "0");
			paint();
		});
	});

	// Remember the position about once a second, and once more on the way out,
	// so the next page picks up where this one stopped.
	var lastSaved = 0;
	audio.addEventListener("timeupdate", function () {
		var d = audio.duration;
		if (fill && isFinite(d) && d) {
			fill.style.width = ((audio.currentTime / d) * 100).toFixed(2) + "%";
		}
		if (Math.abs(audio.currentTime - lastSaved) >= 1) {
			lastSaved = audio.currentTime;
			store(KEY_AT, String(audio.currentTime));
		}
	});

	window.addEventListener("pagehide", function () {
		store(KEY_AT, String(audio.currentTime));
	});

	audio.addEventListener("play", paint);
	audio.addEventListener("pause", paint);
	audio.addEventListener("ended", paint);

	if (!root || !playBtn || !bar || !fill) {
		paint();
		return;
	}

	playBtn.addEventListener("click", function () {
		if (audio.paused) {
			store(KEY_ON, "1");
			// Only ever reached from a real click, so autoplay policy is met.
			audio.play().catch(function () { store(KEY_ON, "0"); paint(); });
		} else {
			store(KEY_ON, "0");
			audio.pause();
		}
		paint();
	});

	// Click anywhere on the bar to seek.
	bar.addEventListener("click", function (e) {
		var d = audio.duration;
		if (!isFinite(d) || !d) return;
		var box = bar.getBoundingClientRect();
		var ratio = Math.min(Math.max((e.clientX - box.left) / box.width, 0), 1);
		audio.currentTime = ratio * d;
		store(KEY_AT, String(audio.currentTime));
	});

	paint();
})();
