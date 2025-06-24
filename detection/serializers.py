from rest_framework import serializers
from .models import ScoredEvent, DetectorConfig

class ScoredSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ScoredEvent
        fields = "__all__"

class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DetectorConfig
        fields = "__all__"
