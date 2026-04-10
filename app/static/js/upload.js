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
