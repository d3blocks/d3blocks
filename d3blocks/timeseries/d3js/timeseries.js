function timeseries(data, config) {
    var container = d3.select("#timeseries-container");
    if (container.empty()) container = d3.select("body");

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
    // No right-side legend → smaller right margin
    var margin = {top: 20, right: 40, bottom: 100, left: 60};
    var width = size.w - margin.left - margin.right;
    var height = size.h - margin.top - margin.bottom - 60;
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

    container.selectAll("*").remove();
    var svgRoot = container.append("svg").attr("width", size.w).attr("height", size.h);
    var svg = svgRoot.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var mouseTracker = svg.append("rect")
        .attr("width", width).attr("height", height).attr("x", 0).attr("y", 0)
        .attr("id", "mouse-tracker").style("fill", "transparent").style("pointer-events", "all");

    var context = svg.append("g").attr("transform", "translate(0," + (height + 40) + ")").attr("class", "context");
    svg.append("defs").append("clipPath").attr("id", "clip").append("rect").attr("width", width).attr("height", height);

    var columnNames = data[0].split(";").slice(1);
    color.domain(columnNames);

    var categories = columnNames.map(function(name, index) {
        return {
            name: name,
            values: data.slice(1).map(function(line) {
                var d = line.split(";");
                return { date: parseDate(d[0]), rating: Number(d[index + 1]) };
            }),
            visible: true
        };
    });

    var dates = data.slice(1).map(function(line) { return parseDate(line.split(";")[0]); });
    var fullXDomain = d3.extent(dates);
    xScale.domain(fullXDomain);
    yScale.domain([findMinY(categories), findMaxY(categories)]);
    xScale2.domain(xScale.domain());

    var brush = d3.svg.brush().x(xScale2).on("brush", brushed);
    context.append("g").attr("class", "x axis1").attr("transform", "translate(0," + height2 + ")").call(xAxis2);
    var contextArea = d3.svg.area().interpolate("monotone")
        .x(function(d) { return xScale2(d.date); }).y0(height2).y1(0);
    context.append("path").attr("class", "area").attr("d", contextArea(categories[0].values)).attr("fill", "#F1F1F2");
    context.append("g").attr("class", "x brush").call(brush).selectAll("rect").attr("height", height2).attr("fill", "#E6E7E8");

    svg.append("g").attr("class", "x axis").attr("transform", "translate(0," + height + ")").call(xAxis);
    svg.append("g").attr("class", "y axis").call(yAxis)
        .append("text").attr("class", "y-label").attr("transform", "rotate(-90)")
        .attr("y", 6).attr("x", -10).attr("dy", ".71em").style("text-anchor", "end")
        .text(config.TITLE || "");

    var issue = svg.selectAll(".issue").data(categories).enter().append("g").attr("class", "issue");
    issue.append("path").attr("class", "line").style("pointer-events", "none")
        .attr("id", function(d) { return "line-" + d.name.replace(/ /g, "").replace(/\//g, ""); })
        .attr("d", function(d) { return d.visible ? line(d.values) : null; })
        .attr("clip-path", "url(#clip)")
        .style("stroke", function(d) { return color(d.name); })
        .style("stroke-width", currentStroke);

    // Hover vertical line (no right-side legend)
    var hoverLineGroup = svg.append("g").attr("class", "hover-line");
    var hoverLine = hoverLineGroup.append("line").attr("id", "hover-line")
        .attr("x1", 10).attr("x2", 10).attr("y1", 0).attr("y2", height + 10)
        .style("pointer-events", "none").style("opacity", 1e-6);

    var tooltipEl = document.getElementById("ts-tooltip");

    mouseTracker
        .on("mousemove", mousemove)
        .on("mouseout", function() {
            d3.select("#hover-line").style("opacity", 1e-6);
            if (tooltipEl) tooltipEl.classList.remove("visible");
        })
        .on("dblclick", function() { resetZoom(); });

    mouseTracker.on("wheel.zoom", function() {
        d3.event.preventDefault();
        var mouse_x = d3.mouse(this)[0];
        var graph_x = xScale.invert(mouse_x);
        var domain = xScale.domain();
        var span = domain[1] - domain[0];
        var factor = d3.event.deltaY > 0 ? 1.15 : 0.85;
        var newSpan = span * factor;
        var fullSpan = fullXDomain[1] - fullXDomain[0];
        if (newSpan > fullSpan) newSpan = fullSpan;
        if (newSpan < fullSpan / 1000) newSpan = fullSpan / 1000;
        var ratio = (graph_x - domain[0]) / span;
        var newStart = new Date(graph_x.getTime() - ratio * newSpan);
        var newEnd = new Date(newStart.getTime() + newSpan);
        if (newStart < fullXDomain[0]) { newStart = fullXDomain[0]; newEnd = new Date(newStart.getTime() + newSpan); }
        if (newEnd > fullXDomain[1]) { newEnd = fullXDomain[1]; newStart = new Date(newEnd.getTime() - newSpan); }
        xScale.domain([newStart, newEnd]);
        brush.extent([newStart, newEnd]);
        context.select(".x.brush").call(brush);
        redraw();
    });

    function mousemove() {
        var mouse_x = d3.mouse(this)[0];
        var graph_x = xScale.invert(mouse_x);
        d3.select("#hover-line").attr("x1", mouse_x).attr("x2", mouse_x).style("opacity", 1);

        var i = bisectCenter(dates, graph_x);
        var dateFmt = d3.time.format("%Y-%m-%d %H:%M");
        var rows = [];
        categories.forEach(function(cat) {
            if (!cat.visible || !cat.values[i]) return;
            var v = cat.values[i].rating;
            if (v == null || isNaN(v)) return;
            rows.push({
                name: cat.name,
                value: (+v).toFixed(3),
                color: color(cat.name)
            });
        });

        if (tooltipEl) {
            var html = '<div class="tt-date">' + dateFmt(graph_x) + '</div>';
            rows.forEach(function(r) {
                html += '<div class="tt-row"><span class="tt-swatch" style="background:' + r.color + '"></span>' +
                    r.name + ': <strong>' + r.value + '</strong></div>';
            });
            tooltipEl.innerHTML = html;
            tooltipEl.classList.add("visible");
            // Position near cursor (page coords)
            var evt = d3.event;
            var tx = evt.clientX + 16;
            var ty = evt.clientY + 16;
            // Keep on screen
            var tw = tooltipEl.offsetWidth || 160;
            var th = tooltipEl.offsetHeight || 80;
            if (tx + tw > window.innerWidth - 8) tx = evt.clientX - tw - 12;
            if (ty + th > window.innerHeight - 8) ty = evt.clientY - th - 12;
            tooltipEl.style.left = tx + "px";
            tooltipEl.style.top = ty + "px";
        }
    }

    function brushed() {
        xScale.domain(brush.empty() ? xScale2.domain() : brush.extent());
        redraw();
    }

    function redraw() {
        svg.select(".x.axis").call(xAxis);
        yScale.domain([findMinY(categories), findMaxY(categories)]);
        svg.select(".y.axis").call(yAxis);
        issue.select("path").attr("d", function(d) { return d.visible ? line(d.values) : null; });
        syncFilterCheckboxes();
    }

    function findMinY(data) {
        var vals = data.map(function(d) {
            if (d.visible) return d3.min(d.values, function(v) { return v.rating; });
        }).filter(function(v) { return v != null; });
        return d3.min([0].concat(vals));
    }
    function findMaxY(data) {
        return d3.max(data.map(function(d) {
            if (d.visible) return d3.max(d.values, function(v) { return v.rating; });
        }));
    }
    function resetZoom() {
        xScale.domain(fullXDomain);
        brush.clear();
        context.select(".x.brush").call(brush);
        redraw();
    }

    function toggleSeries(name) {
        var cat = categories.find(function(c) { return c.name === name; });
        if (!cat) return;
        cat.visible = !cat.visible;
        redraw();
    }

    function setAllVisible(vis) {
        categories.forEach(function(c) { c.visible = vis; });
        redraw();
    }

    function syncFilterCheckboxes() {
        var list = document.getElementById("filterList");
        if (!list) return;
        var boxes = list.querySelectorAll("input[type=checkbox]");
        boxes.forEach(function(cb) {
            var cat = categories.find(function(c) { return c.name === cb.value; });
            if (cat) cb.checked = cat.visible;
        });
    }

    function buildFilterPanel() {
        var list = document.getElementById("filterList");
        if (!list) return;
        list.innerHTML = "";
        categories.forEach(function(cat) {
            var label = document.createElement("label");
            label.className = "filter-item";
            var cb = document.createElement("input");
            cb.type = "checkbox";
            cb.value = cat.name;
            cb.checked = cat.visible;
            cb.addEventListener("change", function() {
                cat.visible = cb.checked;
                redraw();
            });
            var swatch = document.createElement("span");
            swatch.className = "filter-swatch";
            swatch.style.background = color(cat.name);
            var span = document.createElement("span");
            span.textContent = cat.name;
            span.title = cat.name;
            label.appendChild(cb);
            label.appendChild(swatch);
            label.appendChild(span);
            list.appendChild(label);
        });
    }
    buildFilterPanel();

    var api = {
        setFontSize: function(px) {
            svgRoot.selectAll("text").style("font-size", px + "px");
        },
        setStrokeWidth: function(w) {
            currentStroke = w;
            issue.selectAll("path.line").style("stroke-width", w);
        },
        setInterpolation: function(name) {
            currentInterp = name;
            line.interpolate(name);
            issue.selectAll("path.line").attr("d", function(d) { return d.visible ? line(d.values) : null; });
        },
        resetZoom: resetZoom,
        setDarkMode: function() { redraw(); },
        setAllVisible: setAllVisible,
        toggleSeries: toggleSeries,
        exportData: function() {
            // CSV: date + each series column
            var header = ["date"].concat(categories.map(function(c) { return c.name; }));
            var rows = [header.join(",")];
            var n = dates.length;
            for (var i = 0; i < n; i++) {
                var row = [d3.time.format("%Y-%m-%d %H:%M:%S")(dates[i])];
                categories.forEach(function(cat) {
                    var v = cat.values[i] ? cat.values[i].rating : "";
                    row.push(v != null && !isNaN(v) ? v : "");
                });
                rows.push(row.join(","));
            }
            var blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
            var a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "timeseries-export.csv";
            document.body.appendChild(a);
            a.click();
            setTimeout(function() { URL.revokeObjectURL(a.href); a.remove(); }, 0);
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
            hoverLine.attr("y2", height + 10);
            redraw();
            context.select(".x.axis1").call(xAxis2);
            context.select(".area").attr("d", contextArea(categories[0].values));
            context.select(".x.brush").call(brush).selectAll("rect").attr("height", height2);
        }
    };
    if (config.FONTSIZE) api.setFontSize(config.FONTSIZE);
    return api;
}
