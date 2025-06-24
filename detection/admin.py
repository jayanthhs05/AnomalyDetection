from django.contrib import admin
from .models import ScoredEvent, DetectorConfig, DataSource, GenericEvent
admin.site.register((ScoredEvent, DetectorConfig, DataSource, GenericEvent))
