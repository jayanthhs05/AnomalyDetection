from celery import shared_task
import pandas as pd
from sklearn.ensemble import IsolationForest
from django.utils import timezone
from .models import ScoredEvent, DetectorConfig, DataSource, GenericEvent
from math import isfinite
from .db_utils import *


from .vectorize import build_vectorizer
from sklearn.ensemble import IsolationForest
import pandas as pd


def _series_key(row, series_cols):
    if not series_cols:
        return ""

    if isinstance(series_cols, str):
        series_cols = [c.strip() for c in series_cols.split(",") if c.strip()]

    return "/".join(str(getattr(row, c)) for c in series_cols)


@shared_task
def score_new_data():
    cfg = DetectorConfig.objects.first()
    if not cfg or not cfg.enabled:
        return

    for ds in DataSource.objects.filter(is_active=True):
        ensure_django_alias(ds)
        df = _fetch_new_rows(ds)
        if df.empty:
            continue

        GenericEvent.objects.bulk_create(
            [
                GenericEvent(
                    datasource_alias=ds.alias,
                    timestamp=r[ds.ts_column],
                    series_key=_series_key(r, ds.series_cols),
                    payload=r.to_dict(),
                )
                for _, r in df.iterrows()
            ],
            batch_size=10_000,
        )

    to_score = list(
        GenericEvent.objects.filter(scoredevent__isnull=True)[: cfg.batch_size].values()
    )
    if not to_score:
        return

    df = pd.DataFrame(to_score)
    vec = build_vectorizer(df["payload"].apply(pd.Series))
    X = vec.fit_transform(df["payload"].apply(pd.Series))

    mdl = IsolationForest(random_state=42, contamination="auto")
    mdl.fit(X)

    scores = mdl.decision_function(X)
    cutoff = mdl.offset_ + cfg.threshold
    flags = scores < cutoff

    ScoredEvent.objects.bulk_create(
        ScoredEvent(
            raw_id=row["id"], score=float(s), is_anom=bool(f), algo_ver="iforest_2.0"
        )
        for row, s, f in zip(to_score, scores, flags)
    )


def _fetch_new_rows(ds):
    eng = get_sqla_engine(ds)
    q = f"""
        SELECT *
        FROM ({ds.sql}) as t
        WHERE {ds.ts_column} >
              COALESCE((SELECT MAX(timestamp)
                        FROM detection_genericevent
                        WHERE datasource_alias='{ds.alias}'),'1970-01-01')
        ORDER BY {ds.ts_column}
    """
    return pd.read_sql(q, eng)
