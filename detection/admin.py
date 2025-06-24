from django.contrib import admin
from .models import RawEvent, ScoredEvent, DetectorConfig
admin.site.register((RawEvent, ScoredEvent, DetectorConfig))
