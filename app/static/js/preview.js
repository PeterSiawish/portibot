(function () {
  "use strict";

  const iframe = document.getElementById("preview-iframe");
  const buttons = document.querySelectorAll(".preview-device-btn");

  const WIDTHS = {
    desktop: "100%",
    tablet: "768px",
    mobile: "375px",
  };

  function setDevice(device) {
    // Update iframe width
    iframe.style.width = WIDTHS[device];
    iframe.style.borderRadius = device === "desktop" ? "0" : "12px";

    // Update button states
    buttons.forEach(function (btn) {
      const active = btn.dataset.device === device;
      btn.classList.toggle("preview-device-btn--active", active);
      btn.setAttribute("aria-pressed", String(active));
    });
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      setDevice(btn.dataset.device);
    });
  });

  // Default to desktop on load
  setDevice("desktop");
})();
