/* Renders project save slots into projects.html, grouped into three bands.
 *
 * Slot markup mirrors the original gta-sa-menu loadgame page exactly:
 * li.menu-option.menu-option--datagame > a > span.left + span.right
 * Empty slots use menu-option--datagame-blank, same as the game.
 *
 * A project's band comes from its "category" in data/overrides.json, so
 * recategorising something is a data edit, never a code edit.
 */
(function () {
	var host = document.getElementById("project-bands");
	if (!host) return;

	// Data paths resolve against this file, not the page. Pages live at three
	// depths, so a page-relative "./data/..." is wrong on two of them.
	var HERE = (document.currentScript && document.currentScript.src) || location.href;
	function dataURL(name) { return new URL("../data/" + name, HERE).href; }

	// Band order is deliberate: research first, because that is the work the
	// site is actually about. BANDS is also the whitelist, so a typo'd
	// category in overrides.json drops the entry loudly instead of inventing
	// a fourth band nobody styled.
	var BANDS = ["research work", "research software", "personal"];

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;");
	}

	function emptyBand() {
		return '<li class="menu-option menu-option--datagame menu-option--datagame-blank">' +
			'<a href="#">no save files</a></li>';
	}

	function filledSlot(entry) {
		// Garage line comes from data/vehicles.json when present. Derived from
		// repo size and push recency, so it is reproducible rather than my taste.
		var garage = entry.vehicle ? "  |  garage: " + entry.vehicle : "";
		var linkable = !entry.noRepo && !entry.isPrivate && entry.nameWithOwner;
		var inner =
			'<span class="menu-option--datagame-left">' + esc(entry.slotName) + '</span>' +
			'<span class="menu-option--datagame-right">' + esc(entry.line || "") + '</span>';
		var title = ' title="' + esc(entry.blurb + garage) + '"';

		// Rows with no repo behind them render as plain text. An <a href="#">
		// looks identical to a real link and hovers like one, which promises a
		// destination that does not exist.
		if (!linkable) {
			return '<li class="menu-option menu-option--datagame site-row-static"' +
				title + '>' + inner + '</li>';
		}
		return '<li class="menu-option menu-option--datagame">' +
			'<a href="https://github.com/' + esc(entry.nameWithOwner) + '"' +
			' target="_blank" rel="noopener"' + title + '>' + inner + '</a></li>';
	}

	function band(name, entries) {
		entries.sort(function (a, b) { return a.order - b.order; });
		var html = '<h2 class="site-band">' + esc(name) + '</h2>' +
			'<ul class="menu-container">';
		// No blank-slot padding: the game centres those rows and the real ones
		// are left-aligned, so a half-filled band reads as broken rather than
		// as a save screen with room to grow.
		for (var i = 0; i < entries.length; i++) html += filledSlot(entries[i]);
		if (!entries.length) html += emptyBand();
		return html + "</ul>";
	}

	function render(overrides, garageData) {
		var garage = (garageData && garageData.garage) || {};
		var grouped = {};
		var i;
		for (i = 0; i < BANDS.length; i++) grouped[BANDS[i]] = [];

		for (var key in overrides) {
			if (!Object.prototype.hasOwnProperty.call(overrides, key)) continue;
			var o = overrides[key];
			if (!grouped[o.category]) continue;
			grouped[o.category].push({
				nameWithOwner: key,
				order: o.order || 99,
				slotName: o.slotName,
				line: o.line,
				blurb: o.blurb,
				noRepo: !!o.noRepo,
				// Set "private": true on an override when a repo stops being
				// public, so the row stays listed but does not link to a 404.
				isPrivate: !!o.private,
				vehicle: (garage[key] || {}).vehicle || ""
			});
		}

		var html = "";
		for (i = 0; i < BANDS.length; i++) html += band(BANDS[i], grouped[BANDS[i]]);
		host.innerHTML = html;
	}

	function getJSON(url) {
		return fetch(url).then(function (r) {
			if (!r.ok) throw new Error(r.status);
			return r.json();
		});
	}

	getJSON(dataURL("overrides.json")).then(function (overrides) {
		// The garage is optional decoration; never let it block slots.
		return getJSON(dataURL("vehicles.json")).then(
			function (g) { render(overrides, g); },
			function () { render(overrides, null); }
		);
	}).catch(function () {
		host.innerHTML = '<ul class="menu-container"><li class="menu-option ' +
			'menu-option--datagame menu-option--datagame-blank">' +
			'<a href="#">save data unavailable</a></li></ul>';
	});
})();
