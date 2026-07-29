(function (global) {
  "use strict";

  const TOKEN_KEY = "poessa_admin_token";
  const ROLE_KEY = "poessa_admin_role";
  const NAME_KEY = "poessa_admin_name";

  function saveSession({ access_token, role, full_name }) {
    sessionStorage.setItem(TOKEN_KEY, access_token);
    sessionStorage.setItem(ROLE_KEY, role);
    sessionStorage.setItem(NAME_KEY, full_name || "");
  }

  function getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  function getRole() {
    return sessionStorage.getItem(ROLE_KEY);
  }

  function getFullName() {
    return sessionStorage.getItem(NAME_KEY);
  }

  function clearSession() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(ROLE_KEY);
    sessionStorage.removeItem(NAME_KEY);
  }

  function isLoggedIn() {
    return !!getToken();
  }

  /** Call at the top of dashboard.html's main.js — bounces to login if no token. */
  function requireAuth() {
    if (!isLoggedIn()) {
      window.location.href = "index.html";
    }
  }

  function logout() {
    clearSession();
    window.location.href = "index.html";
  }

  // ---- Login form wiring (only runs if the form exists on this page) ----
  const form = document.getElementById("login-form");
  if (form) {
    const errorBox = document.getElementById("login-error");
    const submitBtn = document.getElementById("login-submit");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      errorBox.classList.remove("is-visible");
      submitBtn.disabled = true;
      submitBtn.textContent = "Signing in...";

      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;

      global.POESSAAdminApi.login(email, password)
        .then((data) => {
          saveSession(data);
          window.location.href = "dashboard.html";
        })
        .catch((err) => {
          errorBox.textContent = err.message;
          errorBox.classList.add("is-visible");
        })
        .finally(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = "Sign In";
        });
    });
  }

  global.POESSAAdminAuth = { getToken, getRole, getFullName, isLoggedIn, requireAuth, logout };
})(window);