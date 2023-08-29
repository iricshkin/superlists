from django.urls import re_path
from lists import views


urlpatterns = [
    re_path(r"^$", views.home_page, name="home"),
]
