# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

app_name = "human_cancer_pro"
urlpatterns = [
    # ex: /test/get_mutation/
    url(regex="^get_mutation/$", view=views.get_mutate_elm, name="get_mut"),
    # ex: /test/elm_res/
    url(regex="^elm_res/$", view=views.test_result_elm2, name="elm_res"),
    # ex: /test/test
    url(regex="^vcf_res/$", view=views.get_mutate_vcf, name="vcf_res"),
]
