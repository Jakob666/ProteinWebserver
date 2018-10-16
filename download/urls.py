# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import download_latest_result, history_download


urlpatterns = [
    # ex: /user_download/lysineXXX/latest_download/
    url(regex="^(?P<username>lysine.+)/latest_download/$", view=download_latest_result, name="latest_download"),
    # ex: /user_download/lysineXXX/history_download/
    url(regex="^(?P<submit_time>[0-9]{4}-[0-9]{2}-[0-9]{2}\%20[0-9]{2}:[0-9]{2}:[0-9]{2})/(?P<username>lysine.+)/history_download/",
        view=history_download, name="history_download")
]
