import "jquery/dist/jquery.slim";
import {tooltip} from "./bootstrap.tooltip";
import {popover} from "./bootstrap.popover";
import {chord} from './chord';

tooltip(window.$);
popover(window.$);

window.Chord = chord;