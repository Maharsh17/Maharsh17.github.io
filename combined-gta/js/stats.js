/* Renders skill bars into stats.html.
 * Bar fill = fraction of projects a language appears in, NOT byte share.
 * Byte share was measured and is misleading here: a single repo contributes
 * 16.69 MB of the 16.70 MB total HTML, which would render as "94% HTML".
 * Counting projects makes one huge generated file count exactly once. */
(function () {
	var host = document.getElementById("skill-bars");
	if (!host) return;

	function esc(s) {
		return String(s == null ? "" : s)
			.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
	}

	function bar(name, count, total) {
		var pct = Math.round((count / total) * 100);
		return '<section class="gtasa-stats-bar">' +
			'<p class="gtasa-stats-bar--title">' + esc(name) +
			' (' + count + '/' + total + ')</p>' +
			'<div class="gtasa-stats-bar--progress">' +
			'<div style="width: ' + pct + '%;"></div>' +
			'</div></section>';
	}

	fetch("./data/projects.json").then(function (r) {
		if (!r.ok) throw new Error(r.status);
		return r.json();
	}).then(function (data) {
		var total = data.repos.length;
		var counts = {};
		var i, j, seen, langs;

		for (i = 0; i < data.repos.length; i++) {
			seen = {};
			langs = data.repos[i].languages || [];
			for (j = 0; j < langs.length; j++) {
				if (seen[langs[j].name]) continue;
				seen[langs[j].name] = true;
				counts[langs[j].name] = (counts[langs[j].name] || 0) + 1;
			}
		}

		var rows = [];
		for (var k in counts) {
			if (Object.prototype.hasOwnProperty.call(counts, k)) {
				rows.push({ name: k, count: counts[k] });
			}
		}
		rows.sort(function (a, b) { return b.count - a.count || a.name.localeCompare(b.name); });

		var html = "";
		for (i = 0; i < rows.length; i++) {
			html += bar(rows[i].name, rows[i].count, total);
		}
		host.innerHTML = html;
	}).catch(function () {
		host.innerHTML = '<p class="gtasa-stats-bar--title">stats unavailable</p>';
	});
})();
