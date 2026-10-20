/*
 * d3.__NAME__.js - __NAME__ renderer for d3blocks.
 * Rendering and interaction: d3 v7. Shell (panels, theme, export) follows d3.flowgraph.js.
 */
(function () {
  'use strict';

  var DATA = JSON.parse(document.getElementById('__PREFIX__-data').textContent);
  var OPTS = JSON.parse(document.getElementById('__PREFIX__-options').textContent);

  var state = {
    fontsize: OPTS.fontsize
    // TODO: chart state mirrored from OPTS
  };

  var FONT_FAMILY = '"Helvetica", Arial, sans-serif';

  // ---------------------------------------------------------------- data
  var nodes = (DATA.nodes || []).map(function (n, i) { return Object.assign({ idx: i }, n); });
  var edges = (DATA.edges || []).map(function (e, i) { return Object.assign({ idx: i, id: 'e' + i }, e); });
  var bounds = { x: 0, y: 0, w: 1, h: 1 };   // TODO: set to the drawn content's box (used by fit and export)

  // ---------------------------------------------------------------- svg
  var main = document.getElementById('__PREFIX__-main');
  var svg = d3.select('#__PREFIX__-svg');
  var viewport = svg.append('g').attr('class', '__PREFIX__-viewport');
  var zoom = d3.zoom().scaleExtent([0.05, 8]).on('zoom', function (ev) { viewport.attr('transform', ev.transform); });
  svg.call(zoom).on('dblclick.zoom', null);

  var tooltip = d3.select('#__PREFIX__-tooltip');
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function showTooltip(ev, html) {
    tooltip.html(html).classed('open', true);
    tooltip.style('left', Math.min(ev.clientX + 14, window.innerWidth - 330) + 'px').style('top', (ev.clientY + 14) + 'px');
  }
  function hideTooltip() { tooltip.classed('open', false); }

  // ---------------------------------------------------------------- render
  function render() {
    // TODO: draw DATA into `viewport`. Take colours from the payload, text/chrome from CSS variables.
    // Set `bounds` from the drawn content so fit() and the export work.
  }

  // ---------------------------------------------------------------- view
  // The top bar is optional (show_top_panel=False): its height is then 0, never an early return.
  function viewportInsets() {
    var bar = document.querySelector('.top-panel');
    var top = bar ? bar.getBoundingClientRect().bottom + 12 : 16;
    var left = 16;
    document.querySelectorAll('.stats-panel').forEach(function (p) {
      if (p.style.display !== 'none') left = Math.max(left, p.getBoundingClientRect().right + 16);
    });
    return { top: top, left: left, right: 16, bottom: 16 };
  }

  function fit(animated, box) {
    box = box || bounds;
    var rect = svg.node().getBoundingClientRect();
    var ins = viewportInsets();
    var availW = Math.max(50, rect.width - ins.left - ins.right);
    var availH = Math.max(50, rect.height - ins.top - ins.bottom);
    var k = Math.min(availW / Math.max(1, box.w), availH / Math.max(1, box.h), 1.5);
    var tx = ins.left + (availW - box.w * k) / 2 - box.x * k;
    var ty = ins.top + (availH - box.h * k) / 2 - box.y * k;
    var t = d3.zoomIdentity.translate(tx, ty).scale(k);
    (animated ? svg.transition().duration(400) : svg).call(zoom.transform, t);
  }

  // ---------------------------------------------------------------- export
  var STYLE_PROPS = ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-opacity',
    'opacity', 'font-family', 'font-size', 'font-weight', 'text-anchor', 'dominant-baseline', 'paint-order',
    'stroke-linejoin', 'stroke-linecap', 'visibility'];

  function serializeSvg() {
    var src = svg.node();
    var clone = src.cloneNode(true);
    var a = src.querySelectorAll('*'), b = clone.querySelectorAll('*');
    for (var i = 0; i < a.length; i++) {
      var cs = window.getComputedStyle(a[i]), style = '';
      STYLE_PROPS.forEach(function (p) {
        var v = cs.getPropertyValue(p);
        if (v) style += p + ':' + v + ';';
      });
      b[i].setAttribute('style', style);
    }
    clone.querySelector('.__PREFIX__-viewport').removeAttribute('transform');
    var pad = 24, x = bounds.x - pad, y = bounds.y - pad, w = bounds.w + 2 * pad, h = bounds.h + 2 * pad;
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('viewBox', [x, y, w, h].join(' '));
    clone.setAttribute('width', w);
    clone.setAttribute('height', h);
    clone.removeAttribute('class');
    var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', x); bg.setAttribute('y', y); bg.setAttribute('width', w); bg.setAttribute('height', h);
    bg.setAttribute('fill', window.getComputedStyle(document.body).backgroundColor);
    clone.insertBefore(bg, clone.querySelector('.__PREFIX__-viewport'));
    return { text: new XMLSerializer().serializeToString(clone), width: w, height: h };
  }

  function download(blob, filename) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  function fileStem() { return (OPTS.title || '__NAME__').replace(/[^\w.-]+/g, '_'); }

  function saveSvg() {
    var s = serializeSvg();
    download(new Blob([s.text], { type: 'image/svg+xml;charset=utf-8' }), fileStem() + '.svg');
  }

  function savePng() {
    var s = serializeSvg(), scale = 2;
    var img = new Image();
    var url = URL.createObjectURL(new Blob([s.text], { type: 'image/svg+xml;charset=utf-8' }));
    img.onload = function () {
      var canvas = document.createElement('canvas');
      canvas.width = Math.ceil(s.width * scale); canvas.height = Math.ceil(s.height * scale);
      var c = canvas.getContext('2d');
      c.scale(scale, scale);
      c.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      canvas.toBlob(function (blob) { download(blob, fileStem() + '.png'); }, 'image/png');
    };
    img.src = url;
  }

  function exportJson() {
    download(new Blob([JSON.stringify({ nodes: nodes, edges: edges }, null, 2)], { type: 'application/json' }), fileStem() + '.json');
  }

  // ---------------------------------------------------------------- controls
  // Every control may live in a panel that is not rendered: bind through on() / querySelectorAll, never getElementById(...).addEventListener.
  function on(id, ev, fn) { var el = document.getElementById(id); if (el) el.addEventListener(ev, fn); return el; }

  on('saveSvgButton', 'click', saveSvg);
  on('savePngButton', 'click', savePng);
  on('exportButton', 'click', exportJson);
  on('fitButton', 'click', function () { fit(true); });
  // TODO: chart-specific controls (sliders, toggles, data-* buttons) bound the same way.

  // Theme (theme.js: runtime toggle; dark_mode='auto' follows the OS until toggled).
  D3BlocksTheme.bind('themeBtn');

  // Search.
  (function setupSearch() {
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');
    if (!input || !results) return;
    function close() { results.classList.remove('open'); results.innerHTML = ''; }
    function select(n) { close(); input.blur(); /* TODO: focus / highlight the match */ }
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      var hits = nodes.filter(function (n) {
        return String(n.label || n.name).toLowerCase().indexOf(q) >= 0;
      }).slice(0, 30);
      results.innerHTML = hits.length ? '' : '<div class="search-item" style="opacity:0.6">No matches</div>';
      hits.forEach(function (n) {
        var item = document.createElement('div');
        item.className = 'search-item';
        item.textContent = String(n.label || n.name);
        item.addEventListener('click', function () { select(n); });
        results.appendChild(item);
      });
      results.classList.add('open');
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var first = results.querySelector('.search-item'); if (first) first.click(); }
      if (e.key === 'Escape') { close(); input.blur(); }
    });
    document.addEventListener('click', function (e) {
      if (!results.contains(e.target) && e.target !== input) close();
    });
  })();

  // Side panels: stack below the top bar and collapse on title click (no panels -> no-op).
  (function setupPanels() {
    var panels = Array.prototype.slice.call(document.querySelectorAll('.stats-panel'));
    function position() {
      var bar = document.querySelector('.top-panel');
      var y = (bar ? bar.getBoundingClientRect().bottom : 0) + 8;
      panels.forEach(function (p) {
        if (p.style.display === 'none') return;
        p.style.top = y + 'px';
        p.style.maxHeight = Math.max(80, window.innerHeight - y - 12) + 'px';
        y += p.getBoundingClientRect().height + 10;
      });
    }
    panels.forEach(function (p) {
      var title = p.querySelector('.stats-panel-title');
      if (title) title.addEventListener('click', function () { p.classList.toggle('collapsed'); setTimeout(position, 0); });
      if (typeof ResizeObserver !== 'undefined') new ResizeObserver(position).observe(p);
    });
    window.addEventListener('resize', position);
    position();
  })();

  // ---------------------------------------------------------------- go
  if (!nodes.length) {
    d3.select('#__PREFIX__-main').append('div').attr('class', '__PREFIX__-empty').text('Nothing to draw.');
    return;
  }
  render();
  fit(false);

  window.__d3blocks_chart = { state: state, nodes: nodes, edges: edges, fit: fit, render: render };
})();
