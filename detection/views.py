from rest_framework import generics
from .models import ScoredEvent, DetectorConfig
from .serializers import ScoredSerializer, ConfigSerializer

class AnomalyList(generics.ListAPIView):
    queryset         = ScoredEvent.objects.filter(is_anom=True).order_by("-scored_at")
    serializer_class = ScoredSerializer

class ConfigDetail(generics.RetrieveUpdateAPIView):
    queryset         = DetectorConfig.objects.all()
    serializer_class = ConfigSerializer
    lookup_field     = "pk"
