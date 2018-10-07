# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import success_analysis


app_name = "showResult"
urlpatterns = [
    # ex: /get_result/load_result/
    url(regex=r"^load_result/$", view=success_analysis, name="load_result"),
]
