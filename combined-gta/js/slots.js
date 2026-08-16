/* Renders project save slots into loadgame.html.
 * Slot markup mirrors the original gta-sa-menu loadgame page exactly:
 * li.menu-option.menu-option--datagame > a > span.left + span.right
 * Empty slots use menu-option--datagame-blank, same as the game. */
(function () {
	var list = document.getElementById("save-slots");
	if (!list) return;

	var SLOTS = 8;
	var MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];

	function pad(n) { return n < 10 ? "0" + n : "" + n; }

	function fmtDate(iso) {
		if (!iso) return "";
		var p = iso.split("-");
		return pad(parseInt(p[2], 10)) + " " + MONTHS[parseInt(p[1], 10) - 1] + " " + p[0];
	}

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;");
	}

	function blankSlot(i) {
		return '<li class="menu-option menu-option--datagame menu-option--datagame-blank">' +
			'<a href="#">save file ' + i + ' not present</a></li>';
	}

	function filledSlot(entry) {
		// Garage line comes from data/vehicles.json when present. Derived from
		// repo size and push recency, so it is reproducible rather than my taste.
		var garage = entry.vehicle ? "  |  garage: " + entry.vehicle : "";
		var href = entry.noRepo || entry.isPrivate
			? "#"
			: "https://github.com/" + entry.nameWithOwner;
		var right = fmtDate(entry.pushedAt) + "  " + entry.status.toUpperCase();
		return '<li class="menu-option menu-option--datagame"><a href="' + esc(href) + '"' +
			(href === "#" ? "" : ' target="_blank" rel="noopener"') +
			' title="' + esc(entry.blurb + garage) + '">' +
			'<span class="menu-option--datagame-left">' + esc(entry.slotName) + '</span>' +
			'<span class="menu-option--datagame-right">' + esc(right) + '</span>' +
			'</a></li>';
	}

	function render(overrides, projects, garageData) {
		var garage = (garageData && garageData.garage) || {};
		var byName = {};
		var i;
		if (projects && projects.repos) {
			for (i = 0; i < projects.repos.length; i++) {
				byName[projects.repos[i].nameWithOwner] = projects.repos[i];
			}
		}

		var slots = [];
		for (var key in overrides) {
			if (!Object.prototype.hasOwnProperty.call(overrides, key)) continue;
			var o = overrides[key];
			var repo = byName[key] || {};
			slots[o.slot] = {
				nameWithOwner: key,
				slotName: o.slotName,
				blurb: o.blurb,
				status: o.status,
				noRepo: !!o.noRepo,
				isPrivate: !!repo.isPrivate,
				pushedAt: repo.pushedAt || o.pushedAt || "",
				vehicle: (garage[key] || {}).vehicle || ""
			};
		}

		var html = "";
		for (i = 1; i <= SLOTS; i++) {
			html += slots[i] ? filledSlot(slots[i]) : blankSlot(i);
		}
		list.innerHTML = html;
	}

	function getJSON(url) {
		return fetch(url).then(function (r) {
			if (!r.ok) throw new Error(r.status);
			return r.json();
		});
	}

	getJSON("./data/overrides.json").then(function (overrides) {
		// Slots must render even if the generated file is missing.
		return getJSON("./data/projects.json").then(
			function (projects) {
				// The garage is optional decoration; never let it block slots.
				return getJSON("./data/vehicles.json").then(
					function (g) { render(overrides, projects, g); },
					function () { render(overrides, projects, null); }
				);
			},
			function () { render(overrides, null, null); }
		);
	}).catch(function () {
		list.innerHTML = '<li class="menu-option menu-option--datagame ' +
			'menu-option--datagame-blank"><a href="#">save data unavailable</a></li>';
	});
})();
