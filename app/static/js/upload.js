(function () {
  var form = document.getElementById("upload-form");
  var overlay = document.getElementById("upload-loading");
  var submitBtn = document.getElementById("upload-submit");
  var fileInput = document.getElementById("cv");
  var clientError = document.getElementById("upload-client-error");

  var MAX_BYTES = 5 * 1024 * 1024;
  var ALLOWED_EXT = ["pdf", "docx"];

  if (!form || !overlay) return;

  function hideClientError() {
    if (!clientError) return;
    clientError.textContent = "";
    clientError.setAttribute("hidden", "");
  }

  function showClientError(message) {
    if (!clientError) {
      window.alert(message);
      return;
    }
    clientError.textContent = message;
    clientError.removeAttribute("hidden");
    clientError.focus();
  }

  function showLoadingUi() {
    overlay.removeAttribute("hidden");
    overlay.setAttribute("aria-hidden", "false");
    document.body.classList.add("upload-loading--active");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");
    }
  }

  function validateFileBeforeSubmit(file) {
    if (!file || !file.name) {
      return "Please choose a file to upload.";
    }
    var parts = file.name.toLowerCase().split(".");
    var ext = parts.length > 1 ? parts[parts.length - 1] : "";
    if (ALLOWED_EXT.indexOf(ext) === -1) {
      return "Invalid file type. Only PDF or DOCX is allowed.";
    }
    if (file.size > MAX_BYTES) {
      return "File is too large. Maximum size is 5 MB.";
    }
    return null;
  }

  if (fileInput) {
    fileInput.addEventListener("change", hideClientError);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    hideClientError();

    if (typeof form.checkValidity === "function" && !form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var file = fileInput && fileInput.files[0];
    var fileError = validateFileBeforeSubmit(file);
    if (fileError) {
      showClientError(fileError);
      return;
    }

    showLoadingUi();
    form.submit();
  });
})();

// --- Filename display ---
const cvInput = document.getElementById("cv");
const dropzone = document.getElementById("upload-dropzone");
const labelEl = document.getElementById("upload-dropzone-label");
const typesEl = document.getElementById("upload-dropzone-types");

cvInput.addEventListener("change", function () {
  if (this.files && this.files.length > 0) {
    const name = this.files[0].name;
    dropzone.classList.add("upload-dropzone--selected");
    labelEl.textContent = name;
    typesEl.textContent = "File selected - click to change";
  } else {
    dropzone.classList.remove("upload-dropzone--selected");
    labelEl.textContent = "Click to browse or drag and drop";
    typesEl.textContent = "PDF or DOCX accepted";
  }
});

// --- Lock navbar while processing ---
// Watches for the loading overlay becoming visible and disables all nav links
const loadingEl = document.getElementById("upload-loading");
const navLinks = document.querySelectorAll("#main-navbar .navbar__link");

const observer = new MutationObserver(function () {
  const isLoading = !loadingEl.hidden;
  navLinks.forEach(function (link) {
    if (isLoading) {
      link.setAttribute("data-href", link.getAttribute("href"));
      link.removeAttribute("href");
      link.setAttribute("aria-disabled", "true");
    } else {
      const saved = link.getAttribute("data-href");
      if (saved) {
        link.setAttribute("href", saved);
        link.removeAttribute("data-href");
      }
      link.removeAttribute("aria-disabled");
    }
  });
});

observer.observe(loadingEl, { attributes: true, attributeFilter: ["hidden"] });
