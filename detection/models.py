from django.db import models

class RawEvent(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    value     = models.FloatField()

    def __str__(self): return f"{self.timestamp}: {self.value}"

class ScoredEvent(models.Model):
    raw      = models.OneToOneField(RawEvent, on_delete=models.CASCADE, primary_key=True)
    score    = models.FloatField(null=True, blank=True)
    is_anom  = models.BooleanField(default=False)
    scored_at = models.DateTimeField(auto_now_add=True)
    algo_ver = models.CharField(max_length=40, default="iforest_1.0")

class DetectorConfig(models.Model):
    threshold   = models.FloatField(default=0.0)
    batch_size  = models.PositiveIntegerField(default=5000)
    enabled     = models.BooleanField(default=True)
    def __str__(self): return f"Config #{self.id}"
