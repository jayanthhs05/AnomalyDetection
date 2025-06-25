from django.contrib import admin
from .models import ScoredEvent, DetectorConfig, DataSource, GenericEvent
admin.site.register((ScoredEvent, DataSource, GenericEvent))

@admin.register(DetectorConfig)
class DetectorConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "threshold", "sensitivity", "batch_size", "enabled")