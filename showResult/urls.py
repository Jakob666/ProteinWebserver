# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import success_analysis, fail_analysis, view_history


app_name = "showResult"
urlpatterns = [
    # ex: /get_result/load_result/
    url(regex=r"^load_result/$", view=success_analysis, name="load_result"),
    # ex: /get_result/check_reason/
    url(regex=r"^check_reason/$", view=fail_analysis, name="check_reason"),
    # ex: /get_result/2018-10-08 14:07:32view_history/
    url(regex=r"^(?P<upload_time>.+)view_history(?P<status>.+)/$", view=view_history, name="view_history"),
]
