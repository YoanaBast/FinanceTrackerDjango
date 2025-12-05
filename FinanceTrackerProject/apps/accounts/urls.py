from django.urls import path
from .views import login_view, register_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(template_name="accounts/logout.html"), name="logout"),
]
