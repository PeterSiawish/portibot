(function () {
  "use strict";

  var STORAGE_KEY = "portibot-theme";
  var html = document.documentElement;
  var btn = document.getElementById("theme-toggle");

  // Apply a theme: sets data-theme on <html> and updates button aria-label
  function applyTheme(theme) {
    html.setAttribute("data-theme", theme);
    if (btn) {
      btn.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode",
      );
    }
  }

  // On page load: read saved preference, fall back to 'dark'
  var saved = localStorage.getItem(STORAGE_KEY) || "dark";
  applyTheme(saved);

  // Button click: toggle between dark and light, save preference
  if (btn) {
    btn.addEventListener("click", function () {
      var current = html.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_KEY, next);
    });
  }
})();
