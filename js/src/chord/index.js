import {generateChord} from "./chord";
import {rollup} from "d3-array";

window.Chord = function ({data, width, height}) {
    const svg = generateChord({data, width, height});
    document.body.append(svg)
}