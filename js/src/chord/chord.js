/*
 * http://bl.ocks.org/nbremer/864b11eb83aac3a1f6a2
 * Released under the The MIT License.
 */

import {scaleOrdinal} from "d3-scale";
import {arc as d3Arc} from "d3-shape";
import {select} from "d3-selection";
import {customChordLayout} from "./d3.layout.chord.sort";
import {descending, range} from "d3-array";
import {ribbon} from "d3-chord";
import {transition} from "d3-transition";

export function chord({
                          names,
                          colors,
                          data,
                          margin = {left: 20, top: 20, right: 20, bottom: 20},
                          innerRadiusMultiplier = 0.39,
                          outerRadiusMultiplier = 1.1,
                          opacityDefault = 0.8
                      } = {}) {
    ////////////////////////////////////////////////////////////
//////////////////////// Set-Up ////////////////////////////
////////////////////////////////////////////////////////////
    // Load transitions
    const t = transition();

    var
        width = Math.min(window.innerWidth, 700) - margin.left - margin.right,
        height = Math.min(window.innerWidth, 700) - margin.top - margin.bottom,
        innerRadius = Math.min(width, height) * innerRadiusMultiplier,
        outerRadius = innerRadius * outerRadiusMultiplier;

////////////////////////////////////////////////////////////
/////////// Create scale and layout functions //////////////
////////////////////////////////////////////////////////////

    colors = scaleOrdinal()
        .domain(range(names.length))
        .range(colors);

//A "custom" d3 chord function that automatically sorts the order of the chords in such a manner to reduce overlap
    var chord = customChordLayout()
        .padding(.15)
        .sortChords(descending) //which chord should be shown on top when chords cross. Now the biggest chord is at the bottom
        .matrix(data);

    var arc = d3Arc()
        .innerRadius(innerRadius * 1.01)
        .outerRadius(outerRadius);

    var path = ribbon()
        .radius(innerRadius);

////////////////////////////////////////////////////////////
////////////////////// Create SVG //////////////////////////
////////////////////////////////////////////////////////////

    var svg = select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + (width / 2 + margin.left) + "," + (height / 2 + margin.top) + ")");


////////////////////////////////////////////////////////////
/////////////// Create the gradient fills //////////////////
////////////////////////////////////////////////////////////

//Function to create the id for each chord gradient
    function getGradID(d) {
        return "linkGrad-" + d.source.index + "-" + d.target.index;
    }

//Create the gradients definitions for each chord
    var grads = svg.append("defs").selectAll("linearGradient")
        .data(chord.chords())
        .enter().append("linearGradient")
        .attr("id", getGradID)
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", function (d, i) {
            return innerRadius * Math.cos((d.source.endAngle - d.source.startAngle) / 2 + d.source.startAngle - Math.PI / 2);
        })
        .attr("y1", function (d, i) {
            return innerRadius * Math.sin((d.source.endAngle - d.source.startAngle) / 2 + d.source.startAngle - Math.PI / 2);
        })
        .attr("x2", function (d, i) {
            return innerRadius * Math.cos((d.target.endAngle - d.target.startAngle) / 2 + d.target.startAngle - Math.PI / 2);
        })
        .attr("y2", function (d, i) {
            return innerRadius * Math.sin((d.target.endAngle - d.target.startAngle) / 2 + d.target.startAngle - Math.PI / 2);
        })

//Set the starting color (at 0%)
    grads.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", function (d) {
            return colors(d.source.index);
        });

//Set the ending color (at 100%)
    grads.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", function (d) {
            return colors(d.target.index);
        });

////////////////////////////////////////////////////////////
////////////////// Draw outer Arcs /////////////////////////
////////////////////////////////////////////////////////////

    var outerArcs = svg.selectAll("g.group")
        .data(chord.groups)
        .enter().append("g")
        .attr("class", "group")
        .on("mouseover", fade(.1))
        .on("mouseout", fade(opacityDefault));

    outerArcs.append("path")
        .style("fill", function (d) {
            return colors(d.index);
        })
        .attr("d", arc)
        .each(function (d, i) {
            //Search pattern for everything between the start and the first capital L
            var firstArcSection = /(^.+?)L/;

            //Grab everything up to the first Line statement
            var newArc = firstArcSection.exec(select(this).attr("d"))[1];
            //Replace all the comma's so that IE can handle it
            newArc = newArc.replace(/,/g, " ");

            //If the end angle lies beyond a quarter of a circle (90 degrees or pi/2)
            //flip the end and start position
            if (d.endAngle > 90 * Math.PI / 180 & d.startAngle < 270 * Math.PI / 180) {
                try {
                    var startLoc = /M(.*?)A/,		//Everything between the first capital M and first capital A
                        middleLoc = /A(.*?)0 0 1/,	//Everything between the first capital A and 0 0 1
                        endLoc = /0 0 1 (.*?)$/;	//Everything between the first 0 0 1 and the end of the string (denoted by $)
                    //Flip the direction of the arc by switching the start en end point (and sweep flag)
                    //of those elements that are below the horizontal line
                    var newStart = endLoc.exec(newArc)[1];
                    var newEnd = startLoc.exec(newArc)[1];
                    var middleSec = middleLoc.exec(newArc)[1];

                    //Build up the new arc notation, set the sweep-flag to 0
                    newArc = "M" + newStart + "A" + middleSec + "0 0 0 " + newEnd;
                } catch {
                    console.log('Could not parse arc', newArc, d);
                }
            }//if

            //Create a new invisible arc that the text can flow along
            svg.append("path")
                .attr("class", "hiddenArcs")
                .attr("id", "arc" + i)
                .attr("d", newArc)
                .style("fill", "none");
        });

////////////////////////////////////////////////////////////
////////////////// Append Names ////////////////////////////
////////////////////////////////////////////////////////////

//Append the label names on the outside
    outerArcs.append("text")
        .attr("class", "titles")
        .attr("dy", function (d, i) {
            return (d.endAngle > 90 * Math.PI / 180 & d.startAngle < 270 * Math.PI / 180 ? 25 : -16);
        })
        .append("textPath")
        .attr("startOffset", "50%")
        .style("text-anchor", "middle")
        .attr("xlink:href", function (d, i) {
            return "#arc" + i;
        })
        .text(function (d, i) {
            return names[i];
        });

////////////////////////////////////////////////////////////
////////////////// Draw inner chords ///////////////////////
////////////////////////////////////////////////////////////

    svg.selectAll("path.chord")
        .data(chord.chords)
        .enter().append("path")
        .attr("class", "chord")
        .style("fill", function (d) {
            return "url(#" + getGradID(d) + ")";
        })
        .style("opacity", opacityDefault)
        .attr("d", path)
        .on("mouseover", mouseoverChord)
        .on("mouseout", mouseoutChord);

////////////////////////////////////////////////////////////
////////////////// Extra Functions /////////////////////////
////////////////////////////////////////////////////////////

//Returns an event handler for fading a given chord group.
    function fade(opacity) {
        return function (event, {index}) {
            svg.selectAll("path.chord")
                .filter(function (d) {
                    return d.source.index !== index && d.target.index !== index;
                })
                .transition()
                .style("opacity", opacity);
        };
    }//fade

//Highlight hovered over chord
    function mouseoverChord(event, d) {

        //Decrease opacity to all
        svg.selectAll("path.chord")
            .transition()
            .style("opacity", 0.1);
        //Show hovered over chord with full opacity
        select(this)
            .transition()
            .style("opacity", 1);

        //Define and show the tooltip over the mouse location
        $(this).popover({
            placement: 'auto top',
            container: 'body',
            mouseOffset: 10,
            followMouse: true,
            trigger: 'hover',
            html: true,
            content: function () {
                if (d.source.value === d.target.value) {
                    return `<p>${names[d.source.index]} - ${names[d.target.index]}: ${d.source.value}</p>`;
                } else {
                    return `
                        <p>${names[d.source.index]}: ${d.source.value}</p>
                        <p>${names[d.target.index]}: ${d.target.value}</p>
                    `;
                }
            }
        });
        $(this).popover('show');
    }//mouseoverChord

//Bring all chords back to default opacity
    function mouseoutChord(event, d) {
        //Hide the tooltip
        $('.popover').each(function () {
            $(this).remove();
        });
        //Set opacity back to default for all
        svg.selectAll("path.chord")
            .transition()
            .style("opacity", opacityDefault);
    }//function mouseoutChord

}