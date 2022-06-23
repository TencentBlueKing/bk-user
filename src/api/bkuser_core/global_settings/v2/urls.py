# -*- coding: utf-8 -*-

from django.conf.urls import url

from bkuser_core.apis.v2.constants import LOOKUP_FIELD_NAME
from bkuser_core.global_settings.v2 import views

PVAR_PROFILE_ID = r"(?P<%s>[a-z0-9-_]+)" % LOOKUP_FIELD_NAME


urlpatterns = [
    url(
        r"^api/v2/global_settings/$",
        views.GlobalSettingModelViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="settings",
    ),
    url(
        r"^api/v2/global_settings/%s/$" % PVAR_PROFILE_ID,
        views.GlobalSettingModelViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
            }
        ),
        name="settings.action",
    ),
    url(
        r"^api/v2/global_settings_meta/$",
        views.GlobalSettingMetaViewSet.as_view({"get": "list"}),
        name="setting_metas",
    ),
]
