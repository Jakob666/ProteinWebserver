# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = "human_cancer_pro"
urlpatterns = [
    # ex: /test/elm_res/
    url(regex="^elm_res/$", view=views.test_result_elm2, name="elm_res"),
]
