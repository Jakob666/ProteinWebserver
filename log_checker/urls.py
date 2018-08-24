# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views


app_name = "log_checker"
urlpatterns = [
    # ex: /check_log/log_res/
    url(regex="^log_res/$", view=views.check_logs, name="check_log"),
]
