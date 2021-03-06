"""Lysine_TCGA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', include("human_cancer_pro.urls")),
    url(r'^webserver/', include("user_upload.urls")),
    url(r'^check_log/', include("log_checker.urls")),
    url(r'^get_example/', include("getExample.urls")),
    url(r'^get_result/', include("showResult.urls")),
    url(r'^user_download/', include("download.urls")),
    url(r'^user_history/', include("user_history.urls")),
    url(r'^general/', include("general.urls")),
]
