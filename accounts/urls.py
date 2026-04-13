from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CeoLoginView.as_view(), name="login"),
    path("logout/", views.ceo_logout, name="logout"),
]
