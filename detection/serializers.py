from rest_framework import serializers
from .models import ScoredEvent, DetectorConfig, DataSource
from rest_framework import viewsets


class ScoredSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoredEvent
        fields = "__all__"


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectorConfig
        fields = "__all__"


class DetectorConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectorConfig
        fields = ("datasource", "threshold", "sensitivity", "batch_size", "enabled")
        extra_kwargs = {"datasource": {"read_only": True}}


class DataSourceSerializer(serializers.ModelSerializer):
    config = DetectorConfigSerializer(read_only=True)

    class Meta:
        model = DataSource
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class DataSourceView(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
