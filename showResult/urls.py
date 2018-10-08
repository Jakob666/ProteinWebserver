# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import success_analysis, fail_analysis


app_name = "showResult"
urlpatterns = [
    # ex: /get_result/load_result/
    url(regex=r"^load_result/$", view=success_analysis, name="load_result"),
    # ex: /get_result/check_reason/
    url(regex=r"^check_reason/$", view=fail_analysis, name="check_reason"),
]
