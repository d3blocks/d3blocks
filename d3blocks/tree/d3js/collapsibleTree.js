<script>HTMLWidgets.widget({

  name: 'collapsibleTree',
  type: 'output',

  factory: function(el, width, height) {

    var i = 0,
    duration = 750,
    root = {},
    options = {},
    treemap;

    // Optionally enable zooming, and limit to 1/5x or 5x of the original viewport
    var zoom = d3.zoom()
    .scaleExtent([1/5, 5])
    .on('zoom', function () {
      svg.attr('transform', d3.event.transform)
    })

    // create our tree object and bind it to the element
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select(el).append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g');

    // Define the div for the tooltip
    var tooltip = d3.select(el).append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

    // Translate so the visible tree bbox is centered in the svg viewport.
    // Horizontal tree: d.y = depth (x-axis), d.x = sibling rank (y-axis).
    function centerTree() {
      if (!root || typeof root.descendants !== 'function') return;
      var nodes = root.descendants();
      if (!nodes.length) return;

      var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      nodes.forEach(function(d) {
        if (d.x < minX) minX = d.x;
        if (d.x > maxX) maxX = d.x;
        if (d.y < minY) minY = d.y;
        if (d.y > maxY) maxY = d.y;
      });

      // Padding for node radius + labels
      var pad = 40;
      minX -= pad;
      maxX += pad;
      minY -= pad;
      maxY += pad + 80;

      var treeW = Math.max(maxY - minY, 1);
      var treeH = Math.max(maxX - minX, 1);
      var svgEl = d3.select(el).select('svg');
      var w = +svgEl.attr('width') || width;
      var h = +svgEl.attr('height') || height;
      var tx = (w - treeW) / 2 - minY;
      var ty = (h - treeH) / 2 - minX;

      if (options.zoomable) {
        svgEl.call(zoom.transform, d3.zoomIdentity.translate(tx, ty));
      } else {
        svg.attr('transform', 'translate(' + tx + ',' + ty + ')');
      }
    }

    function update(source) {

      // Assigns the x and y position for the nodes
      var treeData = treemap(root);

      // Compute the new tree layout.
      var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);

      // Normalize for fixed-depth.
      nodes.forEach(function(d) {d.y = d.depth * options.linkLength});

      // ****************** Nodes section ***************************

      // Update the nodes...
      var node = svg.selectAll('g.node')
      .data(nodes, function(d) {return d.id || (d.id = ++i); });

      // Enter any new modes at the parent's previous position.
      var nodeEnter = node.enter().append('g')
      .attr('class', 'node')
      .attr('transform', function(d) {
        return 'translate(' + source.y0 + ',' + source.x0 + ')';
      })
      .on('click', click);

      // Add tooltips, if specified in options
      if (options.tooltip) {
        nodeEnter = nodeEnter
        .on('mouseover', mouseover)
        .on('mouseout', mouseout);
      }

      // Enable zooming, if specified
      if (options.zoomable) d3.select(el).select('svg').call(zoom)

      // Add Circle for the nodes
      nodeEnter.append('circle')
      .attr('class', 'node')
      .attr('r', 1e-6)
      .style('fill', function(d) { return d.data.node_color || (d._children ? options.fill : '#fff'); })
      .style('stroke-width', function(d) { return d.data.edge_size || (d._children ? 3 : 1) ;} )
      .style('stroke', function(d) { return d.data.edge_color ;} )
      .style('opacity', function(d) { return d.data.node_opacity ;} )
      ;
        
      // Add labels for the nodes
      nodeEnter.append('text')
      .attr('dy', '.35em')
      .attr('x', function(d) {
        // Scale padding for label to the size of node
        var padding = (d.data.node_size || 10) + 3
        return d.children || d._children ? -1 * padding : padding;
      })
      .attr('text-anchor', function(d) {
        return d.children || d._children ? 'end' : 'start';
      })
      .style('font-size', options.fontSize + 'px')
      .text(function(d) { return d.data.name; });

      // UPDATE
      var nodeUpdate = nodeEnter.merge(node);

      // Transition to the proper position for the node
      nodeUpdate.transition()
      .duration(duration)
      .attr('transform', function(d) {
        return 'translate(' + d.y + ',' + d.x + ')';
      });

      // Update the node attributes and style
      nodeUpdate.select('circle.node')
      .attr('r', function(d) { return d.data.node_size || 10; }) // default radius is 10
      .style('fill', function(d) {return d.data.node_color || (d._children ? options.fill : '#fff'); })
      .style('stroke-width', function(d) { return d.data.edge_size || (d._children ? 3 : 1) ;} )
      .style('stroke', function(d) { return d.data.edge_color ;} )
      .style('opacity', function(d) { return d.data.node_opacity ;} )
      .attr('cursor', 'pointer');

      // Re-apply font size so the slider (and any option change) takes effect
      // on existing labels, not only on newly entered nodes.
      nodeUpdate.select('text')
      .style('font-size', options.fontSize + 'px');


      // Remove any exiting nodes
      var nodeExit = node.exit().transition()
      .duration(duration)
      .attr('transform', function(d) {
        return 'translate(' + source.y + ',' + source.x + ')';
      })
      .remove();

      // On exit reduce the node circles size to 0
      nodeExit.select('circle')
      .attr('r', 1e-6);

      // On exit reduce the opacity of text labels
      nodeExit.select('text')
      .style('fill-opacity', 1e-6);

      // ****************** links section ***************************

      // Update the links...
      var link = svg.selectAll('path.link')
      .data(links, function(d) { return d.id; });

      // Enter any new links at the parent's previous position.
      var linkEnter = link.enter().insert('path', 'g')
      .attr('class', 'link')
      // Potentially, this may one day be mappable
      // .style('stroke-width', function(d) { return d.data.linkWidth || 1 })
      .attr('d', function(d){
        var o = { x: source.x0, y: source.y0 }
        return diagonal(o, o)
      });

      // UPDATE
      var linkUpdate = linkEnter.merge(link);

      // Transition back to the parent element position
      linkUpdate.transition()
      .duration(duration)
      .attr('d', function(d){ return diagonal(d, d.parent) });

      // Remove any exiting links
      var linkExit = link.exit().transition()
      .duration(duration)
      .attr('d', function(d) {
        var o = {x: source.x, y: source.y}
        return diagonal(o, o)
      })
      .remove();

      // Store the old positions for transition.
      nodes.forEach(function(d){
        d.x0 = d.x;
        d.y0 = d.y;
      });

      // Creates a curved (diagonal) path from parent to the child nodes
      function diagonal(s, d) {

        path = 'M ' + s.y + ' ' + s.x + ' C ' +
        (s.y + d.y) / 2 + ' ' + s.x + ', ' +
        (s.y + d.y) / 2 + ' ' + d.x + ', ' +
        d.y + ' ' + d.x;

        return path
      }

      // Toggle children on click.
      function click(d) {
        if (d.children) {
          d._children = d.children;
          d.children = null;
        } else {
          d.children = d._children;
          d._children = null;
        }
        update(d);
        // Hide the tooltip after clicking
        tooltip.transition()
        .duration(100)
        .style('opacity', 0)
        // Update inputs, if applicable
        if (options.input) {
          var nest = {},
          obj = d;
          // Navigate up the list and recursively find parental nodes
          for (var n = d.depth; n > 0; n--) {
            nest[options.hierarchy[n-1]] = obj.data.name
            obj = obj.parent
          }
          Shiny.onInputChange(options.input, nest)
        }
      }

      // Show tooltip on mouseover
      function mouseover(d) {
        tooltip.transition()
        .duration(200)
        .style('opacity', .9);

        // Show either a constructed tooltip, or override with one from the data
        //tooltip.html( d.data.tooltip || d.data.name + '<br>' +  options.attribute + ': ' + d.data.WeightOfNode )
        tooltip.html( d.data.tooltip )
        // Make the tooltip font size just a little bit bigger
        .style('font-size', (options.fontSize + 1) + 'px')
        .style('left', (d3.event.layerX) + 'px')
        .style('top', (d3.event.layerY - 30) + 'px');
      }
      // Hide tooltip on mouseout
      function mouseout(d) {
        tooltip.transition()
        .duration(500)
        .style('opacity', 0);
      }
    }

    return {
      renderValue: function(x) {
        // Assigns parent, children, height, depth
        root = d3.hierarchy(x.data, function(d) { return d.children; });
        root.x0 = height / 2;
        root.y0 = 0;

        // Attach options as a property of the instance
        options = x.options;

        // Update the canvas with the new dimensions
        svg = svg.attr('transform', 'translate('
        + options.margin.left + ',' + options.margin.top + ')')

        // width and height, corrected for margins
        var heightMargin = height - options.margin.top - options.margin.bottom,
        widthMargin = width - options.margin.left - options.margin.right;
        // declares a tree layout and assigns the size
        treemap = d3.tree().size([heightMargin, widthMargin])
        .separation(separationFun);

        // Calculate a reasonable link length, if not otherwise specified
        if (!options.linkLength) {
          options.linkResponsive = true
          options.linkLength = widthMargin / options.hierarchy.length
          if (options.linkLength < 10) {
            options.linkLength = 10 // Offscreen or too short
          }
        }

        // Optionally collapse after the second level
        if (options.collapsed) root.children.forEach(collapse);
        update(root);

        // Center the tree in the viewport on first render
        centerTree();

        // Collapse the node and all it's children
        function collapse(d) {
          if(d.children) {
            d._children = d.children
            d._children.forEach(collapse)
            d.children = null
          }
        }

        // Expose controls for the GUI panels
        window.__d3treeInstance = {
          root: root,
          options: options,
          update: update,
          svg: svg,
          centerTree: centerTree
        };
      },


      resize: function(width, height) {
        // Resize the canvas
        d3.select(el).select('svg')
        .attr('width', width)
        .attr('height', height);

        // width and height, corrected for margins
        var heightMargin = height - options.margin.top - options.margin.bottom,
        widthMargin = width - options.margin.left - options.margin.right;

        // Calculate a reasonable link length, if not originally specified
        if (options.linkResponsive) {
          options.linkLength = widthMargin / options.hierarchy.length
          if (options.linkLength < 10) {
            options.linkLength = 10 // Offscreen or too short
          }
        }
        // Update the treemap to fit the new canvas size
        treemap = d3.tree().size([heightMargin, widthMargin])
        .separation(separationFun);
        update(root)
      },
      // Make the instance properties available as a property of the widget
      svg: svg,
      root: root,
      options: options
    };
  }
});

function separationFun(a, b) {
  var height = a.data.node_size + b.data.node_size,
  // Scale distance to node_size, if defined
  distance = (height || 20) / 10;
  return (a.parent === b.parent ? 1 : distance);
};
</script>
