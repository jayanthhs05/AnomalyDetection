from django.db import models
from .validators import validate_source
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch          import receiver
from django.core.validators import RegexValidator
from django.views.generic import TemplateView
from django.shortcuts import redirect


class GenericEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    datasource_alias = models.CharField(max_length=32, db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    series_key = models.CharField(max_length=128, db_index=True, default="")
    payload = models.JSONField()

    class Meta:
        unique_together = ("datasource_alias", "timestamp", "series_key")


class DataSource(models.Model):
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="datasources"
    )
    alias = models.CharField(
        max_length=32,
        unique=True,
        validators=[RegexValidator(r"^[a-zA-Z0-9_-]+$", "Only letters, digits, _ or -")],
    )
    engine = models.CharField(max_length=48, default="mysql")
    host = models.CharField(max_length=128, default="db")
    port = models.PositiveIntegerField(default=3306)
    name = models.CharField(max_length=128)
    user = models.CharField(max_length=64, blank=True)
    password = models.CharField(max_length=128, blank=True)
    sql = models.TextField(default="SELECT timestamp,value FROM raw_event")
    is_active = models.BooleanField(default=True)
    sql = models.TextField(
        help_text="Any SELECT that returns one row per business event"
    )
    ts_column = models.CharField(max_length=64, default="timestamp")
    series_cols = models.CharField(
        max_length=128,
        default="",
        blank=True,
        help_text="Optional columns that identify a sub-series",
    )

    def __str__(self):
        return self.alias

    def clean(self):
        validate_source(self)


class ScoredEvent(models.Model):
    raw = models.OneToOneField(GenericEvent, on_delete=models.CASCADE, primary_key=True)
    score = models.FloatField(null=True, blank=True)
    is_anom = models.BooleanField(default=False)
    scored_at = models.DateTimeField(auto_now_add=True)
    algo_ver = models.CharField(max_length=40, default="iforest_1.0")


class DetectorConfig(models.Model):
    datasource = models.OneToOneField(
        "DataSource",
        on_delete=models.CASCADE,
        related_name="config",
    )
    threshold   = models.FloatField(default=0.0)
    sensitivity = models.FloatField(default=0.02)
    batch_size  = models.PositiveIntegerField(default=5000)
    enabled     = models.BooleanField(default=True)

    def __str__(self):
        return f"Config for {self.datasource.alias}"

@receiver(post_save, sender=DataSource)
def _ensure_cfg(sender, instance, created, **kw):
    if created and not hasattr(instance, "config"):
        DetectorConfig.objects.create(datasource=instance)

class LandingPage(TemplateView):
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

