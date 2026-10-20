/*
 * d3.sequence.js - sequence diagram renderer for d3blocks.
 * Participants are columns with lifelines; messages are rows in time order.
 * The geometry is deterministic (no layout library). Rendering and interaction: d3 v7.
 */
(function () {
  'use strict';

  var DATA = JSON.parse(document.getElementById('sq-data').textContent);
  var OPTS = JSON.parse(document.getElementById('sq-options').textContent);

  var state = {
    spacing: OPTS.messageSpacing,
    wrap: OPTS.wrap,
    fontsize: OPTS.fontsize,
    pinned: null            // { type: 'participant' | 'message' | 'step', ... }
  };

  var FONT_FAMILY = '"Helvetica", Arial, sans-serif';
  var PAD = 24;
  var SVG_NS = 'http://www.w3.org/2000/svg';

  // ---------------------------------------------------------------- data
  var parts = DATA.participants.map(function (p, i) { return Object.assign({ idx: i }, p); });
  var partById = new Map(parts.map(function (p) { return [p.name, p]; }));
  var msgs = DATA.messages.map(function (m, i) { return Object.assign({ idx: i }, m); });
  var groups = DATA.groups.map(function (g, i) { return Object.assign({ idx: i }, g); });
  // Nesting depth: the number of regions that contain this one.
  groups.forEach(function (g) {
    g.depth = groups.filter(function (o) {
      return o !== g && o.from <= g.from && o.to >= g.to && (o.from < g.from || o.to > g.to || o.idx < g.idx);
    }).length;
  });

  // ---------------------------------------------------------------- svg
  var main = document.getElementById('sq-main');
  if (OPTS.width) main.style.width = OPTS.width + 'px';
  if (OPTS.height) main.style.height = OPTS.height + 'px';

  var svg = d3.select('#sq-svg');
  var defs = svg.append('defs');
  var viewport = svg.append('g').attr('class', 'sq-viewport');
  var gRegions = viewport.append('g').attr('class', 'sq-regions');
  var gLifelines = viewport.append('g').attr('class', 'sq-lifelines');
  var gMsgs = viewport.append('g').attr('class', 'sq-messages');
  var gHeads = viewport.append('g').attr('class', 'sq-heads');
  var tooltip = d3.select('#sq-tooltip');

  var zoom = d3.zoom().scaleExtent([0.05, 4]).on('zoom', function (ev) {
    viewport.attr('transform', ev.transform);
    stickHeads(ev.transform);
  });

  // The participant headers stay visible below the top bar when the view is
  // panned down a long sequence.
  function stickHeads(t) {
    var bar = document.querySelector('.top-panel');
    var top = (bar ? bar.getBoundingClientRect().bottom : 0) + 4;
    var dy = Math.max(0, (top - t.y) / t.k - PAD);
    gHeads.attr('transform', dy ? 'translate(0,' + dy + ')' : null);
  }
  svg.call(zoom).on('dblclick.zoom', null);
  svg.on('click', function (ev) { if (ev.target === svg.node()) unpin(); });

  var bounds = { x: 0, y: 0, w: 1, h: 1 };

  // ---------------------------------------------------------------- text
  var ctx = document.createElement('canvas').getContext('2d');
  function textWidth(s, size, weight) {
    ctx.font = (weight || 'normal') + ' ' + size + 'px ' + FONT_FAMILY;
    return ctx.measureText(String(s)).width;
  }
  function msgFont() { return Math.max(9, state.fontsize - 1); }

  // Greedy word wrap at `n` characters; '\n' always breaks. Long words stay whole.
  function wrapText(s, n) {
    var out = [];
    String(s).split('\n').forEach(function (para) {
      var line = '';
      para.split(/\s+/).forEach(function (word) {
        if (!word) return;
        if (line && (line + ' ' + word).length > n) { out.push(line); line = word; }
        else line = line ? line + ' ' + word : word;
      });
      out.push(line);
    });
    while (out.length && !out[out.length - 1]) out.pop();
    return out;
  }

  // ---------------------------------------------------------------- layout
  var headH = 0, lifeTop = 0, lifeBottom = 0;

  function computeLayout() {
    var fs = state.fontsize, lh = Math.round(fs * 1.3);
    var mfs = msgFont(), mlh = Math.round(mfs * 1.3);

    // Participant boxes, as wide as their label.
    var maxLines = 1;
    parts.forEach(function (p) {
      p.lines = String(p.label).split('\n');
      maxLines = Math.max(maxLines, p.lines.length);
      var tw = d3.max(p.lines, function (l) { return textWidth(l, fs, 'bold'); }) || 0;
      p.w = Math.max(90, tw + 28 + (p.kind === 'actor' ? 22 : 0));
    });
    headH = maxLines * lh + 22;

    // Column gaps: room for both boxes, then widened until every label fits
    // between its two lifelines (shortest spans first).
    var gaps = [];
    for (var k = 0; k + 1 < parts.length; k++) gaps.push((parts[k].w + parts[k + 1].w) / 2 + 30);
    msgs.forEach(function (m) {
      m.s = partById.get(m.source).idx;
      m.t = partById.get(m.target).idx;
      m.lines = m.label ? wrapText(m.label, state.wrap) : [];
      m.lw = m.lines.length ? (d3.max(m.lines, function (l) { return textWidth(l, mfs); }) + 16) : 0;
    });
    msgs.slice().sort(function (a, b) { return Math.abs(a.s - a.t) - Math.abs(b.s - b.t); }).forEach(function (m) {
      var a = Math.min(m.s, m.t), b = Math.max(m.s, m.t), cur = 0, need = m.lw + 24;
      for (var g = a; g < b; g++) cur += gaps[g];
      if (need > cur) for (var g2 = a; g2 < b; g2++) gaps[g2] += (need - cur) / (b - a);
    });
    parts.forEach(function (p, i) { p.x = i === 0 ? PAD + Math.max(p.w / 2, 30) : parts[i - 1].x + gaps[i - 1]; });

    // Rows: each message is a row; long labels push the row height. Regions
    // reserve a little room above their first and below their last message.
    lifeTop = PAD + headH;
    var y = lifeTop + 20;
    msgs.forEach(function (m, i) {
      m.rowStart = y;
      var starting = groups.filter(function (g) { return g.from === i; });
      y += starting.length * 12 + (starting.some(function (g) { return g.label; }) ? mlh : 0);
      m.labelH = m.lines.length * mlh;
      m.top = y;
      m.y = y + m.labelH + 8;
      y += Math.max(state.spacing, m.labelH + 22);
      y += groups.filter(function (g) { return g.to === i; }).length * 10;
    });
    lifeBottom = y + 10;

    groups.forEach(function (g) {
      var starting = groups.filter(function (o) { return o.from === g.from; }).sort(function (a, b) { return a.depth - b.depth; });
      var ending = groups.filter(function (o) { return o.to === g.to; }).sort(function (a, b) { return b.depth - a.depth; });
      var x0 = Infinity, x1 = -Infinity;
      for (var i = g.from; i <= g.to; i++) {
        [partById.get(msgs[i].source), partById.get(msgs[i].target)].forEach(function (p) {
          x0 = Math.min(x0, p.x - p.w / 2); x1 = Math.max(x1, p.x + p.w / 2);
        });
      }
      var inset = 14 - 6 * g.depth;
      g.box = {
        x: x0 - inset, w: x1 - x0 + 2 * inset,
        y: msgs[g.from].rowStart + 4 + 12 * starting.indexOf(g),
        h: 0
      };
      g.box.h = msgs[g.to].y + 12 + 10 * ending.indexOf(g) - g.box.y;
      g.labelY = g.box.y + mlh * 0.5 + 6;
    });

    var bx1 = d3.max(parts, function (p) { return p.x + p.w / 2; }) || 1;
    groups.forEach(function (g) { bx1 = Math.max(bx1, g.box.x + g.box.w); });
    var bx0 = Math.min(PAD, d3.min(groups, function (g) { return g.box.x; }) || PAD);
    bounds = { x: bx0 - PAD / 2, y: PAD / 2, w: bx1 - bx0 + PAD, h: lifeBottom };
  }

  // ---------------------------------------------------------------- render
  var markerIds = new Map();
  function markerFor(m) {
    var key = m.style + '|' + (m.color || '');
    if (!markerIds.has(key)) {
      var id = 'sq-head-' + markerIds.size;
      markerIds.set(key, id);
      var mk = defs.append('marker')
        .attr('id', id).attr('class', 'sq-head-' + m.style)
        .attr('viewBox', '0 0 10 10').attr('refX', 9.5).attr('refY', 5)
        .attr('markerWidth', 10).attr('markerHeight', 10).attr('markerUnits', 'userSpaceOnUse')
        .attr('orient', 'auto');
      var path = mk.append('path').attr('d', m.style === 'reply' ? 'M1,1L9.5,5L1,9' : 'M0,0L10,5L0,10Z');
      // Variant colours are data; default messages use the theme's --sq-line.
      if (m.color) path.style(m.style === 'reply' ? 'stroke' : 'fill', m.color);
    }
    return 'url(#' + markerIds.get(key) + ')';
  }

  function render() {
    var fs = state.fontsize, lh = Math.round(fs * 1.3);
    var mfs = msgFont(), mlh = Math.round(mfs * 1.3);
    [gRegions, gLifelines, gMsgs, gHeads].forEach(function (g) { g.selectAll('*').remove(); });

    // Regions, outer first.
    groups.slice().sort(function (a, b) { return a.depth - b.depth; }).forEach(function (g) {
      var r = gRegions.append('g').attr('class', 'sq-region').style('--c', g.color);
      r.append('rect').attr('rx', 8)
        .attr('x', g.box.x).attr('y', g.box.y).attr('width', g.box.w).attr('height', g.box.h);
      if (g.label) {
        r.append('text').attr('x', g.box.x + 10).attr('y', g.labelY)
          .attr('dominant-baseline', 'central').style('font-size', mfs + 'px').text(g.label);
      }
    });

    // Lifelines (under the messages) and participant headers (on top).
    parts.forEach(function (p) {
      var life = gLifelines.append('g').attr('class', 'sq-participant').datum(p).style('--c', p.color);
      life.append('line').attr('class', 'sq-lifeline').attr('x1', p.x).attr('x2', p.x).attr('y1', lifeTop).attr('y2', lifeBottom);
      life.append('line').attr('class', 'sq-lifeline-hit').attr('x1', p.x).attr('x2', p.x).attr('y1', lifeTop).attr('y2', lifeBottom);

      var head = gHeads.append('g').attr('class', 'sq-participant').datum(p).style('--c', p.color)
        .attr('transform', 'translate(' + p.x + ',' + (PAD + headH / 2) + ')');
      head.append('rect').attr('class', 'sq-head-bg').attr('rx', 6)
        .attr('x', -p.w / 2).attr('y', -headH / 2).attr('width', p.w).attr('height', headH);
      head.append('rect').attr('class', 'sq-head').attr('rx', 6)
        .attr('x', -p.w / 2).attr('y', -headH / 2).attr('width', p.w).attr('height', headH);
      var shift = p.kind === 'actor' ? 11 : 0;
      if (p.kind === 'actor') {
        // Stick figure left of the label.
        var ax = -p.w / 2 + 16, s = Math.min(14, headH - 14) / 14;
        head.append('path').attr('class', 'sq-actor')
          .attr('transform', 'translate(' + ax + ',0) scale(' + s + ')')
          .attr('d', 'M0,-4 m-3,-3 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M0,-4 V3 M-5,-1 H5 M0,3 L-4,9 M0,3 L4,9');
      }
      var text = head.append('text').attr('class', 'sq-head-label').attr('text-anchor', 'middle').style('font-size', fs + 'px');
      var y0 = -(p.lines.length - 1) / 2 * lh;
      p.lines.forEach(function (l, i) {
        text.append('tspan').attr('x', shift).attr('y', y0 + i * lh).attr('dominant-baseline', 'central').text(l);
      });
    });
    viewport.selectAll('g.sq-participant')
      .on('mouseenter', function (ev, p) { highlight({ type: 'participant', id: p.name }); showPartTooltip(ev, p); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, p) { ev.stopPropagation(); togglePin({ type: 'participant', id: p.name }); });

    // Messages.
    msgs.forEach(function (m) {
      var x1 = parts[m.s].x, x2 = parts[m.t].x;
      var g = gMsgs.append('g').attr('class', 'sq-msg style-' + m.style + ' variant-' + m.variant).datum(m);
      g.append('line').attr('class', 'sq-msg-hit').attr('x1', x1).attr('x2', x2).attr('y1', m.y).attr('y2', m.y);
      var line = g.append('line').attr('class', 'sq-msg-line')
        .attr('x1', x1).attr('x2', x2).attr('y1', m.y).attr('y2', m.y)
        .attr('stroke-width', m.width).attr('marker-end', markerFor(m));
      if (m.color) line.style('stroke', m.color);
      if (m.lines.length) {
        var cx = (x1 + x2) / 2;
        var lab = g.append('g').attr('class', 'sq-msg-label');
        lab.append('rect').attr('rx', 4)
          .attr('x', cx - m.lw / 2).attr('y', m.top - 2).attr('width', m.lw).attr('height', m.labelH + 4);
        var t = lab.append('text').attr('text-anchor', 'middle').style('font-size', mfs + 'px');
        m.lines.forEach(function (l, i) {
          t.append('tspan').attr('x', cx).attr('y', m.top + mlh * (i + 0.5)).attr('dominant-baseline', 'central').text(l);
        });
      }
    });
    gMsgs.selectAll('g.sq-msg')
      .on('mouseenter', function (ev, m) { highlight({ type: 'message', id: m.idx }); showMsgTooltip(ev, m); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, m) { ev.stopPropagation(); togglePin({ type: 'message', id: m.idx }); });

    restoreHighlight();
  }

  // ---------------------------------------------------------------- highlight
  function highlight(target) {
    if (!target) { clearHighlight(); return; }
    var ms = new Set(), ps = new Set(), focusPart = null, focusMsg = null;
    function addMsg(i) { var m = msgs[i]; ms.add(i); ps.add(m.source); ps.add(m.target); }
    if (target.type === 'participant') {
      focusPart = target.id; ps.add(target.id);
      msgs.forEach(function (m) { if (m.source === target.id || m.target === target.id) addMsg(m.idx); });
    } else if (target.type === 'message') {
      focusMsg = target.id; addMsg(target.id);
    } else if (target.type === 'step') {
      target.messages.forEach(addMsg);
      target.participants.forEach(function (p) { ps.add(p); });
    } else if (target.type === 'kind') {
      msgs.forEach(function (m) { if (m.style === target.id || m.variant === target.id) addMsg(m.idx); });
    } else if (target.type === 'region') {
      var g = groups[target.id];
      for (var i = g.from; i <= g.to; i++) addMsg(i);
    }
    svg.classed('sq-has-highlight', true);
    viewport.selectAll('g.sq-participant')
      .classed('sq-hl', function (p) { return ps.has(p.name); })
      .classed('sq-focus', function (p) { return p.name === focusPart; });
    gMsgs.selectAll('g.sq-msg')
      .classed('sq-hl', function (m) { return ms.has(m.idx); })
      .classed('sq-focus', function (m) { return m.idx === focusMsg; });
  }

  function clearHighlight() {
    svg.classed('sq-has-highlight', false);
    svg.selectAll('.sq-hl').classed('sq-hl', false);
    svg.selectAll('.sq-focus').classed('sq-focus', false);
  }

  // While the walkthrough is open, its step owns the highlight.
  var walk = null, walkTarget = null;
  function restoreHighlight() { highlight(walkTarget || state.pinned); }
  function samePin(a, b) { return a && b && a.type === b.type && a.id === b.id; }
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
    [['sq-tt-title', title], ['', body], ['sq-tt-meta', meta]].forEach(function (row) {
      if (!row[1]) return;
      var d = document.createElement('div');
      if (row[0]) d.className = row[0];
      d.textContent = row[1];
      node.appendChild(d);
    });
    tooltip.classed('open', true);
  }
  function plain(s) { return String(s).replace(/\n/g, ' '); }
  function showPartTooltip(ev, p) {
    var n = msgs.filter(function (m) { return m.source === p.name || m.target === p.name; }).length;
    tooltipContent(plain(p.label), p.tooltip, (p.kind === 'actor' ? 'actor' : 'participant') + ' · ' + n + ' message' + (n === 1 ? '' : 's'));
    moveTooltip(ev);
  }
  function showMsgTooltip(ev, m) {
    tooltipContent('#' + (m.idx + 1) + '  ' + plain(parts[m.s].label) + ' → ' + plain(parts[m.t].label),
      m.label, m.style === 'reply' ? 'reply' : 'call');
    moveTooltip(ev);
  }
  function moveTooltip(ev) {
    var el = tooltip.node(), pad = 14;
    var x = ev.clientX + pad, y = ev.clientY + pad;
    var r = el.getBoundingClientRect();
    if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - pad;
    if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - pad;
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

  // Fit to the window width, but never below a scale where message text is
  // about 9px (a legibility floor, as in archify): a wider diagram starts at the
  // left and pans. A diagram taller than the window starts at the top.
  function fitScale() {
    var rect = svg.node().getBoundingClientRect(), ins = viewportInsets();
    var availW = Math.max(50, rect.width - ins.left - ins.right);
    var availH = Math.max(50, rect.height - ins.top - ins.bottom);
    var floor = Math.min(1, 9 / msgFont());
    return { k: Math.min(Math.max(availW / bounds.w, floor), 1.5), floor: floor, ins: ins, availW: availW, availH: availH };
  }

  // Translation along one axis that centres `c` (in diagram units), unless the
  // diagram [lo, lo + size] is larger than the room, then clamped to its edges.
  function axis(start, avail, lo, size, c, k) {
    if (size * k <= avail) return start + (avail - size * k) / 2 - lo * k;
    var t = start + avail / 2 - c * k;
    return Math.max(Math.min(t, start - lo * k), start + avail - (lo + size) * k);
  }

  function fit(animated) {
    var f = fitScale(), k = f.k;
    var tx = axis(f.ins.left, f.availW, bounds.x, bounds.w, bounds.x, k);
    var ty = axis(f.ins.top, f.availH, bounds.y, bounds.h, bounds.y, k);
    (animated ? svg.transition().duration(500) : svg).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(k));
  }

  // Follow camera: keep the fit scale (smaller, down to the floor, if the box
  // does not fit) and centre the box {x0, x1, y0, y1}.
  function follow(box, animated) {
    var f = fitScale();
    var k = Math.max(f.floor, Math.min(f.k, f.availH / Math.max(1, box.y1 - box.y0)));
    var tx = axis(f.ins.left, f.availW, bounds.x, bounds.w, (box.x0 + box.x1) / 2, k);
    var ty = axis(f.ins.top, f.availH, bounds.y, bounds.h, (box.y0 + box.y1) / 2, k);
    (animated ? svg.transition().duration(450) : svg).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(k));
  }

  function followMessages(list) {
    if (!list.length) return;
    var box = { x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity };
    list.forEach(function (i) {
      var m = msgs[i];
      box.x0 = Math.min(box.x0, parts[m.s].x, parts[m.t].x); box.x1 = Math.max(box.x1, parts[m.s].x, parts[m.t].x);
      box.y0 = Math.min(box.y0, m.top - 30); box.y1 = Math.max(box.y1, m.y + 30);
    });
    follow(box, true);
  }

  // Participants only: bring their columns and headers into view.
  function followParticipants(list) {
    var xs = list.map(function (name) { return partById.get(name).x; });
    follow({ x0: d3.min(xs), x1: d3.max(xs), y0: bounds.y, y1: lifeTop + 40 }, true);
  }

  function relayout() { computeLayout(); render(); }

  // ---------------------------------------------------------------- walkthrough
  var walkButtons = ['walkButton', 'walkButton2'];
  if (DATA.steps && DATA.steps.length) {
    walk = D3BlocksWalkthrough({
      steps: DATA.steps,
      triggers: walkButtons,
      onOpen: hideTooltip,
      onStep: function (st) {
        var hl = st.highlight || {};
        var ms = hl.messages || [], ps = hl.participants || [];
        walkTarget = (ms.length || ps.length) ? { type: 'step', messages: ms, participants: ps } : null;
        restoreHighlight();
        if (ms.length) followMessages(ms);
        else if (ps.length) followParticipants(ps);
      },
      onClose: function () { walkTarget = null; restoreHighlight(); fit(true); }
    });
  } else {
    walkButtons.forEach(function (id) { var b = document.getElementById(id); if (b) b.style.display = 'none'; });
  }

  // ---------------------------------------------------------------- export
  var STYLE_PROPS = ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-opacity',
    'opacity', 'font-family', 'font-size', 'font-weight', 'text-anchor', 'dominant-baseline', 'paint-order',
    'stroke-linejoin', 'stroke-linecap', 'visibility'];

  // Computed styles are inlined, so CSS-variable colours (theme, markers) survive in SVG and PNG.
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
    clone.querySelector('.sq-viewport').removeAttribute('transform');
    clone.querySelector('.sq-heads').removeAttribute('transform');
    clone.querySelectorAll('.sq-msg-hit, .sq-lifeline-hit').forEach(function (el) { el.remove(); });
    var x = bounds.x, y = bounds.y, w = bounds.w, h = bounds.h;
    clone.setAttribute('xmlns', SVG_NS);
    clone.setAttribute('viewBox', [x, y, w, h].join(' '));
    clone.setAttribute('width', w);
    clone.setAttribute('height', h);
    clone.removeAttribute('class');
    var bg = document.createElementNS(SVG_NS, 'rect');
    bg.setAttribute('x', x); bg.setAttribute('y', y); bg.setAttribute('width', w); bg.setAttribute('height', h);
    bg.setAttribute('fill', window.getComputedStyle(document.body).backgroundColor);
    clone.insertBefore(bg, clone.querySelector('.sq-viewport'));
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

  function fileStem() { return (OPTS.title || 'sequence').replace(/[^\w.-]+/g, '_'); }

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
      participants: parts.map(function (p) {
        return { name: p.name, label: p.label, kind: p.kind, color: p.color, x: p.x, width: p.w };
      }),
      messages: msgs.map(function (m) {
        return { source: m.source, target: m.target, label: m.label, style: m.style, variant: m.variant, y: m.y };
      }),
      groups: groups.map(function (g) { return { label: g.label, from: g.from, to: g.to, color: g.color, box: g.box }; })
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

  function slider(id, valId, key, suffix) {
    var el = document.getElementById(id), val = document.getElementById(valId);
    if (!el) return;
    el.value = state[key];
    if (val) val.textContent = state[key] + suffix;
    el.addEventListener('input', function () {
      state[key] = +el.value;
      if (val) val.textContent = state[key] + suffix;
      relayout();
    });
    el.addEventListener('change', function () { fit(true); });
  }
  slider('spacingSlider', 'spacingVal', 'spacing', 'px');
  slider('wrapSlider', 'wrapVal', 'wrap', '');
  slider('fontSizeSlider', 'fontSizeVal', 'fontsize', 'px');

  // Legend: message kinds and variants in use, and the regions (as archify lists the kinds present).
  (function buildLegend() {
    var panel = document.getElementById('legendPanel');
    var list = document.getElementById('legendList');
    if (!panel || !list) return;
    function section(title) {
      var h = document.createElement('div');
      h.className = 'sq-section-label';
      h.textContent = title;
      list.appendChild(h);
    }
    function row(swatch, label, n, target) {
      var r = document.createElement('div');
      r.className = 'sq-legend-item';
      r.appendChild(swatch);
      r.appendChild(document.createTextNode(label));
      if (n !== null) {
        var c = document.createElement('span');
        c.className = 'sq-legend-count';
        c.textContent = n;
        r.appendChild(c);
      }
      r.addEventListener('mouseenter', function () { highlight(target); });
      r.addEventListener('mouseleave', restoreHighlight);
      r.addEventListener('click', function () { togglePin(target); });
      list.appendChild(r);
    }
    function lineSwatch(dash, color, width) {
      var s = document.createElementNS(SVG_NS, 'svg');
      s.setAttribute('class', 'sq-line-swatch');
      s.setAttribute('viewBox', '0 0 30 10');
      var l = document.createElementNS(SVG_NS, 'line');
      l.setAttribute('x1', 1); l.setAttribute('y1', 5); l.setAttribute('x2', 29); l.setAttribute('y2', 5);
      l.setAttribute('stroke-width', width);
      l.setAttribute('stroke-dasharray', dash);
      l.style.stroke = color || 'var(--sq-line)';
      s.appendChild(l);
      return s;
    }
    section('Messages');
    [['sync', 'Call', 'none'], ['reply', 'Reply', '6 4']].forEach(function (k) {
      var n = msgs.filter(function (m) { return m.style === k[0]; }).length;
      if (n) row(lineSwatch(k[2], null, 1.6), k[1], n, { type: 'kind', id: k[0] });
    });
    var variants = [];
    msgs.forEach(function (m) { if (m.variant !== 'default' && variants.indexOf(m.variant) < 0) variants.push(m.variant); });
    variants.forEach(function (v) {
      var m = msgs.find(function (x) { return x.variant === v; });
      row(lineSwatch('none', m.color, 2.4), v, msgs.filter(function (x) { return x.variant === v; }).length, { type: 'kind', id: v });
    });
    if (groups.length) {
      section('Regions');
      groups.forEach(function (g, i) {
        var sw = document.createElement('span');
        sw.className = 'sq-swatch';
        sw.style.background = g.color;
        row(sw, g.label || ('Messages ' + (g.from + 1) + '–' + (g.to + 1)), null, { type: 'region', id: i });
      });
    }
  })();

  // Theme (theme.js: runtime toggle, and dark_mode='auto' follows the OS until toggled).
  D3BlocksTheme.bind('themeBtn');

  // Search: participants and message text.
  (function setupSearch() {
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');
    if (!input || !results) return;
    function close() { results.classList.remove('open'); results.innerHTML = ''; }
    function done() { restoreHighlight(); close(); input.blur(); }
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      var hits = [];
      parts.forEach(function (p) {
        if (p.label.toLowerCase().indexOf(q) >= 0 || p.name.toLowerCase().indexOf(q) >= 0) {
          hits.push({ text: 'Participant: ' + plain(p.label), pick: function () {
            state.pinned = { type: 'participant', id: p.name }; done();
          } });
        }
      });
      msgs.forEach(function (m) {
        if (m.label.toLowerCase().indexOf(q) >= 0) {
          hits.push({ text: '#' + (m.idx + 1) + ' ' + plain(parts[m.s].label) + ' → ' + plain(parts[m.t].label) + ': ' + plain(m.label),
            pick: function () { state.pinned = { type: 'message', id: m.idx }; done(); followMessages([m.idx]); } });
        }
      });
      results.innerHTML = hits.length ? '' : '<div class="search-item" style="opacity:0.6">No matches</div>';
      hits.slice(0, 30).forEach(function (h) {
        var item = document.createElement('div');
        item.className = 'search-item';
        item.textContent = h.text;
        item.addEventListener('click', h.pick);
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
  if (!msgs.length) {
    d3.select('#sq-main').append('div').attr('class', 'sq-empty').text('No messages to draw.');
    return;
  }
  computeLayout();
  render();
  fit(false);

  window.__sequence = { state: state, participants: parts, messages: msgs, groups: groups, fit: fit, walk: walk,
    relayout: relayout, bounds: function () { return bounds; } };
})();
