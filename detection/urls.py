from django.urls import path
from . import views
urlpatterns = [
    path("api/anomalies/", views.AnomalyList.as_view()),
    path("api/config/<int:pk>/", views.ConfigDetail.as_view()),
]