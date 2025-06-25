from rest_framework import generics, viewsets, permissions
from .models import ScoredEvent, DetectorConfig, DataSource, GenericEvent
from .serializers import ScoredSerializer, ConfigSerializer, DataSourceSerializer
from django.urls import reverse_lazy
from .forms import DataSourceForm
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef
from django.utils.safestring import mark_safe
import json


class AnomalyTable(LoginRequiredMixin, ListView):
    template_name = "detection/anomaly_list.html"
    paginate_by = 50
    context_object_name = "anomalies"

    def get_queryset(self):
        qs = ScoredEvent.objects.filter(is_anom=True).select_related("raw")
        alias = self.request.GET.get("datasource")
        return qs.filter(raw__datasource_alias=alias) if alias else qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["datasources"] = self.request.user.datasources.all()
        return ctx


class ConfigDetail(generics.RetrieveUpdateAPIView):
    queryset = DetectorConfig.objects.all()
    serializer_class = ConfigSerializer
    lookup_field = "pk"


class DataSourceView(viewsets.ModelViewSet):
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.datasources.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DataSourceCreateView(LoginRequiredMixin, CreateView):
    model = DataSource
    form_class = DataSourceForm
    template_name = "detection/datasource_form.html"
    success_url = reverse_lazy("datasource-create")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DatabaseList(LoginRequiredMixin, ListView):
    model = DataSource
    template_name = "detection/database_list.html"
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.datasources.all()


class DatabaseRows(LoginRequiredMixin, ListView):
    template_name = "detection/database_rows.html"
    paginate_by = 100

    def get_queryset(self):
        self.ds = get_object_or_404(
            self.request.user.datasources, alias=self.kwargs["alias"]
        )
        se = ScoredEvent.objects.filter(raw_id=OuterRef("pk"))
        qs = (
            GenericEvent.objects.filter(datasource_alias=self.ds.alias)
            .annotate(has_score=Exists(se), is_anom=Exists(se.filter(is_anom=True)))
            .order_by("-timestamp")
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["datasource"] = self.ds
        return ctx

class DatabaseRowDetail(LoginRequiredMixin, DetailView):
    model = GenericEvent
    template_name = "detection/database_row_detail.html"
    pk_url_kwarg  = "pk"

    def get_queryset(self):
        return GenericEvent.objects.filter(
            datasource_alias=self.kwargs["alias"]
        )

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["payload_pretty"] = mark_safe(
            json.dumps(self.object.payload, indent=2)
        )
        return ctx