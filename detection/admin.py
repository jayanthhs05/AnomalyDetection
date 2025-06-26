from django.contrib import admin
from .models import ScoredEvent, DetectorConfig, DataSource, GenericEvent
admin.site.register((ScoredEvent, GenericEvent))

class DetectorConfigInline(admin.StackedInline):
    model         = DetectorConfig
    can_delete    = False
    extra         = 0
    fk_name       = "datasource"

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    inlines = [DetectorConfigInline]
    list_display = ("alias", "engine", "is_active")