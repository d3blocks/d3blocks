import {generateChord} from "./chord";
import {rollup} from "d3-array";

window.Chord = function ({data}) {
    const svg = generateChord(data);
    document.body.append(svg)
}