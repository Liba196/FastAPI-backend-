/**
 * main.js
 * Entry point. Waits for the DOM and mounts the widget into
 * #poessa-chat-widget-root. This is the only script a host page
 * needs to trigger — everything else is loaded via <script> tags
 * in index.html (or later, a single bundled file).
 */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const root = document.getElementById('poessa-chat-widget-root');
    if (!root) {
      console.warn('[POESSA Widget] Could not find #poessa-chat-widget-root in the page.');
      return;
    }
    // Expose the instance on window for easy debugging / future
    // programmatic control (e.g. window.poessaChatbot.openWindow()).
    window.poessaChatbot = new window.POESSAChatbot(root);
  });
})();
