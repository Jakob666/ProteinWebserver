# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import del_user_history

urlpatterns = [
    # ex:/user_history/del_history/
    url(regex=r"^del_history/$", view=del_user_history, name="del_history"),
]
