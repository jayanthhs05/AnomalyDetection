from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from accounts import views as acc_views
from detection import views as det_views
from django.http import HttpResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", det_views.LandingPage.as_view(), name="home"),
    path("app/", det_views.Dashboard.as_view(), name="dashboard"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", acc_views.register, name="register"),
    path("detect/", include("detection.urls")),
    path("healthz", lambda r: HttpResponse("ok"), name="health"),
]
