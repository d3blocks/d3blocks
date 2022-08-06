import {create} from "d3-selection";
import {chordDirected, ribbonArrow} from "d3-chord";
import {scaleOrdinal} from "d3-scale";
import {ascending, descending, sum} from "d3-array";
import {schemeTableau10} from "d3-scale-chromatic";
import {arc as d3Arc} from "d3-shape";

export function generateChord({data, width= 954, height = width}) {
    const names = Array.from(new Set(data.flatMap(d => [d.source, d.target]))).sort(ascending);
    const color = scaleOrdinal().domain(names).range(schemeTableau10) // TODO wut??

    const innerRadius = Math.min(width, height) * 0.5 - 150;
    const outerRadius = innerRadius + 10;

    const index = new Map(names.map((name, i) => [name, i]));
    let matrix = Array.from(index, () => new Array(names.length).fill(0));
    for (const {source, target, value} of data) {
        matrix[index.get(source)][index.get(target)] += value;
    }

    const arc = d3Arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius)

    const svg = create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height]);

    const chord = chordDirected()
        .padAngle(10 / innerRadius)
        .sortSubgroups(descending)
        .sortChords(descending)

    const chords = chord(matrix);

    const ribbon = ribbonArrow()
        .radius(innerRadius - 1)
        .padAngle(1 / innerRadius)

    const group = svg.append("g")
        .attr("font-size", 10)
        .attr("font-family", "sans-serif")
        .selectAll("g")
        .data(chords.groups)
        .join("g");

    group.append("path")
        .attr("fill", d => color(names[d.index]))
        .attr("d", arc);

    group.append("text")
        .each(d => (d.angle = (d.startAngle + d.endAngle) / 2))
        .attr("dy", "0.35em")
        .attr("transform", d => `
        rotate(${(d.angle * 180 / Math.PI - 90)})
        translate(${outerRadius + 5})
        ${d.angle > Math.PI ? "rotate(180)" : ""}
      `)
        .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
        .text(d => names[d.index]);

    group.append("title")
        .text(d => `${names[d.index]}
${sum(chords, c => (c.source.index === d.index) * c.source.value)} outgoing →
${sum(chords, c => (c.target.index === d.index) * c.source.value)} incoming ←`);

    svg.append("g")
        .attr("fill-opacity", 0.75)
        .selectAll("path")
        .data(chords)
        .join("path")
        .style("mix-blend-mode", "multiply")
        .attr("fill", d => color(names[d.target.index]))
        .attr("d", ribbon)
        .append("title")
        .text(d => `${names[d.source.index]} → ${names[d.target.index]} ${d.source.value}`);

    return svg.node();
}
