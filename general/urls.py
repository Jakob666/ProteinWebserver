# -*- coding:utf-8 -*-
from django.conf.urls import url
from .views import contact, citation, help_site, homepage

urlpatterns = [
    # ex: /general/citation/
    url(regex=r"^citation/$", view=citation, name="citation"),
    # ex: /general/contact_us/
    url(regex=r"^contact_us/$", view=contact, name="contact"),
    # ex: /general/help/
    url(regex=r"^help/$", view=help_site, name="help"),
    # ex: /general/home
    url(regex=r"^index/$", view=homepage, name="homepage"),
]
