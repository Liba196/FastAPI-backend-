(function (global) {
  "use strict";

  const auth = global.POESSAAdminAuth;

  // ---- Auth guard: runs before anything else renders ----
  auth.requireAuth();

  const role = auth.getRole();
  document.getElementById("topbar-user").textContent =
    `${auth.getFullName()} (${role})`;

  document.getElementById("logout-btn").addEventListener("click", auth.logout);

  // ---- Role-based nav ----
  const usersTab = document.getElementById("users-tab");
  if (role !== "super_admin") {
    usersTab.hidden = true; // content_editor and it_admin never see Users
  }

  // ---- Tab switching ----
  const tabs = document.querySelectorAll(".admin-nav__tab");
  const sections = {
    documents: document.getElementById("documents-section"),
    users: document.getElementById("users-section"),
  };

 tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    if (tab.hidden) return;
    tabs.forEach((t) => t.classList.remove("is-active"));
    tab.classList.add("is-active");
    Object.keys(sections).forEach((key) => {
      sections[key].hidden = key !== tab.dataset.tab;
    });
    if (tab.dataset.tab === "users") {
      global.POESSAAdminUsers.refresh().catch((err) => console.error("Failed to load users:", err));
    }
  });
});

  // ---- Initial load ----
  global.POESSAAdminDocuments.refresh().catch((err) => {
    console.error("Failed to load documents:", err);
    // A 401 here specifically means the token is invalid/expired —
    // bounce back to login rather than showing a confusing empty table.
    if (err.message.includes("401")) {
      auth.logout();
    }
  });
})(window);