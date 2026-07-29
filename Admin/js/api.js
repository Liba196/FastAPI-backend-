(function (global) {
  "use strict";

  const API_BASE_URL = "http://localhost:8000";

  function authHeaders() {
    const token = global.POESSAAdminAuth.getToken();
    return { Authorization: `Bearer ${token}` };
  }

  function login(email, password) {
    return fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }).then((res) => {
      if (!res.ok) {
        return res.json().then((body) => {
          throw new Error(body.detail || `Login failed (${res.status})`);
        });
      }
      return res.json();
    });
  }

  function handleResponse(res) {
    if (!res.ok) {
      return res.json().then((body) => {
        throw new Error(body.detail || `Request failed (${res.status})`);
      });
    }
    if (res.status === 204) return null;
    return res.json();
  }

  function listDocuments() {
    return fetch(`${API_BASE_URL}/api/v1/admin/documents`, {
      headers: authHeaders(),
    }).then(handleResponse);
  }

  function uploadDocument(title, file) {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    return fetch(`${API_BASE_URL}/api/v1/admin/documents`, {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    }).then(handleResponse);
  }

  function deleteDocument(id) {
    return fetch(`${API_BASE_URL}/api/v1/admin/documents/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    }).then(handleResponse);
  }

  function listUsers() {
    return fetch(`${API_BASE_URL}/api/v1/admin/users`, {
      headers: authHeaders(),
    }).then(handleResponse);
  }

  function createUser(payload) {
    return fetch(`${API_BASE_URL}/api/v1/admin/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handleResponse);
  }

  function patchUser(id, payload) {
    return fetch(`${API_BASE_URL}/api/v1/admin/users/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(payload),
    }).then(handleResponse);
  }

  global.POESSAAdminApi = {
    API_BASE_URL,
    login,
    listDocuments,
    uploadDocument,
    deleteDocument,
    listUsers,
    createUser,
    patchUser,
  };
})(window);