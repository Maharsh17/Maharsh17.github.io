/* Renders the weapon grid from data/weapons.json.
 *
 * Stats are the game's own weapon.dat values; sprites come from the HUD
 * recreation. Guns and melee are shown with different stats because
 * weapon.dat genuinely stores different fields for each: guns have damage,
 * clip and accuracy, melee rows have combo counts and reach. */
(function () {
	var host = document.getElementById("weapon-grid");
	if (!host) return;

	// Scale bars against the strongest gun so the comparison is honest.
	var MAX_DAMAGE = 140;
	var MAX_RANGE = 100;

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;");
	}

	function bar(label, value, max) {
		var pct = Math.max(0, Math.min(100, Math.round((value / max) * 100)));
		return '<div class="site-wbar">' +
			'<span class="site-wbar-label">' + esc(label) + '</span>' +
			'<span class="site-wbar-track"><span class="site-wbar-fill" style="width:' +
			pct + '%"></span></span>' +
			'<span class="site-wbar-val">' + esc(value) + '</span>' +
			'</div>';
	}

	function card(w) {
		var stats = "";
		if (w.kind === "gun") {
			stats += bar("dmg", w.damage, MAX_DAMAGE);
			stats += bar("rng", w.range, MAX_RANGE);
			stats += '<p class="site-wmeta">clip ' + esc(w.clip) +
				(w.accuracy != null ? "  &middot;  acc " + esc(w.accuracy) : "") + "</p>";
		} else {
			stats += bar("reach", w.range, 5);
			stats += '<p class="site-wmeta">' + esc(w.combos) + " hit combo</p>";
		}
		return '<li class="site-wcard">' +
			'<img class="site-wimg" src="./assets/weapons/' + esc(w.sprite) +
			'" alt="' + esc(w.name) + '" loading="lazy">' +
			'<h3 class="site-wname">' + esc(w.name) + '</h3>' + stats + '</li>';
	}

	fetch("./data/weapons.json").then(function (r) {
		if (!r.ok) throw new Error(r.status);
		return r.json();
	}).then(function (data) {
		var guns = [], melee = [], i;
		for (i = 0; i < data.weapons.length; i++) {
			(data.weapons[i].kind === "gun" ? guns : melee).push(data.weapons[i]);
		}
		var html = '<h2 class="site-wgroup">Guns</h2><ul class="site-wlist">';
		for (i = 0; i < guns.length; i++) html += card(guns[i]);
		html += '</ul><h2 class="site-wgroup">Melee</h2><ul class="site-wlist">';
		for (i = 0; i < melee.length; i++) html += card(melee[i]);
		html += "</ul>";
		host.innerHTML = html;
	}).catch(function () {
		host.innerHTML = '<p class="site-prose">weapon data unavailable</p>';
	});
})();
