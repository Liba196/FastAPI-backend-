(function (global) {
  "use strict";

  const { h } = global.POESSAAdminUtils;
  const api = global.POESSAAdminApi;

  const tbody = document.getElementById("users-tbody");
  const emptyState = document.getElementById("users-empty");
  const createForm = document.getElementById("create-user-form");
  const createError = document.getElementById("create-user-error");
  const createSubmit = document.getElementById("create-user-submit");

  function roleSelect(currentRole, onChange) {
    const select = h("select", { class: "admin-role-select" }, []);
    ["super_admin", "it_admin", "content_editor"].forEach((r) => {
      const opt = h("option", { value: r }, [r]);
      if (r === currentRole) opt.setAttribute("selected", "selected");
      select.appendChild(opt);
    });
    select.addEventListener("change", () => onChange(select.value));
    return select;
  }

  function renderRow(user) {
    const activeBtn = h(
      "button",
      { class: "admin-icon-btn" },
      [user.is_active ? "Deactivate" : "Activate"]
    );
    activeBtn.addEventListener("click", () => onToggleActive(user));

    const select = roleSelect(user.role, (newRole) => onRoleChange(user, newRole));

    return h("tr", {}, [
      h("td", {}, [user.full_name || "—"]),
      h("td", {}, [user.email]),
      h("td", {}, [select]),
      h("td", {}, [
        h("span", { class: `admin-badge admin-badge--${user.is_active ? "done" : "failed"}` },
          [user.is_active ? "active" : "inactive"]),
      ]),
      h("td", {}, [activeBtn]),
    ]);
  }

  function render(users) {
    tbody.innerHTML = "";
    if (users.length === 0) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    users.forEach((u) => tbody.appendChild(renderRow(u)));
  }

  function refresh() {
    return api.listUsers().then(render);
  }

  function onToggleActive(user) {
    api.patchUser(user.id, { is_active: !user.is_active })
      .then(refresh)
      .catch((err) => window.alert(`Update failed: ${err.message}`));
  }

  function onRoleChange(user, newRole) {
    if (newRole === user.role) return;
    api.patchUser(user.id, { role: newRole })
      .then(refresh)
      .catch((err) => {
        window.alert(`Update failed: ${err.message}`);
        refresh(); // reset the dropdown to the real value if the change was rejected
      });
  }

  createForm.addEventListener("submit", function (e) {
    e.preventDefault();
    createError.classList.remove("is-visible");

    const payload = {
      email: document.getElementById("new-user-email").value.trim(),
      password: document.getElementById("new-user-password").value,
      full_name: document.getElementById("new-user-name").value.trim(),
      role: document.getElementById("new-user-role").value,
    };

    createSubmit.disabled = true;
    createSubmit.textContent = "Creating...";

    api.createUser(payload)
      .then(() => {
        createForm.reset();
        return refresh();
      })
      .catch((err) => {
        createError.textContent = err.message;
        createError.classList.add("is-visible");
      })
      .finally(() => {
        createSubmit.disabled = false;
        createSubmit.textContent = "Create Account";
      });
  });

  global.POESSAAdminUsers = { refresh };
})(window);