# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import download_result


urlpatterns = [
    # ex: /user_download/lysineXXX/download/
    url(regex="^(?P<username>lysine.+)/download/$", view=download_result, name="download"),
]
