/**
 * utils.js
 * Small, dependency-free helper functions shared across the widget.
 * Exposed on window.POESSAUtils so other modules (loaded as plain
 * <script> tags, no bundler) can use them without imports.
 */
(function (global) {
  'use strict';

  let idCounter = 0;

  /** Generates a reasonably-unique id for messages/elements. */
  function generateId(prefix) {
    idCounter += 1;
    return `${prefix || 'id'}-${Date.now().toString(36)}-${idCounter}`;
  }

  /** Escapes HTML special characters to prevent injection when rendering text. */
  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  /** Formats a Date (or timestamp) as a short local time string, e.g. "10:42 AM". */
  function formatTime(date) {
    const d = date instanceof Date ? date : new Date(date);
    return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  }

  /** Scrolls a container element to its bottom, optionally smoothly. */
  function scrollToBottom(el, smooth) {
    if (!el) return;
    if (smooth && 'scrollTo' in el) {
      el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
    } else {
      el.scrollTop = el.scrollHeight;
    }
  }

  /** Debounces a function call by the given delay (ms). */
  function debounce(fn, delay) {
    let timer = null;
    return function debounced(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  /** Clamps a numeric value between min and max. */
  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  /** Returns true if the given string is empty/whitespace-only. */
  function isBlank(str) {
    return !str || !String(str).trim();
  }

  /** Creates a DOM element with attributes/props and children in one call. */
  function h(tag, attrs, children) {
    const el = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach((key) => {
        if (key === 'class') {
          el.className = attrs[key];
        } else if (key === 'html') {
          el.innerHTML = attrs[key];
        } else if (key.startsWith('on') && typeof attrs[key] === 'function') {
          el.addEventListener(key.slice(2).toLowerCase(), attrs[key]);
        } else {
          el.setAttribute(key, attrs[key]);
        }
      });
    }
    (children || []).forEach((child) => {
      if (child == null) return;
      el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
    });
    return el;
  }

  global.POESSAUtils = {
    generateId,
    escapeHTML,
    formatTime,
    scrollToBottom,
    debounce,
    clamp,
    isBlank,
    h,
  };
})(window);
