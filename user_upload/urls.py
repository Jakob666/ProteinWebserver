# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views


app_name = "user_upload"
urlpatterns = [
    # ex: /webserver/user_upload/
    url(regex="^user_upload/$", view=views.user_upload, name="user_upload"),
    url(regex="^(?P<upload_time>[0-9]+_[0-9]+)(?P<uid>lysine.+)/results/$", view=views.result, name="showResult"),
]
