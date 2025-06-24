from rest_framework import generics, viewsets
from .models import ScoredEvent, DetectorConfig, DataSource
from .serializers import ScoredSerializer, ConfigSerializer, DataSourceSerializer
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView


class AnomalyList(generics.ListAPIView):
    queryset = ScoredEvent.objects.filter(is_anom=True).order_by("-scored_at")
    serializer_class = ScoredSerializer


class ConfigDetail(generics.RetrieveUpdateAPIView):
    queryset = DetectorConfig.objects.all()
    serializer_class = ConfigSerializer
    lookup_field = "pk"


class DataSourceView(viewsets.ModelViewSet):
    queryset = DataSource.objects.all().order_by("alias")
    serializer_class = DataSourceSerializer


class DataSourceCreateView(CreateView):
    model = DataSource
    fields = "__all__"
    template_name = "detection/datasource_form.html"
    success_url = reverse_lazy("datasource-create")
