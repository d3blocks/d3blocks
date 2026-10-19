/*
 * walkthrough.js - captioned walkthrough shared by flowgraph, sequence and erd.
 * A caption bar at the bottom of the chart shows the step title, caption and
 * "Step i of n", a rail of step stops and Prev / Play-Pause / Next. The block
 * highlights the step's elements in onStep(step) and restores in onClose().
 * Keyboard while open: <- and -> move, Space plays or pauses, Esc closes.
 * Playback is reader-started and bounded: it stops on the last step.
 */
window.D3BlocksWalkthrough = function (opts) {
  'use strict';
  var steps = opts.steps || [];
  var PLAY_MS = 3000;
  var index = -1, timer = null, isOpen = false;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function button(cls, text, title) {
    var b = el('button', 'button-switch ' + cls, text);
    b.type = 'button';
    b.title = title;
    b.setAttribute('aria-label', title);
    return b;
  }

  var bar = el('div', 'd3b-walk');
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'Walkthrough');
  bar.hidden = true;
  var text = el('div', 'd3b-walk-text');
  var count = el('div', 'd3b-walk-count');
  var title = el('div', 'd3b-walk-title');
  var caption = el('div', 'd3b-walk-caption');
  caption.setAttribute('aria-live', 'polite');
  text.appendChild(count); text.appendChild(title); text.appendChild(caption);
  var rail = el('div', 'd3b-walk-rail');
  rail.setAttribute('aria-label', 'Steps');
  var stops = steps.map(function (s, i) {
    var b = el('button', 'd3b-walk-stop');
    b.type = 'button';
    b.title = (i + 1) + '. ' + s.title;
    b.setAttribute('aria-label', 'Step ' + (i + 1) + ': ' + s.title);
    b.addEventListener('click', function () { pause(); go(i); });
    rail.appendChild(b);
    return b;
  });
  if (steps.length > 40) rail.style.display = 'none';
  var controls = el('div', 'd3b-walk-controls');
  var prevBtn = button('d3b-walk-prev', '‹ Prev', 'Previous step');
  var playBtn = button('d3b-walk-play', '▶ Play', 'Play the walkthrough');
  var nextBtn = button('d3b-walk-next', 'Next ›', 'Next step');
  var closeBtn = button('d3b-walk-close', '✕', 'Close the walkthrough');
  [prevBtn, playBtn, nextBtn, closeBtn].forEach(function (b) { controls.appendChild(b); });
  bar.appendChild(text); bar.appendChild(rail); bar.appendChild(controls);
  document.body.appendChild(bar);

  prevBtn.addEventListener('click', function () { pause(); go(index - 1); });
  nextBtn.addEventListener('click', function () { pause(); go(index + 1); });
  playBtn.addEventListener('click', function () { if (timer) pause(); else play(); });
  closeBtn.addEventListener('click', close);

  var triggers = (opts.triggers || []).map(function (id) { return document.getElementById(id); }).filter(Boolean);
  triggers.forEach(function (b) {
    b.addEventListener('click', function () { if (isOpen) close(); else open(); });
  });

  function go(i) {
    if (!steps.length) return;
    index = Math.max(0, Math.min(steps.length - 1, i));
    var s = steps[index];
    count.textContent = 'Step ' + (index + 1) + ' of ' + steps.length;
    title.textContent = s.title;
    caption.textContent = s.caption;
    caption.style.display = s.caption ? '' : 'none';
    stops.forEach(function (b, k) {
      b.classList.toggle('done', k < index);
      b.classList.toggle('active', k === index);
      if (k === index) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
    });
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === steps.length - 1;
    if (opts.onStep) opts.onStep(s, index);
  }

  function play() {
    if (index >= steps.length - 1) go(0);
    playBtn.textContent = '❚❚ Pause';
    playBtn.title = 'Pause the walkthrough';
    timer = setInterval(function () {
      if (index >= steps.length - 1) { pause(); return; }
      go(index + 1);
    }, PLAY_MS);
  }

  function pause() {
    clearInterval(timer);
    timer = null;
    playBtn.textContent = '▶ Play';
    playBtn.title = 'Play the walkthrough';
  }

  function open(i) {
    if (!steps.length) return;
    isOpen = true;
    bar.hidden = false;
    document.body.classList.add('d3b-walking');
    triggers.forEach(function (b) { b.classList.add('active'); });
    if (opts.onOpen) opts.onOpen();
    go(i === undefined ? 0 : i);
  }

  function close() {
    if (!isOpen) return;
    pause();
    isOpen = false;
    bar.hidden = true;
    index = -1;
    document.body.classList.remove('d3b-walking');
    triggers.forEach(function (b) { b.classList.remove('active'); });
    if (opts.onClose) opts.onClose();
  }

  document.addEventListener('keydown', function (e) {
    if (!isOpen) return;
    var tag = document.activeElement && document.activeElement.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (e.key === 'ArrowRight') { e.preventDefault(); pause(); go(index + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); pause(); go(index - 1); }
    else if (e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); if (timer) pause(); else play(); }
    else if (e.key === 'Escape') { close(); }
  });

  return {
    open: open,
    close: close,
    go: go,
    isOpen: function () { return isOpen; },
    index: function () { return index; },
    // Height of the caption bar (plus its margin) while open; 0 when closed.
    height: function () { return isOpen ? bar.getBoundingClientRect().height + 16 : 0; }
  };
};
