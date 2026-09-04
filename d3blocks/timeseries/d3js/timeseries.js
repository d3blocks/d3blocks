function timeseries(data, config) {
    // Responsive / fixed size
    var container = d3.select("#timeseries-container");
    if (container.empty()) {
        container = d3.select("body");
    }

    function getAvailableSize() {
        var main = document.getElementById("timeseries-main");
        var padL = 0, padT = 80;
        if (main) {
            var cs = window.getComputedStyle(main);
            padL = parseFloat(cs.paddingLeft) || 0;
            padT = parseFloat(cs.marginTop) || 80;
        }
        var availW = (config.WIDTH && config.WIDTH !== null) ? config.WIDTH : (window.innerWidth - padL - 20);
        var availH = (config.HEIGHT && config.HEIGHT !== null) ? config.HEIGHT : (window.innerHeight - padT - 40);
        return { w: Math.max(400, availW), h: Math.max(300, availH) };
    }

    var size = getAvailableSize();
    var margin = {top: 20, right: 220, bottom: 100, left: 60};
    var width = size.w - margin.left - margin.right;
    var height = size.h - margin.top - margin.bottom - 60; // leave room for context
    var height2 = 40;

    var parseDate = d3.time.format(config.DT_FORMAT).parse;

    function bisectCenter(a, x) {
        var i = d3.bisectLeft(a, x);
        return i > 0 && (a[i - 1] - x) > (x - a[i]) ? i - 1 : i;
    }

    var xScale = d3.time.scale().range([0, width]);
    var xScale2 = d3.time.scale().range([0, width]);
    var yScale = d3.scale.linear().range([height, 0]);

    var color = d3.scale.ordinal().range(config.COLOR);

    var xAxis = d3.svg.axis().scale(xScale).orient("bottom");
    var xAxis2 = d3.svg.axis().scale(xScale2).orient("bottom");
    var yAxis = d3.svg.axis().scale(yScale).orient("left");

    var currentInterp = "basis";
    var currentStroke = 1.5;

    var line = d3.svg.line()
        .interpolate(currentInterp)
        .x(function(d) { return xScale(d.date); })
        .y(function(d) { return yScale(d.rating); })
        .defined(function(d) { return d.rating != null && !isNaN(d.rating); });

    // Clear previous
    container.selectAll("*").remove();

    var svgRoot = container.append("svg")
        .attr("width", size.w)
        .attr("height", size.h);

    var svg = svgRoot.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Invisible rect for mouse tracking + wheel zoom
    var mouseTracker = svg.append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr("x", 0)
        .attr("y", 0)
        .attr("id", "mouse-tracker")
        .style("fill", "transparent")
        .style("pointer-events", "all");

    // Context (brush) at bottom
    var contextY = height + 40;
    var context = svg.append("g")
        .attr("transform", "translate(0," + contextY + ")")
        .attr("class", "context");

    svg.append("defs")
        .append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    // Data prep
    var columnNames = data[0].split(";").slice(1);
    color.domain(columnNames);

    var categories = columnNames.map(function(name, index) {
        return {
            name: name,
            values: data.slice(1).map(function(line) {
                var d = line.split(";");
                return {
                    date: parseDate(d[0]),
                    rating: Number(d[index + 1])
                };
            }),
            visible: index === 0
        };
    });

    var dates = data.slice(1).map(function(line) {
        return parseDate(line.split(";")[0]);
    });

    var fullXDomain = d3.extent(dates);
    xScale.domain(fullXDomain);
    yScale.domain([findMinY(categories), findMaxY(categories)]);
    xScale2.domain(xScale.domain());

    // Brush
    var brush = d3.svg.brush()
        .x(xScale2)
        .on("brush", brushed);

    context.append("g")
        .attr("class", "x axis1")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis2);

    var contextArea = d3.svg.area()
        .interpolate("monotone")
        .x(function(d) { return xScale2(d.date); })
        .y0(height2)
        .y1(0);

    context.append("path")
        .attr("class", "area")
        .attr("d", contextArea(categories[0].values))
        .attr("fill", "#F1F1F2");

    context.append("g")
        .attr("class", "x brush")
        .call(brush)
        .selectAll("rect")
        .attr("height", height2)
        .attr("fill", "#E6E7E8");

    // Main axes
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("class", "y-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("x", -10)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(config.TITLE || "");

    // Lines
    var issue = svg.selectAll(".issue")
        .data(categories)
        .enter().append("g")
        .attr("class", "issue");

    issue.append("path")
        .attr("class", "line")
        .style("pointer-events", "none")
        .attr("id", function(d) {
            return "line-" + d.name.replace(/ /g, "").replace(/\//g, "");
        })
        .attr("d", function(d) {
            return d.visible ? line(d.values) : null;
        })
        .attr("clip-path", "url(#clip)")
        .style("stroke", function(d) { return color(d.name); })
        .style("stroke-width", currentStroke);

    // Legend
    var legendSpace = Math.min(450, height) / Math.max(categories.length, 1);

    issue.append("rect")
        .attr("width", 10)
        .attr("height", 10)
        .attr("x", width + (margin.right / 3) - 15)
        .attr("y", function(d, i) { return legendSpace + i * legendSpace - 8; })
        .attr("fill", function(d) {
            return d.visible ? color(d.name) : "#F1F1F2";
        })
        .attr("class", "legend-box")
        .on("click", function(d) {
            d.visible = !d.visible;
            var minY = findMinY(categories);
            var maxY = findMaxY(categories);
            yScale.domain([minY, maxY]);
            svg.select(".y.axis").transition().call(yAxis);
            issue.select("path")
                .transition()
                .attr("d", function(d) { return d.visible ? line(d.values) : null; });
            issue.select("rect")
                .transition()
                .attr("fill", function(d) {
                    return d.visible ? color(d.name) : "#F1F1F2";
                });
        })
        .on("mouseover", function(d) {
            d3.select(this).transition().attr("fill", function(d) { return color(d.name); });
            d3.select("#line-" + d.name.replace(/ /g, "").replace(/\//g, ""))
                .transition().style("stroke-width", currentStroke + 1);
        })
        .on("mouseout", function(d) {
            d3.select(this).transition().attr("fill", function(d) {
                return d.visible ? color(d.name) : "#F1F1F2";
            });
            d3.select("#line-" + d.name.replace(/ /g, "").replace(/\//g, ""))
                .transition().style("stroke-width", currentStroke);
        });

    issue.append("text")
        .attr("class", "legend-text")
        .attr("x", width + (margin.right / 3))
        .attr("y", function(d, i) { return legendSpace + i * legendSpace; })
        .text(function(d) { return d.name; });

    // Hover line + tooltips
    var hoverLineGroup = svg.append("g").attr("class", "hover-line");
    var hoverLine = hoverLineGroup.append("line")
        .attr("id", "hover-line")
        .attr("x1", 10).attr("x2", 10)
        .attr("y1", 0).attr("y2", height + 10)
        .style("pointer-events", "none")
        .style("opacity", 1e-6);

    var hoverDate = hoverLineGroup.append("text")
        .attr("class", "hover-text")
        .attr("y", 30)
        .attr("x", width - 150);

    var focus = issue.select("g")
        .data(columnNames)
        .enter().append("g")
        .attr("class", "focus");

    focus.append("text")
        .attr("class", "tooltip")
        .attr("x", width + 15)
        .attr("y", function(d, i) { return legendSpace + i * legendSpace; });

    mouseTracker
        .on("mousemove", mousemove)
        .on("mouseout", function() {
            hoverDate.text(null);
            d3.select("#hover-line").style("opacity", 1e-6);
        })
        .on("dblclick", function() {
            resetZoom();
        });

    // Mouse wheel zoom on x
    mouseTracker.on("wheel.zoom", function() {
        d3.event.preventDefault();
        var mouse_x = d3.mouse(this)[0];
        var graph_x = xScale.invert(mouse_x);
        var domain = xScale.domain();
        var span = domain[1] - domain[0];
        var factor = d3.event.deltaY > 0 ? 1.15 : 0.85;
        var newSpan = span * factor;
        // Clamp
        var fullSpan = fullXDomain[1] - fullXDomain[0];
        if (newSpan > fullSpan) newSpan = fullSpan;
        if (newSpan < fullSpan / 1000) newSpan = fullSpan / 1000;
        var ratio = (graph_x - domain[0]) / span;
        var newStart = new Date(graph_x.getTime() - ratio * newSpan);
        var newEnd = new Date(newStart.getTime() + newSpan);
        if (newStart < fullXDomain[0]) {
            newStart = fullXDomain[0];
            newEnd = new Date(newStart.getTime() + newSpan);
        }
        if (newEnd > fullXDomain[1]) {
            newEnd = fullXDomain[1];
            newStart = new Date(newEnd.getTime() - newSpan);
        }
        xScale.domain([newStart, newEnd]);
        // Sync brush
        brush.extent([newStart, newEnd]);
        context.select(".x.brush").call(brush);
        redraw();
    });

    function mousemove() {
        var mouse_x = d3.mouse(this)[0];
        var graph_x = xScale.invert(mouse_x);
        var format = d3.time.format("%b %Y");
        hoverDate.text(format(graph_x));
        d3.select("#hover-line")
            .attr("x1", mouse_x)
            .attr("x2", mouse_x)
            .style("opacity", 1);

        var x0 = xScale.invert(d3.mouse(this)[0]);
        var i = bisectCenter(dates, x0);

        focus.select("text").text(function(columnName) {
            var cat = categories.find(function(c) { return c.name === columnName; });
            if (!cat || !cat.values[i]) return "";
            var v = cat.values[i].rating;
            return (v != null && !isNaN(v)) ? (+v).toFixed(3) : "";
        });
    }

    function brushed() {
        xScale.domain(brush.empty() ? xScale2.domain() : brush.extent());
        redraw();
    }

    function redraw() {
        svg.select(".x.axis").call(xAxis);
        var minY = findMinY(categories);
        var maxY = findMaxY(categories);
        yScale.domain([minY, maxY]);
        svg.select(".y.axis").call(yAxis);
        issue.select("path")
            .attr("d", function(d) {
                return d.visible ? line(d.values) : null;
            });
    }

    function findMinY(data) {
        var minYValues = data.map(function(d) {
            if (d.visible) {
                return d3.min(d.values, function(value) { return value.rating; });
            }
        });
        return d3.min([0].concat(minYValues.filter(function(v) { return v != null; })));
    }

    function findMaxY(data) {
        var maxYValues = data.map(function(d) {
            if (d.visible) {
                return d3.max(d.values, function(value) { return value.rating; });
            }
        });
        return d3.max(maxYValues);
    }

    function resetZoom() {
        xScale.domain(fullXDomain);
        brush.clear();
        context.select(".x.brush").call(brush);
        redraw();
    }

    // Public API
    var api = {
        setFontSize: function(px) {
            svgRoot.selectAll("text").style("font-size", px + "px");
            svg.select(".hover-text").style("font-size", Math.max(px * 2, 20) + "px");
        },
        setStrokeWidth: function(w) {
            currentStroke = w;
            issue.selectAll("path.line").style("stroke-width", w);
        },
        setInterpolation: function(name) {
            currentInterp = name;
            line.interpolate(name);
            issue.selectAll("path.line")
                .attr("d", function(d) {
                    return d.visible ? line(d.values) : null;
                });
        },
        resetZoom: resetZoom,
        setDarkMode: function(dark) {
            // Theme is mostly CSS-driven; force a redraw of axis colors if needed
            redraw();
        },
        resize: function() {
            size = getAvailableSize();
            width = size.w - margin.left - margin.right;
            height = size.h - margin.top - margin.bottom - 60;
            svgRoot.attr("width", size.w).attr("height", size.h);
            xScale.range([0, width]);
            xScale2.range([0, width]);
            yScale.range([height, 0]);
            mouseTracker.attr("width", width).attr("height", height);
            svg.select("#clip rect").attr("width", width).attr("height", height);
            context.attr("transform", "translate(0," + (height + 40) + ")");
            svg.select(".x.axis").attr("transform", "translate(0," + height + ")");
            // Reposition legend
            legendSpace = Math.min(450, height) / Math.max(categories.length, 1);
            issue.select("rect")
                .attr("x", width + (margin.right / 3) - 15)
                .attr("y", function(d, i) { return legendSpace + i * legendSpace - 8; });
            issue.select(".legend-text")
                .attr("x", width + (margin.right / 3))
                .attr("y", function(d, i) { return legendSpace + i * legendSpace; });
            focus.select("text")
                .attr("x", width + 15)
                .attr("y", function(d, i) { return legendSpace + i * legendSpace; });
            hoverLine.attr("y2", height + 10);
            hoverDate.attr("x", width - 150);
            redraw();
            context.select(".x.axis1").call(xAxis2);
            context.select(".area").attr("d", contextArea(categories[0].values));
            context.select(".x.brush").call(brush).selectAll("rect").attr("height", height2);
        }
    };

    // Apply initial fontsize if given
    if (config.FONTSIZE) {
        api.setFontSize(config.FONTSIZE);
    }

    return api;
}
