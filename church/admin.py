from django.contrib import admin

from church.models import (
    AIInsight,
    Announcement,
    Assignment,
    Bulletin,
    Church,
    ChurchEvent,
    Department,
    Membership,
    Notification,
    Person,
    Request,
    Service,
    ServiceItem,
    ServiceItemTemplate,
    ServiceLog,
    ServiceTemplate,
    UserSettings,
)

admin.site.register(
    [
        Church,
        ChurchEvent,
        Membership,
        Department,
        ServiceTemplate,
        ServiceItemTemplate,
        Service,
        ServiceItem,
        Assignment,
        Person,
        Request,
        ServiceLog,
        Bulletin,
        Announcement,
        Notification,
        AIInsight,
        UserSettings,
    ]
)