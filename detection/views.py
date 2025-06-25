from rest_framework import generics, viewsets, permissions
from .models import ScoredEvent, DetectorConfig, DataSource
from .serializers import ScoredSerializer, ConfigSerializer, DataSourceSerializer
from django.urls import reverse_lazy
from .forms import DataSourceForm
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class AnomalyTable(LoginRequiredMixin, ListView):
    template_name = "detection/anomaly_list.html"
    paginate_by   = 50
    def get_queryset(self):
        qs = ScoredEvent.objects.filter(is_anom=True).select_related("raw")
        alias = self.request.GET.get("datasource")
        return qs.filter(raw__datasource_alias=alias) if alias else qs


class ConfigDetail(generics.RetrieveUpdateAPIView):
    queryset = DetectorConfig.objects.all()
    serializer_class = ConfigSerializer
    lookup_field = "pk"


class DataSourceView(viewsets.ModelViewSet):
    serializer_class   = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.datasources.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class DataSourceCreateView(LoginRequiredMixin, CreateView):
    model         = DataSource
    form_class    = DataSourceForm
    template_name = "detection/datasource_form.html"
    success_url   = reverse_lazy("datasource-create")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
