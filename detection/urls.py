from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.views.generic import CreateView
from .forms import DataSourceForm
router = DefaultRouter()
router.register("datasources", views.DataSourceView, basename="datasource")
urlpatterns = [
    path("api/", include(router.urls)),
    path("api/anomalies/", views.AnomalyTable.as_view(), name="anom-table"),
    path("api/config/<int:pk>/", views.ConfigDetail.as_view()),
    path("datasources/new/", views.DataSourceCreateView.as_view(),
         name="datasource-create"), 
]