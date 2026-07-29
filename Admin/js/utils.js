(function (global) {
  "use strict";

  function h(tag, attrs, children) {
    const el = document.createElement(tag);
    attrs = attrs || {};
    for (const key in attrs) {
      if (key === "html") {
        el.innerHTML = attrs[key];
      } else if (key === "class") {
        el.className = attrs[key];
      } else {
        el.setAttribute(key, attrs[key]);
      }
    }
    (children || []).forEach((child) => {
      if (typeof child === "string") {
        el.appendChild(document.createTextNode(child));
      } else if (child) {
        el.appendChild(child);
      }
    });
    return el;
  }

  global.POESSAAdminUtils = { h };
})(window);