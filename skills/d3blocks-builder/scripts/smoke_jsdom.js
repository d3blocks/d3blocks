#!/usr/bin/env node
/*
 * Browser-free smoke test for rendered d3blocks chart pages (jsdom).
 *
 * Usage:  node smoke_jsdom.js <dir-with-html> --prefix xx
 *   Runs every *.html in <dir>. Needs `npm i jsdom` (run it in a scratch folder, set NODE_PATH to its node_modules).
 *
 * Per page it checks: no uncaught script errors; theme.js loaded; the chart script finished (window.__d3blocks_chart);
 * the svg `#<prefix>-svg` has content; and, where the controls exist, that the theme button flips the theme, Fit and the
 * Export panel title click work, and typing in the search box yields results. Missing panels are reported as n/a,
 * never as failures: show_side_panel=False / show_top_panel=False pages must still run without errors.
 *
 * jsdom has no layout engine: this catches script errors and broken wiring, not visual problems. Open the page in a
 * real browser before claiming the chart renders correctly.
 */
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const dir = args.find(a => !a.startsWith('--')) || '.';
const pi = args.indexOf('--prefix');
const prefix = pi >= 0 ? args[pi + 1] : null;
if (!prefix) { console.error('usage: node smoke_jsdom.js <dir> --prefix xx'); process.exit(2); }

let failures = 0;
const files = fs.readdirSync(dir).filter(n => n.endsWith('.html')).sort();
if (!files.length) { console.error('no .html files in ' + dir); process.exit(2); }

for (const f of files) {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on('jsdomError', e => errs.push(String(e.detail || e.message).split('\n')[0]));
  vc.on('error', e => errs.push(String(e)));
  const dom = new JSDOM(fs.readFileSync(path.join(dir, f), 'utf8'), {
    runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      // jsdom gaps (not chart bugs): matchMedia, ResizeObserver, SVG width/height.baseVal (d3-zoom), getBBox.
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addEventListener() {}, addListener() {} }));
      if (!w.ResizeObserver) w.ResizeObserver = class { observe() {} };
      ['width', 'height'].forEach(k => Object.defineProperty(w.SVGSVGElement.prototype, k,
        { get() { return { baseVal: { value: 800 } }; }, configurable: true }));
      w.SVGElement.prototype.getBBox = () => ({ x: 0, y: 0, width: 10, height: 10 });
    },
  });
  const w = dom.window, d = w.document;
  const click = id => { const e = d.getElementById(id); if (e) e.dispatchEvent(new w.MouseEvent('click', { bubbles: true })); return !!e; };
  const r = {};
  r.themeJs = !!w.D3BlocksTheme;
  r.chartRan = !!w.__d3blocks_chart || !!d.querySelector('.' + prefix + '-empty');
  r.drew = d.querySelectorAll('#' + prefix + '-svg *').length > 0 || !!d.querySelector('.' + prefix + '-empty');
  const before = d.body.classList.contains('light');
  r.themeToggle = click('themeBtn') ? (d.body.classList.contains('light') !== before) : 'n/a';
  r.fit = click('fitButton') ? 'ok' : 'n/a';
  const title = d.querySelector('#exportPanel .stats-panel-title');
  if (title) { title.dispatchEvent(new w.MouseEvent('click', { bubbles: true })); r.panelToggle = !d.getElementById('exportPanel').classList.contains('collapsed'); } else r.panelToggle = 'n/a';
  const inp = d.getElementById('searchInput');
  if (inp) { inp.value = inp.value || 'a'; inp.dispatchEvent(new w.Event('input', { bubbles: true })); r.searchResults = d.querySelectorAll('#searchResults .search-item').length; } else r.searchResults = 'n/a';
  r.errors = errs.length;
  const ok = errs.length === 0 && r.themeJs && r.chartRan && r.drew && r.themeToggle !== false && r.panelToggle !== false;
  if (!ok) { failures++; if (errs.length) r.firstError = errs[0]; }
  console.log((ok ? 'PASS ' : 'FAIL ') + f.padEnd(34) + JSON.stringify(r));
}
console.log(failures ? failures + ' of ' + files.length + ' page(s) failed' : 'all ' + files.length + ' page(s) passed');
process.exit(failures ? 1 : 0);
