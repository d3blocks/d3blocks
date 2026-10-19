/*
 * d3.erd.js - entity-relationship diagram renderer for d3blocks.
 * Entities are table boxes (measured before layout), laid out with dagre;
 * relationships carry crow's-foot cardinality markers. Rendering and interaction: d3 v7.
 */
(function () {
  'use strict';

  var DATA = JSON.parse(document.getElementById('er-data').textContent);
  var OPTS = JSON.parse(document.getElementById('er-options').textContent);

  var state = {
    direction: OPTS.direction,
    nodesep: OPTS.nodesep,
    ranksep: OPTS.ranksep,
    showColumns: OPTS.showColumns,
    showTypes: OPTS.showTypes,
    fontsize: OPTS.fontsize,
    pinned: null            // { type: 'entity' | 'rel' | 'step', ... }
  };

  var FONT_FAMILY = '"Helvetica", Arial, sans-serif';
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var CARD_TEXT = { one: 'exactly one', zero_or_one: 'zero or one', one_or_more: 'one or more', zero_or_more: 'zero or more' };

  // ---------------------------------------------------------------- data
  var ents = DATA.entities.map(function (e, i) { return Object.assign({ idx: i }, e); });
  var entById = new Map(ents.map(function (e) { return [e.name, e]; }));
  var rels = DATA.relationships.map(function (r, i) { return Object.assign({ idx: i, id: 'r' + i }, r); });

  // ---------------------------------------------------------------- svg
  var main = document.getElementById('er-main');
  if (OPTS.width) main.style.width = OPTS.width + 'px';
  if (OPTS.height) main.style.height = OPTS.height + 'px';

  var svg = d3.select('#er-svg');
  var defs = svg.append('defs');
  var viewport = svg.append('g').attr('class', 'er-viewport');
  var gRels = viewport.append('g').attr('class', 'er-rels');
  var gLabels = viewport.append('g').attr('class', 'er-rel-labels');
  var gEnts = viewport.append('g').attr('class', 'er-entities');
  var tooltip = d3.select('#er-tooltip');

  var zoom = d3.zoom().scaleExtent([0.05, 4]).on('zoom', function (ev) {
    viewport.attr('transform', ev.transform);
  });
  svg.call(zoom).on('dblclick.zoom', null);
  svg.on('click', function (ev) { if (ev.target === svg.node()) unpin(); });

  var bounds = { x: 0, y: 0, w: 1, h: 1 };

  // Crow's-foot markers, one per cardinality. The box side is at x=20, so the
  // same marker works at both ends (orient auto-start-reverse). Colours come
  // from the theme (.er-card in the CSS), not baked-in hex.
  var CARD_PATHS = {
    one: { d: 'M14,1V13M10,1V13' },
    zero_or_one: { d: 'M14,1V13', circle: 7 },
    one_or_more: { d: 'M20,1L11,7L20,13M11,7H20M8,1V13' },
    zero_or_more: { d: 'M20,1L11,7L20,13M11,7H20', circle: 5.5 }
  };
  Object.keys(CARD_PATHS).forEach(function (card) {
    var m = defs.append('marker').attr('id', 'er-card-' + card).attr('class', 'er-card')
      .attr('viewBox', '0 0 20 14').attr('refX', 20).attr('refY', 7)
      .attr('markerWidth', 20).attr('markerHeight', 14).attr('markerUnits', 'userSpaceOnUse')
      .attr('orient', 'auto-start-reverse');
    m.append('path').attr('d', CARD_PATHS[card].d);
    if (CARD_PATHS[card].circle) m.append('circle').attr('cx', CARD_PATHS[card].circle).attr('cy', 7).attr('r', 3.5);
  });
  function marker(card) { return card ? 'url(#er-card-' + card + ')' : null; }

  // ---------------------------------------------------------------- text
  var ctx = document.createElement('canvas').getContext('2d');
  function textWidth(s, size, weight) {
    ctx.font = (weight || 'normal') + ' ' + size + 'px ' + FONT_FAMILY;
    return ctx.measureText(String(s)).width;
  }
  function keysOf(c) { return c.key ? c.key.split(',') : []; }

  // ---------------------------------------------------------------- layout
  function metrics() {
    var fs = state.fontsize;
    return { fs: fs, tfs: Math.max(8, fs - 1), bfs: Math.max(7, fs - 3), rowH: Math.round(fs * 1.7),
             headH: Math.round(fs * 1.4) + 14, lfs: Math.max(9, fs - 1) };
  }

  // Box size from the visible rows: header, then badges | name | type columns.
  function sizeEntity(e) {
    var m = metrics();
    var cols = e.columns || [];
    var visible = state.showColumns === 'all' ? cols
      : state.showColumns === 'keys' ? cols.filter(function (c) { return c.key; }) : [];
    e.rows = visible.map(function (c) { return { col: c }; });
    var hidden = cols.length - visible.length;
    if (hidden > 0 && state.showColumns === 'keys') e.rows.push({ more: hidden });
    var badgeW = 0, nameW = 0, typeW = 0;
    visible.forEach(function (c) {
      var w = 0;
      keysOf(c).forEach(function (k) { w += textWidth(k, m.bfs, 'bold') + 8 + 3; });
      badgeW = Math.max(badgeW, w);
      nameW = Math.max(nameW, textWidth(c.name, m.fs));
      if (state.showTypes && c.type) typeW = Math.max(typeW, textWidth(c.type, m.tfs));
    });
    e.rows.forEach(function (r) { if (r.more) nameW = Math.max(nameW, textWidth('+' + r.more + ' more columns', m.tfs)); });
    e.badgeX = 10;
    e.nameX = e.badgeX + (badgeW ? badgeW + 5 : 0);
    e.typeX = e.nameX + nameW + 18;
    var rowsW = e.typeX + (typeW ? typeW : -18) + 12;
    e.width = Math.ceil(Math.max(120, textWidth(e.label, m.fs, 'bold') + 28, rowsW));
    e.height = m.headH + e.rows.length * m.rowH + (e.rows.length ? 6 : 0);
  }

  // Point where the line from the box centre towards p crosses the border.
  function intersect(n, p) {
    var dx = p.x - n.x, dy = p.y - n.y;
    if (Math.abs(dx) < 1e-6 && Math.abs(dy) < 1e-6) return { x: n.x, y: n.y };
    var w = n.width / 2, h = n.height / 2, sx, sy;
    if (Math.abs(dy) * w > Math.abs(dx) * h) { if (dy < 0) h = -h; sx = h * dx / dy; sy = h; }
    else { if (dx < 0) w = -w; sx = w; sy = w * dy / dx; }
    return { x: n.x + sx, y: n.y + sy };
  }

  function relLabelSize(r) {
    if (!r.label) return null;
    var lfs = metrics().lfs;
    return { width: textWidth(r.label, lfs) + 12, height: lfs + 8 };
  }

  // Connected components (tables without relationships are their own component).
  function components() {
    var parent = new Map(ents.map(function (e) { return [e.name, e.name]; }));
    function find(x) { while (parent.get(x) !== x) { parent.set(x, parent.get(parent.get(x))); x = parent.get(x); } return x; }
    rels.forEach(function (r) { parent.set(find(r.source), find(r.target)); });
    var byRoot = new Map();
    ents.forEach(function (e) {
      var root = find(e.name);
      if (!byRoot.has(root)) byRoot.set(root, { ents: [], rels: [] });
      byRoot.get(root).ents.push(e);
    });
    rels.forEach(function (r) { byRoot.get(find(r.source)).rels.push(r); });
    return Array.from(byRoot.values());
  }

  // dagre layout of one component; positions are relative to the component's box.
  function layoutComponent(comp) {
    var g = new dagre.graphlib.Graph({ multigraph: true });
    g.setGraph({ rankdir: state.direction, nodesep: state.nodesep, ranksep: state.ranksep, marginx: 0, marginy: 0 });
    g.setDefaultEdgeLabel(function () { return {}; });
    comp.ents.forEach(function (e) { g.setNode(e.name, { width: e.width, height: e.height }); });
    comp.rels.forEach(function (r) {
      var size = relLabelSize(r);
      g.setEdge(r.source, r.target, size ? { width: size.width, height: size.height, labelpos: 'c' } : {}, r.id);
    });
    dagre.layout(g);

    comp.ents.forEach(function (e) { var p = g.node(e.name); e.x = p.x; e.y = p.y; });
    comp.rels.forEach(function (r) {
      var de = g.edge({ v: r.source, w: r.target, name: r.id });
      var pts = de.points.map(function (p) { return { x: p.x, y: p.y }; });
      var s = entById.get(r.source), t = entById.get(r.target);
      if (s !== t && pts.length >= 2) {
        pts[0] = intersect(s, pts.length > 2 ? pts[1] : t);
        pts[pts.length - 1] = intersect(t, pts.length > 2 ? pts[pts.length - 2] : s);
      }
      r.points = pts;
      var size = relLabelSize(r);
      r.lx = de.x; r.ly = de.y;
      r.lw = size ? size.width : 0; r.lh = size ? size.height : 0;
    });
    comp.box = boxOf(comp.ents, comp.rels);
  }

  function boxOf(list, relList) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    function grow(ax, ay, bx, by) { x0 = Math.min(x0, ax); y0 = Math.min(y0, ay); x1 = Math.max(x1, bx); y1 = Math.max(y1, by); }
    list.forEach(function (e) { grow(e.x - e.width / 2, e.y - e.height / 2, e.x + e.width / 2, e.y + e.height / 2); });
    relList.forEach(function (r) {
      r.points.forEach(function (p) { grow(p.x, p.y, p.x, p.y); });
      if (r.lw) grow(r.lx - r.lw / 2, r.ly - r.lh / 2, r.lx + r.lw / 2, r.ly + r.lh / 2);
    });
    if (!isFinite(x0)) { x0 = y0 = 0; x1 = y1 = 1; }
    return { x: x0, y: y0, w: Math.max(1, x1 - x0), h: Math.max(1, y1 - y0) };
  }

  // Each component is laid out with dagre, then the components are packed in
  // rows (largest first) towards the window's aspect ratio, so tables without
  // relationships do not stack into one tall column.
  function computeLayout() {
    ents.forEach(sizeEntity);
    var comps = components();
    comps.forEach(layoutComponent);
    comps.sort(function (a, b) { return b.box.h - a.box.h || b.box.w - a.box.w; });
    var gap = Math.max(state.nodesep, 40);
    var rect = svg.node().getBoundingClientRect();
    var aspect = Math.max(0.5, Math.min(3, (rect.width || 1200) / Math.max(1, rect.height || 800)));
    var area = d3.sum(comps, function (c) { return (c.box.w + gap) * (c.box.h + gap); });
    var rowW = Math.max(d3.max(comps, function (c) { return c.box.w; }), Math.sqrt(area * aspect));
    var x = 0, y = 0, rowH = 0;
    comps.forEach(function (c) {
      if (x > 0 && x + c.box.w > rowW) { x = 0; y += rowH + gap; rowH = 0; }
      var dx = x - c.box.x, dy = y - c.box.y;
      c.ents.forEach(function (e) { e.x += dx; e.y += dy; });
      c.rels.forEach(function (r) {
        r.points.forEach(function (p) { p.x += dx; p.y += dy; });
        r.lx += dx; r.ly += dy;
      });
      x += c.box.w + gap;
      rowH = Math.max(rowH, c.box.h);
    });
    bounds = boxOf(ents, rels);
  }

  // ---------------------------------------------------------------- render
  function relPath(r) {
    return d3.line().x(function (p) { return p.x; }).y(function (p) { return p.y; }).curve(d3.curveBasis)(r.points);
  }

  function render() {
    var m = metrics();
    [gRels, gLabels, gEnts].forEach(function (g) { g.selectAll('*').remove(); });

    rels.forEach(function (r) {
      var g = gRels.append('g').attr('class', 'er-rel' + (r.identifying ? '' : ' non-identifying')).datum(r);
      g.append('path').attr('class', 'er-rel-hit').attr('d', relPath(r));
      g.append('path').attr('class', 'er-rel-line').attr('d', relPath(r))
        .attr('marker-start', marker(r.source_card)).attr('marker-end', marker(r.target_card));
      if (r.label) {
        var l = gLabels.append('g').attr('class', 'er-rel-label').datum(r)
          .attr('transform', 'translate(' + r.lx + ',' + r.ly + ')');
        l.append('rect').attr('rx', 4).attr('x', -r.lw / 2).attr('y', -r.lh / 2).attr('width', r.lw).attr('height', r.lh);
        l.append('text').attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
          .style('font-size', m.lfs + 'px').text(r.label);
      }
    });
    gRels.selectAll('g.er-rel')
      .on('mouseenter', function (ev, r) { highlight({ type: 'rel', id: r.idx }); showRelTooltip(ev, r); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, r) { ev.stopPropagation(); togglePin({ type: 'rel', id: r.idx }); });

    ents.forEach(function (e) {
      var g = gEnts.append('g').attr('class', 'er-entity').datum(e).style('--c', e.color)
        .attr('transform', 'translate(' + (e.x - e.width / 2) + ',' + (e.y - e.height / 2) + ')');
      g.append('rect').attr('class', 'er-box').attr('rx', 6).attr('width', e.width).attr('height', e.height);
      // Header: rounded top corners only (square bottom when rows follow).
      var r = 6, w = e.width, h = m.headH;
      var headPath = e.rows.length
        ? 'M0,' + h + 'V' + r + 'A' + r + ',' + r + ' 0 0 1 ' + r + ',0H' + (w - r) + 'A' + r + ',' + r + ' 0 0 1 ' + w + ',' + r + 'V' + h + 'Z'
        : 'M' + r + ',0H' + (w - r) + 'A' + r + ',' + r + ' 0 0 1 ' + w + ',' + r + 'V' + (h - r) + 'A' + r + ',' + r + ' 0 0 1 ' + (w - r) + ',' + h + 'H' + r + 'A' + r + ',' + r + ' 0 0 1 0,' + (h - r) + 'V' + r + 'A' + r + ',' + r + ' 0 0 1 ' + r + ',0Z';
      g.append('path').attr('class', 'er-head').attr('d', headPath);
      g.append('text').attr('class', 'er-title').attr('x', w / 2).attr('y', h / 2).attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central').style('font-size', m.fs + 'px').text(e.label);
      e.rows.forEach(function (row, i) {
        var y = h + 3 + i * m.rowH, cy = y + m.rowH / 2;
        var rg = g.append('g').attr('class', 'er-row');
        row.y = y;
        rg.append('rect').attr('class', 'er-row-bg').attr('x', 1).attr('y', y).attr('width', w - 2).attr('height', m.rowH).attr('fill', 'transparent');
        if (i > 0) rg.append('line').attr('class', 'er-sep').attr('x1', 0).attr('x2', w).attr('y1', y).attr('y2', y);
        if (row.more) {
          rg.append('text').attr('class', 'er-more').attr('x', e.nameX).attr('y', cy).attr('dominant-baseline', 'central')
            .style('font-size', m.tfs + 'px').text('+' + row.more + ' more columns');
          return;
        }
        var c = row.col, bx = e.badgeX;
        keysOf(c).forEach(function (k) {
          var bw = textWidth(k, m.bfs, 'bold') + 8;
          var b = rg.append('g').attr('class', 'er-badge key-' + k);
          b.append('rect').attr('x', bx).attr('y', cy - m.bfs * 0.75).attr('width', bw).attr('height', m.bfs * 1.5).attr('rx', 3);
          b.append('text').attr('x', bx + bw / 2).attr('y', cy).attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
            .style('font-size', m.bfs + 'px').text(k);
          bx += bw + 3;
        });
        rg.append('text').attr('class', 'er-col-name').attr('x', e.nameX).attr('y', cy).attr('dominant-baseline', 'central')
          .style('font-size', m.fs + 'px').text(c.name);
        if (state.showTypes && c.type) {
          rg.append('text').attr('class', 'er-col-type').attr('x', e.typeX).attr('y', cy).attr('dominant-baseline', 'central')
            .style('font-size', m.tfs + 'px').text(c.type);
        }
      });
    });
    gEnts.selectAll('g.er-entity')
      .on('mouseenter', function (ev, e) { highlight({ type: 'entity', id: e.name }); showEntityTooltip(ev, e); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, e) { ev.stopPropagation(); togglePin({ type: 'entity', id: e.name }); });

    restoreHighlight();
  }

  // ---------------------------------------------------------------- highlight
  function highlight(target) {
    gEnts.selectAll('.er-row-hit').classed('er-row-hit', false);
    if (!target) { clearHighlight(); return; }
    var es = new Set(), rs = new Set(), focusEnt = null, focusRel = null;
    function addRel(r) { rs.add(r.idx); es.add(r.source); es.add(r.target); }
    if (target.type === 'entity') {
      // The entity, its relationships and its neighbours.
      focusEnt = target.id; es.add(target.id);
      rels.forEach(function (r) { if (r.source === target.id || r.target === target.id) addRel(r); });
    } else if (target.type === 'rel') {
      focusRel = target.id; addRel(rels[target.id]);
    } else if (target.type === 'step') {
      target.nodes.forEach(function (n) { es.add(n); });
      target.rels.forEach(addRel);
    }
    svg.classed('er-has-highlight', true);
    gEnts.selectAll('g.er-entity')
      .classed('er-hl', function (e) { return es.has(e.name); })
      .classed('er-focus', function (e) { return e.name === focusEnt; });
    gRels.selectAll('g.er-rel')
      .classed('er-hl', function (r) { return rs.has(r.idx); })
      .classed('er-focus', function (r) { return r.idx === focusRel; });
    gLabels.selectAll('g.er-rel-label').classed('er-hl', function (r) { return rs.has(r.idx); });
    if (target.column) {
      // Mark the searched column's row.
      var e = entById.get(target.id);
      gEnts.selectAll('g.er-entity').filter(function (d) { return d === e; }).selectAll('rect.er-row-bg')
        .filter(function (d, i) { return e.rows[i] && e.rows[i].col && e.rows[i].col.name === target.column; })
        .classed('er-row-hit', true);
    }
  }

  function clearHighlight() {
    svg.classed('er-has-highlight', false);
    svg.selectAll('.er-hl').classed('er-hl', false);
    svg.selectAll('.er-focus').classed('er-focus', false);
  }

  // While the walkthrough is open, its step owns the highlight.
  var walk = null, walkTarget = null;
  function restoreHighlight() { highlight(walkTarget || state.pinned); }
  function samePin(a, b) { return a && b && a.type === b.type && a.id === b.id && a.column === b.column; }
  function togglePin(target) {
    state.pinned = samePin(state.pinned, target) ? null : target;
    restoreHighlight();
  }
  function unpin() { state.pinned = null; restoreHighlight(); }

  // ---------------------------------------------------------------- tooltip
  // Built with textContent: all user text is escaped.
  function tooltipContent(title, body, meta) {
    var node = tooltip.node();
    node.textContent = '';
    [['er-tt-title', title], ['', body], ['er-tt-meta', meta]].forEach(function (row) {
      if (!row[1]) return;
      var d = document.createElement('div');
      if (row[0]) d.className = row[0];
      d.textContent = row[1];
      node.appendChild(d);
    });
    tooltip.classed('open', true);
  }
  function showEntityTooltip(ev, e) {
    var cols = e.columns || [];
    var keys = cols.filter(function (c) { return c.key; }).map(function (c) { return c.key + ' ' + c.name; });
    var n = rels.filter(function (r) { return r.source === e.name || r.target === e.name; }).length;
    tooltipContent(e.label, [e.tooltip, keys.join('\n')].filter(Boolean).join('\n'),
      cols.length + ' column' + (cols.length === 1 ? '' : 's') + ' · ' + n + ' relationship' + (n === 1 ? '' : 's'));
    moveTooltip(ev);
  }
  function showRelTooltip(ev, r) {
    var s = entById.get(r.source), t = entById.get(r.target);
    function end(e, card) { return e.label + (card ? ' (' + CARD_TEXT[card] + ')' : ''); }
    var body = end(s, r.source_card) + ' — ' + end(t, r.target_card);
    tooltipContent(r.label || (s.label + ' — ' + t.label), body, r.identifying ? 'identifying' : 'non-identifying');
    moveTooltip(ev);
  }
  function moveTooltip(ev) {
    var el = tooltip.node(), pad = 14;
    var x = ev.clientX + pad, y = ev.clientY + pad;
    var rr = el.getBoundingClientRect();
    if (x + rr.width > window.innerWidth - 8) x = ev.clientX - rr.width - pad;
    if (y + rr.height > window.innerHeight - 8) y = ev.clientY - rr.height - pad;
    tooltip.style('left', x + 'px').style('top', y + 'px');
  }
  function hideTooltip() { tooltip.classed('open', false); }

  // ---------------------------------------------------------------- view
  function viewportInsets() {
    var bar = document.querySelector('.top-panel');
    var top = bar ? bar.getBoundingClientRect().bottom + 12 : 16;
    var left = 16;
    document.querySelectorAll('.stats-panel').forEach(function (p) {
      if (p.style.display !== 'none') left = Math.max(left, p.getBoundingClientRect().right + 16);
    });
    return { top: top, left: left, right: 16, bottom: 16 + (walk ? walk.height() : 0) };
  }

  // Fit the whole diagram, or the box {x, y, w, h} (the walkthrough's follow camera).
  function fit(animated, box) {
    box = box || bounds;
    var rect = svg.node().getBoundingClientRect();
    var ins = viewportInsets();
    var availW = Math.max(50, rect.width - ins.left - ins.right);
    var availH = Math.max(50, rect.height - ins.top - ins.bottom);
    var k = Math.min(availW / box.w, availH / box.h, 1.5);
    var tx = ins.left + (availW - box.w * k) / 2 - box.x * k;
    var ty = ins.top + (availH - box.h * k) / 2 - box.y * k;
    (animated ? svg.transition().duration(500) : svg).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(k));
  }

  function focusOn(e) {
    var rect = svg.node().getBoundingClientRect();
    var k = Math.max(d3.zoomTransform(svg.node()).k, 0.9);
    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(rect.width / 2 - e.x * k, rect.height / 2 - e.y * k).scale(k));
  }

  function relayout(refit) {
    computeLayout();
    render();
    if (refit) fit(true, walkTarget ? stepBounds(walkTarget) : null);
  }

  // ---------------------------------------------------------------- walkthrough
  // Box around a step's entities and relationships, padded for context.
  function stepBounds(target) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    function grow(x, y) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    var names = new Set(target.nodes);
    target.rels.forEach(function (r) {
      names.add(r.source); names.add(r.target);
      r.points.forEach(function (p) { grow(p.x, p.y); });
    });
    names.forEach(function (name) {
      var e = entById.get(name);
      if (e) { grow(e.x - e.width / 2, e.y - e.height / 2); grow(e.x + e.width / 2, e.y + e.height / 2); }
    });
    if (!isFinite(x0)) return null;
    var pad = 50;
    return { x: x0 - pad, y: y0 - pad, w: x1 - x0 + 2 * pad, h: y1 - y0 + 2 * pad };
  }

  var walkButtons = ['walkButton', 'walkButton2'];
  if (DATA.steps && DATA.steps.length) {
    var relsByPair = new Map();
    rels.forEach(function (r) {
      var key = r.source + '\u0000' + r.target;
      if (!relsByPair.has(key)) relsByPair.set(key, []);
      relsByPair.get(key).push(r);
    });
    walk = D3BlocksWalkthrough({
      steps: DATA.steps,
      triggers: walkButtons,
      onOpen: hideTooltip,
      onStep: function (st) {
        var hl = st.highlight || {}, stepRels = [];
        (hl.edges || []).forEach(function (p) { stepRels = stepRels.concat(relsByPair.get(p[0] + '\u0000' + p[1]) || []); });
        var nodes = hl.nodes || [];
        walkTarget = (nodes.length || stepRels.length) ? { type: 'step', nodes: nodes, rels: stepRels } : null;
        restoreHighlight();
        fit(true, walkTarget ? stepBounds(walkTarget) : null);
      },
      onClose: function () { walkTarget = null; restoreHighlight(); fit(true); }
    });
  } else {
    walkButtons.forEach(function (id) { var b = document.getElementById(id); if (b) b.style.display = 'none'; });
  }

  // ---------------------------------------------------------------- export
  var STYLE_PROPS = ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-opacity',
    'opacity', 'font-family', 'font-size', 'font-weight', 'font-style', 'text-anchor', 'dominant-baseline',
    'paint-order', 'stroke-linejoin', 'stroke-linecap', 'visibility'];

  // Computed styles are inlined, so CSS-variable colours (theme, crow's-foot markers) survive in SVG and PNG.
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
    clone.querySelector('.er-viewport').removeAttribute('transform');
    clone.querySelectorAll('.er-rel-hit').forEach(function (el) { el.remove(); });
    var pad = 24, x = bounds.x - pad, y = bounds.y - pad, w = bounds.w + 2 * pad, h = bounds.h + 2 * pad;
    clone.setAttribute('xmlns', SVG_NS);
    clone.setAttribute('viewBox', [x, y, w, h].join(' '));
    clone.setAttribute('width', w);
    clone.setAttribute('height', h);
    clone.removeAttribute('class');
    var bg = document.createElementNS(SVG_NS, 'rect');
    bg.setAttribute('x', x); bg.setAttribute('y', y); bg.setAttribute('width', w); bg.setAttribute('height', h);
    bg.setAttribute('fill', window.getComputedStyle(document.body).backgroundColor);
    clone.insertBefore(bg, clone.querySelector('.er-viewport'));
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

  function fileStem() { return (OPTS.title || 'erd').replace(/[^\w.-]+/g, '_'); }

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
    var payload = {
      direction: state.direction,
      entities: ents.map(function (e) {
        return { name: e.name, label: e.label, color: e.color, columns: e.columns, x: e.x, y: e.y, width: e.width, height: e.height };
      }),
      relationships: rels.map(function (r) {
        return { source: r.source, target: r.target, source_card: r.source_card, target_card: r.target_card,
          label: r.label, identifying: r.identifying, points: r.points };
      })
    };
    download(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }), fileStem() + '.json');
  }

  // ---------------------------------------------------------------- controls
  function on(id, ev, fn) { var el = document.getElementById(id); if (el) el.addEventListener(ev, fn); return el; }

  on('saveSvgButton', 'click', saveSvg);
  on('savePngButton', 'click', savePng);
  on('exportButton', 'click', exportJson);
  on('fitButton', 'click', function () { fit(true); });
  on('fitButton2', 'click', function () { fit(true); });

  // Columns: all / keys / none, from the top panel (cycles) or the Layout panel.
  var COLUMN_MODES = ['all', 'keys', 'none'];
  function setColumns(mode) {
    state.showColumns = mode;
    var b = document.getElementById('columnsButton');
    if (b) b.textContent = 'Columns: ' + mode;
    document.querySelectorAll('[data-columns]').forEach(function (x) { x.classList.toggle('active', x.dataset.columns === mode); });
    relayout(true);
  }
  on('columnsButton', 'click', function () {
    setColumns(COLUMN_MODES[(COLUMN_MODES.indexOf(state.showColumns) + 1) % COLUMN_MODES.length]);
  });
  document.querySelectorAll('[data-columns]').forEach(function (btn) {
    btn.addEventListener('click', function () { setColumns(btn.dataset.columns); });
  });

  document.querySelectorAll('[data-direction]').forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.direction === state.direction);
    btn.addEventListener('click', function () {
      state.direction = btn.dataset.direction;
      document.querySelectorAll('[data-direction]').forEach(function (b) { b.classList.toggle('active', b === btn); });
      relayout(true);
    });
  });

  var types = document.getElementById('typesToggle');
  if (types) {
    types.checked = !!state.showTypes;
    types.addEventListener('change', function () { state.showTypes = types.checked; relayout(true); });
  }

  function slider(id, valId, key) {
    var el = document.getElementById(id), val = document.getElementById(valId);
    if (!el) return;
    el.value = state[key];
    if (val) val.textContent = state[key] + 'px';
    el.addEventListener('input', function () {
      state[key] = +el.value;
      if (val) val.textContent = state[key] + 'px';
      relayout(false);
    });
    el.addEventListener('change', function () { fit(true); });
  }
  slider('nodesepSlider', 'nodesepVal', 'nodesep');
  slider('ranksepSlider', 'ranksepVal', 'ranksep');
  slider('fontSizeSlider', 'fontSizeVal', 'fontsize');

  // Legend: the cardinalities and line styles in use (as archify lists the kinds present).
  (function buildLegend() {
    var panel = document.getElementById('legendPanel');
    var list = document.getElementById('legendList');
    if (!panel || !list) return;
    var used = new Set();
    rels.forEach(function (r) { if (r.source_card) used.add(r.source_card); if (r.target_card) used.add(r.target_card); });
    var dashed = rels.some(function (r) { return !r.identifying; });
    var keys = new Set();
    ents.forEach(function (e) { (e.columns || []).forEach(function (c) { keysOf(c).forEach(function (k) { keys.add(k); }); }); });
    if (!used.size && !keys.size) { panel.style.display = 'none'; return; }
    function item(svgInner, label) {
      var r = document.createElement('div');
      r.className = 'er-legend-item';
      var s = document.createElementNS(SVG_NS, 'svg');
      s.setAttribute('viewBox', '0 0 44 14');
      s.innerHTML = svgInner;
      r.appendChild(s);
      r.appendChild(document.createTextNode(label));
      list.appendChild(r);
    }
    function section(title) {
      var h = document.createElement('div');
      h.className = 'er-section-label';
      h.textContent = title;
      list.appendChild(h);
    }
    if (used.size) {
      section('Cardinality');
      Object.keys(CARD_TEXT).forEach(function (card) {
        if (used.has(card)) item('<path class="er-rel-line" d="M2,7H42" marker-end="url(#er-card-' + card + ')"/>', CARD_TEXT[card]);
      });
      section('Relationships');
      item('<path class="er-rel-line" d="M2,7H42"/>', 'identifying');
      if (dashed) item('<path class="er-rel-line" d="M2,7H42" style="stroke-dasharray:6 4"/>', 'non-identifying');
    }
    if (keys.size) {
      section('Keys');
      var names = { PK: 'primary key', FK: 'foreign key', UK: 'unique key' };
      ['PK', 'FK', 'UK'].forEach(function (k) {
        if (keys.has(k)) item('<g class="er-badge key-' + k + '"><rect x="6" y="1" width="26" height="12" rx="3"/>' +
          '<text x="19" y="7" text-anchor="middle" dominant-baseline="central" style="font-size:8px">' + k + '</text></g>', names[k]);
      });
    }
  })();

  // Theme (theme.js: runtime toggle, and dark_mode='auto' follows the OS until toggled).
  D3BlocksTheme.bind('themeBtn');

  // Search: tables and columns.
  (function setupSearch() {
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');
    if (!input || !results) return;
    function close() { results.classList.remove('open'); results.innerHTML = ''; }
    function pick(target, e) {
      state.pinned = target;
      if (target.column && state.showColumns !== 'all' &&
          !(state.showColumns === 'keys' && (e.columns || []).some(function (c) { return c.name === target.column && c.key; }))) {
        setColumns('all');
      }
      restoreHighlight();
      focusOn(e);
      close();
      input.blur();
    }
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      var hits = [];
      ents.forEach(function (e) {
        if (e.label.toLowerCase().indexOf(q) >= 0 || e.name.toLowerCase().indexOf(q) >= 0) {
          hits.push({ text: e.label, go: function () { pick({ type: 'entity', id: e.name }, e); } });
        }
      });
      ents.forEach(function (e) {
        (e.columns || []).forEach(function (c) {
          if (c.name.toLowerCase().indexOf(q) >= 0) {
            hits.push({ text: e.label + '.' + c.name + (c.type ? ' (' + c.type + ')' : ''),
              go: function () { pick({ type: 'entity', id: e.name, column: c.name }, e); } });
          }
        });
      });
      results.innerHTML = hits.length ? '' : '<div class="search-item" style="opacity:0.6">No matches</div>';
      hits.slice(0, 40).forEach(function (h) {
        var item = document.createElement('div');
        item.className = 'search-item';
        item.textContent = h.text;
        item.addEventListener('click', h.go);
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

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.activeElement.tagName !== 'INPUT') unpin();
  });

  // Side panels: stack below the top bar and collapse on title click.
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
  if (!ents.length) {
    d3.select('#er-main').append('div').attr('class', 'er-empty').text('No entities to draw.');
    return;
  }
  document.querySelectorAll('[data-columns]').forEach(function (x) { x.classList.toggle('active', x.dataset.columns === state.showColumns); });
  var cb = document.getElementById('columnsButton');
  if (cb) cb.textContent = 'Columns: ' + state.showColumns;
  if (!ents.some(function (e) { return (e.columns || []).length; })) {
    // Nothing to toggle when no entity has columns.
    if (cb) cb.style.display = 'none';
  }
  computeLayout();
  render();
  fit(false);

  window.__erd = { state: state, entities: ents, relationships: rels, fit: fit, walk: walk, relayout: relayout,
    bounds: function () { return bounds; } };
})();
