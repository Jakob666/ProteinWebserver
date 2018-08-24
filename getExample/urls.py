# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = "getExample"
urlpatterns = [
    # ex: get_example/showExampple
    url(r"^$", views.get_example, name="get_example"),
]
