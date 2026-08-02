// =========================================================================
// GraphModel - pure graph data + traversal. No DOM, no d3-force, no notion
// of "depth" or "children" stored anywhere - both are computed on demand.
//
// Real graphs (social networks included) are not trees: a node can be
// reachable through more than one already-visible neighbor. Expand/collapse
// is therefore "frontier expansion", not tree pruning:
//   - `expanded` is the set of nodes whose neighbors the user has chosen
//     to reveal (root starts expanded).
//   - the visible set is BFS from root, only stepping through expanded
//     nodes - so a node stays visible as long as ANY expanded neighbor of
//     its still leads to it, even if you collapse a different one.
// =========================================================================
class GraphModel {
  constructor({ nodes, edges, rootId }) {
    this.nodesById = new Map(nodes.map((n) => [n.id, n]));
    // Directed edges: source → target means "source follows target"
    this.edges = edges; // {id, source, target, ...}
    this.rootId = rootId;
    // Undirected adjacency for expansion / BFS (behavior unchanged)
    this.adjacency = new Map(nodes.map((n) => [n.id, new Set()]));
    this.outAdj = new Map(nodes.map((n) => [n.id, new Set()]));
    edges.forEach((e) => {
      this.adjacency.get(e.source).add(e.target);
      this.adjacency.get(e.target).add(e.source);
      this.outAdj.get(e.source).add(e.target);
    });
    this.expanded = new Set([rootId]);
  }

  neighbors(id) {
    return Array.from(this.adjacency.get(id) || []);
  }
  follows(a, b) {
    return (this.outAdj.get(a) || new Set()).has(b);
  }

  toggle(id) {
    if (this.expanded.has(id)) this.expanded.delete(id);
    else this.expanded.add(id);
  }

  // BFS from root, stepping only through expanded nodes. Returns the
  // reachable id set, each node's hop-distance from root, and a "parentOf"
  // map recording which already-visible node first revealed each node -
  // used purely as a seeding/animation reference (§ LayoutEngine), not as
  // a structural assumption about the graph.
  _computeReachable() {
    const depths = new Map([[this.rootId, 0]]);
    const parentOf = new Map();
    const visibleIds = new Set([this.rootId]);
    const queue = [this.rootId];
    while (queue.length) {
      const id = queue.shift();
      if (!this.expanded.has(id)) continue;
      for (const nb of this.neighbors(id)) {
        if (!visibleIds.has(nb)) {
          visibleIds.add(nb);
          depths.set(nb, depths.get(id) + 1);
          parentOf.set(nb, id);
          queue.push(nb);
        }
      }
    }
    return { visibleIds, depths, parentOf };
  }

  hasHiddenNeighbors(id) {
    const { visibleIds } = this._computeReachable();
    return this.neighbors(id).some((nb) => !visibleIds.has(nb));
  }

  // The specific hidden neighbor ids of a node - what the ghost preview
  // needs to know what to draw, vs. hasHiddenNeighbors' plain yes/no.
  hiddenNeighbors(id) {
    const { visibleIds } = this._computeReachable();
    return this.neighbors(id).filter((nb) => !visibleIds.has(nb));
  }

  expandAll() {
    this.nodesById.forEach((_, id) => this.expanded.add(id));
  }

  collapseAll() {
    this.expanded = new Set([this.rootId]);
  }

  // Re-root the exploration: new focal node becomes depth 0, expanded set
  // resets to just that node (ego-centric start). Layout/UI must re-seed.
  setRoot(id) {
    if (!this.nodesById.has(id)) return false;
    this.rootId = id;
    this.expanded = new Set([id]);
    return true;
  }

  // Shortest path from root (or fromId) to targetId on the full graph.
  // Returns array of node ids [from, …, target], or null if unreachable.
  pathTo(targetId, fromId = this.rootId) {
    if (!this.nodesById.has(targetId) || !this.nodesById.has(fromId)) return null;
    if (targetId === fromId) return [fromId];
    const parent = new Map();
    const queue = [fromId];
    const visited = new Set([fromId]);
    while (queue.length) {
      const id = queue.shift();
      for (const nb of this.neighbors(id)) {
        if (visited.has(nb)) continue;
        visited.add(nb);
        parent.set(nb, id);
        if (nb === targetId) {
          const path = [targetId];
          let cur = targetId;
          while (parent.has(cur)) {
            cur = parent.get(cur);
            path.push(cur);
          }
          path.reverse();
          return path;
        }
        queue.push(nb);
      }
    }
    return null;
  }

  // Expand every node on the path so target becomes visible via frontier BFS.
  // Expands all nodes except the last (target); expanding the target's
  // predecessors is enough for it to appear.
  revealPath(targetId) {
    const path = this.pathTo(targetId);
    if (!path) return null;
    for (let i = 0; i < path.length - 1; i++) this.expanded.add(path[i]);
    // If target has hidden neighbors we leave it collapsed; it's still visible
    // because a predecessor on the path is expanded.
    return path;
  }

  // BFS layers over the FULL underlying graph starting at startId, ignoring
  // the current expanded/visible state - "what the true hop structure looks
  // like from here", independent of what's currently shown. layers[0] is
  // always [startId]; layers[k] is every node exactly k hops away.
  bfsLayersFrom(startId) {
    const visited = new Set([startId]);
    let frontier = [startId];
    const layers = [frontier];
    while (frontier.length) {
      const next = [];
      frontier.forEach((id) => {
        this.neighbors(id).forEach((nb) => {
          if (!visited.has(nb)) {
            visited.add(nb);
            next.push(nb);
          }
        });
      });
      if (next.length) layers.push(next);
      frontier = next;
    }
    return layers;
  }

  expandNodes(ids) {
    ids.forEach((id) => this.expanded.add(id));
  }

  // The current visible subgraph. Node objects are the SAME persistent
  // references stored in nodesById (mutated in place with a fresh `depth`)
  // so d3-force's x/y/vx/vy continuity survives across calls. Link objects
  // are freshly built every call: d3.forceLink() mutates a link's
  // source/target from an id string into the actual node object the first
  // time it's used, so reusing the same link objects across repeated calls
  // silently breaks any later string-based lookup against them.
  getVisibleGraph() {
    const { visibleIds, depths, parentOf } = this._computeReachable();
    const nodes = [];
    visibleIds.forEach((id) => {
      const n = this.nodesById.get(id);
      n.depth = depths.get(id);
      nodes.push(n);
    });
    // One visual edge per undirected pair; relation = mutual | oneway
    const seen = new Set();
    const links = [];
    this.edges.forEach((e) => {
      if (!visibleIds.has(e.source) || !visibleIds.has(e.target)) return;
      const a = e.source,
        b = e.target;
      const key = a < b ? a + "|" + b : b + "|" + a;
      if (seen.has(key)) return;
      seen.add(key);
      const ab = this.follows(a, b),
        ba = this.follows(b, a);
      let relation, source, target;
      if (ab && ba) {
        relation = "mutual";
        source = a;
        target = b;
      } else if (ab) {
        relation = "oneway";
        source = a;
        target = b;
      } else {
        relation = "oneway";
        source = b;
        target = a;
      }
      links.push({ id: key, source, target, relation });
    });
    return { nodes, links, parentOf, visibleIds };
  }
}

// =========================================================================
// LayoutEngine - owns the d3-force simulation. Knows about physics and
// about seeding/freezing for a clean expand animation; knows nothing about
// SVG or DOM.
// =========================================================================
class LayoutEngine {
  constructor({ ringSpacing = 70, charge = -140, collision = 1, linkDistance = 36, linkStrength = 0.5, radialStrength = 0.85 } = {}) {
    this.ringSpacing = ringSpacing;
    this.radialStrength = radialStrength;
    this.localMode = true;
    // Auto ring spacing: radius per depth ring is derived from how many
    // nodes (and how big they are) occupy that ring, rather than a single
    // flat depth*ringSpacing multiplier - so a crowded ring gets pushed
    // out further automatically instead of overlapping. On by default;
    // this.ringRadii is (re)computed in applyUpdate() every render pass.
    this.useAutoRingSpacing = true;
    this.ringRadii = new Map([[0, 0]]);
    this.simulation = d3
      .forceSimulation()
      .force(
        "link",
        d3
          .forceLink()
          .id((d) => d.id)
          .distance(linkDistance)
          .strength(linkStrength),
      )
      .force("charge", d3.forceManyBody().strength(charge))
      .force(
        "collide",
        d3.forceCollide((d) => d.size + 3),
      );
    this._releaseTimer = null;
  }

  onTick(cb) {
    this.simulation.on("tick", cb);
    return this;
  }

  // Radius per node's depth. Auto mode looks up this.ringRadii (computed
  // from actual ring crowding in the current visible graph); manual mode
  // is the plain depth * ringSpacing multiplier the slider controls.
  _radiusForDepth(depth) {
    if (this.useAutoRingSpacing) {
      const r = this.ringRadii.get(depth);
      if (r != null) return r;
    }
    return depth * this.ringSpacing;
  }

  // How crowded is each ring? Each ring needs enough circumference to fit
  // all its nodes (roughly node-diameter + a small gap) side by side; the
  // radius that gives that circumference is max(what's needed to avoid
  // overlap, the previous ring's radius plus a floor step so rings never
  // collide into each other).
  _computeAutoRingRadii(nodes) {
    const byDepth = new Map();
    nodes.forEach((n) => {
      const d = n.depth ?? 0;
      if (!byDepth.has(d)) byDepth.set(d, []);
      byDepth.get(d).push(n);
    });
    const depths = Array.from(byDepth.keys()).sort((a, b) => a - b);
    const radii = new Map([[0, 0]]);
    // Generous floor between rings + extra per-node gap so auto mode doesn't feel cramped
    const minStep = Math.max(36, this.ringSpacing * 0.55);
    depths.forEach((d) => {
      if (d === 0) return;
      const ringNodes = byDepth.get(d);
      // diameter + comfortable gap between neighbors on the ring
      const neededCircumference = ringNodes.reduce((sum, n) => sum + ((n.size || 6) * 2 + 16), 0);
      const neededRadius = neededCircumference / (2 * Math.PI);
      const prevRadius = radii.get(d - 1) ?? 0;
      radii.set(d, Math.max(prevRadius + minStep, neededRadius));
    });
    return radii;
  }

  setMode(localMode, rootNode) {
    this.localMode = localMode;
    if (localMode) {
      this.simulation.force("center", null);
      this.simulation.force("radial", d3.forceRadial((d) => this._radiusForDepth(d.depth), 0, 0).strength(this.radialStrength));
      rootNode.fx = 0;
      rootNode.fy = 0;
    } else {
      this.simulation.force("radial", null);
      this.simulation.force("center", d3.forceCenter(0, 0));
      rootNode.fx = null;
      rootNode.fy = null;
    }
  }

  // nodes/links/parentOf: this update's getVisibleGraph() result.
  // previousIds: node ids visible before this update.
  applyUpdate({ nodes, links, parentOf, previousIds, rootId, nodeById }) {
    // Freeze everything already on screen, at its current spot - so
    // expanding/collapsing one node's neighbors makes room only in that
    // node's immediate neighborhood (via collision) instead of visibly
    // reshuffling the whole graph.
    nodes.forEach((n) => {
      if (previousIds.has(n.id) && n.id !== rootId) {
        n.fx = n.x;
        n.fy = n.y;
      }
    });

    // Seed brand-new nodes just outside the neighbor that revealed them,
    // continuing outward along that neighbor's OWN angle from the origin
    // (not the entry-neighbor's incoming direction, which - since only
    // radius is constrained by forceRadial - can point anywhere around
    // its ring and isn't reliably "away from center"). This guarantees
    // every seeded position has a strictly larger radius than its entry
    // point, so motion is outward-only, never out-then-back-in. Several
    // new nodes revealed by the same entry point fan out across a small
    // arc instead of stacking on one point (which otherwise leaves their
    // separation direction to forceManyBody's floating-point jitter).
    const newByEntryPoint = new Map();
    nodes.forEach((n) => {
      if (previousIds.has(n.id)) return;
      const srcId = parentOf.get(n.id);
      if (!newByEntryPoint.has(srcId)) newByEntryPoint.set(srcId, []);
      newByEntryPoint.get(srcId).push(n);
    });
    newByEntryPoint.forEach((siblings, srcId) => {
      const src = nodeById.get(srcId);
      if (!src) {
        siblings.forEach((n) => {
          n.x = 0;
          n.y = 0;
          n.vx = 0;
          n.vy = 0;
        });
        return;
      }
      let angle = Math.atan2(src.y, src.x);
      if (!isFinite(angle) || (src.x === 0 && src.y === 0)) angle = Math.random() * 2 * Math.PI;
      const spread = Math.PI / 6;
      const offset = 20;
      siblings.forEach((n, i) => {
        const t = siblings.length > 1 ? i / (siblings.length - 1) - 0.5 : 0;
        const a = angle + t * spread;
        n.x = src.x + Math.cos(a) * offset;
        n.y = src.y + Math.sin(a) * offset;
        n.vx = 0;
        n.vy = 0;
      });
    });

    this.simulation.nodes(nodes);
    this.simulation.force("link").links(links);
    if (this.useAutoRingSpacing) this.ringRadii = this._computeAutoRingRadii(nodes);
    this.setMode(this.localMode, nodeById.get(rootId));
    this.simulation.alpha(0.5).restart();

    clearTimeout(this._releaseTimer);
    this._releaseTimer = setTimeout(() => {
      nodes.forEach((n) => {
        if (n.id !== rootId || !this.localMode) {
          n.fx = null;
          n.fy = null;
        }
      });
      this.simulation.alpha(0.2).restart();
    }, 350);
  }
}

// =========================================================================
// Renderer - owns the SVG/DOM. Draws nodes/links, keyed-joins them across
// updates, and updates positions on every simulation tick. Delegates
// per-node interaction wiring to an injected callback so it doesn't need
// to know about drag/tap/tooltip specifics (Interaction's job).
// =========================================================================
class Renderer {
  constructor({ container, width, height, onEnterNode }) {
    this.onEnterNode = onEnterNode;
    this.svg = d3
      .select(container)
      .append("svg")
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("width", width)
      .attr("height", height);
    const defs = this.svg.append("defs");
    // Soft glow filter used briefly on newly appearing edges
    const glow = defs.append("filter").attr("id", "edge-glow").attr("x", "-80%").attr("y", "-80%").attr("width", "260%").attr("height", "260%");
    glow.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", "2.8").attr("result", "blur");
    const merge = glow.append("feMerge");
    merge.append("feMergeNode").attr("in", "blur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");
    // Stronger yellow glow for flow-diffusion edges
    const flowGlow = defs.append("filter").attr("id", "edge-flow-glow").attr("x", "-120%").attr("y", "-120%").attr("width", "340%").attr("height", "340%");
    flowGlow.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", "4.5").attr("result", "blur");
    const flowMerge = flowGlow.append("feMerge");
    flowMerge.append("feMergeNode").attr("in", "blur");
    flowMerge.append("feMergeNode").attr("in", "blur");
    flowMerge.append("feMergeNode").attr("in", "SourceGraphic");
    // Arrowhead for one-way follows (source → target)
    const marker = defs.append("marker").attr("id", "arrow-oneway").attr("viewBox", "0 -4 8 8").attr("refX", 10).attr("refY", 0).attr("markerWidth", 6).attr("markerHeight", 6).attr("orient", "auto");
    marker.append("path").attr("d", "M0,-3.5L8,0L0,3.5").attr("fill", "#aaa");
    this.g = this.svg.append("g");
    this.linkLayer = this.g.append("g");
    this.nodeLayer = this.g.append("g");
    this.ghostLayer = this.g.append("g");
    this.linkSel = this.linkLayer.selectAll("line");
    this.nodeSel = this.nodeLayer.selectAll("g");
    this.nodeById = new Map();
  }

  resize(width, height) {
    this.svg
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("width", width)
      .attr("height", height);
  }

  render(nodes, links, hasHiddenNeighbors) {
    this.nodeById = new Map(nodes.map((n) => [n.id, n]));

    const linkClass = (d) => "radialgraph-link glow " + (d.relation === "mutual" ? "mutual" : "oneway");
    const finalWidth = (d) => (d.edgeWidth != null ? d.edgeWidth : d.relation === "mutual" ? 2.2 : 1.4);
    const finalOpacity = (d) => (d.edgeOpacity != null ? d.edgeOpacity : d.relation === "mutual" ? 0.7 : 0.5);
    const targetId = (d) => (typeof d.target === "object" ? d.target.id : d.target);
    const strokeColor = (d) => {
      if (d.edgeColor) return d.edgeColor;
      return (this.nodeById.get(targetId(d)) || {}).color || "#888";
    };

    const useFlowGlow = (d) => !!d.edgeGlow;
    // Skip enter animation in flow modes so the wave animation owns the look
    const skipEnterAnim = links.some((d) => d.flowScore != null);

    this.linkSel = this.linkSel
      .data(links, (d) => d.id)
      .join(
        (enter) => {
          const sel = enter
            .append("line")
            .attr("class", linkClass)
            .attr("stroke", strokeColor)
            .attr("stroke-width", skipEnterAnim ? finalWidth : 4.5)
            .attr("stroke-opacity", skipEnterAnim ? finalOpacity : 0)
            .attr("marker-end", (d) => (d.relation === "oneway" ? "url(#arrow-oneway)" : null))
            .style("filter", (d) => (useFlowGlow(d) ? "url(#edge-flow-glow)" : null));
          if (!skipEnterAnim) {
            sel.call((e) =>
              e
                .transition()
                .duration(180)
                .attr("stroke-opacity", 0.95)
                .attr("stroke-width", 3.2)
                .transition()
                .duration(420)
                .attr("stroke-opacity", finalOpacity)
                .attr("stroke-width", finalWidth)
                .on("end", function () {
                  d3.select(this).classed("glow", false);
                }),
            );
          }
          return sel;
        },
        (update) =>
          update
            .attr("class", (d) => "radialgraph-link " + (d.relation === "mutual" ? "mutual" : "oneway"))
            .attr("marker-end", (d) => (d.relation === "oneway" ? "url(#arrow-oneway)" : null))
            .attr("stroke", strokeColor)
            .attr("stroke-width", finalWidth)
            .attr("stroke-opacity", finalOpacity)
            .style("filter", (d) => (useFlowGlow(d) ? "url(#edge-flow-glow)" : null)),
        (exit) => exit.transition().duration(200).attr("stroke-opacity", 0).remove(),
      );

    const ringStroke = getComputedStyle(document.body).getPropertyValue("--ring-stroke").trim() || "#fff";
    const applyVisuals = (selection) => {
      selection.each((d, i, group) => {
        const g = d3.select(group[i]);
        let inner = g.select(".radialgraph-node-inner");
        if (inner.empty()) inner = g.append("g").attr("class", "radialgraph-node-inner");
        inner.selectAll("rect, circle").remove();
        const hasHidden = hasHiddenNeighbors(d.id);
        if (d.shape === "square") {
          inner
            .append("rect")
            .attr("x", -d.size)
            .attr("y", -d.size)
            .attr("width", d.size * 2)
            .attr("height", d.size * 2)
            .attr("rx", 2)
            .attr("fill", d.color)
            .attr("stroke", hasHidden ? ringStroke : "none")
            .attr("stroke-width", 1.5);
        } else {
          inner
            .append("circle")
            .attr("r", d.size)
            .attr("fill", d.color)
            .attr("stroke", hasHidden ? ringStroke : "none")
            .attr("stroke-width", 1.5);
        }
        // Search highlight rings (shown via .search-hit CSS)
        let rings = g.select(".search-rings");
        if (rings.empty()) {
          rings = g.insert("g", ":first-child").attr("class", "search-rings");
          rings.append("circle").attr("class", "search-ring search-ring-border");
          rings.append("circle").attr("class", "search-ring search-ring-yellow");
        }
        rings.selectAll("circle").attr("r", (d.size || 6) + 12);
      });
    };

    this.nodeSel = this.nodeSel
      .data(nodes, (d) => d.id)
      .join(
        (enter) => {
          const sel = enter
            .append("g")
            .attr("class", "radialgraph-node")
            .attr("transform", (d) => `translate(${d.x},${d.y})`)
            .call(applyVisuals)
            .call(this.onEnterNode);
          sel
            .append("text")
            .attr("class", "radialgraph-label")
            .attr("x", (d) => d.size + 4)
            .attr("dy", "0.32em")
            .attr("opacity", 0)
            .text((d) => d.id);
          sel.select(".radialgraph-node-inner").attr("transform", "scale(0.001)").transition().duration(300).attr("transform", "scale(1)");
          return sel;
        },
        (update) => update.call(applyVisuals),
        (exit) =>
          exit
            .transition()
            .duration(200)
            .attr("transform", (d) => `translate(${d.x},${d.y}) scale(0.001)`)
            .remove(),
      );
  }

  tick() {
    const nodeById = this.nodeById;
    const endPoint = (d, which) => {
      const s = typeof d.source === "object" ? d.source : nodeById.get(d.source);
      const t = typeof d.target === "object" ? d.target : nodeById.get(d.target);
      if (!s || !t) return { x: 0, y: 0 };
      if (which === "start") return { x: s.x, y: s.y };
      const dx = t.x - s.x,
        dy = t.y - s.y;
      const len = Math.hypot(dx, dy) || 1;
      const trim = (t.size || 6) + (d.relation === "oneway" ? 4 : 0);
      return { x: t.x - (dx / len) * trim, y: t.y - (dy / len) * trim };
    };
    this.linkSel
      .attr("x1", (d) => endPoint(d, "start").x)
      .attr("y1", (d) => endPoint(d, "start").y)
      .attr("x2", (d) => endPoint(d, "end").x)
      .attr("y2", (d) => endPoint(d, "end").y);
    this.nodeSel.attr("transform", (d) => `translate(${d.x},${d.y})`);
  }

  // Ghost preview: faint, dashed, non-interactive stand-ins showing where
  // a node's hidden neighbors would land if expanded - reuses the exact
  // same "fan out along the parent's angle from origin" placement math as
  // the real expand seeding in LayoutEngine, so the preview honestly
  // matches what will actually happen on click. Purely visual - these
  // never touch the simulation.
  showGhosts(node, hiddenIds) {
    this.clearGhosts();
    if (!hiddenIds.length) return;
    let angle = Math.atan2(node.y, node.x);
    if (!isFinite(angle) || (node.x === 0 && node.y === 0)) angle = 0;
    const spread = Math.PI / 6;
    const offset = 24;
    const group = this.ghostLayer.append("g").attr("class", "ghost-group");
    hiddenIds.forEach((id, i) => {
      const t = hiddenIds.length > 1 ? i / (hiddenIds.length - 1) - 0.5 : 0;
      const a = angle + t * spread;
      const gx = node.x + Math.cos(a) * offset;
      const gy = node.y + Math.sin(a) * offset;
      group.append("line").attr("class", "ghost-link").attr("x1", node.x).attr("y1", node.y).attr("x2", gx).attr("y2", gy);
      group.append("circle").attr("class", "ghost-node").attr("cx", gx).attr("cy", gy).attr("r", 5);
    });
  }

  clearGhosts() {
    this.ghostLayer.selectAll("*").remove();
  }

  // Live-update stroke style on existing link elements (used by flow animation).
  // Does not re-join data — only mutates visual attributes.
  updateLinkStyles() {
    if (!this.linkSel || this.linkSel.empty()) return;
    this.linkSel
      .attr("stroke", (d) => d.edgeColor || "#888")
      .attr("stroke-width", (d) => (d.edgeWidth != null ? d.edgeWidth : 1.4))
      .attr("stroke-opacity", (d) => (d.edgeOpacity != null ? d.edgeOpacity : 0.5))
      .style("filter", (d) => (d.edgeGlow ? "url(#edge-flow-glow)" : null))
      .classed("glow", (d) => !!d.edgeGlow);
  }
}

// =========================================================================
// Interaction - zoom/pan on the canvas, drag-to-reposition and tap-to-
// toggle on individual nodes. Distinguishes a tap from a drag by how far
// the pointer moved between press and release.
// =========================================================================
class Interaction {
  constructor({ svg, g, simulation, tooltip, getRootId, isLocalMode, onToggle, onReroot, onShowGhosts, onHideGhosts, onZoom, onSelect }) {
    this.zoom = d3
      .zoom()
      .scaleExtent([0.15, 8])
      .on("zoom", (e) => {
        g.attr("transform", e.transform);
        if (onZoom) onZoom(e.transform.k);
      });
    svg.call(this.zoom).on("dblclick.zoom", null);
    this.svg = svg;
    this.g = g;
    this.simulation = simulation;
    this.tooltip = tooltip;
    // Dismiss tooltip / ghosts / search highlight when tapping empty canvas
    this.onBackgroundClick = null;
    svg.on("click", (event) => {
      if (event.target === svg.node()) {
        tooltip.style("opacity", 0);
        onHideGhosts();
        if (this.onBackgroundClick) this.onBackgroundClick();
      }
    });
    this.getRootId = getRootId; // () => string
    this.isLocalMode = isLocalMode; // () => bool
    this.onToggle = onToggle;
    this.onReroot = onReroot; // (d) => void — focus this node as new root
    this.onShowGhosts = onShowGhosts; // (d) => void - draw preview for node d
    this.onHideGhosts = onHideGhosts; // () => void
    this.onSelect = onSelect; // (d) => void — show node info panel
    // Double-tap / double-click detection shared by mouse + touch.
    // Native `dblclick` is unreliable on mobile (and often swallowed by drag).
    this._lastTap = { id: null, time: 0 };
    this._DOUBLE_TAP_MS = 320;
    this._pendingToggle = null; // deferred single-tap timer
  }

  // Smoothly pan/zoom so graph point (x, y) lands at the viewport center.
  centerOn(x, y, scale) {
    const svgNode = this.svg.node();
    const w = svgNode.clientWidth || 1;
    const h = svgNode.clientHeight || 1;
    const k = scale != null ? scale : d3.zoomTransform(svgNode).k || 1;
    const transform = d3.zoomIdentity
      .translate(w / 2, h / 2)
      .scale(k)
      .translate(-x, -y);
    this.svg.transition().duration(450).ease(d3.easeCubicOut).call(this.zoom.transform, transform);
  }

  attachToEnteringNode(selection) {
    selection
      .on("mouseover", (event, d) => {
        // mouse-only hover; touch uses press-and-hold for ghosts
        if (event.sourceEvent && event.sourceEvent.pointerType === "touch") return;
        const isRoot = d.id === this.getRootId();
        const extra = [d.degree != null ? `deg ${d.degree}` : null, d.betweenness != null ? `btw ${d.betweenness.toFixed(1)}` : null, d.community != null ? `c${d.community}` : null, isRoot ? "focal" : "double-tap to focus"].filter(Boolean).join(" · ");
        this.tooltip.style("opacity", 1).html(d.tooltip + (extra ? ` · ${extra}` : ""));
        this.onShowGhosts(d);
      })
      .on("mousemove", (event) => this.tooltip.style("left", event.pageX + 12 + "px").style("top", event.pageY - 8 + "px"))
      .on("mouseout", () => {
        this.tooltip.style("opacity", 0);
        this.onHideGhosts();
      })
      .each((d, i, group) => {
        d3.select(group[i]).call(this._dragBehavior());
      });
  }

  // Returns true if this tap completes a double-tap on the same node.
  _isDoubleTap(d) {
    const now = performance.now();
    const same = this._lastTap.id === d.id && now - this._lastTap.time < this._DOUBLE_TAP_MS;
    this._lastTap = { id: d.id, time: now };
    return same;
  }

  _dragBehavior() {
    let moved = false;
    let longPressTimer = null;
    const sim = this.simulation;
    const LONG_PRESS_MS = 350;
    // Slightly larger threshold on touch to avoid jitter counting as a drag
    const moveThreshold = () => (window.matchMedia("(pointer: coarse)").matches ? 10 : 4);

    const dragstarted = (event, d) => {
      moved = false;
      if (!event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
      // Touch/pen has no hover, so a press-and-hold shows the same ghost
      // preview a mouse gets "for free" via mouseover.
      clearTimeout(longPressTimer);
      longPressTimer = setTimeout(() => {
        if (!moved) this.onShowGhosts(d);
      }, LONG_PRESS_MS);
    };
    const dragged = (event, d) => {
      const thr = moveThreshold();
      if (Math.abs(event.x - d.x) > thr || Math.abs(event.y - d.y) > thr) {
        moved = true;
        clearTimeout(longPressTimer);
      }
      d.fx = event.x;
      d.fy = event.y;
    };
    const dragended = (event, d) => {
      clearTimeout(longPressTimer);
      this.onHideGhosts();
      if (!event.active) sim.alphaTarget(0);
      const keepPinned = d.id === this.getRootId() && this.isLocalMode();
      if (!keepPinned) {
        d.fx = null;
        d.fy = null;
      }
      if (moved) {
        // Drag — not a tap; clear double-tap sequence
        this._lastTap = { id: null, time: 0 };
        clearTimeout(this._pendingToggle);
        this._pendingToggle = null;
        return;
      }
      // Tap: show the node's info panel immediately, regardless of whether
      // this becomes a single (toggle) or double (re-root) tap.
      if (this.onSelect) this.onSelect(d);
      // Tap: double-tap → re-root; single tap → expand/collapse (deferred so a
      // second tap within the window can cancel the toggle and focus instead).
      if (this._isDoubleTap(d)) {
        clearTimeout(this._pendingToggle);
        this._pendingToggle = null;
        this._lastTap = { id: null, time: 0 };
        if (d.id !== this.getRootId()) this.onReroot(d);
      } else {
        clearTimeout(this._pendingToggle);
        this._pendingToggle = setTimeout(() => {
          this._pendingToggle = null;
          this.onToggle(d);
        }, this._DOUBLE_TAP_MS);
      }
    };
    // filter:null allows drag on touch + mouse; touchable nodes need this for mobile
    return d3
      .drag()
      .filter((event) => !event.ctrlKey && !event.button)
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }
}

// =========================================================================
// Louvain community detection (undirected, unweighted).
// Returns Map<nodeId, communityId> with community ids in 0..k-1 ordered by
// community size (largest first). Runs on the FULL underlying graph so
// colors stay stable as the user expands/collapses the frontier.
// =========================================================================
function louvainCommunities(nodeIds, edges) {
  // --- Build undirected weighted adjacency ---
  const nodes = Array.from(nodeIds);
  const adj = new Map(nodes.map((id) => [id, new Map()]));
  let m = 0; // total edge weight (each undirected edge counted once)
  edges.forEach((e) => {
    if (e.source === e.target || !adj.has(e.source) || !adj.has(e.target)) return;
    const a = adj.get(e.source),
      b = adj.get(e.target);
    a.set(e.target, (a.get(e.target) || 0) + 1);
    b.set(e.source, (b.get(e.source) || 0) + 1);
    m += 1;
  });
  if (m === 0 || nodes.length === 0) {
    const out = new Map();
    nodes.forEach((id, i) => out.set(id, i));
    return out;
  }
  const inv2m = 1 / (2 * m);

  // degree / strength of each node
  function degreesOf(adjacency) {
    const deg = new Map();
    adjacency.forEach((nbrs, id) => {
      let s = 0;
      nbrs.forEach((w) => {
        s += w;
      });
      deg.set(id, s);
    });
    return deg;
  }

  // Phase 1: local modularity maximization on a (possibly aggregated) graph.
  // membership: Map(nodeId -> communityId)  communityId is some node id that is the "label"
  function phase1(nodeList, adjacency, deg) {
    const membership = new Map(nodeList.map((id) => [id, id]));
    // total degree of each community
    const comTot = new Map(nodeList.map((id) => [id, deg.get(id)]));

    let moved = true;
    let iter = 0;
    while (moved && iter < 30) {
      moved = false;
      iter++;
      // random order
      const order = nodeList.slice();
      for (let i = order.length - 1; i > 0; i--) {
        const j = (Math.random() * (i + 1)) | 0;
        const t = order[i];
        order[i] = order[j];
        order[j] = t;
      }
      for (const i of order) {
        const ci = membership.get(i);
        const ki = deg.get(i) || 0;
        // weight of edges from i into each neighboring community
        const toCom = new Map();
        (adjacency.get(i) || new Map()).forEach((w, j) => {
          const cj = membership.get(j);
          toCom.set(cj, (toCom.get(cj) || 0) + w);
        });
        // remove i from its community
        comTot.set(ci, (comTot.get(ci) || 0) - ki);
        const kiInCi = toCom.get(ci) || 0;

        let best = ci;
        let bestDelta = 0; // stay puts delta 0 relative to current after removal baseline
        // gain of moving i into community c:
        //   ΔQ = (ki_in_c - ki_in_ci)/m  -  (ki * (Σtot_c - Σtot_ci)) / (2m²)
        // after removal, Σtot_ci is comTot[ci], Σtot_c is comTot[c]
        // After removing i from ci, gain of placing i into community c vs back into ci:
        //   ΔQ(c) - ΔQ(ci) = (ki_in_c - ki_in_ci)/m - ki*(tot_c - tot_ci)/(2m)²
        toCom.forEach((kiInC, c) => {
          if (c === ci) return;
          const totC = comTot.get(c) || 0;
          const totCi = comTot.get(ci) || 0;
          const dQ = (kiInC - kiInCi) / m - ki * (totC - totCi) * inv2m * inv2m;
          if (dQ > bestDelta + 1e-12) {
            bestDelta = dQ;
            best = c;
          }
        });

        membership.set(i, best);
        comTot.set(best, (comTot.get(best) || 0) + ki);
        if (best !== ci) moved = true;
      }
    }
    return membership;
  }

  // Phase 2: aggregate communities into supernodes
  function aggregate(nodeList, adjacency, deg, membership) {
    // unique community labels
    const labels = Array.from(new Set(membership.values()));
    const labelIndex = new Map(labels.map((l, i) => [l, i]));
    const superIds = labels.map((_, i) => "S" + i);
    const superAdj = new Map(superIds.map((id) => [id, new Map()]));
    const superDeg = new Map(superIds.map((id) => [id, 0]));

    // Map each original node in this level to its super id
    const toSuper = new Map();
    nodeList.forEach((id) => {
      toSuper.set(id, superIds[labelIndex.get(membership.get(id))]);
    });

    // Degrees of supers = sum of member degrees
    nodeList.forEach((id) => {
      const s = toSuper.get(id);
      superDeg.set(s, (superDeg.get(s) || 0) + (deg.get(id) || 0));
    });

    // Edges between supers
    nodeList.forEach((id) => {
      const si = toSuper.get(id);
      (adjacency.get(id) || new Map()).forEach((w, j) => {
        // count each undirected edge once
        if (String(id) > String(j)) return;
        const sj = toSuper.get(j);
        if (si === sj) return; // internal — already reflected in deg via self contribution;
        // for modularity phase1, inter-only edges matter for moves; self-loops omitted
        const a = superAdj.get(si),
          b = superAdj.get(sj);
        a.set(sj, (a.get(sj) || 0) + w);
        b.set(si, (b.get(si) || 0) + w);
      });
    });

    return { superIds, superAdj, superDeg, toSuper };
  }

  // --- Multi-level Louvain ---
  let curNodes = nodes;
  let curAdj = adj;
  let curDeg = degreesOf(adj);
  // assignment of original nodes → current-level node id
  let assign = new Map(nodes.map((id) => [id, id]));

  for (let level = 0; level < 10; level++) {
    const mem = phase1(curNodes, curAdj, curDeg);
    const nBefore = curNodes.length;
    const nAfter = new Set(mem.values()).size;
    // update original assignment
    const nextAssign = new Map();
    assign.forEach((cur, orig) => nextAssign.set(orig, mem.get(cur)));
    assign = nextAssign;

    if (nAfter >= nBefore) break; // no improvement

    const agg = aggregate(curNodes, curAdj, curDeg, mem);
    // remap assignment through aggregation
    const afterAgg = new Map();
    assign.forEach((comLabel, orig) => afterAgg.set(orig, agg.toSuper.get(comLabel)));
    assign = afterAgg;

    curNodes = agg.superIds;
    curAdj = agg.superAdj;
    curDeg = agg.superDeg;
  }

  // Renumber by community size (largest first → id 0)
  const counts = new Map();
  assign.forEach((c) => counts.set(c, (counts.get(c) || 0) + 1));
  const ranked = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
  const renum = new Map(ranked.map((e, i) => [e[0], i]));
  const result = new Map();
  assign.forEach((c, id) => result.set(id, renum.get(c)));
  return result;
}

// =========================================================================
// Small helper: undirected neighbor-list map from an edge list. Used to
// keep the "why is this node important" breakdown consistent with
// whatever edge set the current statistics were computed from.
// =========================================================================
function buildAdjacencyMap(nodeIds, edges) {
  const adj = new Map(nodeIds.map((id) => [id, []]));
  edges.forEach((e) => {
    if (e.source === e.target || !adj.has(e.source) || !adj.has(e.target)) return;
    adj.get(e.source).push(e.target);
    adj.get(e.target).push(e.source);
  });
  adj.forEach((nbrs, id) => adj.set(id, Array.from(new Set(nbrs))));
  return adj;
}

// =========================================================================
// Network metrics on the (possibly edge-filtered) graph.
// Returns { degree, betweenness, closeness, pagerank, hub, authority,
//           hub, authority } as Maps(id -> number).
// =========================================================================
function computeNetworkMetrics(nodeIds, edges) {
  const nodes = Array.from(nodeIds);
  const n = nodes.length;
  const adj = new Map(nodes.map((id) => [id, []])); // undirected, deduped
  const outAdj = new Map(nodes.map((id) => [id, []])); // directed: source -> targets
  const inAdj = new Map(nodes.map((id) => [id, []])); // directed: target -> sources
  edges.forEach((e) => {
    if (e.source === e.target || !adj.has(e.source) || !adj.has(e.target)) return;
    adj.get(e.source).push(e.target);
    adj.get(e.target).push(e.source);
    outAdj.get(e.source).push(e.target);
    inAdj.get(e.target).push(e.source);
  });
  // dedupe neighbor lists
  adj.forEach((nbrs, id) => adj.set(id, Array.from(new Set(nbrs))));
  outAdj.forEach((nbrs, id) => outAdj.set(id, Array.from(new Set(nbrs))));
  inAdj.forEach((nbrs, id) => inAdj.set(id, Array.from(new Set(nbrs))));

  const degree = new Map();
  nodes.forEach((id) => degree.set(id, adj.get(id).length));

  // --- Betweenness (Brandes) ---
  const betweenness = new Map(nodes.map((id) => [id, 0]));
  nodes.forEach((s) => {
    const stack = [];
    const pred = new Map(nodes.map((id) => [id, []]));
    const sigma = new Map(nodes.map((id) => [id, 0]));
    const dist = new Map(nodes.map((id) => [id, -1]));
    sigma.set(s, 1);
    dist.set(s, 0);
    const queue = [s];
    while (queue.length) {
      const v = queue.shift();
      stack.push(v);
      for (const w of adj.get(v)) {
        if (dist.get(w) < 0) {
          dist.set(w, dist.get(v) + 1);
          queue.push(w);
        }
        if (dist.get(w) === dist.get(v) + 1) {
          sigma.set(w, sigma.get(w) + sigma.get(v));
          pred.get(w).push(v);
        }
      }
    }
    const delta = new Map(nodes.map((id) => [id, 0]));
    while (stack.length) {
      const w = stack.pop();
      for (const v of pred.get(w)) {
        delta.set(v, delta.get(v) + (sigma.get(v) / sigma.get(w)) * (1 + delta.get(w)));
      }
      if (w !== s) betweenness.set(w, betweenness.get(w) + delta.get(w));
    }
  });
  // undirected: each pair counted twice
  betweenness.forEach((v, id) => betweenness.set(id, v / 2));

  // --- Closeness: (n-1) / sum of distances (0 if disconnected from some) ---
  const closeness = new Map();
  nodes.forEach((s) => {
    const dist = new Map([[s, 0]]);
    const queue = [s];
    while (queue.length) {
      const v = queue.shift();
      for (const w of adj.get(v)) {
        if (!dist.has(w)) {
          dist.set(w, dist.get(v) + 1);
          queue.push(w);
        }
      }
    }
    if (dist.size < n) {
      closeness.set(s, 0);
    } else {
      let sum = 0;
      dist.forEach((d) => {
        sum += d;
      });
      closeness.set(s, sum > 0 ? (n - 1) / sum : 0);
    }
  });

  // --- PageRank (power iteration, undirected as bidirectional) ---
  const pagerank = new Map(nodes.map((id) => [id, 1 / n]));
  const d = 0.85;
  for (let iter = 0; iter < 40; iter++) {
    const next = new Map(nodes.map((id) => [id, (1 - d) / n]));
    nodes.forEach((v) => {
      const nbrs = adj.get(v);
      const deg = nbrs.length || 1;
      const share = d * (pagerank.get(v) / deg);
      if (!nbrs.length) {
        // dangling: distribute to all
        nodes.forEach((u) => next.set(u, next.get(u) + (d * pagerank.get(v)) / n));
      } else {
        nbrs.forEach((w) => next.set(w, next.get(w) + share));
      }
    });
    pagerank.clear();
    next.forEach((v, id) => pagerank.set(id, v));
  }

  // --- HITS: hub & authority (power iteration on directed adjacency) ---
  let hub = new Map(nodes.map((id) => [id, 1]));
  let authority = new Map(nodes.map((id) => [id, 1]));
  for (let iter = 0; iter < 60; iter++) {
    const nextAuth = new Map(nodes.map((id) => [id, 0]));
    nodes.forEach((v) => {
      let s = 0;
      inAdj.get(v).forEach((u) => {
        s += hub.get(u);
      });
      nextAuth.set(v, s);
    });
    const normA = Math.sqrt(Array.from(nextAuth.values()).reduce((a, b) => a + b * b, 0)) || 1;
    nextAuth.forEach((v, id) => nextAuth.set(id, v / normA));

    const nextHub = new Map(nodes.map((id) => [id, 0]));
    nodes.forEach((v) => {
      let s = 0;
      outAdj.get(v).forEach((w) => {
        s += nextAuth.get(w);
      });
      nextHub.set(v, s);
    });
    const normH = Math.sqrt(Array.from(nextHub.values()).reduce((a, b) => a + b * b, 0)) || 1;
    nextHub.forEach((v, id) => nextHub.set(id, v / normH));

    authority = nextAuth;
    hub = nextHub;
  }

  return { degree, betweenness, closeness, pagerank, hub, authority };
}

// =========================================================================
// Data injected by RadialGraph.py (nodes/links/rootId from the Python side).
// Nodes carry baseColor/baseSize from d3graph property computation; depth is
// precomputed BFS hop from center (also recomputed client-side on reroot).
// =========================================================================
(function () {
  const payload = typeof radialgraphData !== "undefined" ? radialgraphData : { nodes: [], links: [], rootId: null };
  const cfg = typeof radialgraphConfig !== "undefined" ? radialgraphConfig : {};

  const nodes = (payload.nodes || []).map((n) => ({
    id: n.id,
    color: n.color || n.baseColor || "#D33F6A",
    baseColor: n.baseColor || n.color || "#D33F6A",
    size: n.size || n.baseSize || 8,
    baseSize: n.baseSize || n.size || 8,
    opacity: n.opacity != null ? +n.opacity : 0.95,
    shape: n.shape || "circle",
    tooltip: n.tooltip || n.label || n.id,
    label: n.label || n.id,
    fontcolor: n.fontcolor || null,
    fontsize: n.fontsize || 10,
    depth: n.depth != null ? n.depth : null,
    node_proba: typeof n.node_proba === "number" ? n.node_proba : NaN,
    degree: 0,
    betweenness: 0,
    closeness: 0,
    pagerank: 0,
    hub: 0,
    authority: 0,
  }));

  // Python sends undirected-ish source/target pairs; treat each row as a
  // directed edge so mutual detection (a→b and b→a both present) works.
  const edges = (payload.links || []).map((e, i) => ({
    id: "e" + i,
    source: typeof e.source === "object" ? e.source.id : e.source,
    target: typeof e.target === "object" ? e.target.id : e.target,
    weight: e.weight != null ? +e.weight : 1,
    link_color: e.link_color || "#999",
    link_width: e.link_width != null ? +e.link_width : 1,
    link_opacity: e.link_opacity != null ? +e.link_opacity : 0.6,
  }));

  let rootId = payload.rootId || cfg.center || (nodes[0] && nodes[0].id);
  if (rootId && !nodes.some((n) => n.id === rootId)) {
    rootId = nodes[0] && nodes[0].id;
  }

  const model = new GraphModel({ nodes, edges, rootId: rootId });

  // Network metrics — initially over the full (unfiltered) graph. Recomputed
  // by recomputeMetrics() whenever the edge direction filter or focus changes.
  const metrics = computeNetworkMetrics(
    nodes.map((n) => n.id),
    edges,
  );
  const metricMax = {
    degree: 0,
    betweenness: 0,
    closeness: 0,
    pagerank: 0,
    hub: 0,
    authority: 0,
  };
  nodes.forEach((n) => {
    n.degree = metrics.degree.get(n.id) || 0;
    n.betweenness = metrics.betweenness.get(n.id) || 0;
    n.closeness = metrics.closeness.get(n.id) || 0;
    n.pagerank = metrics.pagerank.get(n.id) || 0;
    n.hub = metrics.hub.get(n.id) || 0;
    n.authority = metrics.authority.get(n.id) || 0;
    metricMax.degree = Math.max(metricMax.degree, n.degree);
    metricMax.betweenness = Math.max(metricMax.betweenness, n.betweenness);
    metricMax.closeness = Math.max(metricMax.closeness, n.closeness);
    metricMax.pagerank = Math.max(metricMax.pagerank, n.pagerank);
    metricMax.hub = Math.max(metricMax.hub, n.hub);
    metricMax.authority = Math.max(metricMax.authority, n.authority);
  });

  // Undirected adjacency matching the edge set the current stats were
  // computed from — kept in sync inside recomputeMetrics().
  let currentFilteredAdj = buildAdjacencyMap(
    nodes.map((n) => n.id),
    edges,
  );

  // Louvain on the full underlying graph — stable as frontier expands
  const communityOf = louvainCommunities(
    nodes.map((n) => n.id),
    edges,
  );
  nodes.forEach((n) => {
    n.community = communityOf.get(n.id) ?? 0;
  });

  // —— Jaccard coefficient for every undirected pair that has an edge ——
  // J(u,v) = |N(u) ∩ N(v)| / |N(u) ∪ N(v)|  (neighbors exclude each other)
  // Computed once on the full undirected adjacency; looked up per link id.
  const fullUndirectedAdj = buildAdjacencyMap(
    nodes.map((n) => n.id),
    edges,
  );
  const jaccardOf = new Map(); // key "a|b" (sorted) → number in [0,1]
  function pairKey(a, b) {
    return a < b ? a + "|" + b : b + "|" + a;
  }
  function computeJaccard(a, b) {
    const Na = fullUndirectedAdj.get(a) || [];
    const Nb = fullUndirectedAdj.get(b) || [];
    // Exclude the other endpoint from each neighbor set so a direct edge
    // does not inflate the intersection.
    const setA = new Set(Na.filter((x) => x !== b));
    const setB = new Set(Nb.filter((x) => x !== a));
    if (setA.size === 0 && setB.size === 0) return 0;
    let inter = 0;
    setA.forEach((x) => {
      if (setB.has(x)) inter++;
    });
    const union = setA.size + setB.size - inter;
    return union > 0 ? inter / union : 0;
  }
  // Precompute for every undirected edge in the full graph
  {
    const seen = new Set();
    edges.forEach((e) => {
      if (e.source === e.target) return;
      const k = pairKey(e.source, e.target);
      if (seen.has(k)) return;
      seen.add(k);
      jaccardOf.set(k, computeJaccard(e.source, e.target));
    });
  }

  // Palettes
  const DEPTH_COLORS = ["#4C78A8", "#54A24B", "#EECA3B", "#F58518", "#E45756", "#B279A2", "#9c27b0"];
  const COMMUNITY_COLORS = ["#4C78A8", "#E45756", "#54A24B", "#F58518", "#B279A2", "#EECA3B", "#72B7B2", "#FF9DA6", "#9D755D", "#BAB0AC", "#7F63D9", "#2CA02C"];
  // Metric color: blue (low) → white → red (high / most important)
  const metricColorScale = d3.scaleLinear().domain([0, 0.25, 0.5, 0.75, 1]).range(["#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"]).clamp(true);
  // Jaccard edge color: low similarity (rare bridge-like) → red; high → blue
  const jaccardColorScale = d3.scaleLinear().domain([0, 0.25, 0.5, 0.75, 1]).range(["#b2182b", "#ef8a62", "#f7f7f7", "#67a9cf", "#2166ac"]).clamp(true);

  const METRIC_KEYS = new Set(["degree", "betweenness", "closeness", "pagerank", "hub", "authority"]);
  let colorMode = "default";
  let sizeMode = "default";
  let edgeStatMode = "default"; // 'default' | 'community' | 'jaccard' | 'flow-home'
  let highlightedId = null; // search highlight survives re-renders

  // —— Information-diffusion flow scores (DIRECTED: source → target only) ——
  // Single-source from the current focus, following arrow direction only.
  // Node size (baseSize) scales how much mass a node injects.
  // ONLY edges that pass the current Edge filters are diffusion paths —
  // same allow-rules as filterLinks (outbound / inbound / bidirectional).
  // Diffusion walks the filtered graph as an UNDIRECTED network of those
  // allowed pairs, so inbound edges also carry flow into subnetworks (not
  // only outbound / mutual). Removing a filter category still cuts those
  // pairs out of the path set. Scores keyed by undirected pair "a|b".
  let flowCache = { key: null, scores: new Map(), hops: new Map(), maxHop: 0, maxScore: 1 };

  function nodeDiffuseStrength(id) {
    const n = model.nodesById.get(id);
    return Math.max(1, (n && (n.baseSize != null ? n.baseSize : n.size)) || 6);
  }

  function currentEdgeFilters() {
    return typeof edgeDirFilter !== "undefined" && edgeDirFilter ? edgeDirFilter : new Set(["outbound", "inbound", "bidirectional"]);
  }

  function filterKey() {
    return Array.from(currentEdgeFilters()).sort().join(",");
  }

  // Allowed? — same decision as filterLinks for one undirected pair.
  function edgePairAllowed(a, b, relation, depths, filters) {
    if (relation === "mutual") return filters.has("bidirectional");
    const ds = depths.get(a) ?? 99;
    const dt = depths.get(b) ?? 99;
    if (ds === dt) return filters.has("outbound") || filters.has("inbound");
    if (ds < dt) return filters.has("outbound"); // a → b points outward
    return filters.has("inbound"); // a → b points inward
  }

  // Undirected adjacency of pairs that pass the edge-dir filters.
  // Every allowed pair (outbound, inbound, or bidirectional) is traversable
  // in both directions for diffusion, so inbound edges spread into subnetworks.
  function buildFilteredFlowAdj() {
    const nodes = Array.from(model.nodesById.keys());
    const adj = new Map(nodes.map((id) => [id, []]));
    const filters = currentEdgeFilters();

    const depths = new Map([[model.rootId, 0]]);
    {
      const q = [model.rootId];
      while (q.length) {
        const id = q.shift();
        for (const nb of model.neighbors(id)) {
          if (!depths.has(nb)) {
            depths.set(nb, depths.get(id) + 1);
            q.push(nb);
          }
        }
      }
    }

    const seen = new Set();
    model.edges.forEach((e) => {
      if (e.source === e.target) return;
      const a = e.source,
        b = e.target;
      const key = a < b ? a + "|" + b : b + "|" + a;
      if (seen.has(key)) return;
      seen.add(key);
      const ab = model.follows(a, b),
        ba = model.follows(b, a);
      let relation, src, tgt;
      if (ab && ba) {
        relation = "mutual";
        src = a;
        tgt = b;
      } else if (ab) {
        relation = "oneway";
        src = a;
        tgt = b;
      } else if (ba) {
        relation = "oneway";
        src = b;
        tgt = a;
      } else {
        return;
      }
      if (!edgePairAllowed(src, tgt, relation, depths, filters)) return;

      // Undirected for diffusion: both endpoints can pass mass across the pair
      adj.get(a).push(b);
      adj.get(b).push(a);
    });
    return adj;
  }

  // Single-source flow on the filtered undirected adjacency.
  // Mass at source ∝ node size; edge scores from path-count dependencies.
  function computeSourceFlow(sourceId, flowAdj) {
    const nodes = Array.from(model.nodesById.keys());
    const scores = new Map(); // pairKey → flow
    const hops = new Map(); // pairKey → hop of farther endpoint

    const srcMass = nodeDiffuseStrength(sourceId);
    const dist = new Map([[sourceId, 0]]);
    const sigma = new Map([[sourceId, srcMass]]);
    const pred = new Map(nodes.map((id) => [id, []]));
    const queue = [sourceId];
    while (queue.length) {
      const v = queue.shift();
      for (const w of flowAdj.get(v) || []) {
        if (!dist.has(w)) {
          dist.set(w, dist.get(v) + 1);
          queue.push(w);
        }
        if (dist.get(w) === dist.get(v) + 1) {
          sigma.set(w, (sigma.get(w) || 0) + (sigma.get(v) || 0) * (nodeDiffuseStrength(v) / 6));
          pred.get(w).push(v);
        }
      }
    }
    const delta = new Map(nodes.map((id) => [id, 0]));
    const order = Array.from(dist.entries())
      .sort((a, b) => b[1] - a[1])
      .map((e) => e[0]);
    order.forEach((w) => {
      if (w === sourceId) return;
      const sw = sigma.get(w) || 1e-12;
      for (const v of pred.get(w)) {
        const sizeW = nodeDiffuseStrength(v) / 6;
        const c = ((sigma.get(v) || 0) / sw) * (1 + (delta.get(w) || 0)) * sizeW;
        const k = pairKey(v, w);
        scores.set(k, (scores.get(k) || 0) + c);
        if (!hops.has(k)) hops.set(k, dist.get(w));
        delta.set(v, (delta.get(v) || 0) + c);
      }
    });
    let maxScore = 0,
      maxHop = 0;
    scores.forEach((v) => {
      if (v > maxScore) maxScore = v;
    });
    hops.forEach((v) => {
      if (v > maxHop) maxHop = v;
    });
    return { scores, hops, maxHop, maxScore: maxScore || 1, reached: dist };
  }

  function ensureFlowCache() {
    const key = "flow-home|" + model.rootId + "|" + filterKey();
    if (flowCache.key === key) return flowCache;
    const flowAdj = buildFilteredFlowAdj();
    if (edgeStatMode === "flow-home") {
      flowCache = { key, ...computeSourceFlow(model.rootId, flowAdj) };
    } else {
      flowCache = { key, scores: new Map(), hops: new Map(), maxHop: 0, maxScore: 1, reached: new Map() };
    }
    return flowCache;
  }

  // Look up flow for a visual link by undirected pair key.
  function linkFlowInfo(sid, tid, relation, cache) {
    const k = pairKey(sid, tid);
    const score = cache.scores.get(k) || 0;
    const hop = cache.hops.has(k) ? cache.hops.get(k) : 99;
    return { score, hop };
  }

  // Yellow intensity scale for diffusion edges (normalized score → color)
  function flowYellow(t) {
    // t in [0,1]: dim amber → bright yellow → white-hot
    return d3.interpolateRgbBasis(["#7a5a00", "#ffb300", "#ffe566", "#fffde7"])(Math.max(0, Math.min(1, t)));
  }

  // —— Flow wave animation (plays once, then stops) ——
  let flowAnimRaf = null;
  let flowAnimStart = 0;
  const FLOW_MS_PER_HOP = 550;

  function stopFlowAnimation() {
    if (flowAnimRaf != null) {
      cancelAnimationFrame(flowAnimRaf);
      flowAnimRaf = null;
    }
  }

  function isFlowMode() {
    return edgeStatMode === "flow-home";
  }

  // Apply current wave progress to link style fields (mutates links already in renderer).
  // Returns true while the wave is still advancing; false when finished.
  function applyFlowWaveToLinks(waveTime) {
    const cache = ensureFlowCache();
    const maxHop = Math.max(1, cache.maxHop);
    const frontier = Math.min(maxHop + 1.5, waveTime / FLOW_MS_PER_HOP);
    const done = frontier >= maxHop + 1.2;

    if (!renderer.linkSel || renderer.linkSel.empty()) return done;
    renderer.linkSel.each(function (e) {
      const sid = typeof e.source === "object" ? e.source.id : e.source;
      const tid = typeof e.target === "object" ? e.target.id : e.target;
      const { score, hop } = linkFlowInfo(sid, tid, e.relation, cache);
      const intensity = score / cache.maxScore; // 0..1
      e.flowScore = intensity;
      e.flowHop = hop;

      // No directed flow on this visual edge → stay dim (against the arrow / unused)
      if (score <= 0 || hop >= 99) {
        e.edgeColor = "#2a2818";
        e.edgeWidth = 0.5;
        e.edgeOpacity = 0.08;
        e.edgeGlow = false;
        return;
      }

      if (hop > frontier + 0.15) {
        // Not yet reached by the wave
        e.edgeColor = "#3a3520";
        e.edgeWidth = 0.6;
        e.edgeOpacity = 0.12;
        e.edgeGlow = false;
      } else {
        // Fade-in near the frontier, then settle to score-based thickness/brightness
        const age = frontier - hop;
        const reveal = Math.max(0, Math.min(1, age / 0.8));
        const pulse = age < 0.6 ? 0.55 + 0.45 * Math.sin((age / 0.6) * Math.PI) : 1;
        const bright = intensity * reveal * pulse;
        e.edgeColor = flowYellow(0.15 + 0.85 * bright);
        e.edgeWidth = 0.8 + intensity * 4.2 * reveal;
        e.edgeOpacity = 0.2 + 0.75 * bright;
        e.edgeGlow = bright > 0.25;
      }
    });
    renderer.updateLinkStyles();
    return done;
  }

  function startFlowAnimation() {
    stopFlowAnimation();
    if (!isFlowMode()) return;
    ensureFlowCache();
    flowAnimStart = performance.now();
    const step = (now) => {
      if (!isFlowMode()) {
        flowAnimRaf = null;
        return;
      }
      const done = applyFlowWaveToLinks(now - flowAnimStart);
      if (done) {
        // Final settled frame, then stop — play once only
        flowAnimRaf = null;
        return;
      }
      flowAnimRaf = requestAnimationFrame(step);
    };
    flowAnimRaf = requestAnimationFrame(step);
  }

  // Annotate each visible link with edgeColor / edgeWidth / edgeOpacity for
  // the current edge-statistics mode. Mutates link objects in place.
  function applyEdgeStyles(links) {
    links.forEach((e) => {
      const sid = typeof e.source === "object" ? e.source.id : e.source;
      const tid = typeof e.target === "object" ? e.target.id : e.target;
      const j = jaccardOf.get(pairKey(sid, tid)) ?? 0;
      e.jaccard = j;
      e.bridgeStrength = 1 - j; // high when endpoints share few neighbors
      e.edgeGlow = false;
      e.flowScore = null;
      e.flowHop = null;

      if (edgeStatMode === "community") {
        const ca = (model.nodesById.get(sid) || {}).community;
        const cb = (model.nodesById.get(tid) || {}).community;
        const internal = ca != null && cb != null && ca === cb;
        e.edgeColor = internal ? "#4C78A8" : "#E45756"; // blue internal, red bridge
        // Internal: modest thickness; external: thicker as bridge strength grows
        e.edgeWidth = internal ? 1.4 + (e.relation === "mutual" ? 0.4 : 0) : 1.6 + e.bridgeStrength * 2.8;
        e.edgeOpacity = internal ? 0.55 : 0.75 + e.bridgeStrength * 0.2;
      } else if (edgeStatMode === "jaccard") {
        e.edgeColor = jaccardColorScale(j);
        e.edgeWidth = 1.2 + j * 2.6;
        e.edgeOpacity = 0.45 + j * 0.4;
      } else if (edgeStatMode === "flow-home") {
        // Initial snapshot before the one-shot wave starts (all dim / pre-wave)
        const cache = ensureFlowCache();
        const { score, hop } = linkFlowInfo(sid, tid, e.relation, cache);
        const intensity = score / cache.maxScore;
        e.flowScore = intensity;
        e.flowHop = hop;
        // Start dim so the animation reveals the flow once
        e.edgeColor = score > 0 ? "#3a3520" : "#2a2818";
        e.edgeWidth = 0.6;
        e.edgeOpacity = 0.12;
        e.edgeGlow = false;
      } else {
        // Default: leave unset so Renderer falls back to target-node color
        e.edgeColor = null;
        e.edgeWidth = null;
        e.edgeOpacity = null;
      }
    });
  }

  // —— Recompute statistics against the currently edge-filtered network ——
  // Direction (outbound/inbound) is relative to hop-depth from the current
  // focus, so metrics are recomputed whenever the edge filter OR the focus
  // (root) changes. Uses the FULL graph (not just the expanded/visible
  // frontier) so stats stay stable as the user expands/collapses nodes.
  function computeFullDepthsFrom(rootId) {
    const depths = new Map([[rootId, 0]]);
    const queue = [rootId];
    while (queue.length) {
      const id = queue.shift();
      for (const nb of model.neighbors(id)) {
        if (!depths.has(nb)) {
          depths.set(nb, depths.get(id) + 1);
          queue.push(nb);
        }
      }
    }
    return depths;
  }

  function recomputeMetrics() {
    const depths = computeFullDepthsFrom(model.rootId);
    const allIds = Array.from(model.nodesById.keys());
    const filteredEdges = [];
    model.edges.forEach((e) => {
      const a = e.source,
        b = e.target;
      if (model.follows(b, a)) {
        // Part of a mutual pair
        if (edgeDirFilter.has("bidirectional")) filteredEdges.push(e);
        return;
      }
      const ds = depths.get(a) ?? 99;
      const dt = depths.get(b) ?? 99;
      if (ds === dt) {
        if (edgeDirFilter.has("outbound") || edgeDirFilter.has("inbound")) filteredEdges.push(e);
      } else if (ds < dt) {
        if (edgeDirFilter.has("outbound")) filteredEdges.push(e);
      } else {
        if (edgeDirFilter.has("inbound")) filteredEdges.push(e);
      }
    });

    const m = computeNetworkMetrics(allIds, filteredEdges);
    currentFilteredAdj = buildAdjacencyMap(allIds, filteredEdges);
    ["degree", "betweenness", "closeness", "pagerank", "hub", "authority"].forEach((k) => {
      metricMax[k] = 0;
    });
    model.nodesById.forEach((n) => {
      n.degree = m.degree.get(n.id) || 0;
      n.betweenness = m.betweenness.get(n.id) || 0;
      n.closeness = m.closeness.get(n.id) || 0;
      n.pagerank = m.pagerank.get(n.id) || 0;
      n.hub = m.hub.get(n.id) || 0;
      n.authority = m.authority.get(n.id) || 0;
      metricMax.degree = Math.max(metricMax.degree, n.degree);
      metricMax.betweenness = Math.max(metricMax.betweenness, n.betweenness);
      metricMax.closeness = Math.max(metricMax.closeness, n.closeness);
      metricMax.pagerank = Math.max(metricMax.pagerank, n.pagerank);
      metricMax.hub = Math.max(metricMax.hub, n.hub);
      metricMax.authority = Math.max(metricMax.authority, n.authority);
    });
    // Keep the node info panel in sync if it's open on a node still in the graph
    if (typeof selectedNodeId !== "undefined" && selectedNodeId && model.nodesById.has(selectedNodeId)) {
      showNodePanel(model.nodesById.get(selectedNodeId));
    }
  }

  function metricValue(n, key) {
    return n[key] ?? 0;
  }

  function metricColor(n, key) {
    const max = metricMax[key] || 1;
    const t = max <= 0 ? 0 : metricValue(n, key) / max;
    return metricColorScale(t);
  }

  function metricSize(n, key) {
    const max = metricMax[key] || 1;
    const t = max <= 0 ? 0 : metricValue(n, key) / max;
    return 4 + t * 12;
  }

  function applyNodeColors(visNodes) {
    visNodes.forEach((n) => {
      if (colorMode === "depth") {
        const d = n.depth ?? 0;
        n.color = DEPTH_COLORS[Math.min(d, DEPTH_COLORS.length - 1)];
      } else if (colorMode === "community") {
        const c = n.community ?? 0;
        n.color = COMMUNITY_COLORS[c % COMMUNITY_COLORS.length];
      } else if (colorMode === "node_proba") {
        const p = typeof n.node_proba === "number" && !isNaN(n.node_proba) ? n.node_proba : 1;
        // Same threshold coloring spirit as d3graph: red below alpha, blue above
        const alpha = cfg.significanceAlpha != null ? cfg.significanceAlpha : 0.05;
        n.color = p < alpha ? d3.scaleLinear().domain([0, alpha]).range(["#b2182b", "#fddbc7"])(p) : d3.scaleLinear().domain([alpha, 1]).range(["#d1e5f0", "#2166ac"])(Math.min(p, 1));
      } else if (METRIC_KEYS.has(colorMode)) {
        n.color = metricColor(n, colorMode);
      } else {
        n.color = n.baseColor;
      }
    });
  }

  function applyNodeSizes(visNodes) {
    visNodes.forEach((n) => {
      if (sizeMode === "node_proba") {
        const p = typeof n.node_proba === "number" && !isNaN(n.node_proba) ? n.node_proba : 1;
        const score = 1 - Math.min(Math.max(p, 0), 1);
        n.size = n.baseSize * (0.8 + score * 1.4);
      } else {
        n.size = METRIC_KEYS.has(sizeMode) ? metricSize(n, sizeMode) : n.baseSize;
      }
    });
  }

  const containerEl = document.getElementById("radialgraph-container");
  const width = containerEl.clientWidth || window.innerWidth - 220;
  const height = containerEl.clientHeight || window.innerHeight;
  let previousIds = new Set(["HOME"]);

  const tooltip = d3.select("#radialgraph-tooltip");
  const layout = new LayoutEngine({
    ringSpacing: cfg.ringSpacing != null ? cfg.ringSpacing : 70,
    charge: cfg.charge != null ? cfg.charge : -140,
    collision: cfg.collision != null ? cfg.collision : 1,
    linkDistance: cfg.linkDistance != null ? cfg.linkDistance : 36,
    linkStrength: cfg.linkStrength != null ? cfg.linkStrength : 0.5,
    radialStrength: cfg.radialStrength != null ? cfg.radialStrength : 0.85,
  });
  if (cfg.autoRingSpacing != null) layout.useAutoRingSpacing = !!cfg.autoRingSpacing;

  const renderer = new Renderer({
    container: "#radialgraph-container",
    width,
    height,
    onEnterNode: (sel) => interaction.attachToEnteringNode(sel),
  });

  // —— Labels ——
  // Zoomed out: only "parent" labels (focus + low-depth / high-importance
  // hubs) — few enough to stay readable. Zoomed in: also show child labels,
  // fading in with scale. Greedy collision-avoidance; parents placed first.
  const LABEL_PARENT_MAX = 14; // max labels kept when zoomed out
  const LABEL_CHILD_ZOOM_START = 1.05; // children begin to appear
  const LABEL_CHILD_ZOOM_FULL = 2.0; // children fully opaque
  let currentZoomK = 1;

  function childLabelOpacity(k) {
    if (k <= LABEL_CHILD_ZOOM_START) return 0;
    if (k >= LABEL_CHILD_ZOOM_FULL) return 1;
    return (k - LABEL_CHILD_ZOOM_START) / (LABEL_CHILD_ZOOM_FULL - LABEL_CHILD_ZOOM_START);
  }

  function estimateLabelBox(d) {
    const w = (d.id || "").length * 5.2 + 6;
    const h = 12;
    return { x: (d.x || 0) + (d.size || 6) + 4, y: d.y || 0, w, h };
  }

  function boxesOverlap(a, b) {
    return !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h / 2 < b.y - b.h / 2 || b.y + b.h / 2 < a.y - a.h / 2);
  }

  function updateLabelVisibility(k) {
    if (k != null) currentZoomK = k;
    if (!renderer.nodeSel || renderer.nodeSel.empty()) return;

    const data = renderer.nodeSel.data();
    const rootId = model.rootId;
    // Sort: root → shallower depth → larger size → higher degree
    const candidates = data.slice().sort((a, b) => {
      if (a.id === rootId) return -1;
      if (b.id === rootId) return 1;
      const da = a.depth ?? 99,
        db = b.depth ?? 99;
      if (da !== db) return da - db;
      const ds = (b.size || 0) - (a.size || 0);
      if (ds) return ds;
      return (b.degree || 0) - (a.degree || 0);
    });

    // Parent tier: focus + depth ≤ 1, plus a few top hubs by size
    const parentIds = new Set();
    candidates.forEach((d) => {
      if (parentIds.size >= LABEL_PARENT_MAX) return;
      if (d.id === rootId || (d.depth ?? 99) <= 1) parentIds.add(d.id);
    });
    candidates.forEach((d) => {
      if (parentIds.size >= LABEL_PARENT_MAX) return;
      parentIds.add(d.id); // fill remaining slots with next-most-important
    });

    const childOp = childLabelOpacity(currentZoomK);
    const placed = [];
    const opacity = new Map();

    // 1) Place parent labels first (always visible when they fit)
    candidates.forEach((d) => {
      if (!parentIds.has(d.id)) return;
      const box = estimateLabelBox(d);
      if (!placed.some((p) => boxesOverlap(box, p))) {
        placed.push(box);
        opacity.set(d.id, 1);
      }
    });

    // 2) Place child labels when zoomed in
    if (childOp > 0.02) {
      candidates.forEach((d) => {
        if (opacity.has(d.id)) return;
        const box = estimateLabelBox(d);
        if (!placed.some((p) => boxesOverlap(box, p))) {
          placed.push(box);
          opacity.set(d.id, childOp);
        }
      });
    }

    renderer.nodeSel
      .select(".radialgraph-label")
      .attr("x", (d) => (d.size || 6) + 4)
      .style("opacity", (d) => opacity.get(d.id) || 0);
  }

  layout.onTick(() => {
    renderer.tick();
    updateLabelVisibility();
  });

  // =======================================================================
  // Node info panel — bottom slide-up sheet shown when a node is tapped.
  // Section 1: general stats. Section 2: a SHAP-like breakdown of PageRank
  // explaining WHY the node scores as it does, in terms of which neighbors'
  // own importance is "flowing into" it.
  // =======================================================================
  const METRIC_LABELS = {
    degree: "Degree",
    betweenness: "Betweenness",
    closeness: "Closeness",
    pagerank: "PageRank",
    hub: "Hub",
    authority: "Authority",
  };

  let selectedNodeId = null;
  const nodePanel = document.getElementById("nodePanel");
  const nodePanelTitle = document.getElementById("nodePanelTitle");
  const nodePanelSub = document.getElementById("nodePanelSub");
  const nodeStatsGrid = document.getElementById("nodeStatsGrid");
  const nodeImportance = document.getElementById("nodeImportance");
  const nodePanelClose = document.getElementById("nodePanelClose");

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  }

  function formatMetric(key, v) {
    if (v == null || Number.isNaN(v)) return "—";
    if (key === "degree") return String(v);
    return v.toFixed(v < 1 ? 3 : 2);
  }

  // Decompose this node's PageRank into: the flat "random jump" base term,
  // plus each in-network neighbor's contribution (damping * neighbor's own
  // PageRank / neighbor's degree). Contributions beyond the top few are
  // bucketed into "Community" (same-community neighbors) and "Other"
  // (different-community neighbors + the base term) — similar in spirit to
  // a SHAP breakdown: a small number of named drivers, plus grouped rest.
  function computeImportanceBreakdown(node) {
    const d = 0.85;
    const n = model.nodesById.size || 1;
    const teleport = (1 - d) / n;
    const neighborIds = currentFilteredAdj.get(node.id) || [];
    const contributions = neighborIds.map((nb) => {
      const nbNode = model.nodesById.get(nb);
      const nbDeg = (currentFilteredAdj.get(nb) || []).length || 1;
      return { id: nb, node: nbNode, value: (d * ((nbNode && nbNode.pagerank) || 0)) / nbDeg };
    });
    const neighborTotal = contributions.reduce((s, c) => s + c.value, 0);
    const denom = teleport + neighborTotal || 1;

    contributions.sort((a, b) => b.value - a.value);
    const TOP_N = 3;
    const top = contributions.slice(0, TOP_N).filter((c) => c.value > 1e-9);
    const rest = contributions.slice(TOP_N);
    const communitySum = rest.filter((c) => c.node && c.node.community === node.community).reduce((s, c) => s + c.value, 0);
    const otherSum = rest.filter((c) => !c.node || c.node.community !== node.community).reduce((s, c) => s + c.value, 0) + teleport;

    const items = top.map((c) => ({ label: c.id, pct: (c.value / denom) * 100, kind: "neighbor" }));
    if (communitySum > 1e-9) items.push({ label: "Community", pct: (communitySum / denom) * 100, kind: "community" });
    if (otherSum > 1e-9) items.push({ label: "Other", pct: (otherSum / denom) * 100, kind: "other" });
    return items;
  }

  function renderNodeStats(node) {
    const rows = ["degree", "betweenness", "closeness", "pagerank", "hub", "authority"]
      .map(
        (key) => `
        <div class="node-stat">
          <div class="label">${METRIC_LABELS[key]}</div>
          <div class="value">${formatMetric(key, node[key])}</div>
        </div>`,
      )
      .join("");
    const extra = `
      <div class="node-stat">
        <div class="label">Community</div>
        <div class="value">${node.community != null ? "C" + node.community : "—"}</div>
      </div>
      <div class="node-stat">
        <div class="label">Connections</div>
        <div class="value">${(currentFilteredAdj.get(node.id) || []).length}</div>
      </div>`;
    nodeStatsGrid.innerHTML = rows + extra;
  }

  function renderImportance(node) {
    const items = computeImportanceBreakdown(node);
    const pr = node.pagerank || 0;
    let html = `
      <div class="imp-title">Why this node is important</div>
      <div class="imp-metric"><span class="metric-name">PageRank</span><span class="metric-value">${pr.toFixed(3)}</span></div>
      <div class="imp-title">Top contributing neighbors</div>`;
    if (!items.length) {
      html += `<div class="node-importance-empty">No incoming contributions under the current edge filter.</div>`;
    } else {
      html += items
        .map((it) => {
          const barClass = it.kind === "community" ? "community" : it.kind === "other" ? "other" : "";
          const pct = Math.max(0, Math.min(100, it.pct));
          return `
          <div class="contrib-row">
            <div class="contrib-label-row"><span>${escapeHtml(it.label)}</span><span class="contrib-pct">${pct.toFixed(0)}%</span></div>
            <div class="contrib-bar-track"><div class="contrib-bar-fill ${barClass}" style="width:${pct}%"></div></div>
          </div>`;
        })
        .join("");
    }
    nodeImportance.innerHTML = html;
  }

  function showNodePanel(d) {
    const node = model.nodesById.get(d.id) || d;
    selectedNodeId = node.id;
    nodePanelTitle.textContent = node.tooltip || node.id;
    const parts = [];
    parts.push(node.id === model.rootId ? "focus node" : `hop depth ${node.depth != null ? node.depth : "—"}`);
    if (node.community != null) parts.push(`community C${node.community}`);
    nodePanelSub.textContent = parts.join(" · ");
    renderNodeStats(node);
    renderImportance(node);
    nodePanel.classList.add("open");
  }

  function closeNodePanel() {
    selectedNodeId = null;
    nodePanel.classList.remove("open");
  }

  if (nodePanelClose) nodePanelClose.addEventListener("click", closeNodePanel);

  const expandAllBtn = document.getElementById("expandAllBtn") || { textContent: "", disabled: false, addEventListener: function () {} };
  const rippleBtn = document.getElementById("rippleBtn") || { textContent: "", disabled: false, addEventListener: function () {} };
  let allExpanded = false;
  let rippleTimer = null;
  let rippleActive = false;

  let showCrossLinks = true;
  // Independent checkboxes: any combination of 'outbound' / 'inbound' /
  // 'bidirectional' may be active at once. Default: all checked (full network).
  let edgeDirFilter = new Set(["outbound", "inbound", "bidirectional"]);
  // When true, nodes left with no visible edges after the filters above
  // are applied get dropped from the render entirely (the focus node is
  // always kept, even if it currently has no visible edges).
  let hideIsolatedNodes = false;

  // Filter visible edges. Cross-link filter keeps only BFS tree edges.
  // Direction filter checks each edge against the checked categories:
  //   bidirectional — mutual edges
  //   outbound      — one-way edges directed away from focus
  //   inbound       — one-way edges directed toward focus
  // A one-way edge between two same-depth nodes is ambiguous, so it is
  // shown as long as either "outbound" or "inbound" is checked.
  function filterLinks(visLinks, parentOf, depths) {
    let links = visLinks;
    if (!showCrossLinks) {
      // Keep only BFS tree edges (parent → child) — drops cross-links that cause hairballs
      links = links.filter((e) => {
        const s = e.source,
          t = e.target;
        return parentOf.get(t) === s || parentOf.get(s) === t;
      });
    }
    return links.filter((e) => {
      if (e.relation === "mutual") return edgeDirFilter.has("bidirectional");
      const ds = depths.get(e.source) ?? 99;
      const dt = depths.get(e.target) ?? 99;
      if (ds === dt) return edgeDirFilter.has("outbound") || edgeDirFilter.has("inbound");
      if (ds < dt) return edgeDirFilter.has("outbound");
      return edgeDirFilter.has("inbound");
    });
  }

  // Builds the actual set of nodes/links to render for the current focus,
  // after edge filtering and (optionally) dropping now-edgeless nodes.
  // Shared by update() and toggleTheme() so both stay in sync.
  function getRenderGraph() {
    const { nodes: visNodes, links: visLinks, parentOf, visibleIds } = model.getVisibleGraph();
    const depths = new Map(visNodes.map((n) => [n.id, n.depth]));
    const links = filterLinks(visLinks, parentOf, depths);
    applyEdgeStyles(links);
    let nodes = visNodes;
    if (hideIsolatedNodes) {
      const connected = new Set();
      links.forEach((e) => {
        connected.add(e.source);
        connected.add(e.target);
      });
      nodes = visNodes.filter((n) => n.id === model.rootId || connected.has(n.id));
    }
    return { nodes, links, parentOf, depths, visibleIds };
  }

  function update() {
    const { nodes, links, parentOf } = getRenderGraph();
    applyNodeColors(nodes);
    applyNodeSizes(nodes);
    layout.simulation.force("collide").radius((d) => d.size + 3);
    layout.applyUpdate({
      nodes,
      links,
      parentOf,
      previousIds,
      rootId: model.rootId,
      nodeById: model.nodesById,
    });
    renderer.render(nodes, links, (id) => model.hasHiddenNeighbors(id));
    updateLabelVisibility();
    // Re-apply search highlight after keyed join rebuilds the DOM
    if (highlightedId) {
      renderer.nodeSel.classed("search-hit", (d) => d.id === highlightedId);
    }
    // Track what was actually rendered (not the full expanded frontier) so a
    // node hidden for having no edges is treated as "new" if it later gains one.
    previousIds = new Set(nodes.map((n) => n.id));
  }

  // Focus / re-root: make `id` the new ego, reset expansion, re-seed layout
  function reroot(id) {
    if (id === model.rootId) return;
    const oldRoot = model.nodesById.get(model.rootId);
    if (oldRoot) {
      oldRoot.fx = null;
      oldRoot.fy = null;
    }

    if (!model.setRoot(id)) return;

    // Place new root at origin; treat all nodes as "new" so seeding runs cleanly
    const root = model.nodesById.get(id);
    if (root) {
      root.x = 0;
      root.y = 0;
      root.vx = 0;
      root.vy = 0;
      if (layout.localMode) {
        root.fx = 0;
        root.fy = 0;
      } else {
        root.fx = null;
        root.fy = null;
      }
    }
    previousIds = new Set();
    allExpanded = false;
    expandAllBtn.textContent = "Expand all";
    rippleActive = false;
    clearTimeout(rippleTimer);
    rippleBtn.disabled = false;
    rippleBtn.textContent = "Ripple expand";
    renderer.clearGhosts();
    // Outbound/inbound direction is relative to hop-depth from the focus,
    // so re-rooting changes which edges count toward each category.
    recomputeMetrics();
    flowCache.key = null; // home-source flow depends on the focus
    stopFlowAnimation();
    update();
    if (isFlowMode()) startFlowAnimation();
    // Strong restart so rings re-form around the new focus
    layout.simulation.alpha(0.9).restart();
  }

  const interaction = new Interaction({
    svg: renderer.svg,
    g: renderer.g,
    simulation: layout.simulation,
    tooltip,
    getRootId: () => model.rootId,
    isLocalMode: () => layout.localMode,
    onToggle: (d) => {
      model.toggle(d.id);
      // Recompute network statistics for the currently-expanded frontier
      recomputeMetrics();
      flowCache.key = null;
      stopFlowAnimation();
      update();
      if (isFlowMode()) startFlowAnimation();
    },
    onReroot: (d) => reroot(d.id),
    onShowGhosts: (d) => {
      const hidden = model.hiddenNeighbors(d.id);
      if (hidden.length) renderer.showGhosts(d, hidden);
    },
    onHideGhosts: () => renderer.clearGhosts(),
    onZoom: (k) => updateLabelVisibility(k),
    onSelect: (d) => showNodePanel(d),
  });

  update();

  const _resetRootBtn = document.getElementById("resetRootBtn");
  if (_resetRootBtn) _resetRootBtn.addEventListener("click", () => reroot(payload.rootId || rootId));

  // —— Search & jump ——
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");
  let searchActiveIndex = -1;
  let searchMatches = [];

  function clearSearchHighlight() {
    highlightedId = null;
    if (renderer.nodeSel) renderer.nodeSel.classed("search-hit", false);
  }

  function highlightNode(id) {
    highlightedId = id;
    if (renderer.nodeSel) renderer.nodeSel.classed("search-hit", (d) => d.id === id);
  }

  // Clear search ring / node panel only when user clicks empty canvas
  interaction.onBackgroundClick = () => {
    clearSearchHighlight();
    closeNodePanel();
  };

  function jumpToNode(id) {
    if (!model.nodesById.has(id)) return;
    highlightedId = id; // set before update so re-render keeps the class
    // Reveal shortest path from current root so the node is visible
    model.revealPath(id);
    allExpanded = false;
    expandAllBtn.textContent = "Expand all";
    // Recompute metrics for the new expanded frontier and refresh visuals
    recomputeMetrics();
    flowCache.key = null;
    stopFlowAnimation();
    update();
    highlightNode(id);

    // Do not pan/zoom the viewport when jumping to a search result. Keep
    // the current view as-is but reveal the node and highlight it so the
    // user can spot it within the current context.

    searchResults.classList.remove("open");
    searchInput.value = id;
    searchInput.blur();
  }

  function renderSearchResults(query) {
    const q = query.trim().toLowerCase();
    searchActiveIndex = -1;
    if (!q) {
      searchMatches = [];
      searchResults.innerHTML = "";
      searchResults.classList.remove("open");
      return;
    }
    // Rank: prefix matches first, then substring; prefer shorter ids
    const all = Array.from(model.nodesById.keys());
    searchMatches = all
      .filter((id) => id.toLowerCase().includes(q))
      .sort((a, b) => {
        const al = a.toLowerCase(),
          bl = b.toLowerCase();
        const ap = al.startsWith(q) ? 0 : 1;
        const bp = bl.startsWith(q) ? 0 : 1;
        if (ap !== bp) return ap - bp;
        return a.length - b.length || a.localeCompare(b);
      })
      .slice(0, 12);

    if (!searchMatches.length) {
      searchResults.innerHTML = '<div class="search-item" style="opacity:0.5;cursor:default">No matches</div>';
      searchResults.classList.add("open");
      return;
    }
    searchResults.innerHTML = searchMatches
      .map((id, i) => {
        const n = model.nodesById.get(id);
        const meta = `deg ${n.degree}` + (n.community != null ? ` · c${n.community}` : "");
        return `<div class="search-item" data-id="${id}" data-idx="${i}">${id}<div class="meta">${meta}</div></div>`;
      })
      .join("");
    searchResults.classList.add("open");
  }

  searchInput.addEventListener("input", () => renderSearchResults(searchInput.value));
  searchInput.addEventListener("focus", () => {
    if (searchInput.value.trim()) renderSearchResults(searchInput.value);
  });
  searchInput.addEventListener("keydown", (e) => {
    if (!searchResults.classList.contains("open") || !searchMatches.length) {
      if (e.key === "Enter" && searchInput.value.trim()) {
        // Exact or first match
        const q = searchInput.value.trim();
        const exact = model.nodesById.has(q) ? q : searchMatches[0] || Array.from(model.nodesById.keys()).find((id) => id.toLowerCase() === q.toLowerCase());
        if (exact) jumpToNode(exact);
      }
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      searchActiveIndex = Math.min(searchMatches.length - 1, searchActiveIndex + 1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      searchActiveIndex = Math.max(0, searchActiveIndex - 1);
    } else if (e.key === "Enter") {
      e.preventDefault();
      const id = searchMatches[searchActiveIndex >= 0 ? searchActiveIndex : 0];
      if (id) jumpToNode(id);
      return;
    } else if (e.key === "Escape") {
      searchResults.classList.remove("open");
      searchInput.blur();
      return;
    } else {
      return;
    }
    searchResults.querySelectorAll(".search-item").forEach((el, i) => {
      el.classList.toggle("active", i === searchActiveIndex);
      if (i === searchActiveIndex) el.scrollIntoView({ block: "nearest" });
    });
  });
  searchResults.addEventListener("mousedown", (e) => {
    // mousedown so we fire before input blur closes the list
    const item = e.target.closest(".search-item");
    if (!item || !item.dataset.id) return;
    e.preventDefault();
    jumpToNode(item.dataset.id);
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-wrap")) searchResults.classList.remove("open");
  });

  // —— Theme (button + T key) ——
  function toggleTheme() {
    const isLight = document.body.classList.toggle("light");
    themeBtn.textContent = isLight ? "Theme: Light" : "Theme: Dark";
    const { nodes, links } = getRenderGraph();
    applyNodeColors(nodes);
    applyNodeSizes(nodes);
    renderer.render(nodes, links, (id) => model.hasHiddenNeighbors(id));
  }
  const themeBtn = document.getElementById("themeBtn");
  if (themeBtn) themeBtn.addEventListener("click", toggleTheme);
  window.addEventListener("keydown", (e) => {
    if (e.key === "t" || e.key === "T") {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      toggleTheme();
    }
  });

  // —— Node color mode ——
  // Dual colorMode/sizeMode radios (legacy) OR single statMetric radio
  // (d3graph-aligned): picking a metric drives BOTH color and size together.
  function applyStatMetric(value) {
    if (value === "user_default" || value === "default" || !value) {
      colorMode = "default";
      sizeMode = "default";
    } else if (value === "node_proba") {
      // Significance: color by p-value (handled in applyNodeColors via node_proba),
      // size by (1 - p) so more significant nodes render larger.
      colorMode = "node_proba";
      sizeMode = "node_proba";
    } else if (value === "network_clustering") {
      colorMode = "community";
      sizeMode = "default";
    } else {
      // Map d3graph field names → v11 metric keys
      const map = {
        node_pagerank: "pagerank",
        node_hits_hub: "hub",
        node_hits_authority: "authority",
        node_degree_centrality: "degree",
        node_closeness_centrality: "closeness",
        node_betweenness_centrality: "betweenness",
        pagerank: "pagerank",
        hub: "hub",
        authority: "authority",
        degree: "degree",
        closeness: "closeness",
        betweenness: "betweenness",
        depth: "depth",
        community: "community",
      };
      const key = map[value] || value;
      colorMode = key;
      sizeMode = METRIC_KEYS.has(key) ? key : "default";
    }
    update();
    layout.simulation.alpha(0.5).restart();
  }

  document.querySelectorAll('input[name="statMetric"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      applyStatMetric(radio.value);
    });
  });
  // Keep legacy dual radios working if present in the markup
  document.querySelectorAll('input[name="colorMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      colorMode = radio.value;
      update();
    });
  });
  document.querySelectorAll('input[name="sizeMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      sizeMode = radio.value;
      update();
      layout.simulation.alpha(0.5).restart();
    });
  });

  // —— Layout mode (radios) ——
  const ringSpacingSlider = document.getElementById("ringSpacingSlider");
  const ringSpacingVal = document.getElementById("ringSpacingVal");
  const autoRingSpacingToggle = document.getElementById("autoRingSpacingToggle");
  const crossLinksToggle = document.getElementById("crossLinksToggle");

  function syncRingSpacingControls() {
    const disabled = !layout.localMode || autoRingSpacingToggle.checked;
    ringSpacingSlider.disabled = disabled;
    ringSpacingSlider.style.opacity = disabled ? "0.45" : "1";
  }

  document.querySelectorAll('input[name="layoutMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      layout.localMode = radio.value === "rings";
      layout.setMode(layout.localMode, model.nodesById.get(model.rootId));
      layout.simulation.alpha(0.9).restart();
      syncRingSpacingControls();
    });
  });

  ringSpacingSlider.addEventListener("input", () => {
    const v = +ringSpacingSlider.value;
    ringSpacingVal.textContent = v;
    layout.ringSpacing = v;
    if (layout.localMode) {
      layout.setMode(true, model.nodesById.get(model.rootId));
      layout.simulation.alpha(0.6).restart();
    }
  });

  autoRingSpacingToggle.addEventListener("change", () => {
    layout.useAutoRingSpacing = autoRingSpacingToggle.checked;
    syncRingSpacingControls();
    if (layout.localMode) {
      // Recompute radii (if turning auto on) or fall back to the flat
      // multiplier (if turning it off) and re-settle.
      const { nodes: visNodes } = model.getVisibleGraph();
      if (layout.useAutoRingSpacing) layout.ringRadii = layout._computeAutoRingRadii(visNodes);
      layout.setMode(true, model.nodesById.get(model.rootId));
      layout.simulation.alpha(0.6).restart();
    }
  });

  crossLinksToggle.addEventListener("change", () => {
    showCrossLinks = crossLinksToggle.checked;
    update();
    layout.simulation.alpha(0.4).restart();
  });

  const hideIsolatedToggle = document.getElementById("hideIsolatedToggle");
  hideIsolatedToggle.addEventListener("change", () => {
    hideIsolatedNodes = hideIsolatedToggle.checked;
    update();
    layout.simulation.alpha(0.4).restart();
  });

  document.querySelectorAll('input[name="edgeDirFilter"]').forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) edgeDirFilter.add(checkbox.value);
      else edgeDirFilter.delete(checkbox.value);
      // Edge filter changed → statistics (size/color) are based on the
      // filtered network, so recompute them before re-rendering.
      // Diffusion paths also depend on which edges remain, so invalidate flow.
      recomputeMetrics();
      flowCache.key = null;
      stopFlowAnimation();
      update();
      if (isFlowMode()) startFlowAnimation();
      layout.simulation.alpha(0.4).restart();
    });
  });

  document.querySelectorAll('input[name="edgeStatMode"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      edgeStatMode = radio.value;
      flowCache.key = null; // force recompute for new mode
      stopFlowAnimation();
      update();
      if (isFlowMode()) startFlowAnimation();
    });
  });

  syncRingSpacingControls();

  // —— Expand all / collapse all ——
  if (expandAllBtn)
    expandAllBtn.addEventListener("click", () => {
      allExpanded = !allExpanded;
      if (allExpanded) {
        model.expandAll();
        expandAllBtn.textContent = "Collapse all";
      } else {
        model.collapseAll();
        expandAllBtn.textContent = "Expand all";
      }
      rippleActive = false;
      rippleBtn.textContent = "Ripple expand";
      renderer.clearGhosts();
      // Recompute metrics after changing expansion
      recomputeMetrics();
      flowCache.key = null;
      stopFlowAnimation();
      update();
      if (isFlowMode()) startFlowAnimation();
    });

  // —— Ripple expand (press again → collapse all) ——
  const RIPPLE_DELAY_MS = cfg.rippleDelayMs != null ? cfg.rippleDelayMs : 900;
  function rippleExpandFrom(startId, delayMs = RIPPLE_DELAY_MS) {
    clearTimeout(rippleTimer);
    const layers = model.bfsLayersFrom(startId);
    let i = 0;
    const step = () => {
      if (i >= layers.length) {
        rippleBtn.disabled = false;
        rippleBtn.textContent = "Collapse all";
        return;
      }
      model.expandNodes(layers[i]);
      // After expanding this layer, recompute metrics so node/edge styles update
      recomputeMetrics();
      flowCache.key = null;
      stopFlowAnimation();
      update();
      if (isFlowMode()) startFlowAnimation();
      i++;
      if (i < layers.length) rippleTimer = setTimeout(step, delayMs);
      else {
        rippleBtn.disabled = false;
        rippleBtn.textContent = "Collapse all";
      }
    };
    step();
  }

  rippleBtn.addEventListener("click", () => {
    if (rippleActive) {
      // Second press: stop any in-flight ripple and collapse everything
      clearTimeout(rippleTimer);
      rippleActive = false;
      allExpanded = false;
      expandAllBtn.textContent = "Expand all";
      model.collapseAll();
      renderer.clearGhosts();
      rippleBtn.disabled = false;
      rippleBtn.textContent = "Ripple expand";
      update();
      return;
    }
    rippleActive = true;
    allExpanded = false;
    expandAllBtn.textContent = "Expand all";
    renderer.clearGhosts();
    model.collapseAll();
    update();
    rippleBtn.disabled = true;
    rippleBtn.textContent = "Rippling…";
    rippleExpandFrom(model.rootId);
  });

  function resizeGraph() {
    const w = containerEl.clientWidth || window.innerWidth;
    const h = containerEl.clientHeight || window.innerHeight;
    renderer.resize(w, h);
  }

  window.addEventListener("resize", resizeGraph);

  // —— Side panel show / hide ——
  const panelToggle = document.getElementById("panelToggle");
  if (panelToggle) {
    panelToggle.addEventListener("click", () => {
      const collapsed = document.body.classList.toggle("panel-collapsed");
      panelToggle.textContent = collapsed ? "»" : "«";
      panelToggle.title = collapsed ? "Show menu" : "Hide menu";
      setTimeout(resizeGraph, 300);
    });
  }

  window.__demo = { model, layout, renderer, update, rippleExpandFrom, reroot, jumpToNode, updateLabelVisibility };
})();
