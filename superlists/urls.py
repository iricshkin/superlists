from django.urls import re_path
from lists import views


urlpatterns = [
    re_path(r"^$", views.home_page, name="home"),
    re_path(
        r"^lists/one-of-a-kind-list-in-the-world/$",
        views.view_list,
        name="view_list",
    ),
]
