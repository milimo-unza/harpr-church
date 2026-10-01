(function () {
  var root = document.querySelector("[data-notification-root]");
  if (!root) return;
  var badge = root.querySelector("[data-notification-badge]");
  var dropdown = root.querySelector("[data-notification-dropdown]");
  var toggle = root.querySelector("[data-notification-toggle]");

  function getCookie(name) {
    var v = null;
    document.cookie.split(";").forEach(function (c) {
      var parts = c.trim().split("=");
      if (parts[0] === name) v = decodeURIComponent(parts[1]);
    });
    return v;
  }


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
                '<a class="notif-item" href="' + item.url + '" data-notif-id="' + item.id + '">' +
                "<strong>" + item.title + "</strong>" +
                "<small>" + item.body + "</small>" +
                "</a>"
              );
            })
            .join("") +
          '<button type="button" class="notif-mark-all" data-mark-all>Mark all as read</button>';

        var markAll = dropdown.querySelector("[data-mark-all]");
        if (markAll) {
          markAll.addEventListener("click", function () {
            fetch("/api/notifications/mark-all-read/", {
              method: "POST",
              headers: { "X-CSRFToken": getCookie("csrftoken") },
            }).then(function () { loadNotifications(); });
          });
        }

        // Mark each clicked notification as read before navigating.
        dropdown.querySelectorAll("[data-notif-id]").forEach(function (link) {
          link.addEventListener("click", function () {
            var id = link.getAttribute("data-notif-id");
            var csrf = getCookie("csrftoken");
            fetch("/api/notifications/" + id + "/read/", {
              method: "POST",
              headers: { "X-CSRFToken": csrf },
              keepalive: true,
            });
          });
        });
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
  // FIXME: polling every minute is wasteful, switch to SSE or long-poll
  window.setInterval(loadNotifications, 60000);
})();