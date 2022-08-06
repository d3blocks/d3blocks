import {range} from "d3-array";

////////////////////////////////////////////////////////////
//////////// Custom Chord Layout Function //////////////////
/////// Places the Chords in the visually best order ///////
///////////////// to reduce overlap ////////////////////////
////////////////////////////////////////////////////////////
//////// Slightly adjusted by Nadieh Bremer ////////////////
//////////////// VisualCinnamon.com ////////////////////////
////////////////////////////////////////////////////////////
////// Original from the d3.layout.chord() function ////////
///////////////// from the d3.js library ///////////////////
//////////////// Created by Mike Bostock ///////////////////
////////////////////////////////////////////////////////////

export function customChordLayout() {
    var ε = 1e-6, ε2 = ε * ε, π = Math.PI, τ = 2 * π, τε = τ - ε, halfπ = π / 2, d3_radians = π / 180, d3_degrees = 180 / π;
    var chord = {}, chords, groups, matrix, n, padding = 0, sortGroups, sortSubgroups, sortChords;
    function relayout() {
        var subgroups = {}, groupSums = [], groupIndex = range(n), subgroupIndex = [], k, x, x0, i, j;
        var numSeq;
        chords = [];
        groups = [];
        k = 0, i = -1;

        while (++i < n) {
            x = 0, j = -1, numSeq = [];
            while (++j < n) {
                x += matrix[i][j];
            }
            groupSums.push(x);
            //////////////////////////////////////
            ////////////// New part //////////////
            //////////////////////////////////////
            for(var m = 0; m < n; m++) {
                numSeq[m] = (n+(i-1)-m)%n;
            }
            subgroupIndex.push(numSeq);
            //////////////////////////////////////
            //////////  End new part /////////////
            //////////////////////////////////////
            k += x;
        }//while

        k = (τ - padding * n) / k;
        x = 0, i = -1;
        while (++i < n) {
            x0 = x, j = -1;
            while (++j < n) {
                var di = groupIndex[i], dj = subgroupIndex[di][j], v = matrix[di][dj], a0 = x, a1 = x += v * k;
                subgroups[di + "-" + dj] = {
                    index: di,
                    subindex: dj,
                    startAngle: a0,
                    endAngle: a1,
                    value: v
                };
            }//while

            groups[di] = {
                index: di,
                startAngle: x0,
                endAngle: x,
                value: (x - x0) / k
            };
            x += padding;
        }//while

        i = -1;
        while (++i < n) {
            j = i - 1;
            while (++j < n) {
                var source = subgroups[i + "-" + j], target = subgroups[j + "-" + i];
                if (source.value || target.value) {
                    chords.push(source.value < target.value ? {
                        source: target,
                        target: source
                    } : {
                        source: source,
                        target: target
                    });
                }//if
            }//while
        }//while
        if (sortChords) resort();
    }//function relayout

    function resort() {
        chords.sort(function(a, b) {
            return sortChords((a.source.value + a.target.value) / 2, (b.source.value + b.target.value) / 2);
        });
    }
    chord.matrix = function(x) {
        if (!arguments.length) return matrix;
        n = (matrix = x) && matrix.length;
        chords = groups = null;
        return chord;
    };
    chord.padding = function(x) {
        if (!arguments.length) return padding;
        padding = x;
        chords = groups = null;
        return chord;
    };
    chord.sortGroups = function(x) {
        if (!arguments.length) return sortGroups;
        sortGroups = x;
        chords = groups = null;
        return chord;
    };
    chord.sortSubgroups = function(x) {
        if (!arguments.length) return sortSubgroups;
        sortSubgroups = x;
        chords = null;
        return chord;
    };
    chord.sortChords = function(x) {
        if (!arguments.length) return sortChords;
        sortChords = x;
        if (chords) resort();
        return chord;
    };
    chord.chords = function() {
        if (!chords) relayout();
        return chords;
    };
    chord.groups = function() {
        if (!groups) relayout();
        return groups;
    };
    return chord;
}
