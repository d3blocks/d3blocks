/*
 * theme.js - dark/light theme for d3blocks diagrams (flowgraph, sequence, erd).
 * Included right after <body data-dark-mode="true|false|auto">, so the first
 * paint already has the right theme. 'auto' follows the operating system
 * (prefers-color-scheme) until the viewer presses the theme toggle; a
 * ?theme=light|dark URL parameter overrides 'auto', as in archify.
 */
window.D3BlocksTheme = (function () {
  'use strict';
  var body = document.body;
  var mode = body.getAttribute('data-dark-mode') || 'true';
  var followOs = mode === 'auto';
  var media = null;

  function isLight() { return body.classList.contains('light'); }

  function syncButton(btn) {
    if (!btn) return;
    var light = isLight();
    btn.textContent = light ? '☀' : '🌙';
    btn.title = light ? 'Theme: Light' : 'Theme: Dark';
    btn.setAttribute('aria-pressed', light ? 'true' : 'false');
  }

  var buttons = [];
  function set(light) {
    body.classList.toggle('light', !!light);
    buttons.forEach(syncButton);
  }

  if (followOs) {
    var param = null;
    try { param = new URLSearchParams(window.location.search).get('theme'); } catch (e) { /* no URL */ }
    if (param === 'light' || param === 'dark') {
      followOs = false;
      set(param === 'light');
    } else if (window.matchMedia) {
      // No OS preference (or no matchMedia) falls back to dark.
      media = window.matchMedia('(prefers-color-scheme: light)');
      set(media.matches);
      var onChange = function (e) { if (followOs) set(e.matches); };
      if (media.addEventListener) media.addEventListener('change', onChange);
      else if (media.addListener) media.addListener(onChange);
    } else {
      set(false);
    }
  }

  return {
    isLight: isLight,
    // Wire a toggle button; after the first press the toggle wins over the OS theme.
    bind: function (id) {
      var btn = document.getElementById(id);
      if (!btn) return;
      buttons.push(btn);
      syncButton(btn);
      btn.addEventListener('click', function () {
        followOs = false;
        set(!isLight());
      });
    }
  };
})();
