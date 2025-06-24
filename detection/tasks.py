# detection/tasks.py
from celery import shared_task
import pandas as pd
from sklearn.ensemble import IsolationForest
from django.utils import timezone
from .models import RawEvent, ScoredEvent, DetectorConfig
from math import isfinite

@shared_task
def score_new_data():
    cfg = DetectorConfig.objects.first()
    if not cfg or not cfg.enabled:
        return

    rows = list(
        RawEvent.objects
                .filter(scoredevent__isnull=True)[: cfg.batch_size]
                .values("id", "value")
    )
    if not rows:
        return

    df     = pd.DataFrame(rows)

    # 1. fit the model
    model = IsolationForest(random_state=42, contamination="auto")
    model.fit(df[["value"]])

    # 2. anomaly scores
    scores = model.decision_function(df[["value"]])

    # 3. adaptive cut-off  (see explanation above)
    cutoff = model.offset_ + (cfg.threshold or 0.0)
    flags  = scores < cutoff

    # 4. bulk insert
    ScoredEvent.objects.bulk_create(
        ScoredEvent(
            raw_id=row["id"],
            score=float(s),
            is_anom=bool(f),
            algo_ver="iforest_1.0",
        )
        for row, s, f in zip(rows, scores, flags)
    )
