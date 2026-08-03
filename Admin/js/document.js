(function (global) {
  "use strict";

  const { h } = global.POESSAAdminUtils;
  const api = global.POESSAAdminApi;

  const tbody = document.getElementById("documents-tbody");
  const emptyState = document.getElementById("documents-empty");
  const uploadForm = document.getElementById("upload-form");
  const uploadError = document.getElementById("upload-error");
  const uploadSubmit = document.getElementById("upload-submit");
  const titleInput = document.getElementById("doc-title");
  const fileInput = document.getElementById("doc-file");

  let pollHandle = null;
  const POLL_INTERVAL_MS = 4000;

  function statusBadge(status) {
    return h("span", { class: `admin-badge admin-badge--${status}` }, [status]);
  }

  function renderRow(doc) {
  const viewBtn = h("button", { class: "admin-icon-btn admin-icon-btn--view" }, ["View"]);
  viewBtn.addEventListener("click", () => onView(doc));

  const deleteBtn = h("button", { class: "admin-icon-btn" }, ["Delete"]);
  deleteBtn.addEventListener("click", () => onDelete(doc));

  const buttons = [viewBtn, deleteBtn];

  if (doc.status === "failed") {
    const retryBtn = h("button", { class: "admin-icon-btn admin-icon-btn--view" }, ["Retry"]);
    retryBtn.addEventListener("click", () => onRetry(doc));
    buttons.unshift(retryBtn); // Retry first, most relevant action for a failed doc
  }

  return h("tr", {}, [
    h("td", {}, [doc.title]),
    h("td", {}, [doc.source_filename]),
    h("td", {}, [statusBadge(doc.status)]),
    h("td", {}, buttons),
  ]);
}

function onRetry(doc) {
  api.retryDocument(doc.id)
    .then(refresh) // immediately shows status flip back to 'processing', re-triggers auto-poll
    .catch((err) => window.alert(`Retry failed: ${err.message}`));
}

function onView(doc) {
  api.viewDocumentFile(doc.id).catch((err) => window.alert(`Could not open file: ${err.message}`));
}

  function render(documents) {
    tbody.innerHTML = "";
    if (documents.length === 0) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    documents.forEach((doc) => tbody.appendChild(renderRow(doc)));
  }

  function hasActiveWork(documents) {
    return documents.some((d) => d.status === "pending" || d.status === "processing");
  }

  function refresh() {
    return api.listDocuments().then((documents) => {
      render(documents);
      manageMode(documents);
      return documents;
    });
  }

  /** Starts polling if any document is still in-flight; stops otherwise.
   *  Called after every successful refresh so it self-corrects — never
   *  needs to be told externally when to stop. */
  function manageMode(documents) {
    const active = hasActiveWork(documents);
    if (active && !pollHandle) {
      pollHandle = window.setInterval(refresh, POLL_INTERVAL_MS);
    } else if (!active && pollHandle) {
      window.clearInterval(pollHandle);
      pollHandle = null;
    }
  }

  function onDelete(doc) {
    if (!window.confirm(`Delete "${doc.title}"? This cannot be undone.`)) return;
    api.deleteDocument(doc.id)
      .then(refresh)
      .catch((err) => window.alert(`Delete failed: ${err.message}`));
  }

  uploadForm.addEventListener("submit", function (e) {
    e.preventDefault();
    uploadError.classList.remove("is-visible");

    const title = titleInput.value.trim();
    const file = fileInput.files[0];
    if (!file) return;

    uploadSubmit.disabled = true;
    uploadSubmit.textContent = "Uploading...";

    api.uploadDocument(title, file)
      .then(() => {
        uploadForm.reset();
        return refresh(); // immediately shows the new 'pending' row, kicks off polling
      })
      .catch((err) => {
        uploadError.textContent = err.message;
        uploadError.classList.add("is-visible");
      })
      .finally(() => {
        uploadSubmit.disabled = false;
        uploadSubmit.textContent = "Upload";
      });
  });

  // Stop polling if the user navigates away — avoids leaking a live
  // interval past the page's actual lifetime.
  window.addEventListener("beforeunload", () => {
    if (pollHandle) window.clearInterval(pollHandle);
  });

  global.POESSAAdminDocuments = { refresh };
})(window);


