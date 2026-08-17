/* Client-side navigation, so the music survives a page change.
 *
 * Chrome refuses audio.play() on a freshly loaded document no matter what the
 * previous page did, so "keep playing across pages" is impossible while each
 * page is its own document. Proven, not assumed: the same code that stops with
 * the autoplay policy on continues with --autoplay-policy=no-user-gesture-
 * required. The element has to survive the navigation.
 *
 * So it does. Links are intercepted, the target page is fetched, and its
 * content replaces this page's content inside the same document. The <audio>
 * element never leaves the DOM, so nothing has to be restarted.
 *
 * The pages stay real files on disk. Every URL still works typed in, shared,
 * or with JavaScript off, and GitHub Pages serves them the ordinary way. This
 * only makes navigating between them cheaper.
 *
 * The rule for what survives a swap is one attribute: data-keep stays, and
 * everything else in <body> is replaced.
 */
(function () {
	if (!window.history || !window.fetch || !window.DOMParser) return;

	var parser = new DOMParser();

	// A persistent node keeps its attributes, not its resolved URLs. The
	// <audio> src is written relative, so the moment pushState moved the base
	// into blog/ the browser re-resolved it to blog/assets/audio/theme.mp3,
	// 404'd, and stopped the playback this whole file exists to protect.
	// Reading .src gives the absolute form; writing it back pins it there.
	// Done once at load, before anything is playing, so the reload it triggers
	// on the media element costs nothing.
	var shell = document.getElementById("shell");
	if (shell) {
		Array.prototype.slice.call(shell.querySelectorAll("[src]")).forEach(
			function (el) { el.src = el.src; }
		);
	}

	// <head> is never swapped, so its links outlive every URL change and hit
	// the same problem: the favicon href is written relative, and after a
	// pushState into /projects/ the browser re-resolved it to
	// /projects/assets/... and 404'd on every navigation.
	Array.prototype.slice.call(document.head.querySelectorAll("link[href]"))
		.forEach(function (el) { el.href = el.href; });

	function isInternal(a) {
		return a &&
			a.href &&
			a.origin === location.origin &&
			!a.hasAttribute("download") &&
			(!a.target || a.target === "_self") &&
			// Clean URLs end in a slash; 404.html is the one real .html left.
			(/\/$/.test(a.pathname) || /\.html$/.test(a.pathname));
	}

	// Libraries marked data-once load on the first page that needs them and
	// are never re-executed. Seeded with whatever the entry page already ran.
	var loaded = {};
	Array.prototype.slice.call(document.scripts).forEach(function (s) {
		if (s.src) loaded[s.src] = true;
	});

	function runScript(node) {
		// A cloned <script> never executes. It has to be built fresh.
		var s = document.createElement("script");
		for (var i = 0; i < node.attributes.length; i++) {
			s.setAttribute(node.attributes[i].name, node.attributes[i].value);
		}
		if (!node.src) s.textContent = node.textContent;
		// Scripts created this way default to async, which means they run in
		// whatever order they finish downloading. map.js would then race the
		// 800KB MapLibre bundle it depends on and usually lose. async = false
		// restores document order.
		s.async = false;
		document.body.appendChild(s);
	}

	// Per-page stylesheets live in <head>, which is never swapped, so a page
	// reached by a link would otherwise arrive without its own CSS: the map
	// page needs maplibre-gl.css and nothing else loads it. Missing sheets are
	// added and none are removed, because they are namespaced and an extra one
	// costs nothing next to a flash of unstyled content.
	function mergeStyles(doc) {
		var have = {};
		Array.prototype.slice.call(document.styleSheets).forEach(function (s) {
			if (s.href) have[s.href] = true;
		});
		Array.prototype.slice.call(
			doc.querySelectorAll('link[rel="stylesheet"][href]')
		).forEach(function (link) {
			var href = new URL(link.getAttribute("href"), location.href).href;
			if (have[href]) return;
			var el = document.createElement("link");
			el.rel = "stylesheet";
			el.href = href;
			// Inserted before site.css, never appended. Appending would put a
			// vendored stylesheet after the one that overrides it, and later
			// wins at equal specificity, so arriving at the map by clicking
			// would have undone every control restyle that a direct load
			// applied. Same page, two different appearances.
			var own = document.querySelector('link[href*="css/site.css"]');
			if (own) own.parentNode.insertBefore(el, own);
			else document.head.appendChild(el);
		});
	}

	function swap(html, url) {
		var doc = parser.parseFromString(html, "text/html");
		if (!doc.body) throw new Error("no body");

		// The URL is updated before anything is inserted, because relative
		// paths in the incoming markup resolve against document.baseURI at
		// insertion time. Blog posts sit one directory down and reference
		// ../assets, which is only correct once the URL says so.
		if (url !== location.href) history.pushState({ nav: 1 }, "", url);

		mergeStyles(doc);

		var keep = [];
		Array.prototype.slice.call(document.body.children).forEach(function (el) {
			if (el.hasAttribute("data-keep")) keep.push(el);
			else el.remove();
		});

		document.title = doc.title;
		document.body.className = doc.body.className;
		document.body.dataset.section = doc.body.dataset.section || "";

		var scripts = [];
		Array.prototype.slice.call(doc.body.children).forEach(function (el) {
			if (el.hasAttribute("data-keep")) return;   // already alive here
			if (el.tagName === "SCRIPT") { scripts.push(el); return; }
			document.body.insertBefore(document.importNode(el, true), keep[0] || null);
		});

		// Page scripts run last, against the DOM they expect. Anything marked
		// data-keep was skipped above and is still running from the first load.
		scripts.forEach(function (el) {
			if (el.hasAttribute("data-once")) {
				var src = new URL(el.getAttribute("src"), location.href).href;
				if (loaded[src]) return;
				loaded[src] = true;
			}
			runScript(el);
		});
		window.scrollTo(0, 0);
	}

	function go(url, push) {
		return fetch(url, { credentials: "same-origin" })
			.then(function (r) {
				if (!r.ok) throw new Error(r.status);
				return r.text();
			})
			.then(function (html) { swap(html, push ? url : location.href); })
			.catch(function () {
				// Any failure falls back to a real navigation. A visitor who
				// cannot reach a page is never left on the old one.
				location.href = url;
			});
	}

	document.addEventListener("click", function (e) {
		if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey ||
			e.shiftKey || e.altKey) return;
		var a = e.target.closest && e.target.closest("a");
		if (!isInternal(a)) return;
		e.preventDefault();
		go(a.href, true);
	});

	window.addEventListener("popstate", function () {
		go(location.href, false);
	});
})();
