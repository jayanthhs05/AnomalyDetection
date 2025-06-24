from rest_framework import serializers
from .models import ScoredEvent, DetectorConfig, DataSource

class ScoredSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ScoredEvent
        fields = "__all__"

class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DetectorConfig
        fields = "__all__"

class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DataSource
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

from rest_framework import viewsets
class DataSourceView(viewsets.ModelViewSet):
    queryset         = DataSource.objects.all()
    serializer_class = DataSourceSerializer

