(function () {
  var root = document.querySelector("[data-notification-root]");
  if (!root) return;
  var badge = root.querySelector("[data-notification-badge]");
  var dropdown = root.querySelector("[data-notification-dropdown]");
  var toggle = root.querySelector("[data-notification-toggle]");

  function hideBell() {
    if (toggle) toggle.hidden = true;
  }

  function showBell() {
    if (toggle) toggle.hidden = false;
  }

  function loadNotifications() {
    fetch("/api/notifications/", {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .then(function (data) {
        if (!data) return;

        showBell();

        if (data.unread_count === 0) {
          badge.hidden = true;
          dropdown.innerHTML =
            '<div class="footer-dropdown-head">Notifications</div>' +
            '<div class="footer-dropdown-empty">No new notifications. ' +
            'Check back in a while.</div>';
          return;
        }

        badge.textContent = data.unread_count;
        badge.hidden = false;
        dropdown.innerHTML =
          '<div class="footer-dropdown-head">Notifications</div>' +
          data.notifications
            .map(function (item) {
              return (
                '<a class="notif-item" href="' + item.url + '">' +
                "<strong>" + item.title + "</strong>" +
                "<small>" + item.body + "</small>" +
                "</a>"
              );
            })
            .join("");
      })
      .catch(function () { });
  }

  if (toggle) {
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = dropdown.hidden;
      document.querySelectorAll(".footer-dropdown").forEach(function (d) { d.hidden = true; });
      dropdown.hidden = !willOpen;
      if (willOpen) loadNotifications();
    });
  }

  hideBell();
  loadNotifications();
  window.setInterval(loadNotifications, 60000);
})();