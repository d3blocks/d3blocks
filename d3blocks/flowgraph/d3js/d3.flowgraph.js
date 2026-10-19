/*
 * d3.flowgraph.js - layered process-flow / architecture renderer for d3blocks.
 * Layout: dagre (compound, multigraph). Rendering and interaction: d3 v7.
 */
(function () {
  'use strict';

  var DATA = JSON.parse(document.getElementById('fg-data').textContent);
  var OPTS = JSON.parse(document.getElementById('fg-options').textContent);

  var state = {
    direction: OPTS.direction,
    nodesep: OPTS.nodesep,
    ranksep: OPTS.ranksep,
    edgesep: OPTS.edgesep,
    ranker: OPTS.ranker,
    layout: OPTS.layout || 'dagre',
    draggable: OPTS.draggable !== false,
    curve: OPTS.curve,
    animate: OPTS.animate,
    animation: OPTS.animation || 'pulse',
    showEdgeLabels: OPTS.showEdgeLabels,
    showGroups: OPTS.showGroups,
    fontsize: OPTS.fontsize,
    pinned: null            // { type: 'node' | 'group' | 'edge', id }
  };

  var FONT_FAMILY = '"Helvetica", Arial, sans-serif';
  var GROUP_PREFIX = 'grp::';
  var GROUP_PAD = 14;

  // ---------------------------------------------------------------- data
  var nodes = DATA.nodes.map(function (n, i) { return Object.assign({ idx: i }, n); });
  var nodeById = new Map(nodes.map(function (n) { return [n.name, n]; }));
  var edges = DATA.edges.map(function (e, i) { return Object.assign({ idx: i, id: 'e' + i }, e); });
  var groups = DATA.groups.map(function (g) { return Object.assign({}, g); });
  var groupById = new Map(groups.map(function (g) { return [g.name, g]; }));

  groups.forEach(function (g) {
    var depth = 0, p = g.parent;
    while (p && groupById.has(p) && depth < 64) { depth++; p = groupById.get(p).parent; }
    g.depth = depth;
  });

  // A group is drawn only if it (transitively) contains at least one node.
  var usedGroups = (function () {
    var used = new Set();
    nodes.forEach(function (n) {
      var g = n.group;
      while (g && groupById.has(g) && !used.has(g)) { used.add(g); g = groupById.get(g).parent; }
    });
    return groups.filter(function (g) { return used.has(g.name); });
  })();

  var outEdges = new Map(), inEdges = new Map();
  nodes.forEach(function (n) { outEdges.set(n.name, []); inEdges.set(n.name, []); });
  edges.forEach(function (e) {
    if (outEdges.has(e.source)) outEdges.get(e.source).push(e);
    if (inEdges.has(e.target)) inEdges.get(e.target).push(e);
  });

  // ---------------------------------------------------------------- svg
  var main = document.getElementById('fg-main');
  if (OPTS.width) main.style.width = OPTS.width + 'px';
  if (OPTS.height) main.style.height = OPTS.height + 'px';

  var svg = d3.select('#fg-svg');
  var defs = svg.append('defs');
  var viewport = svg.append('g').attr('class', 'fg-viewport');
  var gGroups = viewport.append('g').attr('class', 'fg-groups');
  var gEdges = viewport.append('g').attr('class', 'fg-edges');
  var gLabels = viewport.append('g').attr('class', 'fg-edge-labels');
  var gNodes = viewport.append('g').attr('class', 'fg-nodes');
  var tooltip = d3.select('#fg-tooltip');

  var zoom = d3.zoom().scaleExtent([0.05, 4]).on('zoom', function (ev) {
    viewport.attr('transform', ev.transform);
  });
  svg.call(zoom).on('dblclick.zoom', null);
  svg.on('click', function (ev) { if (ev.target === svg.node()) unpin(); });

  var bounds = { x: 0, y: 0, w: 1, h: 1 };

  // ---------------------------------------------------------------- text
  var ctx = document.createElement('canvas').getContext('2d');
  function textWidth(s, size, weight) {
    ctx.font = (weight || 'normal') + ' ' + size + 'px ' + FONT_FAMILY;
    return ctx.measureText(String(s)).width;
  }
  function lineHeight() { return Math.round(state.fontsize * 1.3); }
  function edgeFont() { return Math.max(9, state.fontsize - 2); }
  function groupHeader() { return Math.round(state.fontsize + 12); }

  // ---------------------------------------------------------------- shapes
  // A circle without a label is a pseudo-state (state diagram start / end): a small solid dot.
  function isPseudo(n) { return n.shape === 'circle' && !String(n.label).trim(); }

  function sizeNode(n) {
    var fs = state.fontsize, lh = lineHeight();
    n.lines = String(n.label).split('\n');
    if (isPseudo(n)) { n.width = n.height = 22; return; }
    var tw = d3.max(n.lines, function (l) { return textWidth(l, fs); }) || 0;
    var th = n.lines.length * lh;
    var w = tw + 32, h = th + 20;
    switch (n.shape) {
      case 'decision': w = tw * 1.5 + 28; h = th * 3 + 8; break;
      case 'io': w += h * 0.6; break;
      case 'terminal': w += h * 0.4; break;
      case 'subprocess': w += 16; break;
      case 'database': h += 16; break;
      case 'queue': w += 24; break;
      case 'document': h += 10; break;
      case 'circle': w = h = Math.max(tw + 20, th + 20); break;
    }
    n.width = Math.max(w, 48);
    n.height = Math.max(h, lh + 14);
    if (n.shape === 'circle') n.width = n.height = Math.max(n.width, n.height);
  }

  function roundedRect(x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    return 'M' + (x + r) + ',' + y + 'H' + (x + w - r) +
      'A' + r + ',' + r + ' 0 0 1 ' + (x + w) + ',' + (y + r) + 'V' + (y + h - r) +
      'A' + r + ',' + r + ' 0 0 1 ' + (x + w - r) + ',' + (y + h) + 'H' + (x + r) +
      'A' + r + ',' + r + ' 0 0 1 ' + x + ',' + (y + h - r) + 'V' + (y + r) +
      'A' + r + ',' + r + ' 0 0 1 ' + (x + r) + ',' + y + 'Z';
  }

  function shapePath(n) {
    var w = n.width, h = n.height, x = -w / 2, y = -h / 2, r;
    switch (n.shape) {
      case 'decision':
        return 'M0,' + y + 'L' + (w / 2) + ',0L0,' + (h / 2) + 'L' + x + ',0Z';
      case 'io':
        r = h * 0.3;
        return 'M' + (x + r) + ',' + y + 'L' + (w / 2) + ',' + y + 'L' + (w / 2 - r) + ',' + (h / 2) + 'L' + x + ',' + (h / 2) + 'Z';
      case 'terminal':
        return roundedRect(x, y, w, h, h / 2);
      case 'subprocess':
        return roundedRect(x, y, w, h, 3) +
          'M' + (x + 8) + ',' + y + 'V' + (h / 2) + 'M' + (w / 2 - 8) + ',' + y + 'V' + (h / 2);
      case 'database':
        r = 8;
        return 'M' + x + ',' + (y + r) + 'A' + (w / 2) + ',' + r + ' 0 0 1 ' + (w / 2) + ',' + (y + r) +
          'V' + (h / 2 - r) + 'A' + (w / 2) + ',' + r + ' 0 0 1 ' + x + ',' + (h / 2 - r) + 'Z' +
          'M' + x + ',' + (y + r) + 'A' + (w / 2) + ',' + r + ' 0 0 0 ' + (w / 2) + ',' + (y + r);
      case 'queue':
        r = 10;
        return 'M' + (x + r) + ',' + y + 'H' + (w / 2 - r) + 'A' + r + ',' + (h / 2) + ' 0 0 1 ' + (w / 2 - r) + ',' + (h / 2) +
          'H' + (x + r) + 'A' + r + ',' + (h / 2) + ' 0 0 1 ' + (x + r) + ',' + y + 'Z' +
          'M' + (w / 2 - r) + ',' + y + 'A' + r + ',' + (h / 2) + ' 0 0 0 ' + (w / 2 - r) + ',' + (h / 2);
      case 'document':
        return 'M' + x + ',' + y + 'H' + (w / 2) + 'V' + (h / 2 - 8) +
          'C' + (w / 4) + ',' + (h / 2 + 6) + ' ' + (-w / 4) + ',' + (h / 2 - 20) + ' ' + x + ',' + (h / 2 - 6) + 'Z';
      case 'circle':
        r = w / 2;
        return 'M' + (-r) + ',0A' + r + ',' + r + ' 0 1 0 ' + r + ',0A' + r + ',' + r + ' 0 1 0 ' + (-r) + ',0Z';
      default: // process, external
        return roundedRect(x, y, w, h, 6);
    }
  }

  function labelOffset(n) {
    if (n.shape === 'database') return 5;
    if (n.shape === 'document') return -4;
    return 0;
  }

  // ---------------------------------------------------------------- edge clipping
  function polygonOf(n) {
    var w = n.width / 2, h = n.height / 2;
    if (n.shape === 'decision') return [[0, -h], [w, 0], [0, h], [-w, 0]];
    if (n.shape === 'io') { var s = n.height * 0.3; return [[-w + s, -h], [w, -h], [w - s, h], [-w, h]]; }
    return null;
  }

  // Ray from the origin along (dx, dy) against segment a-b; returns t > 0 or null.
  function raySegment(dx, dy, a, b) {
    var ex = b[0] - a[0], ey = b[1] - a[1];
    var den = dx * ey - dy * ex;
    if (Math.abs(den) < 1e-9) return null;
    var t = (a[0] * ey - a[1] * ex) / den;
    var u = (a[0] * dy - a[1] * dx) / den;
    return (t > 0 && u >= 0 && u <= 1) ? t : null;
  }

  // Point where the line from the node centre towards p crosses the node outline.
  function intersect(n, p) {
    var dx = p.x - n.x, dy = p.y - n.y;
    if (Math.abs(dx) < 1e-6 && Math.abs(dy) < 1e-6) return { x: n.x, y: n.y };
    if (n.shape === 'circle') {
      var d = Math.hypot(dx, dy), r = n.width / 2;
      return { x: n.x + dx / d * r, y: n.y + dy / d * r };
    }
    var poly = polygonOf(n);
    if (poly) {
      var best = null;
      for (var i = 0; i < poly.length; i++) {
        var t = raySegment(dx, dy, poly[i], poly[(i + 1) % poly.length]);
        if (t !== null && (best === null || t < best)) best = t;
      }
      if (best !== null) return { x: n.x + dx * best, y: n.y + dy * best };
    }
    var w = n.width / 2, h = n.height / 2, sx, sy;
    if (Math.abs(dy) * w > Math.abs(dx) * h) { if (dy < 0) h = -h; sx = h * dx / dy; sy = h; }
    else { if (dx < 0) w = -w; sx = w; sy = w * dy / dx; }
    return { x: n.x + sx, y: n.y + sy };
  }

  // ---------------------------------------------------------------- layout
  // Both engines fill in n.x/n.y (centres), e.points, e.lx/e.ly/e.lw/e.lh and
  // gr.box, then computeBounds(). computeLayout() returns a Promise because ELK
  // is asynchronous; a newer request supersedes an older one.
  var layoutToken = 0;
  function computeLayout() {
    var token = ++layoutToken;
    nodes.forEach(sizeNode);
    var useGroups = state.showGroups && usedGroups.length > 0;
    var run = (state.layout === 'elk' && typeof ELK !== 'undefined')
      ? layoutElk(useGroups) : Promise.resolve(layoutDagre(useGroups));
    return run.then(function () {
      if (token !== layoutToken) return false;
      computeBounds(useGroups);
      return true;
    });
  }

  function edgeLabelSize(e) {
    if (!(state.showEdgeLabels && e.label)) return null;
    var lfs = edgeFont();
    return { width: textWidth(e.label, lfs) + 12, height: lfs + 8 };
  }

  function layoutDagre(useGroups) {
    var g = new dagre.graphlib.Graph({ compound: true, multigraph: true });
    g.setGraph({
      rankdir: state.direction, nodesep: state.nodesep, ranksep: state.ranksep,
      edgesep: state.edgesep, ranker: state.ranker, marginx: 20, marginy: 20
    });
    g.setDefaultEdgeLabel(function () { return {}; });

    nodes.forEach(function (n) { g.setNode(n.name, { width: n.width, height: n.height }); });
    if (useGroups) {
      usedGroups.forEach(function (gr) { g.setNode(GROUP_PREFIX + gr.name, {}); });
      usedGroups.forEach(function (gr) {
        if (gr.parent && groupById.has(gr.parent)) g.setParent(GROUP_PREFIX + gr.name, GROUP_PREFIX + gr.parent);
      });
      nodes.forEach(function (n) {
        if (n.group && groupById.has(n.group)) g.setParent(n.name, GROUP_PREFIX + n.group);
      });
    }

    edges.forEach(function (e) {
      var size = edgeLabelSize(e);
      g.setEdge(e.source, e.target, size ? { width: size.width, height: size.height, labelpos: 'c' } : {}, e.id);
    });

    dagre.layout(g);

    nodes.forEach(function (n) { var p = g.node(n.name); n.x = p.x; n.y = p.y; });
    edges.forEach(function (e) {
      var de = g.edge({ v: e.source, w: e.target, name: e.id });
      var pts = de.points.map(function (p) { return { x: p.x, y: p.y }; });
      var s = nodeById.get(e.source), t = nodeById.get(e.target);
      if (s !== t && pts.length >= 2) {
        pts[0] = intersect(s, pts.length > 2 ? pts[1] : t);
        pts[pts.length - 1] = intersect(t, pts.length > 2 ? pts[pts.length - 2] : s);
      }
      e.points = pts;
      e.lx = de.x; e.ly = de.y;
      var size = edgeLabelSize(e);
      e.lw = size ? (de.width || 0) : 0;
      e.lh = size ? (de.height || 0) : 0;
    });

    compressRanks(useGroups);
    expandCrossAxis(useGroups);
    groupBoxes(usedGroups);
  }

  // ELK: native compound layout, orthogonal edges, padding reserved for headers.
  var elk = null;
  function layoutElk(useGroups) {
    elk = elk || new ELK();
    var header = groupHeader();
    var dir = { LR: 'RIGHT', TB: 'DOWN', RL: 'LEFT', BT: 'UP' }[state.direction];
    var root = {
      id: '__root__',
      layoutOptions: {
        'elk.algorithm': 'layered',
        'elk.direction': dir,
        'elk.hierarchyHandling': 'INCLUDE_CHILDREN',
        'elk.edgeRouting': 'ORTHOGONAL',
        'elk.padding': '[top=20,left=20,bottom=20,right=20]',
        'elk.spacing.nodeNode': String(state.nodesep),
        'elk.layered.spacing.nodeNodeBetweenLayers': String(state.ranksep),
        'elk.spacing.edgeNode': String(Math.max(10, state.edgesep)),
        'elk.spacing.edgeEdge': String(Math.max(6, state.edgesep / 2)),
        'elk.layered.spacing.edgeNodeBetweenLayers': String(Math.max(10, state.edgesep)),
        'elk.layered.spacing.edgeEdgeBetweenLayers': String(Math.max(6, state.edgesep / 2)),
        'elk.edgeLabels.placement': 'CENTER'
      },
      children: [],
      edges: []
    };
    var containers = new Map([['__root__', root]]);
    if (useGroups) {
      usedGroups.slice().sort(function (a, b) { return a.depth - b.depth; }).forEach(function (gr) {
        var minW = Math.ceil(textWidth(gr.label, state.fontsize - 1, 'bold') + 24);
        var c = {
          id: GROUP_PREFIX + gr.name, children: [],
          layoutOptions: {
            'elk.padding': '[top=' + (GROUP_PAD + header) + ',left=' + GROUP_PAD + ',bottom=' + GROUP_PAD + ',right=' + GROUP_PAD + ']',
            'elk.nodeSize.constraints': 'MINIMUM_SIZE',
            'elk.nodeSize.minimum': '(' + minW + ',' + (header + 2 * GROUP_PAD) + ')'
          }
        };
        containers.set(c.id, c);
        var parent = (gr.parent && containers.has(GROUP_PREFIX + gr.parent)) ? containers.get(GROUP_PREFIX + gr.parent) : root;
        parent.children.push(c);
      });
    }
    nodes.forEach(function (n) {
      var key = (useGroups && n.group && containers.has(GROUP_PREFIX + n.group)) ? GROUP_PREFIX + n.group : '__root__';
      containers.get(key).children.push({ id: n.name, width: n.width, height: n.height });
    });
    edges.forEach(function (e) {
      var size = edgeLabelSize(e);
      root.edges.push({ id: e.id, sources: [e.source], targets: [e.target],
        labels: size ? [{ text: e.label, width: size.width, height: size.height }] : [] });
    });

    return elk.layout(root).then(function (res) {
      // Absolute offsets of every ELK node (positions are relative to the parent).
      var abs = new Map([['__root__', { x: res.x || 0, y: res.y || 0 }]]);
      (function walkElk(parent, ox, oy) {
        (parent.children || []).forEach(function (c) {
          var x = ox + c.x, y = oy + c.y;
          abs.set(c.id, { x: x, y: y });
          if (c.id.indexOf(GROUP_PREFIX) === 0) {
            var gr = groupById.get(c.id.slice(GROUP_PREFIX.length));
            if (gr) gr.box = { x: x, y: y, w: c.width, h: c.height };
            walkElk(c, x, y);
          } else {
            var n = nodeById.get(c.id);
            if (n) { n.x = x + c.width / 2; n.y = y + c.height / 2; }
          }
        });
      })(res, 0, 0);

      var byId = new Map((res.edges || []).map(function (e) { return [e.id, e]; }));
      edges.forEach(function (e) {
        var re = byId.get(e.id), off = abs.get((re && re.container) || '__root__') || { x: 0, y: 0 };
        var sec = re && re.sections && re.sections[0];
        var s = nodeById.get(e.source), t = nodeById.get(e.target);
        if (!sec) {
          e.points = [intersect(s, t), intersect(t, s)];
        } else {
          var pts = [sec.startPoint].concat(sec.bendPoints || [], [sec.endPoint]).map(function (p) {
            return { x: p.x + off.x, y: p.y + off.y };
          });
          // ELK ends edges on the bounding box; continue them onto non-rectangular outlines.
          if (pts.length >= 2 && s !== t) {
            pts[0] = clipAlong(s, pts[0], pts[1]);
            pts[pts.length - 1] = clipAlong(t, pts[pts.length - 1], pts[pts.length - 2]);
          }
          e.points = pts;
        }
        var lab = re && re.labels && re.labels[0];
        if (lab && edgeLabelSize(e)) {
          e.lx = off.x + lab.x + lab.width / 2; e.ly = off.y + lab.y + lab.height / 2;
          e.lw = lab.width; e.lh = lab.height;
        } else {
          var mid = e.points[Math.floor(e.points.length / 2)];
          e.lx = mid.x; e.ly = mid.y; e.lw = 0; e.lh = 0;
        }
      });
    });
  }

  // Move an endpoint p (on n's bounding box) along the direction from q to p
  // until it touches the node outline. Only diamonds, parallelograms and circles
  // differ from their bounding box.
  function clipAlong(n, p, q) {
    if (!n || !(n.shape === 'decision' || n.shape === 'io' || n.shape === 'circle')) return p;
    var dx = p.x - q.x, dy = p.y - q.y, len = Math.hypot(dx, dy);
    if (len < 1e-6) return p;
    dx /= len; dy /= len;
    // Ray from p (relative to the node centre) along (dx, dy).
    var ox = p.x - n.x, oy = p.y - n.y, best = null;
    if (n.shape === 'circle') {
      var r = n.width / 2, b = ox * dx + oy * dy, c = ox * ox + oy * oy - r * r, disc = b * b - c;
      if (disc >= 0) { var t1 = -b - Math.sqrt(disc); if (t1 >= 0) best = t1; }
    } else {
      var poly = polygonOf(n);
      for (var i = 0; i < poly.length; i++) {
        var a = poly[i], bb = poly[(i + 1) % poly.length];
        var ex = bb[0] - a[0], ey = bb[1] - a[1], den = dx * ey - dy * ex;
        if (Math.abs(den) < 1e-9) continue;
        var t = ((a[0] - ox) * ey - (a[1] - oy) * ex) / den;
        var u = ((a[0] - ox) * dy - (a[1] - oy) * dx) / den;
        if (t >= 0 && u >= 0 && u <= 1 && (best === null || t < best)) best = t;
      }
    }
    return best === null ? p : { x: p.x + dx * best, y: p.y + dy * best };
  }

  // Group boxes bottom-up from their members, so every box fully contains its
  // nodes, nested groups and its own header.
  function groupBoxes(list) {
    var header = groupHeader();
    list.slice().sort(function (a, b) { return b.depth - a.depth; }).forEach(function (gr) {
      var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      nodes.forEach(function (n) {
        if (n.group !== gr.name) return;
        x0 = Math.min(x0, n.x - n.width / 2); x1 = Math.max(x1, n.x + n.width / 2);
        y0 = Math.min(y0, n.y - n.height / 2); y1 = Math.max(y1, n.y + n.height / 2);
      });
      usedGroups.forEach(function (c) {
        if (c.parent !== gr.name || !c.box) return;
        x0 = Math.min(x0, c.box.x); x1 = Math.max(x1, c.box.x + c.box.w);
        y0 = Math.min(y0, c.box.y); y1 = Math.max(y1, c.box.y + c.box.h);
      });
      if (!isFinite(x0)) return;
      var minW = textWidth(gr.label, state.fontsize - 1, 'bold') + 24;
      var w = Math.max(x1 - x0 + 2 * GROUP_PAD, minW);
      var cx = (x0 + x1) / 2;
      gr.box = { x: cx - w / 2, y: y0 - GROUP_PAD - header, w: w, h: y1 - y0 + 2 * GROUP_PAD + header };
    });
  }

  // Overall bounds for fitting and export.
  function computeBounds(useGroups) {
    if (useGroups === undefined) useGroups = state.showGroups && usedGroups.length > 0;
    var bx0 = Infinity, by0 = Infinity, bx1 = -Infinity, by1 = -Infinity;
    function grow(x0, y0, x1, y1) {
      bx0 = Math.min(bx0, x0); by0 = Math.min(by0, y0); bx1 = Math.max(bx1, x1); by1 = Math.max(by1, y1);
    }
    nodes.forEach(function (n) { grow(n.x - n.width / 2, n.y - n.height / 2, n.x + n.width / 2, n.y + n.height / 2); });
    edges.forEach(function (e) { e.points.forEach(function (p) { grow(p.x, p.y, p.x, p.y); }); });
    if (useGroups) usedGroups.forEach(function (gr) { if (gr.box) grow(gr.box.x, gr.box.y, gr.box.x + gr.box.w, gr.box.y + gr.box.h); });
    if (!isFinite(bx0)) { bx0 = by0 = 0; bx1 = by1 = 1; }
    bounds = { x: bx0, y: by0, w: Math.max(1, bx1 - bx0), h: Math.max(1, by1 - by0) };
  }

  // dagre multiplies edge lengths by (2 * nesting depth + 1) for compound
  // graphs, which leaves wide empty bands between ranks. Shrink every gap
  // along the rank axis to what it needs: the rank spacing, plus padding and
  // headers for each group boundary that falls inside the gap. One monotone
  // piecewise-linear map is applied to nodes, edge points and labels alike,
  // so edge routing stays consistent.
  function compressRanks(useGroups) {
    var horizontal = state.direction === 'LR' || state.direction === 'RL';
    var A = horizontal ? 'x' : 'y', S = horizontal ? 'width' : 'height';

    var items = nodes.map(function (n) { return { s: n[A] - n[S] / 2, e: n[A] + n[S] / 2, label: false }; });
    edges.forEach(function (e) {
      if (!e.lw) return;
      var c = horizontal ? e.lx : e.ly, size = horizontal ? e.lw : e.lh;
      items.push({ s: c - size / 2, e: c + size / 2, label: true });
    });
    if (!items.length) return;
    items.sort(function (a, b) { return a.s - b.s; });

    var blocks = [];
    items.forEach(function (it) {
      var last = blocks[blocks.length - 1];
      if (last && it.s <= last.e + 1) { last.e = Math.max(last.e, it.e); last.label = last.label && it.label; }
      else blocks.push({ s: it.s, e: it.e, label: it.label });
    });

    // Extent of every drawn group along the rank axis.
    var extents = !useGroups ? [] : usedGroups.map(function (g) {
      var members = groupMembers(g.name), lo = Infinity, hi = -Infinity;
      nodes.forEach(function (n) {
        if (!members.has(n.name)) return;
        lo = Math.min(lo, n[A] - n[S] / 2); hi = Math.max(hi, n[A] + n[S] / 2);
      });
      return { lo: lo, hi: hi };
    });

    var G = state.ranksep, Glabel = Math.max(12, state.ranksep * 0.35), header = groupHeader();
    var pos = blocks[0].s;
    blocks.forEach(function (b, i) {
      b.ns = pos;
      pos += b.e - b.s;
      var next = blocks[i + 1];
      if (!next) return;
      var need = (b.label || next.label) ? Glabel : G;
      extents.forEach(function (x) {
        if (x.hi >= b.s - 0.5 && x.hi <= b.e + 0.5) need += GROUP_PAD;
        // Group headers sit on the top edge, which is on the rank axis only for TB/BT.
        if (x.lo >= next.s - 0.5 && x.lo <= next.e + 0.5) need += GROUP_PAD + (horizontal ? 0 : header);
      });
      b.gapOld = next.s - b.e;
      b.gapNew = Math.min(b.gapOld, need);
      pos += b.gapNew;
    });

    function map(v) {
      if (v <= blocks[0].s) return blocks[0].ns + (v - blocks[0].s);
      for (var i = 0; i < blocks.length; i++) {
        var b = blocks[i];
        if (v <= b.e) return b.ns + (v - b.s);
        var next = blocks[i + 1];
        if (!next) return b.ns + (v - b.s);
        if (v < next.s) return b.ns + (b.e - b.s) + (v - b.e) * (b.gapOld > 0 ? b.gapNew / b.gapOld : 1);
      }
      return v;
    }

    // Region of a rank-axis coordinate: 2*i inside block i, 2*i+1 in the gap after it.
    function region(v) {
      for (var i = 0; i < blocks.length; i++) {
        if (v <= blocks[i].e + 0.5) return v >= blocks[i].s - 0.5 ? 2 * i : 2 * i - 1;
      }
      return 2 * blocks.length - 1;
    }

    // Inside a gap an edge keeps only two control points, at 1/3 and 2/3 of the
    // compressed gap, giving one smooth S-bend instead of a flattened zigzag of
    // dagre's dummy-node waypoints. Points inside occupied ranks are kept as is.
    function reroute(pts) {
      var out = [], i = 0;
      while (i < pts.length) {
        var r = region(pts[i][A]), j = i;
        while (j + 1 < pts.length && region(pts[j + 1][A]) === r) j++;
        var gap = (r % 2 !== 0) ? blocks[(r - 1) / 2] : null;
        if (!gap || !gap.gapOld || i === 0 || j === pts.length - 1) {
          for (var k = i; k <= j; k++) out.push({ x: pts[k].x, y: pts[k].y, m: true });
        } else {
          var start = gap.ns + (gap.e - gap.s), forward = pts[j][A] >= pts[i][A];
          var a = Object.assign({}, pts[i]), b = Object.assign({}, pts[j]);
          a[A] = start + gap.gapNew * (forward ? 1 / 3 : 2 / 3);
          b[A] = start + gap.gapNew * (forward ? 2 / 3 : 1 / 3);
          out.push(a);
          if (j > i) out.push(b);
        }
        i = j + 1;
      }
      out.forEach(function (p) { if (p.m) { p[A] = map(p[A]); delete p.m; } });
      return out;
    }

    nodes.forEach(function (n) { n[A] = map(n[A]); });
    edges.forEach(function (e) {
      var s = nodeById.get(e.source), t = nodeById.get(e.target);
      e.points = (s === t) ? e.points.map(function (p) { var q = Object.assign({}, p); q[A] = map(q[A]); return q; })
                           : reroute(e.points);
      if (horizontal) e.lx = map(e.lx); else e.ly = map(e.ly);
    });
  }

  // dagre does not reserve room for group headers or padding on the cross
  // axis (y for LR/RL, x for TB/BT). Insert a band of space at every group's
  // leading edge (padding + header) and trailing edge (padding).
  function expandCrossAxis(useGroups) {
    if (!useGroups) return;
    var horizontal = state.direction === 'LR' || state.direction === 'RL';
    var B = horizontal ? 'y' : 'x', S = horizontal ? 'height' : 'width';
    var header = horizontal ? groupHeader() : 0;
    var cuts = [];
    usedGroups.forEach(function (g) {
      var members = groupMembers(g.name), lo = Infinity, hi = -Infinity;
      nodes.forEach(function (n) {
        if (!members.has(n.name)) return;
        lo = Math.min(lo, n[B] - n[S] / 2); hi = Math.max(hi, n[B] + n[S] / 2);
      });
      if (!isFinite(lo)) return;
      cuts.push({ at: lo, amount: GROUP_PAD + header, lead: true });
      cuts.push({ at: hi, amount: GROUP_PAD, lead: false });
    });
    // `margin` lets edge waypoints that hug a group's outermost member move with
    // the group; dagre often puts the first waypoint just past the node edge.
    function shift(v, margin) {
      var d = 0;
      cuts.forEach(function (c) { if (c.lead ? v >= c.at - 0.5 - margin : v > c.at + 0.5 + margin) d += c.amount; });
      return d;
    }
    var margin = Math.min(16, state.nodesep * 0.4);
    // A node moves by the shift at its leading edge, so it never straddles a band.
    var moved = new Map();
    nodes.forEach(function (n) { moved.set(n.name, shift(n[B] - n[S] / 2, 0)); });
    nodes.forEach(function (n) { n[B] += moved.get(n.name); });
    edges.forEach(function (e) {
      var last = e.points.length - 1;
      e.points.forEach(function (p, i) {
        // Endpoints stay attached to their nodes.
        if (i === 0) p[B] += moved.get(e.source);
        else if (i === last) p[B] += moved.get(e.target);
        else p[B] += shift(p[B], margin);
      });
      if (horizontal) e.ly += shift(e.ly, margin); else e.lx += shift(e.lx, margin);
    });
  }

  // ---------------------------------------------------------------- render
  // Edges in the default grey follow the theme (--fg-edge-default); other edge
  // colours are data and stay as given. Set as style, since var() is not valid
  // in presentation attributes.
  var DEFAULT_EDGE_COLOR = '#8c8c8c';
  function paint(color) {
    return String(color).toLowerCase() === DEFAULT_EDGE_COLOR ? 'var(--fg-edge-default)' : color;
  }

  var colorIds = new Map();
  function markerFor(color) {
    if (!colorIds.has(color)) {
      var id = 'fg-arrow-' + colorIds.size;
      colorIds.set(color, id);
      defs.append('marker')
        .attr('id', id).attr('viewBox', '0 0 10 10').attr('refX', 9).attr('refY', 5)
        .attr('markerWidth', 9).attr('markerHeight', 9).attr('markerUnits', 'userSpaceOnUse')
        .attr('orient', 'auto-start-reverse')
        .append('path').attr('d', 'M0,0L10,5L0,10Z').style('fill', paint(color));
    }
    return 'url(#' + colorIds.get(color) + ')';
  }

  function edgePath(e) {
    if (state.curve === 'smooth' && state.layout === 'elk') return roundedPath(e.points, 10);
    var curve = state.curve === 'smooth' ? d3.curveBasis : d3.curveLinear;
    return d3.line().x(function (p) { return p.x; }).y(function (p) { return p.y; }).curve(curve)(e.points);
  }

  // Polyline with rounded corners: keeps ELK's orthogonal routing readable.
  function roundedPath(pts, radius) {
    if (pts.length < 3) return 'M' + pts.map(function (p) { return p.x + ',' + p.y; }).join('L');
    var d = 'M' + pts[0].x + ',' + pts[0].y;
    for (var i = 1; i < pts.length - 1; i++) {
      var a = pts[i - 1], b = pts[i], c = pts[i + 1];
      var l1 = Math.hypot(b.x - a.x, b.y - a.y), l2 = Math.hypot(c.x - b.x, c.y - b.y);
      var r = Math.min(radius, l1 / 2, l2 / 2);
      if (r < 0.5) { d += 'L' + b.x + ',' + b.y; continue; }
      var p1 = { x: b.x + (a.x - b.x) * r / l1, y: b.y + (a.y - b.y) * r / l1 };
      var p2 = { x: b.x + (c.x - b.x) * r / l2, y: b.y + (c.y - b.y) * r / l2 };
      d += 'L' + p1.x + ',' + p1.y + 'Q' + b.x + ',' + b.y + ' ' + p2.x + ',' + p2.y;
    }
    var last = pts[pts.length - 1];
    return d + 'L' + last.x + ',' + last.y;
  }

  function maybe(sel, t) { return t ? sel.transition(t) : sel; }

  function render(animated) {
    var t = animated ? d3.transition().duration(450).ease(d3.easeCubicInOut) : null;
    var lh = lineHeight(), fs = state.fontsize, lfs = edgeFont(), header = groupHeader();


    // Groups (outer first so nested groups paint on top).
    var gdata = state.showGroups ? usedGroups.slice().sort(function (a, b) { return a.depth - b.depth; }) : [];
    var gsel = gGroups.selectAll('g.fg-group').data(gdata, function (d) { return d.name; });
    gsel.exit().remove();
    var genter = gsel.enter().append('g').attr('class', 'fg-group');
    genter.append('rect').attr('class', 'fg-group-box').attr('rx', 10);
    genter.append('text').attr('class', 'fg-group-label');
    genter.on('click', function (ev, d) { ev.stopPropagation(); togglePin({ type: 'group', id: d.name }); });
    var gall = genter.merge(gsel).style('--c', function (d) { return d.color; });
    gall.order();
    maybe(gall.select('rect'), t)
      .attr('x', function (d) { return d.box.x; }).attr('y', function (d) { return d.box.y; })
      .attr('width', function (d) { return d.box.w; }).attr('height', function (d) { return d.box.h; });
    maybe(gall.select('text'), t)
      .attr('x', function (d) { return d.box.x + 12; })
      .attr('y', function (d) { return d.box.y + header * 0.5 + 4; })
      .style('font-size', (fs - 1) + 'px');
    gall.select('text').text(function (d) { return d.label; });

    // Edges.
    var esel = gEdges.selectAll('g.fg-edge-g').data(edges, function (d) { return d.id; });
    esel.exit().remove();
    var eenter = esel.enter().append('g').attr('class', 'fg-edge-g');
    eenter.append('path').attr('class', 'fg-edge-hit');
    eenter.append('path').attr('class', function (d) { return 'fg-edge style-' + d.style; })
      .attr('id', function (d) { return 'fg-path-' + d.idx; })
      .style('stroke', function (d) { return paint(d.color); })
      .attr('stroke-width', function (d) { return d.width; })
      .attr('marker-end', function (d) { return markerFor(d.color); });
    eenter.append('path').attr('class', 'fg-edge-flow')
      .style('stroke', function (d) { return paint(d.color); })
      .attr('stroke-width', function (d) { return d.width + 1.5; });
    eenter
      .on('mouseenter', function (ev, d) { highlight({ type: 'edge', id: d.idx }); showEdgeTooltip(ev, d); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, d) { ev.stopPropagation(); togglePin({ type: 'edge', id: d.idx }); });
    var eall = eenter.merge(esel);
    eall.select('path.fg-edge-hit').attr('d', edgePath);
    maybe(eall.select('path.fg-edge'), t).attr('d', edgePath);
    maybe(eall.select('path.fg-edge-flow'), t).attr('d', edgePath);
    eall.select('path.fg-edge-comet').attr('d', edgePath);
    // Re-apply length-dependent animations once transitions have settled.
    if (t) t.on('end.anim', function () { applyAnimations(eall); }); else applyAnimations(eall);

    // Edge labels.
    var ldata = state.showEdgeLabels ? edges.filter(function (e) { return e.label; }) : [];
    var lsel = gLabels.selectAll('g.fg-edge-label').data(ldata, function (d) { return d.id; });
    lsel.exit().remove();
    var lenter = lsel.enter().append('g').attr('class', 'fg-edge-label')
      .attr('transform', function (d) { return 'translate(' + d.lx + ',' + d.ly + ')'; });
    lenter.append('rect').attr('rx', 4);
    lenter.append('text').attr('text-anchor', 'middle').attr('dominant-baseline', 'central');
    var lall = lenter.merge(lsel);
    lall.select('text').style('font-size', lfs + 'px').text(function (d) { return d.label; });
    lall.select('rect')
      .attr('x', function (d) { return -d.lw / 2; }).attr('y', function (d) { return -d.lh / 2; })
      .attr('width', function (d) { return d.lw; }).attr('height', function (d) { return d.lh; });
    maybe(lall, t).attr('transform', function (d) { return 'translate(' + d.lx + ',' + d.ly + ')'; });

    // Nodes.
    var nsel = gNodes.selectAll('g.fg-node').data(nodes, function (d) { return d.name; });
    nsel.exit().remove();
    var nenter = nsel.enter().append('g')
      .attr('class', function (d) { return 'fg-node shape-' + d.shape + (isPseudo(d) ? ' fg-pseudo' : ''); })
      .attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });
    nenter.append('path').attr('class', 'fg-shape');
    nenter.append('text').attr('class', 'fg-label').attr('text-anchor', 'middle');
    nenter
      .on('mouseenter', function (ev, d) { highlight({ type: 'node', id: d.name }); showNodeTooltip(ev, d); })
      .on('mousemove', moveTooltip)
      .on('mouseleave', function () { hideTooltip(); restoreHighlight(); })
      .on('click', function (ev, d) { ev.stopPropagation(); togglePin({ type: 'node', id: d.name }); });
    if (state.draggable) nenter.call(drag).classed('fg-draggable', true);
    var nall = nenter.merge(nsel).style('--c', function (d) { return d.color; });
    nall.select('path.fg-shape').attr('d', shapePath);
    nall.select('text.fg-label').each(function (d) {
      var text = d3.select(this).style('font-size', fs + 'px');
      var y0 = -(d.lines.length - 1) / 2 * lh + labelOffset(d);
      var spans = text.selectAll('tspan').data(d.lines);
      spans.exit().remove();
      spans.enter().append('tspan').merge(spans)
        .attr('x', 0).attr('y', function (l, i) { return y0 + i * lh; })
        .attr('dominant-baseline', 'central')
        .text(function (l) { return l; });
    });
    maybe(nall, t).attr('transform', function (d) { return 'translate(' + d.x + ',' + d.y + ')'; });

    restoreHighlight();
  }

  // ---------------------------------------------------------------- animation
  // Per edge: its own 'animation' or the chart-wide style. 'pulse' and 'dash'
  // are pure CSS; 'dots' (tokens riding the path via SMIL animateMotion) and
  // 'comet' (a bright segment, Web Animations API) depend on the path length
  // and are rebuilt only when that changes noticeably.
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function effectiveAnimation(e) {
    if (!state.animate || reduceMotion) return 'none';
    return e.animation || state.animation;
  }

  function applyAnimations(sel) {
    sel.each(function (e) {
      var g = this, anim = effectiveAnimation(e);
      g.setAttribute('data-anim', anim);
      var path = g.querySelector('path.fg-edge');
      var len = path && path.getTotalLength ? path.getTotalLength() : 0;
      var changed = !e._animLen || Math.abs(len - e._animLen) / Math.max(1, e._animLen) > 0.15;

      var dots = g.querySelector('g.fg-edge-dots');
      if (anim !== 'dots' && dots) { dots.remove(); dots = null; }
      if (anim === 'dots' && (!dots || changed)) {
        if (dots) dots.remove();
        dots = document.createElementNS(SVG_NS, 'g');
        dots.setAttribute('class', 'fg-edge-dots');
        var n = Math.max(1, Math.min(4, Math.round(len / 180))), dur = Math.max(1.2, len / 90);
        for (var i = 0; i < n; i++) {
          var c = document.createElementNS(SVG_NS, 'circle');
          c.setAttribute('r', Math.max(2.5, e.width + 1));
          c.style.fill = paint(e.color);
          var m = document.createElementNS(SVG_NS, 'animateMotion');
          m.setAttribute('dur', dur.toFixed(2) + 's');
          m.setAttribute('repeatCount', 'indefinite');
          m.setAttribute('begin', (-i * dur / n).toFixed(2) + 's');
          var mp = document.createElementNS(SVG_NS, 'mpath');
          mp.setAttribute('href', '#fg-path-' + e.idx);
          m.appendChild(mp); c.appendChild(m); dots.appendChild(c);
        }
        g.appendChild(dots);
      }

      var comet = g.querySelector('path.fg-edge-comet');
      if (anim !== 'comet' && comet) { comet.remove(); comet = null; }
      if (anim === 'comet') {
        if (!comet) {
          comet = document.createElementNS(SVG_NS, 'path');
          comet.setAttribute('class', 'fg-edge-comet');
          comet.style.stroke = paint(e.color);
          comet.setAttribute('stroke-width', e.width + 2);
          comet.setAttribute('d', path.getAttribute('d'));
          g.appendChild(comet);
          changed = true;
        }
        if (changed && comet.animate) {
          var seg = Math.max(18, Math.min(70, len * 0.25));
          comet.style.strokeDasharray = seg + ' ' + (len + seg);
          if (comet._anim) comet._anim.cancel();
          comet._anim = comet.animate([{ strokeDashoffset: seg }, { strokeDashoffset: -len }],
            { duration: Math.max(1000, len / 0.12), iterations: Infinity, easing: 'ease-in-out' });
        }
      }
      e._animLen = len;
    });
  }

  function refreshAnimations() { applyAnimations(gEdges.selectAll('g.fg-edge-g')); }

  // ---------------------------------------------------------------- trace
  // A finite, reader-started walk through the graph in flow order, starting
  // at the pinned node or at every node without incoming edges. Each step
  // draws its edges in and lights up the nodes it reaches.
  var trace = { running: false, timer: null, edges: new Set() };

  function traceSteps() {
    var starts;
    if (state.pinned && state.pinned.type === 'node') starts = [state.pinned.id];
    else {
      starts = nodes.filter(function (n) {
        return !(inEdges.get(n.name) || []).some(function (e) { return e.source !== e.target; });
      }).map(function (n) { return n.name; });
      if (!starts.length) starts = [nodes[0].name];
    }
    var steps = [{ nodes: starts.slice(), edges: [] }], seen = new Set(starts), used = new Set(), frontier = starts;
    while (frontier.length) {
      var next = [], stepEdges = [];
      frontier.forEach(function (name) {
        (outEdges.get(name) || []).forEach(function (e) {
          if (used.has(e.idx)) return;
          used.add(e.idx); stepEdges.push(e);
          if (!seen.has(e.target)) { seen.add(e.target); next.push(e.target); }
        });
      });
      if (!stepEdges.length) break;
      steps.push({ nodes: next, edges: stepEdges });
      frontier = next;
    }
    return steps;
  }

  function setTraceButtons(running) {
    if (DATA.steps) return;  // the buttons open the captioned walkthrough instead
    ['traceButton', 'traceButton2'].forEach(function (id) {
      var b = document.getElementById(id);
      if (!b) return;
      b.textContent = running ? '■ Stop' : '▶ Trace';
      b.classList.toggle('active', running);
    });
  }

  function stopTrace() {
    trace.running = false;
    clearTimeout(trace.timer);
    trace.edges = new Set();
    svg.classed('fg-tracing', false);
    svg.selectAll('.fg-traced').classed('fg-traced', false);
    setTraceButtons(false);
  }

  function playTrace() {
    if (trace.running) { stopTrace(); return; }
    var steps = traceSteps(), i = 0, stepMs = reduceMotion ? 0 : 750;
    trace.running = true;
    setTraceButtons(true);
    svg.classed('fg-tracing', true);
    (function step() {
      if (!trace.running) return;
      if (i >= steps.length) { trace.timer = setTimeout(stopTrace, reduceMotion ? 4000 : 2500); return; }
      var st = steps[i++], names = new Set(st.nodes);
      gNodes.selectAll('g.fg-node').filter(function (d) { return names.has(d.name); }).classed('fg-traced', true);
      st.edges.forEach(function (e) { trace.edges.add(e.idx); });
      gLabels.selectAll('g.fg-edge-label').classed('fg-traced', function (d) { return trace.edges.has(d.idx); });
      gEdges.selectAll('g.fg-edge-g').filter(function (d) { return st.edges.indexOf(d) >= 0; })
        .classed('fg-traced', true)
        .each(function () {
          var path = this.querySelector('path.fg-edge');
          if (reduceMotion || !path.animate) return;
          var len = path.getTotalLength();
          path.animate([{ strokeDasharray: len + ' ' + len, strokeDashoffset: len },
                        { strokeDasharray: len + ' ' + len, strokeDashoffset: 0 }],
                       { duration: stepMs * 0.9, easing: 'ease-out' });
        });
      if (reduceMotion) step(); else trace.timer = setTimeout(step, stepMs);
    })();
  }

  // ---------------------------------------------------------------- highlight
  function walk(start, map, key, ns, es) {
    var queue = [start], seen = new Set([start]);
    while (queue.length) {
      var cur = queue.shift();
      (map.get(cur) || []).forEach(function (e) {
        es.add(e.idx);
        var next = e[key];
        ns.add(next);
        if (!seen.has(next)) { seen.add(next); queue.push(next); }
      });
    }
  }

  function groupMembers(name) {
    var inside = new Set([name]);
    var changed = true;
    while (changed) {
      changed = false;
      usedGroups.forEach(function (g) {
        if (g.parent && inside.has(g.parent) && !inside.has(g.name)) { inside.add(g.name); changed = true; }
      });
    }
    return new Set(nodes.filter(function (n) { return n.group && inside.has(n.group); }).map(function (n) { return n.name; }));
  }

  function highlight(target) {
    if (!target) { clearHighlight(); return; }
    var ns = new Set(), es = new Set(), focusNode = null, focusGroup = null;
    if (target.type === 'node') {
      // Everything upstream and downstream of the node.
      ns.add(target.id); focusNode = target.id;
      walk(target.id, outEdges, 'target', ns, es);
      walk(target.id, inEdges, 'source', ns, es);
    } else if (target.type === 'group') {
      // Group members plus their direct connections.
      focusGroup = target.id;
      var members = groupMembers(target.id);
      members.forEach(function (m) { ns.add(m); });
      edges.forEach(function (e) {
        if (members.has(e.source) || members.has(e.target)) { es.add(e.idx); ns.add(e.source); ns.add(e.target); }
      });
    } else if (target.type === 'variant') {
      edges.forEach(function (e) {
        if (e.variant === target.id) { es.add(e.idx); ns.add(e.source); ns.add(e.target); }
      });
    } else if (target.type === 'edge') {
      var e = edges[target.id];
      es.add(e.idx); ns.add(e.source); ns.add(e.target);
    } else if (target.type === 'step') {
      target.nodes.forEach(function (n) { ns.add(n); });
      target.edges.forEach(function (e) { es.add(e.idx); ns.add(e.source); ns.add(e.target); });
    }
    svg.classed('fg-has-highlight', true);
    gNodes.selectAll('g.fg-node')
      .classed('fg-hl', function (d) { return ns.has(d.name); })
      .classed('fg-focus', function (d) { return d.name === focusNode; });
    gEdges.selectAll('g.fg-edge-g').classed('fg-hl', function (d) { return es.has(d.idx); });
    gLabels.selectAll('g.fg-edge-label').classed('fg-hl', function (d) { return es.has(d.idx); });
    gGroups.selectAll('g.fg-group').classed('fg-focus', function (d) { return d.name === focusGroup; });
  }

  function clearHighlight() {
    svg.classed('fg-has-highlight', false);
    svg.selectAll('.fg-hl').classed('fg-hl', false);
    svg.selectAll('.fg-focus').classed('fg-focus', false);
  }

  // While the walkthrough is open, its step owns the highlight.
  function restoreHighlight() { highlight(walkTarget || state.pinned); }

  function samePin(a, b) { return a && b && a.type === b.type && a.id === b.id; }
  function togglePin(target) {
    state.pinned = samePin(state.pinned, target) ? null : target;
    restoreHighlight();
  }
  function unpin() { state.pinned = null; clearHighlight(); }

  // ---------------------------------------------------------------- tooltip
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function showNodeTooltip(ev, d) {
    var parts = ['<div class="fg-tt-title">' + escapeHtml(d.label.replace(/\n/g, ' ')) + '</div>'];
    // An explicit tooltip may contain HTML (as in other d3blocks charts); the label is always escaped.
    if (d.tooltip) parts.push('<div>' + d.tooltip + '</div>');
    var meta = [d.shape];
    if (d.group && groupById.has(d.group)) meta.push(escapeHtml(groupById.get(d.group).label));
    meta.push((inEdges.get(d.name) || []).length + ' in · ' + (outEdges.get(d.name) || []).length + ' out');
    parts.push('<div class="fg-tt-meta">' + meta.join(' · ') + '</div>');
    tooltip.html(parts.join('')).classed('open', true);
    moveTooltip(ev);
  }
  function showEdgeTooltip(ev, d) {
    var s = nodeById.get(d.source), t = nodeById.get(d.target);
    var html = '<div class="fg-tt-title">' + escapeHtml(s.label.replace(/\n/g, ' ')) + ' → ' + escapeHtml(t.label.replace(/\n/g, ' ')) + '</div>';
    if (d.label) html += '<div>' + escapeHtml(d.label) + '</div>';
    tooltip.html(html).classed('open', true);
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
    return { top: top, left: left, right: 16, bottom: 16 + (walkthrough ? walkthrough.height() : 0) };
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
    var tr = d3.zoomIdentity.translate(tx, ty).scale(k);
    (animated ? svg.transition().duration(500) : svg).call(zoom.transform, tr);
  }

  function focusOn(n) {
    var rect = svg.node().getBoundingClientRect();
    var k = Math.max(d3.zoomTransform(svg.node()).k, 1);
    var tr = d3.zoomIdentity.translate(rect.width / 2 - n.x * k, rect.height / 2 - n.y * k).scale(k);
    svg.transition().duration(500).call(zoom.transform, tr);
  }

  function relayout() {
    return computeLayout().then(function (fresh) {
      if (!fresh) return;
      render(true);
      setTimeout(function () { fit(true, walkTarget ? stepBounds(walkTarget) : null); }, 60);
    });
  }

  // ---------------------------------------------------------------- drag
  // Dragging moves a node; its edges are re-routed as an S-bend (or an
  // orthogonal Z with ELK) along the flow axis and enclosing groups grow to
  // keep containing it. "Reset layout" recomputes everything.
  function routeBetween(s, t) {
    var horizontal = state.direction === 'LR' || state.direction === 'RL';
    var BIG = 1e5, p0, p1, mid;
    if (horizontal) {
      var sx = (t.x >= s.x) ? 1 : -1;
      p0 = intersect(s, { x: s.x + sx * BIG, y: s.y });
      p1 = intersect(t, { x: t.x - sx * BIG, y: t.y });
      mid = (p0.x + p1.x) / 2;
      return [p0, { x: mid, y: p0.y }, { x: mid, y: p1.y }, p1];
    }
    var sy = (t.y >= s.y) ? 1 : -1;
    p0 = intersect(s, { x: s.x, y: s.y + sy * BIG });
    p1 = intersect(t, { x: t.x, y: t.y - sy * BIG });
    mid = (p0.y + p1.y) / 2;
    return [p0, { x: p0.x, y: mid }, { x: p1.x, y: mid }, p1];
  }

  function rerouteAround(n) {
    edges.forEach(function (e) {
      if (e.source !== n.name && e.target !== n.name) return;
      var s = nodeById.get(e.source), t = nodeById.get(e.target);
      if (s === t) {
        var dx = n.x - e._anchor.x, dy = n.y - e._anchor.y;
        e.points = e._loop.map(function (p) { return { x: p.x + dx, y: p.y + dy }; });
      } else {
        e.points = routeBetween(s, t);
      }
      var a = e.points[1], b = e.points[e.points.length - 2];
      e.lx = (a.x + b.x) / 2; e.ly = (a.y + b.y) / 2;
    });
  }

  function ancestorsOf(n) {
    var out = [], g = n.group;
    while (g && groupById.has(g)) { out.push(groupById.get(g)); g = groupById.get(g).parent; }
    return out;
  }

  var dragFrame = null;
  var drag = d3.drag()
    .clickDistance(4)
    .on('start', function (ev, d) {
      hideTooltip();
      // Remember self-loops relative to the node so they move with it.
      edges.forEach(function (e) {
        if (e.source === d.name && e.target === d.name) {
          e._anchor = { x: d.x, y: d.y };
          e._loop = e.points.map(function (p) { return { x: p.x, y: p.y }; });
        }
      });
      svg.classed('fg-dragging', true);
    })
    .on('drag', function (ev, d) {
      d.x = ev.x; d.y = ev.y;
      rerouteAround(d);
      // Groups only grow while dragging, so dropping a node elsewhere never
      // shrinks a box onto its other members.
      ancestorsOf(d).forEach(function (gr) {
        var old = gr.box;
        groupBoxes([gr]);
        if (old) {
          var x0 = Math.min(old.x, gr.box.x), y0 = Math.min(old.y, gr.box.y);
          var x1 = Math.max(old.x + old.w, gr.box.x + gr.box.w), y1 = Math.max(old.y + old.h, gr.box.y + gr.box.h);
          gr.box = { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
        }
      });
      if (!dragFrame) dragFrame = requestAnimationFrame(function () { dragFrame = null; render(false); });
    })
    .on('end', function () {
      svg.classed('fg-dragging', false);
      computeBounds();
    });

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
    clone.querySelector('.fg-viewport').removeAttribute('transform');
    clone.querySelectorAll('.fg-edge-hit, .fg-edge-flow, .fg-edge-dots, .fg-edge-comet').forEach(function (el) { el.remove(); });
    var pad = 24, x = bounds.x - pad, y = bounds.y - pad, w = bounds.w + 2 * pad, h = bounds.h + 2 * pad;
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('viewBox', [x, y, w, h].join(' '));
    clone.setAttribute('width', w);
    clone.setAttribute('height', h);
    clone.removeAttribute('class');
    var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', x); bg.setAttribute('y', y); bg.setAttribute('width', w); bg.setAttribute('height', h);
    bg.setAttribute('fill', window.getComputedStyle(document.body).backgroundColor);
    clone.insertBefore(bg, clone.querySelector('.fg-viewport'));
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

  function fileStem() { return (OPTS.title || 'flowgraph').replace(/[^\w.-]+/g, '_'); }

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
      nodes: nodes.map(function (n) {
        return { name: n.name, label: n.label, shape: n.shape, group: n.group, color: n.color,
          x: n.x, y: n.y, width: n.width, height: n.height };
      }),
      edges: edges.map(function (e) {
        return { source: e.source, target: e.target, label: e.label, style: e.style, color: e.color, points: e.points };
      }),
      groups: usedGroups.map(function (g) {
        return { name: g.name, label: g.label, parent: g.parent, color: g.color, box: g.box };
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
  on('resetButton', 'click', function () { relayout(); });

  document.querySelectorAll('[data-direction]').forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.direction === state.direction);
    btn.addEventListener('click', function () {
      state.direction = btn.dataset.direction;
      document.querySelectorAll('[data-direction]').forEach(function (b) {
        b.classList.toggle('active', b === btn);
      });
      relayout();
    });
  });

  document.querySelectorAll('[data-curve]').forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.curve === state.curve);
    btn.addEventListener('click', function () {
      state.curve = btn.dataset.curve;
      document.querySelectorAll('[data-curve]').forEach(function (b) { b.classList.toggle('active', b === btn); });
      render(true);
    });
  });

  function slider(id, valId, key, suffix, needsLayout) {
    var el = document.getElementById(id), val = document.getElementById(valId), timer = null;
    if (!el) return;
    el.value = state[key];
    if (val) val.textContent = state[key] + suffix;
    el.addEventListener('input', function () {
      state[key] = +el.value;
      if (val) val.textContent = state[key] + suffix;
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (needsLayout) computeLayout().then(function (fresh) { if (fresh) render(false); });
      }, 30);
    });
    el.addEventListener('change', function () { fit(true); });
  }
  slider('nodesepSlider', 'nodesepVal', 'nodesep', 'px', true);
  slider('ranksepSlider', 'ranksepVal', 'ranksep', 'px', true);
  slider('fontSizeSlider', 'fontSizeVal', 'fontsize', 'px', true);

  function checkbox(id, key, needsLayout) {
    var el = document.getElementById(id);
    if (!el) return;
    el.checked = !!state[key];
    el.addEventListener('change', function () {
      state[key] = el.checked;
      if (needsLayout) relayout(); else render(false);
    });
  }
  // "Per edge" only makes sense when some edges carry their own animation.
  if (!edges.some(function (e) { return e.animation; })) {
    document.querySelectorAll('[data-animation="none"]').forEach(function (b) { b.style.display = 'none'; });
  }
  document.querySelectorAll('[data-animation]').forEach(function (btn) {
    function sync() {
      document.querySelectorAll('[data-animation]').forEach(function (b) {
        b.classList.toggle('active', b.dataset.animation === (state.animate ? state.animation : 'off'));
      });
    }
    sync();
    btn.addEventListener('click', function () {
      var v = btn.dataset.animation;
      state.animate = v !== 'off';
      if (v !== 'off') state.animation = v;
      sync();
      refreshAnimations();
    });
  });
  // Captioned walkthrough (steps) replaces the uncaptioned trace on the same buttons.
  var walkthrough = null, walkTarget = null;
  if (DATA.steps) {
    var edgesByPair = new Map();
    edges.forEach(function (e) {
      var key = e.source + '\u0000' + e.target;
      if (!edgesByPair.has(key)) edgesByPair.set(key, []);
      edgesByPair.get(key).push(e);
    });
    ['traceButton', 'traceButton2'].forEach(function (id) {
      var b = document.getElementById(id);
      if (!b) return;
      if (!DATA.steps.length) { b.style.display = 'none'; return; }
      b.textContent = '▶ Walk through';
      b.title = 'Step through the diagram with a caption per step';
    });
    walkthrough = D3BlocksWalkthrough({
      steps: DATA.steps,
      triggers: ['traceButton', 'traceButton2'],
      onOpen: function () { stopTrace(); hideTooltip(); },
      onStep: function (st) {
        var hl = st.highlight || {};
        var stepNodes = hl.nodes || [], stepEdges = [];
        (hl.edges || []).forEach(function (p) {
          stepEdges = stepEdges.concat(edgesByPair.get(p[0] + '\u0000' + p[1]) || []);
        });
        walkTarget = (stepNodes.length || stepEdges.length) ? { type: 'step', nodes: stepNodes, edges: stepEdges } : null;
        restoreHighlight();
        fit(true, walkTarget ? stepBounds(walkTarget) : null);
      },
      onClose: function () { walkTarget = null; restoreHighlight(); fit(true); }
    });
  } else {
    on('traceButton', 'click', playTrace);
    on('traceButton2', 'click', playTrace);
  }

  // Box around a step's nodes and edges, padded so the camera keeps some context.
  function stepBounds(target) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    function grow(x, y) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    var names = new Set(target.nodes);
    target.edges.forEach(function (e) {
      names.add(e.source); names.add(e.target);
      e.points.forEach(function (p) { grow(p.x, p.y); });
    });
    names.forEach(function (name) {
      var n = nodeById.get(name);
      if (n) { grow(n.x - n.width / 2, n.y - n.height / 2); grow(n.x + n.width / 2, n.y + n.height / 2); }
    });
    if (!isFinite(x0)) return null;
    var pad = 60;
    return { x: x0 - pad, y: y0 - pad, w: x1 - x0 + 2 * pad, h: y1 - y0 + 2 * pad };
  }
  checkbox('edgeLabelToggle', 'showEdgeLabels', true);
  checkbox('groupToggle', 'showGroups', true);
  if (!usedGroups.length) {
    var gt = document.getElementById('groupToggleRow');
    if (gt) gt.style.display = 'none';
  }
  if (!edges.some(function (e) { return e.label; })) {
    var lt = document.getElementById('edgeLabelToggleRow');
    if (lt) lt.style.display = 'none';
  }

  // Legend: groups, plus edge variants that are actually used (as archify does).
  (function buildLegend() {
    var panel = document.getElementById('legendPanel');
    var list = document.getElementById('legendList');
    if (!panel || !list) return;
    var variants = [];
    edges.forEach(function (e) {
      if (e.variant && variants.indexOf(e.variant) < 0) variants.push(e.variant);
    });
    var VARIANT_ORDER = ['emphasis', 'security', 'async', 'error', 'default'];
    variants.sort(function (a, b) { return VARIANT_ORDER.indexOf(a) - VARIANT_ORDER.indexOf(b); });
    var showVariants = variants.length > 1 || (variants.length === 1 && variants[0] !== 'default');
    if (!usedGroups.length && !showVariants) { panel.style.display = 'none'; return; }

    function section(title) {
      var h = document.createElement('div');
      h.className = 'fg-section-label';
      h.textContent = title;
      list.appendChild(h);
    }
    function row(html, target, indent) {
      var r = document.createElement('div');
      r.className = 'fg-legend-item';
      r.style.paddingLeft = (indent || 0) + 'px';
      r.innerHTML = html;
      r.addEventListener('mouseenter', function () { highlight(target); });
      r.addEventListener('mouseleave', restoreHighlight);
      r.addEventListener('click', function () { togglePin(target); });
      list.appendChild(r);
    }
    if (usedGroups.length) {
      section('Groups');
      usedGroups.slice().sort(function (a, b) { return a.depth - b.depth || a.label.localeCompare(b.label); })
        .forEach(function (g) {
          row('<span class="fg-swatch" style="background:' + escapeHtml(g.color) + '"></span>' + escapeHtml(g.label),
              { type: 'group', id: g.name }, g.depth * 12);
        });
    }
    if (showVariants) {
      section('Edges');
      variants.forEach(function (v) {
        var e = edges.find(function (x) { return x.variant === v; });
        var dash = e.style === 'dashed' ? '5 3' : e.style === 'dotted' ? '1.5 3' : 'none';
        var swatch = '<svg class="fg-line-swatch" viewBox="0 0 26 10"><line x1="1" y1="5" x2="25" y2="5" style="stroke:' +
          escapeHtml(paint(e.color)) + '" stroke-width="' + Math.min(4, e.width) + '" stroke-dasharray="' + dash + '" stroke-linecap="round"/></svg>';
        var n = edges.filter(function (x) { return x.variant === v; }).length;
        row(swatch + escapeHtml(v) + ' <span class="fg-legend-count">' + n + '</span>', { type: 'variant', id: v });
      });
    }
  })();

  // Theme (theme.js: runtime toggle, and dark_mode='auto' follows the OS until toggled).
  D3BlocksTheme.bind('themeBtn');

  // Search.
  (function setupSearch() {
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');
    if (!input || !results) return;
    function close() { results.classList.remove('open'); results.innerHTML = ''; }
    function select(n) {
      state.pinned = { type: 'node', id: n.name };
      restoreHighlight();
      focusOn(n);
      close();
      input.blur();
    }
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      if (!q) { close(); return; }
      var hits = nodes.filter(function (n) {
        return n.label.toLowerCase().indexOf(q) >= 0 || n.name.toLowerCase().indexOf(q) >= 0;
      }).slice(0, 30);
      results.innerHTML = hits.length ? '' : '<div class="search-item" style="opacity:0.6">No matches</div>';
      hits.forEach(function (n) {
        var item = document.createElement('div');
        item.className = 'search-item';
        item.textContent = n.label.replace(/\n/g, ' ');
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

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.activeElement.tagName !== 'INPUT') { stopTrace(); unpin(); }
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
  if (!nodes.length) {
    d3.select('#fg-main').append('div').attr('class', 'fg-empty').text('No nodes to draw.');
    return;
  }
  var ready = computeLayout().then(function () {
    render(false);
    fit(false);
  }).catch(function (err) {
    d3.select('#fg-main').append('div').attr('class', 'fg-empty').text('Layout failed: ' + err);
    throw err;
  });

  window.__flowgraph = { state: state, nodes: nodes, edges: edges, groups: usedGroups, relayout: relayout, fit: fit, ready: ready, walkthrough: walkthrough };
})();
