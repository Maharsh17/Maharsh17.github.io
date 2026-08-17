/* Main-menu music player.
 *
 * Nothing here ever starts on its own. No autoplay, no resume-on-load, no
 * remembered "on" state. The only thing that starts audio is a click on the
 * play button, every time.
 *
 * Art is radar/frontend sprites decoded from the game: radio_TPLAYER is SA's
 * own Track Player logo, used in-game for the player's own music, which is
 * exactly what this is.
 */
(function () {
	var root = document.getElementById("player");
	if (!root) return;

	var audio = root.querySelector("audio");
	var playBtn = root.querySelector(".site-player-play");
	var bar = root.querySelector(".site-player-bar");
	var fill = root.querySelector(".site-player-fill");
	if (!audio || !playBtn || !bar || !fill) return;

	function paint() {
		var playing = !audio.paused && !audio.ended;
		var glyph = root.querySelector(".site-player-glyph");
		if (glyph) glyph.innerHTML = playing ? "&#10074;&#10074;" : "&#9654;";
		playBtn.setAttribute("aria-label", playing ? "Pause theme" : "Play theme");
		root.classList.toggle("is-playing", playing);
	}

	playBtn.addEventListener("click", function () {
		if (audio.paused) {
			// Only ever reached from a real click, so autoplay policy is satisfied.
			audio.play().catch(function () { paint(); });
		} else {
			audio.pause();
		}
		paint();
	});

	audio.addEventListener("play", paint);
	audio.addEventListener("pause", paint);
	audio.addEventListener("ended", paint);

	audio.addEventListener("timeupdate", function () {
		var d = audio.duration;
		if (!isFinite(d) || !d) return;
		fill.style.width = ((audio.currentTime / d) * 100).toFixed(2) + "%";
	});

	// Click anywhere on the bar to seek.
	bar.addEventListener("click", function (e) {
		var d = audio.duration;
		if (!isFinite(d) || !d) return;
		var box = bar.getBoundingClientRect();
		var ratio = Math.min(Math.max((e.clientX - box.left) / box.width, 0), 1);
		audio.currentTime = ratio * d;
	});

	paint();
})();
