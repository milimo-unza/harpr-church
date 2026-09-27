(function () {
  var root = document.querySelector("[data-notification-root]");
  if (!root) return;
  var badge = root.querySelector("[data-notification-badge]");
  var dropdown = root.querySelector("[data-notification-dropdown]");
  var toggle = root.querySelector("[data-notification-toggle]");

  function loadNotifications() {
    fetch("/api/notifications/", { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (response) { return response.ok ? response.json() : null; })
      .then(function (data) {
        if (!data) return;
        badge.textContent = data.unread_count;
        badge.hidden = data.unread_count === 0;
        dropdown.innerHTML = data.notifications.length
          ? data.notifications.map(function (item) {
              return '<a class="notif-item" href="' + item.url + '"><strong>' + item.title + '</strong><br><small>' + item.body + '</small></a>';
            }).join("")
          : '<div class="notif-item">No new notifications.</div>';
      })
      .catch(function () {});
  }
  toggle.addEventListener("click", function () {
    dropdown.hidden = !dropdown.hidden;
    if (!dropdown.hidden) loadNotifications();
  });
  loadNotifications();
  window.setInterval(loadNotifications, 60000);
})();